// Header con el emblema y el nombre de la marca ficticia ConsultaVoto, más la navegación principal.
import { Link } from 'react-router-dom';
import emblema from '../../assets/iconos/voto-emblema.svg';
import { RUTA_CONSULTA } from '../../utils/rutas.js';
import MainNav from './MainNav.jsx';
import estilos from './SiteHeader.module.css';

/** Franja blanca de 96 px dentro del <header> de PageLayout: marca a la izquierda (enlaza al inicio) y MainNav a la derecha. */
export default function SiteHeader() {
  return (
    <div className={estilos.header}>
      <div className={`contenedor ${estilos.contenido}`}>
        <Link to={RUTA_CONSULTA} className={estilos.marca}>
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
    </div>
  );
}
