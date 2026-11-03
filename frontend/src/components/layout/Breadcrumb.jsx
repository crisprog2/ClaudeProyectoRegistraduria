// Migas de pan: Inicio > Consulta electoral > Resultado.
import { Fragment } from 'react';
import { Link } from 'react-router-dom';
import iconoChevron from '../../assets/iconos/chevron-derecha.svg';
import iconoInicio from '../../assets/iconos/inicio.svg';
import estilos from './Breadcrumb.module.css';

/**
 * Ruta de navegación. Recibe los niveles en orden: [{ texto, a? }].
 * El primero lleva el ícono de inicio; el último es la página actual (aria-current) y no es enlace.
 */
export default function Breadcrumb({ niveles }) {
  return (
    <nav aria-label="Ruta de navegación">
      <ol className={estilos.ruta}>
        {niveles.map(({ texto, a }, indice) => {
          const esActual = indice === niveles.length - 1;
          return (
            <Fragment key={texto}>
              {indice > 0 && (
                <li aria-hidden="true" className={estilos.separador}>
                  <img src={iconoChevron} alt="" width="13" height="13" />
                </li>
              )}
              <li className={estilos.nivel}>
                {indice === 0 && <img src={iconoInicio} alt="" width="15" height="15" />}
                {esActual ? (
                  <span className={estilos.actual} aria-current="page">{texto}</span>
                ) : (
                  <Link to={a}>{texto}</Link>
                )}
              </li>
            </Fragment>
          );
        })}
      </ol>
    </nav>
  );
}
