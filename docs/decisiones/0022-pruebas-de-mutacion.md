# ADR 0022 · Toda regla importante se comprueba también con una prueba de mutación

- **Estado:** Aceptada
- **Fecha de la decisión:** 2026-11-03, desde las primeras pruebas del backend y la API, y aplicada en todas las fases
- **Documentado:** 2026-11-18, a posteriori, a partir de `CLAUDE.md`
- **Aprobada por:** el dueño del producto

## Contexto

Que una prueba pase no demuestra que proteja algo. Una prueba mal escrita puede pasar siempre: compara dos valores que siempre coinciden, no llega a la línea que importa, o revisa un dato que la respuesta descarta. La cobertura de código tampoco lo detecta, porque solo mide qué se ejecutó.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| Confiar en que las pruebas pasan | Sin esfuerzo extra | Una prueba débil da una falsa sensación de seguridad |
| Una herramienta de mutación automática (por ejemplo, mutmut) sobre todo el código | Exhaustiva | Lenta; genera miles de mutaciones, muchas irrelevantes, que hay que revisar una por una |
| **Mutación manual y dirigida** | Rápida, y cada mutación representa un defecto real y plausible | Depende de elegir bien qué mutar |

## Decisión

**Cuando una prueba protege una regla de seguridad o de negocio, se comprueba al menos una vez que falla si se reintroduce el defecto.** No basta con que pase.

El procedimiento:
1. Se cambia el código para reintroducir el defecto (por ejemplo, quitar `HttpOnly` de la cookie).
2. Se corre la suite y se confirma qué pruebas fallan.
3. Se restaura el código. Los scripts de mutación restauran el archivo original aunque algo falle.

Las mutaciones verificadas se registran en `CLAUDE.md` (sección de cada suite) y en el ADR de cada decisión.

## Consecuencias

- **A favor:** la mutación encontró debilidades reales en las propias pruebas. Por ejemplo, en la fase 1:
  - una prueba del vencimiento del token comparaba dos tokens creados en el mismo segundo y no notaba que la sesión se alargaba. Se corrigió;
  - una mutación "token en el JSON" no era un defecto real, porque el serializador descarta los campos que no declara. Se rehízo hasta que lo fuera.
- **En contra:** exige tiempo en cada fase. Se reserva para las reglas que importan, no para cada línea.

## Cómo se verifica

Algunas de las mutaciones registradas:

| Área | Mutaciones detectadas |
|---|---|
| API | Exponer `genero`, aceptar el 0 inicial, `NUM_PROXIES` por defecto |
| BDD | Omitir la designación de jurado en la respuesta |
| Interfaz | Cédula en la URL, quitar el aviso de demostración, conservar el estado al recargar, edad visible para el jurado, contraste bajo |
| Documentación | Campo sin documentar, ejemplo desactualizado, Swagger desde un CDN |
| Cobertura | Un módulo sin pruebas hace fallar la corrida |
| Sesión (fase 1) | 17 mutaciones (12 en el backend y 5 contra el servidor real), todas detectadas |

**Un límite conocido:** axe-core no detectó una mutación de texto blanco sobre fondo blanco, y no evalúa el contraste de los placeholders. Ahí la mutación mostró un hueco de la herramienta, no de las pruebas propias.
