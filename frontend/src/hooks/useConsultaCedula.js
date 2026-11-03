// Hook que encapsula el estado de la consulta: valida, llama a la API y navega al resultado.
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { consultarCedula } from '../services/api.js';
import { RUTA_RESULTADO } from '../utils/rutas.js';
import { validarCedula } from '../utils/validarCedula.js';

/**
 * Estado de la pantalla de consulta.
 *  - consultando: true mientras espera la respuesta de la API.
 *  - error: { codigo, mensaje } del último intento, o null.
 *  - consultar(valor): valida en el cliente; si es válido consulta la API y, si hay resultado,
 *    navega a /consulta/resultado con el resultado en el estado de navegación (nunca en la URL).
 *  - limpiarError(): quita el error (se llama cuando la persona edita el campo).
 */
export default function useConsultaCedula() {
  const navigate = useNavigate();
  const [consultando, setConsultando] = useState(false);
  const [error, setError] = useState(null);

  async function consultar(valor) {
    const validacion = validarCedula(valor);
    if (validacion.error) {
      setError(validacion.error);
      return;
    }

    setError(null);
    setConsultando(true);
    try {
      const resultado = await consultarCedula(validacion.cedula);
      navigate(RUTA_RESULTADO, { state: { resultado } });
    } catch (errorConsulta) {
      setError({ codigo: errorConsulta.codigo, mensaje: errorConsulta.message });
      setConsultando(false);
    }
  }

  return { consultando, error, consultar, limpiarError: () => setError(null) };
}
