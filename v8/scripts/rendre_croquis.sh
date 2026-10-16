#!/bin/sh
# Régénère les croquis SVG puis leurs aperçus PNG (Chromium sans interface).
set -e
cd "$(dirname "$0")/../.."
python3 v8/scripts/croquis_dizzy.py
B=${CHROME:-$(find /opt/pw-browsers -name chrome -type f | head -1)}
T=$(mktemp -d)
for f in v8/croquis/*.svg; do
  n=$(basename "$f" .svg)
  set -- $(grep -o 'viewBox="0 0 [0-9]* [0-9]*"' "$f" | tr -d '"' | awk '{print $3, $4}')
  printf '<html><body style="margin:0"><img src="file://%s/%s" width="%s" height="%s"></body></html>' "$PWD" "$f" "$1" "$2" > "$T/p.html"
  "$B" --headless --no-sandbox --disable-gpu --hide-scrollbars --allow-file-access-from-files --window-size="$1,$(($2 + 200))" --screenshot="$T/s.png" "file://$T/p.html" >/dev/null 2>&1
  python3 -c "from PIL import Image; Image.open('$T/s.png').crop((0,0,$1,$2)).save('v8/croquis/$n.png')"
done
rm -rf "$T"
