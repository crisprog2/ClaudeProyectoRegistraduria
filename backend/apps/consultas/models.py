"""
Modelo de datos de la consulta electoral.

Jerarquía geográfica y electoral:
    Departamento -> Ciudad -> PuestoVotacion -> Mesa -> Persona (donde vota)

Una persona es jurado solo si tiene una DesignacionJurado, que apunta a su
mesa de servicio (puede ser distinta a la mesa donde vota).
"""
from datetime import date

from django.db import models


class Departamento(models.Model):
    """
    Modelo de Departamento.
    Representa un departamento administrativo de Colombia.

    Campos:
        cod_departamento (CharField): Código del departamento, 2 dígitos (PK).
        nombre (CharField): Nombre del departamento.
    """
    cod_departamento = models.CharField(max_length=2, primary_key=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        """Ejemplo: 'Antioquia'."""
        return self.nombre


class Ciudad(models.Model):
    """
    Modelo de Ciudad.
    Representa una ciudad asociada a un departamento.

    Campos:
        cod_ciudad (CharField): Código de la ciudad, 5 dígitos: 2 del departamento + 3 del municipio (PK).
        nombre (CharField): Nombre de la ciudad.
        departamento (ForeignKey): Departamento al que pertenece la ciudad.
    """
    cod_ciudad = models.CharField(max_length=5, primary_key=True)
    nombre = models.CharField(max_length=255)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, db_column='cod_departamento', related_name='ciudades')

    def __str__(self):
        """Ejemplo: 'Medellín'."""
        return self.nombre


class PuestoVotacion(models.Model):
    """
    Modelo de Puesto de Votación.
    Representa un lugar físico donde se vota, asociado a una ciudad.

    Campos:
        cod_puesto (CharField): Código del puesto, hasta 10 caracteres (PK).
        nombre (CharField): Nombre del puesto.
        direccion (CharField): Dirección física.
        ciudad (ForeignKey): Ciudad a la que pertenece el puesto.
    """
    cod_puesto = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, db_column='cod_ciudad', related_name='puestos')

    class Meta:
        verbose_name = 'puesto de votación'
        verbose_name_plural = 'puestos de votación'

    def __str__(self):
        """Ejemplo: 'Colegio Cívico La Esperanza - Calle 48 # 65-20'."""
        return f"{self.nombre} - {self.direccion}"


class Mesa(models.Model):
    """
    Modelo de Mesa de Votación.
    Representa una mesa dentro de un puesto de votación.

    Campos:
        cod_mesa (BigAutoField): ID único de la mesa (PK).
        numero (PositiveSmallIntegerField): Número de la mesa; único dentro de cada puesto.
        puesto (ForeignKey): Puesto de votación al que pertenece la mesa.
    """
    cod_mesa = models.BigAutoField(primary_key=True)
    numero = models.PositiveSmallIntegerField()
    puesto = models.ForeignKey(PuestoVotacion, on_delete=models.PROTECT, db_column='cod_puesto', related_name='mesas')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['puesto', 'numero'], name='mesa_unica_por_puesto'),
        ]

    def __str__(self):
        """
        Ejemplo: 'Mesa 018 · Colegio Cívico La Esperanza'.

        Lee el puesto relacionado: en listados usar select_related('puesto')
        para no hacer una consulta por cada mesa.
        """
        return f"Mesa {self.numero:03d} · {self.puesto.nombre}"


class Persona(models.Model):
    """
    Modelo de Persona.
    Representa a una persona registrada para votar.

    Campos:
        cedula (CharField): Número de cédula, solo dígitos y sin separadores (PK).
        primer_nombre, primer_apellido (CharField): Nombre y apellido obligatorios.
        segundo_nombre, segundo_apellido (CharField): Opcionales.
        genero (CharField): Género de la persona (F, M u O).
        fecha_nacimiento (DateField): Fecha de nacimiento.
        mesa (ForeignKey): Mesa de votación asignada.

    La edad no se guarda: se calcula a partir de fecha_nacimiento (propiedad edad).
    Si la persona fue designada jurado, tiene un registro asociado en
    DesignacionJurado (accesible como persona.designacion_jurado).
    """

    class Genero(models.TextChoices):
        """Valores permitidos para el campo genero (se guarda la letra)."""
        FEMENINO = 'F', 'Femenino'
        MASCULINO = 'M', 'Masculino'
        OTRO = 'O', 'Otro'

    cedula = models.CharField(max_length=10, primary_key=True)
    primer_nombre = models.CharField(max_length=255)
    segundo_nombre = models.CharField(max_length=255, blank=True)
    primer_apellido = models.CharField(max_length=255)
    segundo_apellido = models.CharField(max_length=255, blank=True)
    genero = models.CharField(max_length=1, choices=Genero.choices)
    fecha_nacimiento = models.DateField()
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, db_column='cod_mesa', related_name='votantes')

    def calcular_edad(self, fecha_referencia=None):
        """
        Edad en años cumplidos a la fecha de referencia (hoy si no se indica).

        Recibir la fecha como parámetro permite probar la regla con resultados
        fijos, sin depender del día en que se ejecutan las pruebas. Una persona
        nacida un 29 de febrero cumple años el 1 de marzo en años no bisiestos.
        """
        fecha_referencia = fecha_referencia or date.today()
        cumplio_este_anio = (fecha_referencia.month, fecha_referencia.day) >= (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        return fecha_referencia.year - self.fecha_nacimiento.year - (0 if cumplio_este_anio else 1)

    @property
    def edad(self):
        """Edad actual en años cumplidos. No se guarda en la base de datos."""
        return self.calcular_edad()

    def __str__(self):
        """Ejemplo: 'Carlos Martínez' (primer nombre y primer apellido)."""
        return f"{self.primer_nombre} {self.primer_apellido}"


class DesignacionJurado(models.Model):
    """
    Modelo de Designación como Jurado.
    Representa la designación de una persona como jurado de votación.
    Si una persona no tiene designación, es solo votante.

    Campos:
        cod_designacion (BigAutoField): ID único de la designación (PK).
        persona (OneToOneField): Persona designada; máximo una designación por persona.
        mesa_servicio (ForeignKey): Mesa donde presta servicio como jurado. Puede ser
            distinta a la mesa donde vota; el puesto y la dirección de servicio
            se obtienen a través de la mesa.
        rol (CharField): Rol del jurado (titular o remanente).
    """

    class Rol(models.TextChoices):
        """Roles posibles de un jurado de votación."""
        TITULAR = 'TITULAR', 'Jurado titular'
        REMANENTE = 'REMANENTE', 'Jurado remanente'

    cod_designacion = models.BigAutoField(primary_key=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, db_column='cedula', related_name='designacion_jurado')
    mesa_servicio = models.ForeignKey(Mesa, on_delete=models.PROTECT, db_column='cod_mesa_servicio', related_name='jurados')
    rol = models.CharField(max_length=20, choices=Rol.choices)

    def __str__(self):
        """
        Ejemplo: 'Jurado titular · Carlos Martínez · Mesa 018 · Colegio Cívico La Esperanza'.

        Lee la persona, la mesa y el puesto relacionados: en listados usar
        select_related('persona', 'mesa_servicio__puesto').
        """
        return f"{self.get_rol_display()} · {self.persona} · {self.mesa_servicio}"
