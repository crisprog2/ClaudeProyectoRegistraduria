// Punto de entrada: carga la fuente y los estilos globales y monta <App /> en el DOM.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource-variable/inter';
import './styles/tokens.css';
import './styles/global.css';
import App from './App.jsx';

// El navegador conserva el estado de navegación al recargar. Se borra al cargar la página para
// que el resultado (datos del ciudadano) no sobreviva a una recarga: ResultadoPage vuelve a /consulta.
window.history.replaceState(null, '');

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
