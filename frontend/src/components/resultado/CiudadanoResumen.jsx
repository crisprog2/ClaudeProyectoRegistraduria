// Resumen del ciudadano: nombre, cédula formateada, edad (solo votante), badge y "Realizar otra consulta".
import { Link } from 'react-router-dom';
import iconoFlecha from '../../assets/iconos/flecha-izquierda.svg';
import iconoPersona from '../../assets/iconos/persona.svg';
import { formatearCedula } from '../../utils/formatearCedula.js';
import { RUTA_CONSULTA } from '../../utils/rutas.js';
import Badge from '../common/Badge.jsx';
import estilos from './CiudadanoResumen.module.css';

/** La API siempre devuelve la edad; mostrarEdad decide si se ve (en el Figma, solo el votante la muestra). */
export default function CiudadanoResumen({ ciudadano, mostrarEdad }) {
  return (
    <section className={estilos.resumen} aria-label="Persona consultada">
      <div className={estilos.identificacion}>
        <span className={estilos.avatar}>
          <img src={iconoPersona} alt="" width="22" height="22" />
        </span>
        <div className={estilos.datos}>
          <p className={estilos.nombre}>{ciudadano.nombre_completo}</p>
          <p className={estilos.detalle}>Cédula de ciudadanía · {formatearCedula(ciudadano.cedula)}</p>
          {mostrarEdad && <p className={estilos.detalle}>Edad · {ciudadano.edad} años</p>}
        </div>
        <Badge variante="ficticio">DATOS FICTICIOS</Badge>
      </div>
      <Link to={RUTA_CONSULTA} className={estilos.accion}>
        <img src={iconoFlecha} alt="" width="18" height="18" />
        Realizar otra consulta
      </Link>
    </section>
  );
}
