#!/bin/sh
# Rendus réalistes Cycles. BPY_PYTHON : interpréteur Python où bpy (Blender 5.x) est installé.
set -e
cd "$(dirname "$0")/../.."
PY=${BPY_PYTHON:-python3}
RES=${RES:-1600}
ECH=${ECH:-64}
python3 v8/scripts/exporter_scene.py
for a in "P1 soir" "P2 soir" "P3 soir" "P3 jour" "P4 soir" "P5 soir" "P6 soir" "P6 jour"; do
  set -- $a
  "$PY" v8/scripts/rendu_blender.py --vue "$1" --ambiance "$2" --res "$RES" --echantillons "$ECH" 2>&1 | grep -E "rendu :|Error" || true
done
# rendus studio du mobilier et planche de matériaux
python3 v8/scripts/exporter_mobilier.py
"$PY" v8/scripts/rendu_mobilier_blender.py --res 1200 --echantillons 48 2>&1 | grep -E "rendu :|Error" || true
echo FIN
