// Rutas: /consulta y /consulta/resultado. La cédula viaja en el estado de navegación, nunca en la URL.
import { Navigate } from 'react-router-dom';
import ConsultaPage from './pages/ConsultaPage.jsx';
import NotFoundPage from './pages/NotFoundPage.jsx';
import ResultadoPage from './pages/ResultadoPage.jsx';
import { RUTA_CONSULTA, RUTA_RESULTADO } from './utils/rutas.js';

/** Tabla de rutas: la raíz redirige a la consulta y cualquier otra ruta muestra la página 404. */
export const rutas = [
  { path: '/', element: <Navigate to={RUTA_CONSULTA} replace /> },
  { path: RUTA_CONSULTA, element: <ConsultaPage /> },
  { path: RUTA_RESULTADO, element: <ResultadoPage /> },
  { path: '*', element: <NotFoundPage /> },
];
