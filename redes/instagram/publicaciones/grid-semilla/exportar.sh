#!/usr/bin/env bash
# Exporta cada diapositiva de piezas.html a JPEG de 1080×1440 en jpg/<pieza>/NN.jpg.
# Se ejecuta desde Git Bash en esta carpeta: bash exportar.sh
# Necesita Chrome y FFmpeg (la API de Instagram solo acepta JPEG).
set -euo pipefail
cd "$(dirname "$0")"
CH="/c/Program Files/Google/Chrome/Application/chrome.exe"
U="file:///$(pwd -W)/piezas.html"

declare -A SLIDES=( [foto-f0345]=1 [foto-f0524]=1 [foto-f1839]=1 [ideas-fotos]=10 [naranja-beige]=4 )

for p in "${!SLIDES[@]}"; do
  mkdir -p "jpg/$p"
  for ((s = 0; s < ${SLIDES[$p]}; s++)); do
    n=$(printf '%02d' $((s + 1)))
    png="$(pwd -W)/jpg/$p/$n.png"
    "$CH" --headless=new --hide-scrollbars --allow-file-access-from-files \
      --virtual-time-budget=6000 --window-size=1080,1440 \
      --screenshot="$png" "$U?p=$p&s=$s" 2>/dev/null
    ffmpeg -v error -y -i "jpg/$p/$n.png" -q:v 2 "jpg/$p/$n.jpg"
    rm "jpg/$p/$n.png"
  done
  echo "$p: ${SLIDES[$p]} diapositivas"
done
