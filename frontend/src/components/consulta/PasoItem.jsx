// Ítem individual de la sección de pasos: ícono en un cuadro blanco, título y descripción.
import estilos from './PasoItem.module.css';

/** Un paso de la guía "Una consulta sencilla, paso a paso". */
export default function PasoItem({ icono, titulo, descripcion }) {
  return (
    <li className={estilos.paso}>
      <span className={estilos.icono}>
        <img src={icono} alt="" width="19" height="19" />
      </span>
      <div className={estilos.textos}>
        <h3 className={estilos.titulo}>{titulo}</h3>
        <p className={estilos.descripcion}>{descripcion}</p>
      </div>
    </li>
  );
}
