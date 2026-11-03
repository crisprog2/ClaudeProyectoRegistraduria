// Header con el emblema y el nombre de la marca ficticia ConsultaVoto, más la navegación principal.
import { Link } from 'react-router-dom';
import emblema from '../../assets/iconos/voto-emblema.svg';
import { RUTA_CONSULTA } from '../../utils/rutas.js';
import MainNav from './MainNav.jsx';
import estilos from './SiteHeader.module.css';

/** Header blanco de 96 px: marca a la izquierda (enlaza al inicio) y MainNav a la derecha. */
export default function SiteHeader() {
  return (
    <header className={estilos.header}>
      <div className={`contenedor ${estilos.contenido}`}>
        <Link to={RUTA_CONSULTA} className={estilos.marca} aria-label="ConsultaVoto, ir al inicio">
          <span className={estilos.emblema}>
            <img src={emblema} alt="" width="28" height="28" />
          </span>
          <span className={estilos.nombres}>
            <span className={estilos.nombre}>CONSULTAVOTO</span>
            <span className={estilos.subtitulo}>Proyecto de portafolio QA</span>
          </span>
        </Link>
        <MainNav />
      </div>
    </header>
  );
}
