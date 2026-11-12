// Configuración del reporte de Allure 3: nombre, idioma, agrupación, etiquetas ocultas e historial.
import { defineConfig } from "allure";

export default defineConfig({
  name: "ConsultaVoto · Pruebas",
  output: "./allure-report",
  // Nombre del equipo e hilo de ejecución: no aportan al reporte y exponen el nombre de la máquina.
  hideLabels: ["host", "thread"],
  // Historial para las tendencias: cada generación agrega una línea con los resultados.
  // En local queda en historial/ (fuera de Git). En el CI, la variable ALLURE_HISTORIAL apunta
  // al archivo descargado de GitHub Pages, que luego se publica junto al reporte.
  historyPath: process.env.ALLURE_HISTORIAL || "./historial/history.jsonl",
  // Últimas 30 corridas: suficiente para ver tendencias sin que el archivo crezca sin límite.
  historyLimit: 30,
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
