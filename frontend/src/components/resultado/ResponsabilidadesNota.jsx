// Nota "Una mesa, dos responsabilidades" (solo si es jurado); su texto cambia según dónde presta servicio.
import iconoResponsabilidades from '../../assets/iconos/responsabilidades.svg';
import NotaDestacada from '../common/NotaDestacada.jsx';

/** Título y texto vienen de utils/textosJurado.js. */
export default function ResponsabilidadesNota({ titulo, texto }) {
  return (
    <NotaDestacada id="titulo-responsabilidades" icono={iconoResponsabilidades} titulo={titulo}>
      {texto}
    </NotaDestacada>
  );
}
