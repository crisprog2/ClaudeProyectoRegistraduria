// Panel rojo claro para cuando la consulta no devuelve resultado: cédula no encontrada (Figma 17:288)
// y, con el mismo diseño, demasiadas consultas o una falla de conexión (estados no diseñados en el Figma).
import iconoSinResultado from '../../assets/iconos/busqueda-sin-resultado.svg';
import estilos from './ConsultaSinResultado.module.css';

const TEXTOS = {
  CEDULA_NO_ENCONTRADA: {
    titulo: 'No encontramos información para esta cédula',
    detalle: 'Verifica el número e inténtalo de nuevo. Solo existen cédulas de ejemplo.',
  },
  DEMASIADAS_CONSULTAS: {
    titulo: 'Hiciste demasiadas consultas',
    detalle: 'Intenta de nuevo en unos segundos.',
  },
};

const TEXTO_POR_DEFECTO = {
  titulo: 'No pudimos completar la consulta',
  detalle: 'Intenta de nuevo más tarde.',
};

/** Muestra el título y el detalle que corresponden al código de error de la API. */
export default function ConsultaSinResultado({ id, codigo }) {
  const { titulo, detalle } = TEXTOS[codigo] ?? TEXTO_POR_DEFECTO;
  return (
    <div id={id} className={estilos.panel} role="alert">
      <img src={iconoSinResultado} alt="" width="20" height="20" />
      <div className={estilos.textos}>
        <p className={estilos.titulo}>{titulo}</p>
        <p className={estilos.detalle}>{detalle}</p>
      </div>
    </div>
  );
}
