// Etiqueta corta (DATOS FICTICIOS, VOTANTE, JURADO).
import estilos from './Badge.module.css';

/** Variantes del Figma: 'ficticio' (gris), 'votante' (verde) y 'jurado' (amarillo). */
export default function Badge({ variante, children }) {
  return <span className={`${estilos.badge} ${estilos[variante]}`}>{children}</span>;
}
