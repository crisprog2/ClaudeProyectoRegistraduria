# ADR 0007 · Modelo de datos: jurado por designación, edad calculada y referencias protegidas

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 (commit `50c8ada`)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md` y `backend/apps/consultas/models.py`
- **Aprobada por:** el dueño del producto, que escribió el modelo; se ajustó con revisión de Claude

## Contexto

La consulta debe responder dónde vota una persona y, si es jurado, dónde presta servicio, que puede ser otra mesa u otro puesto. Hacía falta un modelo que no permitiera datos contradictorios.

## Decisión

- **Jerarquía:** `Departamento` → `Ciudad` → `PuestoVotacion` → `Mesa` → `Persona` (donde vota). Los códigos son los de la geografía colombiana: departamento de 2 caracteres, ciudad de 5 y puesto de hasta 10.
- **Ser jurado depende de que exista una `DesignacionJurado`** (relación uno a uno con la persona). **No hay un campo booleano "es_jurado"**: con dos fuentes de verdad podrían contradecirse.
- **La ubicación de servicio no se duplica:** el puesto, la dirección, la ciudad y el departamento salen de `mesa_servicio.puesto`.
- **La edad no se guarda:** se calcula desde `fecha_nacimiento`. Para que las pruebas no dependan del día, `calcular_edad(fecha_referencia)` recibe la fecha.
- **`PROTECT` en todas las referencias:** no se puede borrar una ciudad con puestos ni una mesa con votantes. La única excepción es `DesignacionJurado.persona`, con `CASCADE`: si se borra la persona, se borra su designación.
- **La cédula es la clave primaria** (texto de hasta 10 caracteres). Su formato se valida en `validators.py`, no en el modelo.
- **`models.py` es del dueño del producto:** cualquier cambio estructural se propone y se aplica solo con su aprobación.

## Consecuencias

- **A favor:** no hay estados contradictorios posibles, y la consulta trae todo en una sola consulta SQL (`select_related`).
- **En contra:** los `__str__` de `Mesa` y `DesignacionJurado` leen modelos relacionados, así que en los listados hay que usar `select_related` para no hacer una consulta por fila.
- La fase 2 de roles agrega un modelo (`RegistroConsulta`) y requiere la aprobación del dueño del producto.

## Cómo se verifica

- `backend/tests/test_models.py`:
  - `nombre_completo` omite el segundo nombre y el segundo apellido cuando están vacíos;
  - la edad en los días límite: el día antes y el día del cumpleaños, 29 de febrero en años bisiestos y no bisiestos, y la mayoría de edad exacta;
  - los textos de `__str__`.
- `backend/tests/test_services.py`: la consulta hace exactamente 1 consulta SQL.
- `backend/tests/test_admin.py`: el listado de personas no hace una consulta por fila.
