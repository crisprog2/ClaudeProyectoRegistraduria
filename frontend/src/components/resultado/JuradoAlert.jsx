// Aviso de designación como jurado (badge JURADO); solo se renderiza si es jurado.
import iconoJurado from '../../assets/iconos/jurado-aviso.svg';
import AvisoCondicion from './AvisoCondicion.jsx';

/** El título y el detalle dependen de dónde presta servicio (ver utils/textosJurado.js). */
export default function JuradoAlert({ titulo, detalle }) {
  return (
    <AvisoCondicion variante="jurado" icono={iconoJurado} tamanoIcono="26" titulo={titulo} badge="JURADO">
      {detalle}
    </AvisoCondicion>
  );
}
