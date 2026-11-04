// Textos de la pantalla del jurado según dónde presta servicio.
// El caso "misma mesa" es el del Figma (6:2609); "otra mesa" y "otro puesto" fueron aprobados
// aparte porque el Figma no los diseña. Todos son neutros en género.
import { formatearMesa } from './formatearUbicacion.js';

/** True si las dos ubicaciones corresponden al mismo puesto. */
function mismoPuesto(lugar, jurado) {
  return lugar.puesto === jurado.puesto && lugar.direccion === jurado.direccion && lugar.ciudad === jurado.ciudad;
}

/**
 * Devuelve los textos del aviso, la tarjeta, el mapa y la nota final.
 * lugar es lugar_votacion y jurado es la designación de la respuesta de la API.
 */
export function textosJurado(lugar, jurado) {
  const mesaVoto = formatearMesa(lugar.mesa);
  const mesaServicio = formatearMesa(jurado.mesa);

  if (jurado.misma_mesa) {
    return {
      tituloAviso: 'Tienes una designación como jurado en la misma mesa donde votas',
      detalleAviso: 'En este caso de ejemplo, votas y prestas servicio como jurado en la misma mesa. Revisa el puesto, la dirección y la mesa común.',
      detalleTarjeta: 'Es la misma mesa donde vas a votar',
      notaMapa: `En este ejemplo, votas y prestas servicio como jurado en la misma mesa ${mesaVoto}.`,
      tituloNota: 'Una mesa, dos responsabilidades',
      textoNota: `En este caso de ejemplo, votas y prestas servicio como jurado en la misma mesa ${mesaVoto}, en el mismo puesto y con la misma dirección.`,
    };
  }

  if (mismoPuesto(lugar, jurado)) {
    return {
      tituloAviso: 'Tienes una designación como jurado en otra mesa de tu puesto',
      detalleAviso: `En este caso de ejemplo, votas en la mesa ${mesaVoto} y prestas servicio en la mesa ${mesaServicio}. Revisa ambas mesas.`,
      detalleTarjeta: 'Es otra mesa del mismo puesto donde vas a votar',
      notaMapa: `En este ejemplo, votas en la mesa ${mesaVoto} y prestas servicio en la mesa ${mesaServicio}.`,
      tituloNota: 'Dos mesas, un mismo puesto',
      textoNota: `En este caso de ejemplo, votas en la mesa ${mesaVoto} y prestas servicio en la mesa ${mesaServicio}, en el mismo puesto y con la misma dirección.`,
    };
  }

  return {
    tituloAviso: 'Tienes una designación como jurado en otro puesto',
    detalleAviso: 'En este caso de ejemplo, votas y prestas servicio en lugares distintos. Revisa ambas direcciones.',
    detalleTarjeta: 'Es un puesto distinto al de tu votación',
    notaMapa: `Este mapa muestra tu lugar de votación. Tu puesto de servicio es ${jurado.puesto}.`,
    tituloNota: 'Dos lugares, dos responsabilidades',
    textoNota: `En este caso de ejemplo, votas en ${lugar.puesto} y prestas servicio en ${jurado.puesto}.`,
  };
}
