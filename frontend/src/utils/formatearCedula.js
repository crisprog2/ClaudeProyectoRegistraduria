// Formateo de cédula con separador de miles para mostrar (1.098.765.432).

/** Agrupa los dígitos de tres en tres con puntos: '1098765432' → '1.098.765.432', '4567891' → '4.567.891'. */
export function formatearCedula(cedula) {
  return String(cedula).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}
