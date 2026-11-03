// Navegación principal: "Consulta electoral" (activa) y los enlaces solo visuales "Cómo consultar" y "Ayuda".
import { NavLink } from 'react-router-dom';
import iconoAyuda from '../../assets/iconos/ayuda.svg';
import { RUTA_CONSULTA } from '../../utils/rutas.js';
import estilos from './MainNav.module.css';

/**
 * Secciones del sitio. "Consulta electoral" queda activa también en el resultado.
 * "Cómo consultar" y "Ayuda" no tienen página: se muestran como enlaces deshabilitados
 * (sin href, aria-disabled) para que no sean navegables ni engañen a quien usa lector de pantalla.
 */
export default function MainNav() {
  return (
    <nav aria-label="Principal">
      <ul className={estilos.secciones}>
        <li>
          <NavLink
            to={RUTA_CONSULTA}
            end={false}
            className={({ isActive }) => `${estilos.enlace} ${isActive ? estilos.activo : ''}`}
          >
            Consulta electoral
          </NavLink>
        </li>
        <li>
          <a className={estilos.enlace} aria-disabled="true">Cómo consultar</a>
        </li>
        <li>
          <a className={`${estilos.enlace} ${estilos.conIcono}`} aria-disabled="true">
            <img src={iconoAyuda} alt="" width="18" height="18" />
            Ayuda
          </a>
        </li>
      </ul>
    </nav>
  );
}
