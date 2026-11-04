// Aviso para quien solo es votante: "Eres votante y no tienes designación como jurado" (badge VOTANTE).
import iconoCheck from '../../assets/iconos/check-votante.svg';
import AvisoCondicion from './AvisoCondicion.jsx';

/** El texto es neutro: no depende del género de la persona. */
export default function VotanteAlert() {
  return (
    <AvisoCondicion
      variante="votante"
      icono={iconoCheck}
      tamanoIcono="26"
      titulo="Eres votante y no tienes designación como jurado"
      badge="VOTANTE"
    >
      En este resultado de ejemplo no tienes una asignación como jurado. A continuación encontrarás tu lugar de votación.
    </AvisoCondicion>
  );
}
