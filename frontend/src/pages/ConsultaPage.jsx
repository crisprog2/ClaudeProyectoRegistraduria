// Pantalla 1 (Figma 6:2319 y estados de error 17:2, 17:145 y 17:288): consulta por cédula.
import PageHeading from '../components/common/PageHeading.jsx';
import Stepper from '../components/common/Stepper.jsx';
import CedulaForm from '../components/consulta/CedulaForm.jsx';
import PasosConsulta from '../components/consulta/PasosConsulta.jsx';
import PromoPanel from '../components/consulta/PromoPanel.jsx';
import Breadcrumb from '../components/layout/Breadcrumb.jsx';
import PageLayout from '../components/layout/PageLayout.jsx';
import useConsultaCedula from '../hooks/useConsultaCedula.js';
import { RUTA_CONSULTA } from '../utils/rutas.js';
import estilos from './ConsultaPage.module.css';

/** Pantalla de inicio: encabezado, formulario con el panel "Tu voz cuenta" y la guía de pasos. */
export default function ConsultaPage() {
  const { consultando, error, consultar, limpiarError } = useConsultaCedula();

  return (
    <PageLayout>
      <div className={estilos.pagina}>
        <Breadcrumb niveles={[{ texto: 'Inicio', a: RUTA_CONSULTA }, { texto: 'Consulta electoral' }]} />
        <PageHeading
          variante="portada"
          antetitulo="Consulta electoral"
          titulo={<>Tu participación,<br />con toda la información.</>}
          subtitulo="Consulta dónde votar y conoce si tienes una designación como jurado de votación. Empieza con tu número de cédula."
          extremo={<Stepper pasoActual={1} />}
        />
        <div className={estilos.consulta}>
          <CedulaForm consultando={consultando} error={error} onConsultar={consultar} onEditar={limpiarError} />
          <PromoPanel />
        </div>
        <PasosConsulta />
      </div>
    </PageLayout>
  );
}
