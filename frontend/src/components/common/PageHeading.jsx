// Encabezado de página: antetítulo opcional, título (h1), subtítulo y un elemento opcional a la derecha (el Stepper).
import { useEffect, useRef } from 'react';
import estilos from './PageHeading.module.css';

/**
 * Dos variantes del Figma:
 *  - 'portada' (Consulta): antetítulo, título de 44 px en dos líneas; el extremo se alinea arriba.
 *  - 'seccion' (Resultado): título de 34 px sin antetítulo; el extremo se centra verticalmente.
 *
 * 'enfocar' lleva el foco al h1 al montar: al cambiar de pantalla sin recargar, el foco se perdería
 * y quien usa teclado o lector de pantalla no sabría que la página cambió.
 */
export default function PageHeading({ antetitulo, titulo, subtitulo, extremo, variante = 'seccion', enfocar = false }) {
  const encabezado = useRef(null);

  useEffect(() => {
    if (enfocar) encabezado.current?.focus();
  }, [enfocar]);

  return (
    <div className={`${estilos.encabezado} ${estilos[variante]}`}>
      <div className={estilos.textos}>
        {antetitulo && <p className={estilos.antetitulo}>{antetitulo}</p>}
        <h1 ref={encabezado} tabIndex={-1} className={estilos.titulo}>{titulo}</h1>
        {subtitulo && <p className={estilos.subtitulo}>{subtitulo}</p>}
      </div>
      {extremo && <div className={estilos.extremo}>{extremo}</div>}
    </div>
  );
}
