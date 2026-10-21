#!/usr/bin/env bash
# Exporta cada historia de historias.html a jpg/<id>.jpg (1080×1920). Se ejecuta desde esta carpeta,
# después de `python preparar.py`. Necesita Chrome y Python con Pillow.
set -e
CH="/c/Program Files/Google/Chrome/Application/chrome.exe"
U="file:///$(pwd -W)/historias.html"
mkdir -p jpg png_tmp
for id in $(grep -o "id: '[0-9][^']*'" historias.html | cut -d"'" -f2); do
  "$CH" --headless=new --hide-scrollbars --virtual-time-budget=5000 --window-size=1080,1920 \
    --screenshot="$(pwd -W)/png_tmp/$id.png" "$U?id=$id" >/dev/null 2>&1
done
python -c "
from pathlib import Path
from PIL import Image
for p in Path('png_tmp').glob('*.png'):
    Image.open(p).convert('RGB').save(Path('jpg') / (p.stem + '.jpg'), quality=90)
    p.unlink()
"
rmdir png_tmp
ls jpg | wc -l
