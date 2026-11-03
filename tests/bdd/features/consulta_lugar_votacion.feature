# language: es
@bdd
Característica: Consulta del lugar de votación
  Como ciudadano
  Quiero consultar mi lugar de votación con mi número de cédula
  Para saber a dónde ir el día de las elecciones

  @smoke
  Escenario: Ciudadano que solo es votante
    Dado un ciudadano registrado que no fue designado jurado
    Cuando consulta con su número de cédula
    Entonces ve su nombre completo y su edad
    Y ve su puesto, dirección, ciudad, departamento y mesa de votación
    Y se le informa que no tiene designación como jurado

  Escenario: La cédula se acepta con espacios al inicio o al final
    Dado un ciudadano registrado que no fue designado jurado
    Cuando consulta con su número de cédula rodeado de espacios
    Entonces ve su puesto, dirección, ciudad, departamento y mesa de votación
