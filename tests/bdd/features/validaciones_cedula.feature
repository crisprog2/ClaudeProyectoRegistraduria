# language: es
@bdd
Característica: Validaciones del número de cédula
  Como ciudadano
  Quiero recibir un mensaje claro cuando la cédula no es válida o no está registrada
  Para corregirla y volver a consultar

  @smoke
  Escenario: Consulta sin escribir la cédula
    Cuando consulta sin escribir el número de cédula
    Entonces ve el mensaje "Ingresa tu número de cédula para consultar."
    Y no ve información de votación

  Esquema del escenario: Cédula con formato inválido (<caso>)
    Cuando consulta con la cédula "<cedula>"
    Entonces ve el mensaje "El número no es válido. Escribe solo números, sin puntos, espacios ni comas."
    Y no ve información de votación

    Ejemplos:
      | caso                  | cedula        |
      | con puntos            | 1.098.765.432 |
      | con comas             | 1,098,765,432 |
      | con espacios internos | 1098 765 432  |
      | con letras            | abc123456     |
      | empieza por cero      | 0123456789    |
      | menos de 6 dígitos    | 12345         |
      | más de 10 dígitos     | 10987654321   |

  @smoke
  Escenario: Cédula con formato válido que no está registrada
    Dado una cédula con formato válido que no está registrada
    Cuando consulta con esa cédula
    Entonces ve el mensaje "No encontramos información para esta cédula."
    Y no ve información de votación
