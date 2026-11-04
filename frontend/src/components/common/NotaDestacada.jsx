// Nota sobre fondo gris azulado con ícono, título y texto ("Antes de ir a votar", notas del jurado).
import estilos from './NotaDestacada.module.css';

/** Bloque de orientación; se usa como aside con su título enlazado por aria-labelledby. */
export default function NotaDestacada({ id, icono, titulo, children }) {
  return (
    <aside className={estilos.nota} aria-labelledby={id}>
      <img src={icono} alt="" width="20" height="20" />
      <div className={estilos.textos}>
        <h2 id={id} className={estilos.titulo}>{titulo}</h2>
        <p className={estilos.texto}>{children}</p>
      </div>
    </aside>
  );
}
