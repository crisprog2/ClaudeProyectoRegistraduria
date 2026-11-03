// Validación de formato de cédula en el cliente. Replica la regla del backend
// (backend/apps/consultas/validators.py) para mostrar el error sin llamar a la API;
// el backend sigue siendo la regla definitiva.

export const CEDULA_REQUERIDA = 'CEDULA_REQUERIDA';
export const CEDULA_FORMATO_INVALIDO = 'CEDULA_FORMATO_INVALIDO';

/** Textos del Figma para los errores del campo. */
export const MENSAJES_CEDULA = {
  [CEDULA_REQUERIDA]: 'Ingresa tu número de cédula para consultar.',
  [CEDULA_FORMATO_INVALIDO]: 'El número no es válido. Escribe solo números, sin puntos, espacios ni comas.',
};

// De 6 a 10 dígitos ASCII, sin cero inicial. Se usa [0-9] y no \d por coherencia con el backend.
const PATRON_CEDULA = /^[1-9][0-9]{5,9}$/;

/**
 * Valida el texto escrito en el campo.
 * Devuelve { cedula } con la cédula sin espacios externos, o { error: { codigo, mensaje } }.
 */
export function validarCedula(valor) {
  const cedula = (valor ?? '').trim();
  if (cedula === '') {
    return { error: { codigo: CEDULA_REQUERIDA, mensaje: MENSAJES_CEDULA[CEDULA_REQUERIDA] } };
  }
  if (!PATRON_CEDULA.test(cedula)) {
    return { error: { codigo: CEDULA_FORMATO_INVALIDO, mensaje: MENSAJES_CEDULA[CEDULA_FORMATO_INVALIDO] } };
  }
  return { cedula };
}
