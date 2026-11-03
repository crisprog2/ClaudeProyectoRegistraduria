// Aviso de sitio de demostración con datos ficticios. Debe estar visible en todas las pantallas.
import iconoInfo from '../../assets/iconos/info-aviso.svg';
import estilos from './DemoBanner.module.css';

/** Franja amarilla clara bajo el header que aclara que el sitio no es oficial. */
export default function DemoBanner() {
  return (
    <div className={estilos.aviso} role="note" aria-label="Aviso de demostración">
      <div className={`contenedor ${estilos.contenido}`}>
        <img src={iconoInfo} alt="" width="17" height="17" />
        <p className={estilos.titulo}>Sitio de demostración.</p>
        <p className={estilos.detalle}>Datos ficticios de muestra. No está conectado a los registros oficiales.</p>
      </div>
    </div>
  );
}
