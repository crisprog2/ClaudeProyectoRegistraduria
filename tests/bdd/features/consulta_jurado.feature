# language: es
@bdd
Característica: Consulta de la designación como jurado de votación
  Como ciudadano designado jurado
  Quiero ver con qué rol y en qué mesa prestaré servicio
  Para presentarme en el lugar correcto el día de las elecciones

  @smoke
  Escenario: Jurado que sirve en la misma mesa donde vota
    Dado un ciudadano designado jurado titular en la misma mesa donde vota
    Cuando consulta con su número de cédula
    Entonces ve su puesto, dirección, ciudad, departamento y mesa de votación
    Y ve su designación como "Jurado titular"
    Y su mesa de servicio es la misma donde vota

  @smoke
  Escenario: Jurado que sirve en otra mesa del mismo puesto
    Dado un ciudadano designado jurado remanente en otra mesa del mismo puesto
    Cuando consulta con su número de cédula
    Entonces ve su designación como "Jurado remanente"
    Y su mesa de servicio es distinta a la mesa donde vota
    Y su puesto de servicio es el mismo donde vota

  @smoke
  Escenario: Jurado que sirve en otro puesto de votación
    Dado un ciudadano designado jurado titular en otro puesto de votación
    Cuando consulta con su número de cédula
    Entonces ve su designación como "Jurado titular"
    Y su puesto y su dirección de servicio son distintos a los de votación
