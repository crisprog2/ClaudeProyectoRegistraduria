// Tarjeta "Tu lugar para votar".
import iconoVoto from '../../assets/iconos/voto-tarjeta.svg';
import { formatearMesa } from '../../utils/formatearUbicacion.js';
import TarjetaMesa from './TarjetaMesa.jsx';

/** Como en el Figma, el número va solo para el votante ("012") y con etiqueta para el jurado ("018 · Votación"). */
export default function LugarVotacionCard({ lugar, esJurado }) {
  const mesa = formatearMesa(lugar.mesa);
  return (
    <TarjetaMesa
      icono={iconoVoto}
      titulo="Tu lugar para votar"
      mesa={{
        variante: 'votacion',
        numero: esJurado ? `${mesa} · Votación` : mesa,
        titulo: 'Mesa de votación',
        detalle: 'Aquí ejerces tu derecho al voto',
      }}
      etiquetaPuesto="Puesto de votación"
      etiquetaDireccion="Dirección"
      ubicacion={lugar}
    />
  );
}
