// Sección "Una consulta sencilla, paso a paso": tres pasos de orientación.
import iconoCedula from '../../assets/iconos/cedula-paso.svg';
import iconoJurados from '../../assets/iconos/jurados-paso.svg';
import iconoUbicacion from '../../assets/iconos/ubicacion-paso.svg';
import PasoItem from './PasoItem.jsx';
import estilos from './PasosConsulta.module.css';

const PASOS = [
  { icono: iconoCedula, titulo: 'Ten tu cédula a la mano', descripcion: 'Solo necesitas el número de tu cédula de ciudadanía.' },
  { icono: iconoUbicacion, titulo: 'Ubica dónde votar', descripcion: 'Encuentra tu mesa, la dirección y una referencia en el mapa.' },
  { icono: iconoJurados, titulo: 'Revisa si eres jurado', descripcion: 'Si tienes una designación, verás tus datos de servicio por separado.' },
];

/** Guía de tres pasos bajo el formulario. */
export default function PasosConsulta() {
  return (
    <section className={estilos.seccion} aria-labelledby="titulo-pasos">
      <h2 id="titulo-pasos" className={estilos.titulo}>Una consulta sencilla, paso a paso</h2>
      <ol className={estilos.pasos}>
        {PASOS.map((paso) => (
          <PasoItem key={paso.titulo} {...paso} />
        ))}
      </ol>
    </section>
  );
}
