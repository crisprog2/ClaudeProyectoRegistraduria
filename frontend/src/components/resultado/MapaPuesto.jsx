// Mapa ilustrativo (no cartográfico) del puesto de votación. No usa servicios de mapas externos.
import iconoInfo from '../../assets/iconos/info-mapa.svg';
import iconoMapa from '../../assets/iconos/mapa.svg';
import iconoNorte from '../../assets/iconos/norte.svg';
import iconoUbicacion from '../../assets/iconos/ubicacion-mapa.svg';
import arbolChico from '../../assets/ilustraciones/arbol-chico.svg';
import arbolGrande from '../../assets/ilustraciones/arbol-grande.svg';
import areaMarcador from '../../assets/ilustraciones/area-marcador.svg';
import centroMarcador from '../../assets/ilustraciones/centro-marcador.svg';
import marcadorPuesto from '../../assets/ilustraciones/marcador-puesto.svg';
import { formatearLugar, formatearMesa } from '../../utils/formatearUbicacion.js';
import Card from '../common/Card.jsx';
import estilos from './MapaPuesto.module.css';

// Posición de las manzanas: [izquierda, ancho]. Las cuatro primeras son las del Figma (486 px); las demás
// solo se ven cuando la tarjeta se apila a todo el ancho, para que el plano no quede vacío a la derecha.
const COLUMNAS = [[12, 74], [116, 135], [280, 87], [397, 90], [515, 135], [680, 87], [797, 135], [962, 90]];
const CARRERAS = [92, 258, 373, 491, 656, 773, 938];
// Posición de las filas: [arriba, alto].
const FILAS = [[15, 84], [129, 95], [254, 80]];

// El dibujo nombra las calles que rodean a este puesto; en los demás sería información falsa.
const DIRECCION_CON_CALLES = { direccion: 'Calle 48 # 65-20', ciudad: 'Medellín' };

/** Tarjeta "Ubica tu puesto". 'mesaEnTitulo' agrega "· Mesa 018" (jurado) y 'nota' agrega el aviso azul. */
export default function MapaPuesto({ lugar, mesaEnTitulo = false, nota }) {
  const mostrarCalles = lugar.direccion === DIRECCION_CON_CALLES.direccion && lugar.ciudad === DIRECCION_CON_CALLES.ciudad;
  const titulo = mesaEnTitulo ? `${lugar.puesto} · Mesa ${formatearMesa(lugar.mesa)}` : lugar.puesto;

  return (
    <Card como="section" className={estilos.tarjeta} aria-labelledby="titulo-mapa">
      <div className={estilos.encabezado}>
        <img src={iconoMapa} alt="" width="21" height="21" />
        <h2 id="titulo-mapa" className={estilos.titulo}>Ubica tu puesto</h2>
        <span className={estilos.tipo}>ILUSTRATIVO</span>
      </div>

      <div className={estilos.plano} role="img" aria-label={`Plano ilustrativo de ${lugar.puesto}, no cartográfico`}>
        {FILAS.flatMap(([arriba, alto]) => COLUMNAS.map(([izquierda, ancho]) => (
          <span
            key={`${arriba}-${izquierda}`}
            className={estilos.manzana}
            style={{ left: izquierda, top: arriba, width: ancho, height: alto }}
          />
        )))}
        <span className={`${estilos.via} ${estilos.calle}`} style={{ top: 103 }} />
        <span className={`${estilos.via} ${estilos.calle}`} style={{ top: 230 }} />
        {CARRERAS.map((izquierda) => (
          <span key={izquierda} className={`${estilos.via} ${estilos.carrera}`} style={{ left: izquierda }} />
        ))}
        <span className={estilos.parque} />
        <img className={estilos.arbolChico} src={arbolChico} alt="" width="14" height="14" />
        <img className={estilos.arbolGrande} src={arbolGrande} alt="" width="16" height="16" />
        <span className={estilos.predio} />
        <span className={estilos.edificio} />
        <span className={estilos.patio} />

        {mostrarCalles && (
          <>
            <span className={estilos.nombreCalle} style={{ left: 295, top: 106 }}>Calle 49</span>
            <span className={estilos.nombreCalle} style={{ left: 140, top: 233 }}>Calle 48</span>
            <span className={estilos.nombreCarrera} style={{ left: 267.5, top: 262 }}>Carrera 65</span>
            <span className={estilos.nombreCarrera} style={{ left: 102.5, top: 257 }}>Carrera 66</span>
          </>
        )}

        <div className={estilos.referencia}>
          <p className={estilos.referenciaPuesto}>{lugar.puesto}</p>
          <p className={estilos.referenciaDireccion}>{lugar.direccion}</p>
        </div>
        <img className={estilos.areaMarcador} src={areaMarcador} alt="" width="54" height="20" />
        <img className={estilos.marcador} src={marcadorPuesto} alt="" width="60" height="73" />
        <img className={estilos.centroMarcador} src={centroMarcador} alt="" width="14" height="14" />
        <div className={estilos.norte}>
          <span>N</span>
          <img src={iconoNorte} alt="" width="14" height="14" />
        </div>
        <span className={estilos.localidad}>{formatearLugar(lugar.ciudad, lugar.departamento)}</span>
      </div>

      <div className={estilos.pie}>
        <div className={estilos.ubicacion}>
          <img src={iconoUbicacion} alt="" width="21" height="21" />
          <div className={estilos.ubicacionTextos}>
            <p className={estilos.ubicacionPuesto}>{titulo}</p>
            <p className={estilos.ubicacionDireccion}>
              {lugar.direccion} · {formatearLugar(lugar.ciudad, lugar.departamento, ', ')}
            </p>
          </div>
        </div>
        {nota && (
          <p className={estilos.nota}>
            <img src={iconoInfo} alt="" width="16" height="16" />
            {nota}
          </p>
        )}
        <p className={estilos.aclaracion}>
          Representación de ejemplo, no cartografía oficial. El puesto y la dirección son ficticios; no usar para navegación.
        </p>
      </div>
    </Card>
  );
}
