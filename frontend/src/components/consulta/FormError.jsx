// Mensaje de error del campo (campo vacío, formato inválido). Ocupa el lugar del texto de ayuda.
import iconoAlerta from '../../assets/iconos/alerta-error.svg';
import estilos from './FormError.module.css';

/** Ícono de alerta y mensaje en rojo. role="alert" hace que el lector de pantalla lo anuncie. */
export default function FormError({ id, children }) {
  return (
    <p id={id} className={estilos.error} role="alert">
      <img src={iconoAlerta} alt="" width="16" height="16" />
      {children}
    </p>
  );
}
