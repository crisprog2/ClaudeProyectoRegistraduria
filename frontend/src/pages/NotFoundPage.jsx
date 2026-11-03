// Página para rutas inexistentes (fase 1: versión mínima; se pule en la fase 4).
import { Link } from 'react-router-dom';
import PageHeading from '../components/common/PageHeading.jsx';
import PageLayout from '../components/layout/PageLayout.jsx';
import { RUTA_CONSULTA } from '../utils/rutas.js';

/** Muestra el layout común con un enlace de regreso a la consulta. */
export default function NotFoundPage() {
  return (
    <PageLayout>
      <PageHeading
        titulo="Página no encontrada"
        subtitulo={<>La dirección no existe. <Link to={RUTA_CONSULTA}>Volver a la consulta</Link></>}
      />
    </PageLayout>
  );
}
