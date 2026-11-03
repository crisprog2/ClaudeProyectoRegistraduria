// Franja tricolor decorativa bajo el header (amarillo 50 %, azul 25 %, rojo 25 %).
import estilos from './FlagStripe.module.css';

/** Acento de 3 px de alto; es decorativo, así que se oculta a los lectores de pantalla. */
export default function FlagStripe() {
  return (
    <div className={estilos.franja} aria-hidden="true">
      <span className={estilos.amarillo} />
      <span className={estilos.azul} />
      <span className={estilos.rojo} />
    </div>
  );
}
