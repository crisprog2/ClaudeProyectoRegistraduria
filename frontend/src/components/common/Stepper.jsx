// Indicador de pasos Consulta -> Resultado.
import { Fragment } from 'react';
import iconoCheck from '../../assets/iconos/check-paso.svg';
import estilos from './Stepper.module.css';

const PASOS = ['Consulta', 'Resultado'];

/**
 * Progreso de la consulta. pasoActual es 1 (Consulta) o 2 (Resultado).
 * Los pasos anteriores muestran un check; el actual va resaltado y marcado con aria-current="step".
 */
export default function Stepper({ pasoActual }) {
  return (
    <ol className={estilos.pasos} aria-label="Progreso de la consulta">
      {PASOS.map((texto, indice) => {
        const numero = indice + 1;
        const estado = numero < pasoActual ? 'completado' : numero === pasoActual ? 'actual' : 'pendiente';
        return (
          <Fragment key={texto}>
            {indice > 0 && <li aria-hidden="true" className={estilos.conector} />}
            <li className={`${estilos.paso} ${estilos[estado]}`} aria-current={estado === 'actual' ? 'step' : undefined}>
              <span className={estilos.indicador}>
                {estado === 'completado' ? <img src={iconoCheck} alt="" width="14" height="14" /> : numero}
              </span>
              {texto}
              {estado === 'completado' && <span className="solo-lector"> (completado)</span>}
            </li>
          </Fragment>
        );
      })}
    </ol>
  );
}
