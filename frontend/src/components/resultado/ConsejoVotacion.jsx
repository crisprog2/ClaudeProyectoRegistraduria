// Consejo "Antes de ir a votar" que se muestra solo a quien no es jurado.
import iconoConsejo from '../../assets/iconos/consejo.svg';
import NotaDestacada from '../common/NotaDestacada.jsx';

/** Texto fijo del Figma. */
export default function ConsejoVotacion() {
  return (
    <NotaDestacada id="titulo-consejo" icono={iconoConsejo} titulo="Antes de ir a votar">
      Identifica el nombre del puesto y tu número de mesa. La dirección y el mapa te ayudan a reconocer el lugar de votación de este ejemplo.
    </NotaDestacada>
  );
}
