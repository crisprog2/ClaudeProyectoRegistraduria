// Aviso de condición electoral: base común de VotanteAlert y JuradoAlert.
import Badge from '../common/Badge.jsx';
import estilos from './AvisoCondicion.module.css';

/**
 * Tarjeta con ícono circular, título, badge y detalle.
 * variante: 'votante' (fondo blanco) o 'jurado' (fondo azul claro).
 */
export default function AvisoCondicion({ variante, icono, tamanoIcono, titulo, badge, children }) {
  return (
    <section className={`${estilos.aviso} ${estilos[variante]}`} aria-labelledby="titulo-condicion">
      <span className={estilos.icono}>
        <img src={icono} alt="" width={tamanoIcono} height={tamanoIcono} />
      </span>
      <div className={estilos.textos}>
        <div className={estilos.condicion}>
          <h2 id="titulo-condicion" className={estilos.titulo}>{titulo}</h2>
          <Badge variante={variante}>{badge}</Badge>
        </div>
        <p className={estilos.detalle}>{children}</p>
      </div>
    </section>
  );
}
