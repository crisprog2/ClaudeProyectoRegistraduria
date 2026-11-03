// Contenedor tipo tarjeta reutilizable: fondo blanco, borde gris claro y radio de 16 px.
import estilos from './Card.module.css';

/**
 * Tarjeta base. 'como' define la etiqueta HTML (section, div, article...) y 'className'
 * agrega el relleno, el espaciado o la sombra que necesite cada uso.
 */
export default function Card({ como: Etiqueta = 'div', className = '', children, ...resto }) {
  return (
    <Etiqueta className={`${estilos.tarjeta} ${className}`} {...resto}>
      {children}
    </Etiqueta>
  );
}
