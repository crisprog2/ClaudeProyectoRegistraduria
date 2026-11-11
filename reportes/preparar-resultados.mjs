// Limpia los resultados de Allure antes de generar el reporte.
//
// - Quita las fixtures que terminaron bien. allure-pytest registra cada fixture
//   (las de pytest-django, Playwright y las propias) como un paso de
//   "Configuración" o "Desmontaje": unas 20 por prueba. Las que fallaron se
//   conservan, porque explican por qué la prueba no corrió.
// - Quita el parámetro interno de pytest-bdd con el ejemplo completo del
//   esquema: el plugin de tests/support/allure_reporte.py ya agrega cada
//   columna como parámetro propio, y Allure 3 no respeta el modo oculto.
import { readdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const carpeta = process.argv[2] ?? "allure-results";
const fallo = (fixture) => fixture.status && fixture.status !== "passed";
const PARAMETRO_INTERNO_BDD = "_pytest_bdd_example";

let archivos;
try {
  archivos = await readdir(carpeta);
} catch {
  console.error(`No existe la carpeta de resultados "${carpeta}". Corre primero las pruebas con --alluredir.`);
  process.exit(1);
}

let quitadas = 0;
for (const nombre of archivos.filter((archivo) => archivo.endsWith("-container.json"))) {
  const ruta = join(carpeta, nombre);
  const contenedor = JSON.parse(await readFile(ruta, "utf-8"));
  for (const fase of ["befores", "afters"]) {
    const antes = contenedor[fase]?.length ?? 0;
    contenedor[fase] = (contenedor[fase] ?? []).filter(fallo);
    quitadas += antes - contenedor[fase].length;
  }
  await writeFile(ruta, JSON.stringify(contenedor));
}
let parametros = 0;
for (const nombre of archivos.filter((archivo) => archivo.endsWith("-result.json"))) {
  const ruta = join(carpeta, nombre);
  const resultado = JSON.parse(await readFile(ruta, "utf-8"));
  const visibles = (resultado.parameters ?? []).filter((parametro) => parametro.name !== PARAMETRO_INTERNO_BDD);
  if (visibles.length !== (resultado.parameters ?? []).length) {
    resultado.parameters = visibles;
    parametros += 1;
    await writeFile(ruta, JSON.stringify(resultado));
  }
}
console.log(`Fixtures exitosas quitadas del reporte: ${quitadas}`);
console.log(`Escenarios BDD sin el parámetro interno de pytest-bdd: ${parametros}`);
