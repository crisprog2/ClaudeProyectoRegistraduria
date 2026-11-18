# language: es
@bdd
Característica: Inicio de sesión de los usuarios de la aplicación
  Como administrador o analista de ConsultaVoto
  Quiero iniciar y cerrar sesión de forma segura
  Para usar las funciones de mi rol sin que otra persona pueda hacerlo en mi nombre

  @smoke
  Esquema del escenario: Un usuario con rol inicia sesión (<rol>)
    Dado el usuario de demostración con rol "<rol>"
    Cuando inicia sesión con su contraseña
    Entonces entra a la aplicación con el rol "<rol>"

    Ejemplos:
      | rol           |
      | Administrador |
      | Analista      |

  Escenario: Contraseña incorrecta
    Dado el usuario de demostración con rol "Analista"
    Cuando inicia sesión con una contraseña incorrecta
    Entonces ve el mensaje "Usuario o contraseña incorrectos."
    Y no entra a la aplicación

  Escenario: Usuario que no existe
    Cuando inicia sesión con un usuario que no existe
    Entonces ve el mensaje "Usuario o contraseña incorrectos."
    Y no entra a la aplicación

  Escenario: Sin escribir el usuario ni la contraseña
    Cuando inicia sesión sin escribir el usuario ni la contraseña
    Entonces ve el mensaje "Escribe tu usuario y tu contraseña."
    Y no entra a la aplicación

  Escenario: La sesión sigue abierta mientras trabaja
    Dado que el usuario con rol "Analista" inició sesión
    Cuando su acceso se renueva
    Entonces sigue en la aplicación con el rol "Analista"

  @smoke
  Escenario: Cerrar sesión
    Dado que el usuario con rol "Administrador" inició sesión
    Cuando cierra sesión
    Entonces su sesión ya no se puede renovar
