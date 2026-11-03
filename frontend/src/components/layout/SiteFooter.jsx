// Footer con la marca ficticia y el aviso de prototipo sin validez oficial.
import estilos from './SiteFooter.module.css';

/** Pie de página blanco con borde superior. */
export default function SiteFooter() {
  return (
    <footer className={estilos.pie}>
      <div className={`contenedor ${estilos.contenido}`}>
        <div className={estilos.identidad}>
          <p className={estilos.marca}>ConsultaVoto · Proyecto de portafolio QA</p>
          <p className={estilos.aviso}>Prototipo visual · Información de ejemplo, sin validez oficial.</p>
        </div>
        <p className={estilos.lema}>Información clara para participar.</p>
      </div>
    </footer>
  );
}
