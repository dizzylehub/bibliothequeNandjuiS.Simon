"""Rendus studio (Blender Cycles) de chaque variante de mobilier et de chaque assise.

Mêmes volumes que les fiches et planches (mobilier.py), mêmes matériaux que les rendus
d'intérieur (rendu_blender.py). Vue de trois quarts avant-gauche, comme les axonométries.

Usage (bpy 5.x) : python rendu_mobilier_blender.py [--res 1400] [--echantillons 96] [CLÉ ...]
  ->  v8/rendus/mobilier/<CLÉ>.png
"""
import argparse
import json
import math
import os
import sys

import bpy
from mathutils import Vector

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import rendu_blender as RB  # noqa: E402

CORRESP = {"noyer": "Noyer", "noyer clair": "Noyer clair", "cognac": "Velours cognac", "olive": "Velours olive",
           "creme": "Crème", "laiton": "Laiton", "verre": "Verre", "canne": "Canne", "acier": "Acier noir",
           "corde": "Corde", "moutarde": "Moutarde", "contreplaque": "Contreplaqué", "terre": "Claustra terre cuite",
           "livre1": "Livres bleu", "livre2": "Livres rouge", "livre3": "Livres or", "feutre": "Feutre"}


def boite(v, mat):
    x0, y0, z0, x1, y1, z1 = v[1:7]
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.scale = (max(x1 - x0, 1e-3), max(y1 - y0, 1e-3), max(z1 - z0, 1e-3))
    o.data.materials.append(mat)


def barre(v, mat):
    p, q, e = Vector(v[1]), Vector(v[2]), v[4]
    d = q - p
    if d.length < 1e-4:
        return
    bpy.ops.mesh.primitive_cylinder_add(radius=e / 2, depth=d.length, location=(p + q) / 2, vertices=20)
    o = bpy.context.active_object
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)


def studio(lo, hi, res, ratio=4 / 3, marge=0.78):
    fond = RB.uni("Fond studio", "#efe8dc", 0.9, 0, 0.02, 1, 0)
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, lo.z - 0.001))
    bpy.context.active_object.data.materials.append(fond)
    c = (lo + hi) / 2
    r = (hi - lo).length / 2
    w = bpy.data.worlds.new("studio")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.95, 0.92, 0.87, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.25
    for (pos, e, taille) in (((-3, -4, 4.5), 110, 3.0), ((4, -2, 2.5), 35, 2.0), ((0, 4, 3.5), 45, 2.5)):
        l = bpy.data.lights.new("boite", "AREA")
        l.size = taille * max(r, 0.5)
        l.energy = e * max(r, 0.5) ** 2
        l.color = (1.0, 0.95, 0.88)
        o = bpy.data.objects.new("boite", l)
        o.location = c + Vector(pos) * max(r, 0.5)
        o.rotation_euler = (c - o.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.collection.objects.link(o)
    cam = bpy.data.cameras.new("cam")
    cam.lens = 70
    o = bpy.data.objects.new("cam", cam)
    direction = Vector((-1.0, -1.25, 0.75)).normalized()
    fov = 2 * math.atan(cam.sensor_width / 2 / cam.lens) / ratio
    o.location = c + direction * (r / math.sin(fov / 2)) * marge
    o.rotation_euler = (c - o.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(o)
    sc = bpy.context.scene
    sc.camera = o
    sc.render.resolution_x = res
    sc.render.resolution_y = int(res / ratio)


def rendre(cle, vol, res, ech):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MAT = RB.materiaux()
    MAT["Corde"] = RB.uni("Corde", "#3f6a5e", 0.7, 0, 0.1, 60)
    # chaque livre est un objet séparé : une couleur franche par famille suffit
    MAT["Livres bleu"] = RB.uni("Dos bleu", "#24426e", 0.55, 0, 0.08, 20)
    MAT["Livres rouge"] = RB.uni("Dos rouge", "#7e3024", 0.55, 0, 0.08, 20)
    MAT["Livres or"] = RB.uni("Dos or", "#b8862c", 0.5, 0, 0.08, 20)
    for v in vol:
        if v[0] == "b":
            boite(v, MAT[CORRESP[v[7]]])
        else:
            barre(v, MAT[CORRESP[v[3]]])
    pts = [o.matrix_world @ Vector(c) for o in bpy.data.objects for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    studio(lo, hi, res)
    RB.regler(ech, False)
    sc = bpy.context.scene
    sc.view_settings.exposure = 0.0
    sortie = os.path.abspath(os.path.join(ICI, "..", "rendus", "mobilier", cle + ".png"))
    sc.render.filepath = sortie
    bpy.ops.render.render(write_still=True)
    print("rendu :", sortie)


ECHANTILLONS = ["Noyer", "Noyer clair", "Velours cognac", "Velours olive", "Moutarde", "Laiton",
                "Sol intérieur", "Cloison neuve", "Claustra terre cuite", "Canne", "Contreplaqué", "Acier noir"]


def echantillon(nom, res, ech):
    """Un échantillon de matériau : pavé arrondi de 30 × 30 × 6 cm, vu de trois quarts."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MAT = RB.materiaux()
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.03))
    o = bpy.context.active_object
    o.scale = (0.30, 0.30, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new("arrondi", "BEVEL")
    bv.width, bv.segments = 0.012, 6
    bpy.ops.object.shade_smooth()
    o.data.materials.append(MAT[nom])
    studio(Vector((-0.15, -0.15, 0)), Vector((0.15, 0.15, 0.06)), res, 1.0, 1.05)
    RB.regler(ech, False)
    sc = bpy.context.scene
    sc.view_settings.exposure = 0.0
    cle = "MAT_" + nom.replace(" ", "_").replace("é", "e").replace("è", "e")
    sc.render.filepath = os.path.abspath(os.path.join(ICI, "..", "rendus", "mobilier", cle + ".png"))
    bpy.ops.render.render(write_still=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=1400)
    ap.add_argument("--echantillons", type=int, default=96)
    ap.add_argument("cles", nargs="*")
    a = ap.parse_args()
    data = json.load(open(os.path.join(ICI, "..", "rendus", "mobilier_volumes.json"), encoding="utf-8"))
    os.makedirs(os.path.join(ICI, "..", "rendus", "mobilier"), exist_ok=True)
    for cle in a.cles or sorted(data) + ["MATERIAUX"]:
        if cle == "MATERIAUX":
            for nom in ECHANTILLONS:
                echantillon(nom, 600, a.echantillons)
        else:
            rendre(cle, data[cle], a.res, a.echantillons)


if __name__ == "__main__":
    main()
