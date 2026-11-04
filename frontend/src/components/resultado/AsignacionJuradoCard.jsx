// Tarjeta "Tu asignación como jurado" (solo si es jurado).
import iconoJurado from '../../assets/iconos/jurado-tarjeta.svg';
import { formatearMesa } from '../../utils/formatearUbicacion.js';
import TarjetaMesa from './TarjetaMesa.jsx';

/** Muestra la mesa de servicio, que puede ser distinta a la mesa donde vota. */
export default function AsignacionJuradoCard({ jurado, detalle }) {
  const mesa = formatearMesa(jurado.mesa);
  return (
    <TarjetaMesa
      icono={iconoJurado}
      titulo="Tu asignación como jurado"
      mesa={{
        variante: 'jurado',
        numero: `${mesa} · Jurado`,
        titulo: `Mesa de servicio · ${jurado.rol_display} · Mesa ${mesa}`,
        detalle,
      }}
      etiquetaPuesto="Puesto de servicio como jurado"
      etiquetaDireccion="Dirección de servicio"
      ubicacion={jurado}
    />
  );
}
