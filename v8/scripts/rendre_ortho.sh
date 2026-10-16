#!/bin/sh
# Plan rendu et coupes rendues (Blender Cycles), puis habillage façon Photoshop.
set -e
cd "$(dirname "$0")/../.."
PY=${BPY_PYTHON:-python3}
ECH=${ECH:-48}
for a in "PLAN jour" "COUPE_AA soir" "COUPE_AA jour" "COUPE_BB jour"; do
  set -- $a
  "$PY" v8/scripts/rendu_blender.py --vue "$1" --ambiance "$2" --echantillons "$ECH" 2>&1 | grep -E "rendu :|Error" || true
done
python3 v8/scripts/habillage_ortho.py
echo FIN_ORTHO
