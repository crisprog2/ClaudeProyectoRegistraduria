// Configuración del reporte de Allure 3: nombre, idioma, agrupación y etiquetas ocultas.
import { defineConfig } from "allure";

export default defineConfig({
  name: "ConsultaVoto · Pruebas",
  output: "./allure-report",
  // Nombre del equipo e hilo de ejecución: no aportan al reporte y exponen el nombre de la máquina.
  hideLabels: ["host", "thread"],
  plugins: {
    awesome: {
      options: {
        reportLanguage: "es",
        // Backend / API / BDD / E2E, luego el módulo o el canal BDD, luego el feature.
        groupBy: ["parentSuite", "suite", "subSuite"],
      },
    },
  },
});
