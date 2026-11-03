// Panel "Tu voz cuenta" con la ilustración de la urna y el tarjetón.
// La ilustración se arma con las piezas del Figma en sus posiciones; es decorativa (aria-hidden).
import iconoCasilla from '../../assets/iconos/casilla-marcada.svg';
import iconoCheck from '../../assets/iconos/check-urna.svg';
import destello from '../../assets/ilustraciones/destello.svg';
import detalleCivico from '../../assets/ilustraciones/detalle-civico.svg';
import haloExterior from '../../assets/ilustraciones/halo-exterior.svg';
import haloInterior from '../../assets/ilustraciones/halo-interior.svg';
import lateralUrna from '../../assets/ilustraciones/lateral-urna.svg';
import sombraUrna from '../../assets/ilustraciones/sombra-urna.svg';
import tapaUrna from '../../assets/ilustraciones/tapa-urna.svg';
import estilos from './PromoPanel.module.css';

/** Panel azul oscuro de la pantalla de consulta. */
export default function PromoPanel() {
  return (
    <aside className={estilos.panel} aria-labelledby="titulo-promo">
      <div className={estilos.ilustracion} aria-hidden="true">
        <img className={estilos.haloExterior} src={haloExterior} alt="" width="340" height="340" />
        <img className={estilos.haloInterior} src={haloInterior} alt="" width="270" height="270" />
        <img className={estilos.sombra} src={sombraUrna} alt="" width="225" height="18" />
        <div className={estilos.urna}>
          <img className={estilos.tapa} src={tapaUrna} alt="" width="200" height="32" />
          <span className={estilos.frente} />
          <img className={estilos.lateral} src={lateralUrna} alt="" width="25" height="136" />
          <span className={estilos.ranura} />
          <span className={estilos.simbolo}>
            <img src={iconoCheck} alt="" width="27" height="27" />
          </span>
        </div>
        <div className={estilos.tarjeton}>
          <span className={estilos.marca} />
          <span className={estilos.seleccion}>
            <img src={iconoCasilla} alt="" width="24" height="24" />
            <span className={estilos.opcion} />
          </span>
        </div>
        <img className={estilos.detalle} src={detalleCivico} alt="" width="9" height="9" />
        <img className={estilos.destello} src={destello} alt="" width="23" height="23" />
      </div>

      <p className={estilos.antetitulo}>
        <span className={estilos.acento} aria-hidden="true" />
        TU VOZ CUENTA
      </p>
      <div className={estilos.mensaje}>
        <h2 id="titulo-promo" className={estilos.titulo}>Participar empieza por estar bien informado.</h2>
        <p className={estilos.detalleTexto}>Tu puesto, tu mesa y tus responsabilidades, en un solo lugar.</p>
      </div>
    </aside>
  );
}
