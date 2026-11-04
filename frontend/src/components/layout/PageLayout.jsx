// Estructura común: enlace para saltar al contenido, TopBar, SiteHeader, FlagStripe, DemoBanner, contenido y SiteFooter.
import { useRef } from 'react';
import DemoBanner from './DemoBanner.jsx';
import FlagStripe from './FlagStripe.jsx';
import SiteFooter from './SiteFooter.jsx';
import SiteHeader from './SiteHeader.jsx';
import TopBar from './TopBar.jsx';
import estilos from './PageLayout.module.css';

/** Envuelve cada página. El contenido va en <main>, centrado en el contenedor de 1200 px. */
export default function PageLayout({ children }) {
  const principal = useRef(null);

  // Se mueve el foco a mano: con un cambio de hash en la URL, el router crearía una entrada
  // nueva sin estado de navegación y el resultado de la consulta se perdería.
  function saltarAlContenido(evento) {
    evento.preventDefault();
    principal.current?.focus();
  }

  return (
    <div className={estilos.pagina}>
      <a href="#contenido" className={estilos.saltar} onClick={saltarAlContenido}>Saltar al contenido</a>
      <header>
        <TopBar />
        <SiteHeader />
        <FlagStripe />
        <DemoBanner />
      </header>
      <main ref={principal} id="contenido" tabIndex={-1} className={`contenedor ${estilos.principal}`}>{children}</main>
      <SiteFooter />
    </div>
  );
}
