// Pantalla 2 (Figma 6:2442 y 6:2609): información electoral del ciudadano y, si aplica, designación como jurado.
import { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import PageHeading from '../components/common/PageHeading.jsx';
import Stepper from '../components/common/Stepper.jsx';
import Breadcrumb from '../components/layout/Breadcrumb.jsx';
import PageLayout from '../components/layout/PageLayout.jsx';
import AsignacionJuradoCard from '../components/resultado/AsignacionJuradoCard.jsx';
import CiudadanoResumen from '../components/resultado/CiudadanoResumen.jsx';
import ConsejoVotacion from '../components/resultado/ConsejoVotacion.jsx';
import JuradoAlert from '../components/resultado/JuradoAlert.jsx';
import LugarVotacionCard from '../components/resultado/LugarVotacionCard.jsx';
import MapaPuesto from '../components/resultado/MapaPuesto.jsx';
import ResponsabilidadesNota from '../components/resultado/ResponsabilidadesNota.jsx';
import ResultadoDisclaimer from '../components/resultado/ResultadoDisclaimer.jsx';
import VotanteAlert from '../components/resultado/VotanteAlert.jsx';
import useTituloPagina from '../hooks/useTituloPagina.js';
import { RUTA_CONSULTA } from '../utils/rutas.js';
import { textosJurado } from '../utils/textosJurado.js';
import estilos from './ResultadoPage.module.css';

/**
 * El resultado llega en el estado de navegación desde ConsultaPage. Sin él (entrada directa
 * o recarga, ver main.jsx) no hay nada que mostrar y se vuelve a la consulta.
 */
export default function ResultadoPage() {
  const { state } = useLocation();
  const resultado = state?.resultado;
  useTituloPagina('Tu información electoral');

  // La navegación del router conserva el desplazamiento: el resultado debe verse desde arriba.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  if (!resultado) {
    return <Navigate to={RUTA_CONSULTA} replace />;
  }

  const { ciudadano, lugar_votacion: lugar, jurado } = resultado;
  const textos = jurado ? textosJurado(lugar, jurado) : null;

  return (
    <PageLayout>
      <div className={estilos.pagina}>
        <div className={estilos.presentacion}>
          <Breadcrumb
            niveles={[
              { texto: 'Inicio', a: RUTA_CONSULTA },
              { texto: 'Consulta electoral', a: RUTA_CONSULTA },
              { texto: 'Resultado' },
            ]}
          />
          <PageHeading
            enfocar
            titulo="Tu información electoral"
            subtitulo="Revisa tu lugar de votación y si tienes una designación como jurado."
            extremo={<Stepper pasoActual={2} />}
          />
          <CiudadanoResumen ciudadano={ciudadano} mostrarEdad={!jurado} />
        </div>

        {jurado ? <JuradoAlert titulo={textos.tituloAviso} detalle={textos.detalleAviso} /> : <VotanteAlert />}

        <div className={estilos.columnas}>
          <div className={estilos.columnaPrincipal}>
            <LugarVotacionCard lugar={lugar} esJurado={Boolean(jurado)} />
            {jurado ? <AsignacionJuradoCard jurado={jurado} detalle={textos.detalleTarjeta} /> : <ConsejoVotacion />}
          </div>
          <div className={estilos.columnaLateral}>
            <MapaPuesto lugar={lugar} mesaEnTitulo={Boolean(jurado)} nota={textos?.notaMapa} />
            {jurado && <ResponsabilidadesNota titulo={textos.tituloNota} texto={textos.textoNota} />}
          </div>
        </div>

        <ResultadoDisclaimer />
      </div>
    </PageLayout>
  );
}
