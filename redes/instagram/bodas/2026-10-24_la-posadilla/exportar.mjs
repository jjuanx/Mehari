// Exporta cada diapositiva de piezas.html a JPEG de 1080×1440 en jpg/<pieza>/NN.jpg.
// Uso, desde esta carpeta: node exportar.mjs
// Necesita Node.js y Playwright (npm i -g playwright && npx playwright install chromium).
// La API de Instagram, y por tanto Metricool, solo acepta JPEG en los carruseles.
import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const AQUI = dirname(fileURLToPath(import.meta.url));
const PIEZAS = { 'la-boda': 9, 'el-beige': 4 };

const nav = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const pag = await nav.newPage({ viewport: { width: 1080, height: 1440 } });
for (const [pieza, n] of Object.entries(PIEZAS)) {
  mkdirSync(join(AQUI, 'jpg', pieza), { recursive: true });
  for (let s = 0; s < n; s++) {
    await pag.goto(`${pathToFileURL(join(AQUI, 'piezas.html')).href}?p=${pieza}&s=${s}`);
    await pag.waitForLoadState('networkidle');
    await pag.evaluate(() => document.fonts.ready);
    await pag.screenshot({ path: join(AQUI, 'jpg', pieza, `${String(s + 1).padStart(2, '0')}.jpg`), type: 'jpeg', quality: 90 });
  }
  console.log(`${pieza}: ${n} diapositivas`);
}
await nav.close();
