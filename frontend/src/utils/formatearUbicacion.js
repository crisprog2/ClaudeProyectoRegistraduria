// Formateo de los datos de ubicación para mostrar.

/** Número de mesa con tres dígitos: 18 → '018'. */
export function formatearMesa(numero) {
  return String(numero).padStart(3, '0');
}

/**
 * Une ciudad y departamento: 'Medellín · Antioquia'.
 * Si tienen el mismo nombre (Bogotá, D.C.) lo muestra una sola vez.
 */
export function formatearLugar(ciudad, departamento, separador = ' · ') {
  return ciudad === departamento ? ciudad : `${ciudad}${separador}${departamento}`;
}
