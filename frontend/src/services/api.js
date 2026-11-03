// Cliente HTTP hacia la API de consultas. Es el único módulo del frontend que hace peticiones.
//
// En desarrollo la URL base queda vacía y Vite reenvía /api al backend (ver vite.config.js).
// VITE_API_BASE_URL permite apuntar a otra API si el frontend se sirve desde otro origen.

const URL_BASE = import.meta.env.VITE_API_BASE_URL ?? '';

/** Códigos de error propios del cliente, para fallas en las que la API no llegó a responder. */
export const SIN_CONEXION = 'SIN_CONEXION';
export const RESPUESTA_INESPERADA = 'RESPUESTA_INESPERADA';

/** Error de la consulta con el código y el mensaje de la API ({codigo, mensaje}) y el estado HTTP. */
export class ErrorConsulta extends Error {
  constructor(codigo, mensaje, estadoHttp = null) {
    super(mensaje);
    this.name = 'ErrorConsulta';
    this.codigo = codigo;
    this.estadoHttp = estadoHttp;
  }
}

/**
 * POST /api/consulta/ con {"cedula": cedula}. La cédula viaja en el cuerpo, nunca en la URL.
 * Devuelve el resultado ({ciudadano, lugar_votacion, jurado}) o lanza ErrorConsulta.
 */
export async function consultarCedula(cedula) {
  let respuesta;
  try {
    respuesta = await fetch(`${URL_BASE}/api/consulta/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ cedula }),
    });
  } catch {
    throw new ErrorConsulta(SIN_CONEXION, 'No pudimos conectarnos con el servicio.');
  }

  let cuerpo;
  try {
    cuerpo = await respuesta.json();
  } catch {
    throw new ErrorConsulta(RESPUESTA_INESPERADA, 'La respuesta del servicio no es válida.', respuesta.status);
  }

  if (!respuesta.ok) {
    throw new ErrorConsulta(cuerpo.codigo ?? RESPUESTA_INESPERADA, cuerpo.mensaje ?? '', respuesta.status);
  }
  return cuerpo;
}
