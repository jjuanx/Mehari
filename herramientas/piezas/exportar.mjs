// Exporta las diapositivas de una plantilla estática a JPEG (calidad 90).
// Uso: node exportar.mjs <proyecto> <n> <ancho> <alto> <carpeta salida> <prefijo>
// Abre <proyecto>/index.html?s=i para i = 0..n-1 y guarda <prefijo>NN.jpg (NN desde 01).
// Espera a las tipografías y a todas las imágenes antes de cada captura.
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , proyecto, n, ancho, alto, salida, prefijo = ''] = process.argv;
if (!salida) {
  console.error('Uso: node exportar.mjs <proyecto> <n> <ancho> <alto> <carpeta salida> <prefijo>');
  process.exit(2);
}
mkdirSync(salida, { recursive: true });
const base = pathToFileURL(join(resolve(proyecto), 'index.html')).href;

const nav = await chromium.launch({ args: ['--allow-file-access-from-files'] });
try {
  const pag = await nav.newPage({ viewport: { width: Number(ancho), height: Number(alto) } });
  for (let s = 0; s < Number(n); s++) {
    await pag.goto(`${base}?s=${s}`);
    await pag.waitForSelector('body[data-listo="1"]');
    await pag.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map(i => i.complete && i.naturalWidth ? 0 : i.decode()));
    });
    const nombre = `${prefijo}${String(s + 1).padStart(2, '0')}.jpg`;
    await pag.screenshot({ path: join(salida, nombre), type: 'jpeg', quality: 90 });
  }
} finally {
  await nav.close();
}
