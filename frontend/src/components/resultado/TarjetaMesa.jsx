// Tarjeta de una mesa: encabezado, MesaDestacada, puesto, dirección, ciudad y departamento.
// Es la base común de LugarVotacionCard y AsignacionJuradoCard.
import { useId } from 'react';
import Card from '../common/Card.jsx';
import DataField from '../common/DataField.jsx';
import MesaDestacada from './MesaDestacada.jsx';
import estilos from './TarjetaMesa.module.css';

/** ubicacion trae puesto, direccion, ciudad y departamento; mesa son las props de MesaDestacada. */
export default function TarjetaMesa({ icono, titulo, mesa, etiquetaPuesto, etiquetaDireccion, ubicacion }) {
  const idTitulo = useId();
  return (
    <Card como="section" className={estilos.tarjeta} aria-labelledby={idTitulo}>
      <div className={estilos.encabezado}>
        <img src={icono} alt="" width="22" height="22" />
        <h2 id={idTitulo} className={estilos.titulo}>{titulo}</h2>
      </div>
      <MesaDestacada {...mesa} />
      <dl className={estilos.datos}>
        <DataField etiqueta={etiquetaPuesto} valor={ubicacion.puesto} />
        <DataField etiqueta={etiquetaDireccion} valor={ubicacion.direccion} />
      </dl>
      <dl className={estilos.administrativa}>
        <DataField etiqueta="Ciudad" valor={ubicacion.ciudad} />
        <DataField etiqueta="Departamento" valor={ubicacion.departamento} />
      </dl>
    </Card>
  );
}
