// Página para rutas inexistentes. No está en el Figma: reutiliza el layout, el encabezado y la tarjeta de las demás pantallas.
import { Link } from 'react-router-dom';
import iconoFlecha from '../assets/iconos/flecha-izquierda.svg';
import Card from '../components/common/Card.jsx';
import PageHeading from '../components/common/PageHeading.jsx';
import Breadcrumb from '../components/layout/Breadcrumb.jsx';
import PageLayout from '../components/layout/PageLayout.jsx';
import useTituloPagina from '../hooks/useTituloPagina.js';
import { RUTA_CONSULTA } from '../utils/rutas.js';
import estilos from './NotFoundPage.module.css';

/** Muestra el layout común con un enlace de regreso a la consulta. */
export default function NotFoundPage() {
  useTituloPagina('Página no encontrada');

  return (
    <PageLayout>
      <div className={estilos.pagina}>
        <Breadcrumb niveles={[{ texto: 'Inicio', a: RUTA_CONSULTA }, { texto: 'Página no encontrada' }]} />
        <PageHeading
          titulo="Página no encontrada"
          subtitulo="La dirección que buscas no existe en este prototipo."
        />
        <Card className={estilos.tarjeta}>
          <p className={estilos.texto}>Puedes volver al inicio y hacer tu consulta con un número de cédula.</p>
          <Link to={RUTA_CONSULTA} className={estilos.accion}>
            <img src={iconoFlecha} alt="" width="18" height="18" />
            Volver a la consulta
          </Link>
        </Card>
      </div>
    </PageLayout>
  );
}
