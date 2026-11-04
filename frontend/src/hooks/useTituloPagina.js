// Hook que pone el título de la pestaña según la pantalla: es lo primero que anuncia un lector de pantalla.
import { useEffect } from 'react';

/** Título de la pestaña con la marca ficticia: "Consulta electoral · ConsultaVoto". */
export default function useTituloPagina(titulo) {
  useEffect(() => {
    document.title = `${titulo} · ConsultaVoto`;
  }, [titulo]);
}
