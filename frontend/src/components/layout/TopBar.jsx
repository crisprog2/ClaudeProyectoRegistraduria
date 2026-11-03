// Barra superior: contexto "Colombia · Información electoral", Accesibilidad e idioma (solo visuales).
import estilos from './TopBar.module.css';

/** Franja azul oscura de 32 px sobre el header. */
export default function TopBar() {
  return (
    <div className={estilos.barra}>
      <div className={`contenedor ${estilos.contenido}`}>
        <p>Colombia · Información electoral</p>
        <div className={estilos.opciones}>
          <span>Accesibilidad</span>
          <span>Español · ES</span>
        </div>
      </div>
    </div>
  );
}
