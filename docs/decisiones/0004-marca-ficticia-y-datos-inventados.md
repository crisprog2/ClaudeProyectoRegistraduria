# ADR 0004 · Marca ficticia y solo datos inventados

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03 (commits `d866bc1` y `b801900`)
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`, el README y el historial de Git
- **Aprobada por:** el dueño del producto

## Contexto

El proyecto es un portafolio de QA. El sistema bajo prueba es una aplicación de consulta electoral para Colombia, un dominio real y sensible. Una aplicación así puede confundirse con un servicio oficial o terminar mostrando datos personales reales.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| Imitar el servicio oficial (nombre, logo, colores) | Más "realista" | Suplantación de una entidad pública; confusión para los visitantes; riesgo legal |
| **Marca propia y datos inventados** | Sin confusión posible; el portafolio se puede publicar sin riesgo | Hay que diseñar la marca y fabricar datos de prueba coherentes |

## Decisión

- **Marca ficticia ConsultaVoto**, con el subtítulo "Proyecto de portafolio QA". Nunca se usa el nombre ni el logo de la entidad real ni de ninguna otra entidad.
- **El sitio no debe parecer oficial:** el `DemoBanner`, la insignia "DATOS FICTICIOS" y los avisos de prototipo están siempre visibles. La documentación de la API también avisa que los datos son ficticios.
- **Solo datos inventados:** nunca cédulas, nombres ni direcciones reales. La excepción es la geografía pública: los 33 departamentos con su código DIVIPOLA del DANE y algunas ciudades. Los puestos, mesas, personas y jurados son ficticios.
- Las cédulas de ejemplo siguen el formato colombiano. Cualquier coincidencia con una real es accidental.

## Consecuencias

- **A favor:** el repositorio, la aplicación y los reportes (Allure en GitHub Pages) se pueden publicar sin exponer a nadie.
- **En contra:** los datos de demostración hay que mantenerlos a mano (`datos_demo.json`), cubriendo cada escenario: solo votante, jurado en la misma mesa, en otra mesa y en otro puesto, cédulas antiguas y nuevas, y casos límite de edad.
- La regla se extiende a todo lo nuevo, incluidos los usuarios de demostración (`admin.demo` y `analista.demo`, fase 1).

## Cómo se verifica

- `tests/e2e/test_flujo_consulta.py`: los avisos obligatorios están en cada pantalla y no se menciona ninguna entidad real (las frases prohibidas están en `tests/data/textos_interfaz.json`).
- `tests/api/test_documentacion_api.py`: la documentación de la API no menciona entidades reales y avisa que los datos son ficticios.
- **Mutaciones verificadas:** quitar el `DemoBanner` y escribir el nombre de la entidad real hacen fallar las pruebas.
