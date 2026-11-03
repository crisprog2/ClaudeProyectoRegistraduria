// Componente raíz: router del navegador con las rutas de la aplicación.
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { rutas } from './routes.jsx';

/** Monta el router y una <Route> por cada entrada de routes.jsx. */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {rutas.map(({ path, element }) => (
          <Route key={path} path={path} element={element} />
        ))}
      </Routes>
    </BrowserRouter>
  );
}
