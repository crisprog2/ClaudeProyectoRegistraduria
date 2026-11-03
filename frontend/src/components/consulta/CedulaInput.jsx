// Campo de número de cédula con ícono. El borde se pone rojo cuando hay un error de formato.
import { forwardRef } from 'react';
import iconoCedula from '../../assets/iconos/cedula-campo.svg';
import estilos from './CedulaInput.module.css';

/**
 * Input de texto (no type="number": se deben poder escribir puntos o letras para mostrar el error).
 * inputMode="numeric" abre el teclado numérico en el celular. 'conError' marca aria-invalid.
 */
const CedulaInput = forwardRef(function CedulaInput({ id, conError, describedBy, ...resto }, ref) {
  return (
    <div className={`${estilos.caja} ${conError ? estilos.conError : ''}`}>
      <img src={iconoCedula} alt="" width="20" height="20" />
      <input
        ref={ref}
        id={id}
        name="cedula"
        type="text"
        inputMode="numeric"
        autoComplete="off"
        placeholder="Ej.: 1023456789"
        aria-invalid={conError ? 'true' : 'false'}
        aria-describedby={describedBy}
        className={estilos.entrada}
        {...resto}
      />
    </div>
  );
});

export default CedulaInput;
