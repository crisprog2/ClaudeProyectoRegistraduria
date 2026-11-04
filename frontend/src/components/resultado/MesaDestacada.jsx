// Bloque destacado de mesa con variantes votación (azul) y jurado (amarillo).
import estilos from './MesaDestacada.module.css';

/** 'numero' es el texto grande: "012", "018 · Votación" o "018 · Jurado". */
export default function MesaDestacada({ variante, numero, titulo, detalle }) {
  return (
    <div className={`${estilos.bloque} ${estilos[variante]}`}>
      <p className={estilos.numero}>{numero}</p>
      <div className={estilos.textos}>
        <p className={estilos.titulo}>{titulo}</p>
        <p className={estilos.detalle}>{detalle}</p>
      </div>
    </div>
  );
}
