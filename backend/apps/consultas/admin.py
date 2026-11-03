"""
Registro de modelos en el admin de Django para consultar y gestionar los datos de demostración.

Convenciones usadas en todos los ModelAdmin:
    - list_select_related: trae los modelos relacionados en la misma consulta
      que el listado, para no hacer una consulta adicional por fila.
    - autocomplete_fields: selector con búsqueda para las relaciones. Requiere
      que el admin del modelo relacionado defina search_fields.
"""
from django.contrib import admin

from .models import Ciudad, Departamento, DesignacionJurado, Mesa, Persona, PuestoVotacion


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    """Listado de departamentos con búsqueda por código o nombre."""
    list_display = ('cod_departamento', 'nombre')
    search_fields = ('cod_departamento', 'nombre')
    ordering = ('nombre',)


@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    """Listado de ciudades, filtrable por departamento."""
    list_display = ('cod_ciudad', 'nombre', 'departamento')
    list_select_related = ('departamento',)
    list_filter = ('departamento',)
    search_fields = ('cod_ciudad', 'nombre', 'departamento__nombre')
    autocomplete_fields = ('departamento',)
    ordering = ('nombre',)


@admin.register(PuestoVotacion)
class PuestoVotacionAdmin(admin.ModelAdmin):
    """Listado de puestos de votación, filtrable por departamento."""
    list_display = ('cod_puesto', 'nombre', 'direccion', 'ciudad')
    list_select_related = ('ciudad',)
    list_filter = ('ciudad__departamento',)
    search_fields = ('cod_puesto', 'nombre', 'direccion', 'ciudad__nombre')
    autocomplete_fields = ('ciudad',)
    ordering = ('cod_puesto',)


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    """Listado de mesas agrupadas por puesto, filtrable por ciudad."""
    list_display = ('numero', 'puesto', 'ciudad')
    list_select_related = ('puesto__ciudad',)
    list_filter = ('puesto__ciudad',)
    search_fields = ('puesto__nombre', 'puesto__cod_puesto')
    autocomplete_fields = ('puesto',)
    ordering = ('puesto', 'numero')

    @admin.display(description='Ciudad', ordering='puesto__ciudad__nombre')
    def ciudad(self, obj):
        """Ciudad del puesto al que pertenece la mesa."""
        return obj.puesto.ciudad


class EsJuradoFilter(admin.SimpleListFilter):
    """Filtra personas según tengan o no una designación como jurado."""
    title = 'es jurado'
    parameter_name = 'es_jurado'

    def lookups(self, request, model_admin):
        """Opciones del filtro: (valor en la URL, texto visible)."""
        return (('si', 'Sí'), ('no', 'No'))

    def queryset(self, request, queryset):
        """Aplica el filtro según exista o no la designación."""
        if self.value() == 'si':
            return queryset.filter(designacion_jurado__isnull=False)
        if self.value() == 'no':
            return queryset.filter(designacion_jurado__isnull=True)
        return queryset


class DesignacionJuradoInline(admin.StackedInline):
    """Permite ver y editar la designación como jurado desde la ficha de la persona."""
    model = DesignacionJurado
    extra = 0
    max_num = 1
    autocomplete_fields = ('mesa_servicio',)


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    """
    Listado de personas con su mesa de votación y si son jurado.

    La ficha de cada persona incluye su designación como jurado (inline) y
    muestra la edad calculada como campo de solo lectura.
    """
    list_display = ('cedula', 'nombre_completo', 'edad', 'genero', 'mesa', 'puesto', 'es_jurado')
    list_select_related = ('mesa__puesto', 'designacion_jurado')
    list_filter = (EsJuradoFilter, 'genero', 'mesa__puesto__ciudad')
    search_fields = ('cedula', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido')
    autocomplete_fields = ('mesa',)
    readonly_fields = ('edad',)
    inlines = (DesignacionJuradoInline,)
    ordering = ('primer_apellido', 'primer_nombre')

    @admin.display(description='Nombre completo', ordering='primer_apellido')
    def nombre_completo(self, obj):
        """Columna ordenable que muestra Persona.nombre_completo."""
        return obj.nombre_completo

    @admin.display(description='Puesto', ordering='mesa__puesto__nombre')
    def puesto(self, obj):
        """Nombre del puesto donde vota la persona."""
        return obj.mesa.puesto.nombre

    @admin.display(description='Es jurado', boolean=True)
    def es_jurado(self, obj):
        """True si la persona tiene una designación como jurado."""
        return hasattr(obj, 'designacion_jurado')


@admin.register(DesignacionJurado)
class DesignacionJuradoAdmin(admin.ModelAdmin):
    """Listado de designaciones de jurado, indicando si sirve en la misma mesa donde vota."""
    list_display = ('persona', 'cedula', 'rol', 'mesa_servicio', 'puesto_servicio', 'misma_mesa')
    list_select_related = ('persona', 'mesa_servicio__puesto')
    list_filter = ('rol', 'mesa_servicio__puesto__ciudad')
    search_fields = ('persona__cedula', 'persona__primer_nombre', 'persona__primer_apellido')
    autocomplete_fields = ('persona', 'mesa_servicio')

    @admin.display(description='Cédula', ordering='persona__cedula')
    def cedula(self, obj):
        """Cédula de la persona designada."""
        return obj.persona.cedula

    @admin.display(description='Puesto de servicio', ordering='mesa_servicio__puesto__nombre')
    def puesto_servicio(self, obj):
        """Nombre del puesto donde presta servicio como jurado."""
        return obj.mesa_servicio.puesto.nombre

    @admin.display(description='Vota en la misma mesa', boolean=True)
    def misma_mesa(self, obj):
        """True si la mesa de servicio es la misma donde la persona vota."""
        return obj.mesa_servicio_id == obj.persona.mesa_id
