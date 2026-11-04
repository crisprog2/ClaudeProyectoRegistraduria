// Par etiqueta/valor (Puesto, Dirección, Ciudad, Departamento). Se usa dentro de un <dl>.
import estilos from './DataField.module.css';

/** Etiqueta gris de 12 px y valor de 15 px. */
export default function DataField({ etiqueta, valor }) {
  return (
    <div className={estilos.dato}>
      <dt className={estilos.etiqueta}>{etiqueta}</dt>
      <dd className={estilos.valor}>{valor}</dd>
    </div>
  );
}
