// Encabezado de página: antetítulo opcional, título (h1), subtítulo y un elemento opcional a la derecha (el Stepper).
import estilos from './PageHeading.module.css';

/**
 * Dos variantes del Figma:
 *  - 'portada' (Consulta): antetítulo, título de 44 px en dos líneas; el extremo se alinea arriba.
 *  - 'seccion' (Resultado): título de 34 px sin antetítulo; el extremo se centra verticalmente.
 */
export default function PageHeading({ antetitulo, titulo, subtitulo, extremo, variante = 'seccion' }) {
  return (
    <div className={`${estilos.encabezado} ${estilos[variante]}`}>
      <div className={estilos.textos}>
        {antetitulo && <p className={estilos.antetitulo}>{antetitulo}</p>}
        <h1 className={estilos.titulo}>{titulo}</h1>
        {subtitulo && <p className={estilos.subtitulo}>{subtitulo}</p>}
      </div>
      {extremo && <div className={estilos.extremo}>{extremo}</div>}
    </div>
  );
}
