# Portadas de las destacadas

Portadas de las destacadas de Instagram. Qué lleva cada destacada y por qué está en
[docs/planes/perfil-redes.md](../../../docs/planes/perfil-redes.md) §6.

| Fichero | Qué es |
|---|---|
| `portadas.html` | Fuente: iconos en SVG y colores de `marca/tokens.css`. Sin parámetros, abre la galería (cómo se ven en el perfil); con `?c=<id>&v=<variante>`, dibuja una portada a 1080×1920 |
| `png/naranja/` | **Recomendada.** Fondo naranja Méhari, trazo azahar |
| `png/cal/` | Alternativa. Fondo cal, trazo naranja tostado |
| `historias/` | Las historias de cada destacada: qué se sube, en qué orden y con qué texto ([README](historias/README.md)) |

Orden en el perfil: `01_bodas` (Bodas), `02_volante` (Al volante), `03_mehari` (Los Méhari),
`04_reservar` (Reservar), `05_preguntas` (Preguntas), `06_sevilla` (Sevilla). `07_parejas` y
`08_prensa` se añaden cuando haya testimonios por escrito y permiso de prensa.

## Subirlas

En Instagram: destacada → Editar destacada → Editar portada → icono de galería → elegir el PNG.
El icono ya está centrado en la zona que recorta el círculo.

## Volver a exportar

Si cambia un icono o un color (por ejemplo, al elegir el logo), se edita `portadas.html` y se
regeneran los PNG con Chrome sin interfaz. Desde Git Bash, en esta carpeta:

```bash
CH="/c/Program Files/Google/Chrome/Application/chrome.exe"
U="file:///$(pwd -W)/portadas.html"
n=1
for c in bodas volante mehari reservar preguntas sevilla parejas prensa; do
  for v in naranja cal; do
    "$CH" --headless=new --hide-scrollbars --window-size=1080,1920 \
      --screenshot="$(pwd -W)/png/$v/0${n}_$c.png" "$U?c=$c&v=$v"
  done
  n=$((n+1))
done
```
