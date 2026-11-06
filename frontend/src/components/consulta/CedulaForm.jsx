// Tarjeta "Empieza con tu cédula": campo, ayuda o error, botón Consultar y aviso de datos ficticios.
import { useEffect, useRef, useState } from 'react';
import iconoBuscar from '../../assets/iconos/buscar.svg';
import iconoCedula from '../../assets/iconos/cedula-formulario.svg';
import { CEDULA_FORMATO_INVALIDO, CEDULA_REQUERIDA } from '../../utils/validarCedula.js';
import Card from '../common/Card.jsx';
import InfoNote from '../common/InfoNote.jsx';
import CedulaInput from './CedulaInput.jsx';
import ConsultaSinResultado from './ConsultaSinResultado.jsx';
import FormError from './FormError.jsx';
import estilos from './CedulaForm.module.css';

const ERRORES_DEL_CAMPO = [CEDULA_REQUERIDA, CEDULA_FORMATO_INVALIDO];
const ID_CAMPO = 'cedula';
const ID_AYUDA = 'cedula-ayuda';
const ID_ERROR = 'cedula-error';

/**
 * Formulario de consulta. Recibe del hook useConsultaCedula el estado y las acciones.
 * Debajo del campo se muestra solo una cosa, en lugar del texto de ayuda (como en el Figma):
 *  - error del campo (vacío o formato inválido): FormError y borde rojo;
 *  - cualquier otro error (no encontrada, 429, sin conexión): ConsultaSinResultado, borde normal.
 */
export default function CedulaForm({ consultando, error, onConsultar, onEditar }) {
  const [valor, setValor] = useState('');
  const campo = useRef(null);
  const errorDelCampo = error && ERRORES_DEL_CAMPO.includes(error.codigo);

  // Con un error del campo, el foco vuelve al campo para corregirlo.
  useEffect(() => {
    if (errorDelCampo) campo.current?.focus();
  }, [error, errorDelCampo]);

  /** Evita la recarga del navegador y entrega el valor tal como se escribió (el hook lo valida). */
  function enviar(evento) {
    evento.preventDefault();
    onConsultar(valor);
  }

  /** Actualiza el valor y quita el error en cuanto la persona empieza a corregir. */
  function cambiar(evento) {
    setValor(evento.target.value);
    if (error) onEditar();
  }

  return (
    <Card como="section" className={estilos.tarjeta} aria-labelledby="titulo-formulario">
      <div className={estilos.encabezado}>
        <span className={estilos.icono}>
          <img src={iconoCedula} alt="" width="23" height="23" />
        </span>
        <div className={estilos.textosEncabezado}>
          <h2 id="titulo-formulario" className={estilos.titulo}>Empieza con tu cédula</h2>
          <p className={estilos.subtitulo}>Un dato para conocer tu información electoral.</p>
        </div>
      </div>

      <form className={estilos.formulario} onSubmit={enviar} noValidate>
        <div className={estilos.campo}>
          <label htmlFor={ID_CAMPO} className={estilos.etiqueta}>Número de cédula de ciudadanía</label>
          <CedulaInput
            ref={campo}
            id={ID_CAMPO}
            value={valor}
            onChange={cambiar}
            conError={errorDelCampo}
            describedBy={error ? ID_ERROR : ID_AYUDA}
          />
          {!error && <p id={ID_AYUDA} className={estilos.ayuda}>Escribe solo números, sin puntos, espacios ni comas.</p>}
          {errorDelCampo && <FormError id={ID_ERROR}>{error.mensaje}</FormError>}
          {error && !errorDelCampo && <ConsultaSinResultado id={ID_ERROR} codigo={error.codigo} />}
        </div>

        <button type="submit" className={estilos.boton} disabled={consultando} aria-busy={consultando}>
          {consultando ? 'Consultando…' : 'Consultar'}
          <img src={iconoBuscar} alt="" width="18" height="18" />
        </button>
      </form>

      <InfoNote className={estilos.nota}>
        El número mostrado es ficticio y sirve para ilustrar esta consulta. No ingreses datos personales reales en este prototipo.
      </InfoNote>
    </Card>
  );
}
