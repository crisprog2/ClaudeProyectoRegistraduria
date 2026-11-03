// Pantalla 2 (Figma 6:2442 y 6:2609): información electoral del ciudadano y, si aplica, designación como jurado.
// Fase 1: layout, migas de pan y encabezado. Las tarjetas del resultado llegan en la fase 3.
import PageHeading from '../components/common/PageHeading.jsx';
import Stepper from '../components/common/Stepper.jsx';
import Breadcrumb from '../components/layout/Breadcrumb.jsx';
import PageLayout from '../components/layout/PageLayout.jsx';
import { RUTA_CONSULTA } from '../utils/rutas.js';
import estilos from './ResultadoPage.module.css';

/** Pantalla del resultado de la consulta. */
export default function ResultadoPage() {
  return (
    <PageLayout>
      <div className={estilos.pagina}>
        <Breadcrumb
          niveles={[
            { texto: 'Inicio', a: RUTA_CONSULTA },
            { texto: 'Consulta electoral', a: RUTA_CONSULTA },
            { texto: 'Resultado' },
          ]}
        />
        <PageHeading
          titulo="Tu información electoral"
          subtitulo="Revisa tu lugar de votación y si tienes una designación como jurado."
          extremo={<Stepper pasoActual={2} />}
        />
      </div>
    </PageLayout>
  );
}
