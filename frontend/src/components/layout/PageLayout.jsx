// Estructura común: TopBar, SiteHeader, FlagStripe, DemoBanner, contenido principal y SiteFooter.
import DemoBanner from './DemoBanner.jsx';
import FlagStripe from './FlagStripe.jsx';
import SiteFooter from './SiteFooter.jsx';
import SiteHeader from './SiteHeader.jsx';
import TopBar from './TopBar.jsx';
import estilos from './PageLayout.module.css';

/** Envuelve cada página. El contenido va en <main>, centrado en el contenedor de 1200 px. */
export default function PageLayout({ children }) {
  return (
    <div className={estilos.pagina}>
      <TopBar />
      <SiteHeader />
      <FlagStripe />
      <DemoBanner />
      <main className={`contenedor ${estilos.principal}`}>{children}</main>
      <SiteFooter />
    </div>
  );
}
