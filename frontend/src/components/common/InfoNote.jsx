// Nota informativa con ícono de información (avisos de datos ficticios y aclaraciones).
import iconoInfo from '../../assets/iconos/info-nota.svg';
import estilos from './InfoNote.module.css';

/** Texto gris de 12 px precedido por el ícono de información de 16 px. */
export default function InfoNote({ children, className = '' }) {
  return (
    <div className={`${estilos.nota} ${className}`}>
      <img src={iconoInfo} alt="" width="16" height="16" />
      <p>{children}</p>
    </div>
  );
}
