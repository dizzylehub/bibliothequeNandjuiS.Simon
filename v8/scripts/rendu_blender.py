"""Rendus réalistes (Blender Cycles) du café-bibliothèque, depuis la maquette IFC V8.

La géométrie vient de v8/rendus/scene_v8.npz (exporter_scene.py) : mêmes cotes que le plan E01
et l'IFC. Les matériaux sont procéduraux (noyer, velours, laiton, terrazzo, enduit à la chaux) ;
l'éclairage reprend le plan T01 (suspensions globe, lignes LED, lampadaires, globes de pergola).

Usage (bpy 5.x, Python 3.13) :
  python rendu_blender.py --vue P1 --ambiance soir --res 1600 --echantillons 128
  vues : P1 entrée, P2 salon, P3 terrasse, P4 réunion, P5 accueil, P6 terrasse vue haute
"""
import argparse
import json
import math
import os

import bpy
import numpy as np
from mathutils import Vector

ICI = os.path.dirname(os.path.abspath(__file__))
SCENE = os.path.join(ICI, "..", "rendus", "scene_v8.npz")

# caméra : oeil, cible, angle de champ horizontal (degrés)
VUES = {
    "P1": ((4.3, 0.15, 1.6), (4.9, 7.0, 1.0), 78),
    "P2": ((5.45, 6.85, 1.65), (1.4, 1.6, 0.95), 72),
    "P3": ((5.2, -7.8, 1.8), (3.2, 0.0, 1.1), 60),
    "P4": ((2.88, 5.02, 1.78), (0.45, 2.55, 0.70), 84),
    "P5": ((3.75, 0.22, 1.65), (0.80, 2.00, 0.90), 82),
    "P6": ((-3.2, -9.6, 4.2), (3.4, -2.2, 0.7), 55),
}
EXCLURE = ("Mur séparatif à démolir",)


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1.0,)


# ------------------------------------------------------------------ matériaux procéduraux
def nouveau(nom):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return m, nt, bsdf


def coord(nt, echelle=1.0):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (echelle, echelle, echelle)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    return mp.outputs[0]


def rampe(nt, entree, c0, c1, p0=0.0, p1=1.0):
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].position, r.color_ramp.elements[0].color = p0, c0
    r.color_ramp.elements[1].position, r.color_ramp.elements[1].color = p1, c1
    nt.links.new(entree, r.inputs[0])
    return r.outputs[0]


def biseau(nt, bsdf, rayon=0.004):
    b = nt.nodes.new("ShaderNodeBevel")
    b.samples = 4
    b.inputs["Radius"].default_value = rayon
    nt.links.new(b.outputs[0], bsdf.inputs["Normal"])


def bois(nom, fonce, clair, rugo=0.42, vernis=0.25):
    m, nt, b = nouveau(nom)
    v = coord(nt)
    # cernes : ondes très distordues ; fil : bruit étiré dans le sens du bois
    onde = nt.nodes.new("ShaderNodeTexWave")
    onde.wave_type, onde.bands_direction = "BANDS", "X"
    onde.inputs["Scale"].default_value = 9.0
    onde.inputs["Distortion"].default_value = 2.5
    onde.inputs["Detail"].default_value = 6
    onde.inputs["Detail Scale"].default_value = 1.6
    nt.links.new(v, onde.inputs["Vector"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (90.0, 3.0, 3.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    fil = nt.nodes.new("ShaderNodeTexNoise")
    fil.inputs["Scale"].default_value = 1.0
    fil.inputs["Detail"].default_value = 10
    nt.links.new(mp.outputs[0], fil.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.62
    nt.links.new(onde.outputs["Fac"], mix.inputs["A"])
    nt.links.new(fil.outputs["Fac"], mix.inputs["B"])
    nt.links.new(rampe(nt, mix.outputs["Result"], rgb(fonce), rgb(clair), 0.2, 0.85), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rugo
    b.inputs["Coat Weight"].default_value = vernis
    b.inputs["Coat Roughness"].default_value = 0.25
    biseau(nt, b)
    return m


def velours(nom, couleur, clair):
    m, nt, b = nouveau(nom)
    v = coord(nt)
    bruit = nt.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = 18.0
    nt.links.new(v, bruit.inputs["Vector"])
    nt.links.new(rampe(nt, bruit.outputs["Fac"], rgb(couleur), rgb(clair), -0.6, 1.6), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    b.inputs["Sheen Weight"].default_value = 1.0
    b.inputs["Sheen Tint"].default_value = rgb(clair)
    b.inputs["Sheen Roughness"].default_value = 0.35
    biseau(nt, b, 0.012)
    return m


def uni(nom, couleur, rugo=0.6, metal=0.0, varia=0.06, echelle=4.0, bevel=0.003):
    m, nt, b = nouveau(nom)
    v = coord(nt)
    bruit = nt.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = echelle
    bruit.inputs["Detail"].default_value = 8
    nt.links.new(v, bruit.inputs["Vector"])
    c = rgb(couleur)
    c0 = tuple(max(0, x * (1 - varia)) for x in c[:3]) + (1,)
    c1 = tuple(min(1, x * (1 + varia)) for x in c[:3]) + (1,)
    nt.links.new(rampe(nt, bruit.outputs["Fac"], c0, c1, 0.3, 0.7), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rugo
    b.inputs["Metallic"].default_value = metal
    if bevel:
        biseau(nt, b, bevel)
    return m


def terrazzo(nom):
    m, nt, b = nouveau(nom)
    v = coord(nt)
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.distance = "MINKOWSKI"
    vo.inputs["Exponent"].default_value = 0.75
    vo.inputs["Scale"].default_value = 30.0
    nt.links.new(v, vo.inputs["Vector"])
    base = rgb("#cfc0a6")
    pierre = rampe(nt, vo.outputs["Color"], rgb("#7a4a2c"), rgb("#f2ead9"), 0.25, 0.8)
    seuil = nt.nodes.new("ShaderNodeMath")
    seuil.operation = "LESS_THAN"
    seuil.inputs[1].default_value = 0.5
    nt.links.new(vo.outputs["Distance"], seuil.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = base
    nt.links.new(seuil.outputs[0], mix.inputs["Factor"])
    nt.links.new(pierre, mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.22
    b.inputs["Coat Weight"].default_value = 0.4
    return m


def dallage(nom):
    m, nt, b = nouveau(nom)
    v = coord(nt)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 1.6
    br.inputs["Color1"].default_value = rgb("#cdbfa6")
    br.inputs["Color2"].default_value = rgb("#bfae92")
    br.inputs["Mortar"].default_value = rgb("#8f8576")
    br.inputs["Mortar Size"].default_value = 0.01
    br.offset = 0.0
    nt.links.new(v, br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.8
    return m


def verre(nom):
    m, nt, b = nouveau(nom)
    b.inputs["Base Color"].default_value = (0.92, 0.96, 0.95, 1)
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.02
    b.inputs["IOR"].default_value = 1.45
    return m


def livres(nom, a, c):
    m, nt, b = nouveau(nom)
    v = coord(nt)
    # une couleur tirée au hasard par tranche de 4 cm : un dos de livre
    snap = nt.nodes.new("ShaderNodeVectorMath")
    snap.operation = "SNAP"
    snap.inputs[1].default_value = (0.04, 0.04, 0.35)
    nt.links.new(v, snap.inputs[0])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn.noise_dimensions = "3D"
    nt.links.new(snap.outputs[0], wn.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.interpolation = "CONSTANT"
    els = r.color_ramp.elements
    els[0].position, els[0].color = 0.0, rgb(a)
    els[1].position, els[1].color = 0.86, rgb("#e9dfc8")
    for pos, h in ((0.18, c), (0.34, "#5a3a26"), (0.50, "#2f4a3a"), (0.64, "#b8862c"), (0.76, "#8a2f24")):
        e = els.new(pos)
        e.color = rgb(h)
    nt.links.new(wn.outputs["Value"], r.inputs[0])
    nt.links.new(r.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.55
    biseau(nt, b, 0.002)
    return m


def vegetal(nom):
    m, nt, b = nouveau(nom)
    v = coord(nt)
    bruit = nt.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = 9.0
    nt.links.new(v, bruit.inputs["Vector"])
    nt.links.new(rampe(nt, bruit.outputs["Fac"], rgb("#1f3a1c"), rgb("#6f9446"), 0.3, 0.8), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.55
    b.inputs["Subsurface Weight"].default_value = 0.15
    return m


def materiaux():
    return {
        "Noyer": bois("Noyer", "#26140a", "#5e3820"),
        "Noyer clair": bois("Noyer clair", "#5a3820", "#8f6040"),
        "Contreplaqué": bois("Contreplaqué", "#a07c4c", "#cfae7c", 0.5, 0.1),
        "Velours cognac": velours("Velours cognac", "#7a3a14", "#c27a42"),
        "Velours olive": velours("Velours olive", "#3a4224", "#7a8450"),
        "Moutarde": velours("Moutarde", "#9a6e18", "#d9a842"),
        "Feutre": velours("Feutre", "#3e4628", "#6a7448"),
        "Laiton": uni("Laiton", "#c9a24a", 0.22, 1.0, 0.04, 30, 0.002),
        "Acier noir": uni("Acier noir", "#1c1c1c", 0.45, 0.8, 0.05),
        "Crème": uni("Crème", "#efe4cc", 0.55),
        "Faïence blanche": uni("Faïence blanche", "#f4f2ee", 0.12, 0, 0.02),
        "Maçonnerie existante": uni("Maçonnerie existante", "#e3d6bf", 0.9, 0, 0.07, 2.5, 0),
        "Cloison neuve": uni("Cloison neuve", "#e8dcc4", 0.9, 0, 0.06, 2.5, 0),
        "Béton": uni("Béton", "#a9a59c", 0.85, 0, 0.1, 3, 0),
        "Claustra terre cuite": uni("Claustra terre cuite", "#b0603a", 0.8, 0, 0.1, 6),
        "Sol intérieur": terrazzo("Sol intérieur"),
        "Dallage terrasse": dallage("Dallage terrasse"),
        "Verre": verre("Verre"),
        "Livres bleu": livres("Livres bleu", "#22406b", "#8a3b2e"),
        "Livres rouge": livres("Livres rouge", "#7a2e22", "#22406b"),
        "Livres or": livres("Livres or", "#b8862c", "#3a5a4a"),
        "Végétal": vegetal("Végétal"),
        "Mur à démolir": uni("Mur à démolir", "#d0c4ae", 0.9),
        "Canne": uni("Canne", "#d6b679", 0.6, 0, 0.1, 40),
    }


# ------------------------------------------------------------------ géométrie
def construire(MAT):
    d = np.load(SCENE)
    V, T, M = d["V"], d["T"], d["M"]
    objets = json.loads(str(d["objets"]))
    noms = json.loads(str(d["materiaux"]))
    ov, ot = 0, 0
    for o in objets:
        v = V[ov:ov + o["n_v"]]
        t = T[ot:ot + o["n_t"]]
        mm = M[ot:ot + o["n_t"]]
        ov += o["n_v"]
        ot += o["n_t"]
        if o["nom"].startswith(EXCLURE):
            continue
        if o["nom"] == "Plante en pot":
            plante(v, MAT["Végétal"])
            continue
        me = bpy.data.meshes.new(o["nom"])
        me.from_pydata(v.tolist(), [], t.tolist())
        uniques = sorted(set(mm.tolist()))
        for u in uniques:
            me.materials.append(MAT.get(noms[u], MAT["Crème"]))
        idx = {u: i for i, u in enumerate(uniques)}
        me.polygons.foreach_set("material_index", [idx[x] for x in mm.tolist()])
        me.validate()
        ob = bpy.data.objects.new(o["nom"], me)
        bpy.context.collection.objects.link(ob)


def plante(v, mat):
    """Remplace la boîte « plante en pot » par un feuillage de sphères déformées."""
    x0, y0, z0 = v.min(0)
    x1, y1, z1 = v.max(0)
    rng = np.random.default_rng(int(abs(x0 * 100 + y0 * 10)))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for k in range(26):
        r = rng.uniform(0.09, 0.17)
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0, 0.24)
        z = rng.uniform(z0 + 0.15, z1)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(cx + d * math.cos(a), cy + d * math.sin(a), z))
        ob = bpy.context.active_object
        ob.scale = (1.0, rng.uniform(0.35, 0.6), rng.uniform(0.25, 0.5))
        ob.rotation_euler = (rng.uniform(0, 1), rng.uniform(0, 1), a)
        ob.data.materials.append(mat)


# ------------------------------------------------------------------ éclairage
def emissif(nom, kelvin, force):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    bb = nt.nodes.new("ShaderNodeBlackbody")
    bb.inputs[0].default_value = kelvin
    nt.links.new(bb.outputs[0], em.inputs["Color"])
    em.inputs["Strength"].default_value = force
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def lampe(pos, watts, kelvin=2700, rayon=0.08):
    l = bpy.data.lights.new("lampe", "POINT")
    l.energy = watts
    l.shadow_soft_size = rayon
    l.use_custom_distance = False
    l.color = kelvin_rgb(kelvin)
    o = bpy.data.objects.new("lampe", l)
    o.location = pos
    bpy.context.collection.objects.link(o)


def kelvin_rgb(k):
    t = k / 100.0
    r = 1.0 if t <= 66 else min(1, 1.292936 * ((t - 60) ** -0.1332047592))
    g = min(1, (99.4708025861 * math.log(t) - 161.1195681661) / 255) if t <= 66 else min(1, 1.129890861 * ((t - 60) ** -0.0755148492))
    b = 1.0 if t >= 66 else (0 if t <= 19 else min(1, (138.5177312231 * math.log(t - 10) - 305.0447927307) / 255))
    return (r, max(g, 0), max(b, 0))


def globe(pos, r, mat_verre, watts):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=pos, segments=32, ring_count=16)
    o = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat_verre)
    o.visible_shadow = False
    lampe(pos, watts, 2700, r * 0.8)
    # suspente
    bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=3.0 - pos[2] - r, location=(pos[0], pos[1], (3.0 + pos[2] + r) / 2))


def lampadaire(x, y, mat_laiton, mat_abat):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=1.45, location=(x, y, 0.725))
    bpy.context.active_object.data.materials.append(mat_laiton)
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.14, depth=0.26, location=(x, y, 1.50))
    o = bpy.context.active_object
    o.data.materials.append(mat_abat)
    lampe((x, y, 1.45), 45, 2700, 0.1)


def eclairage(soir, MAT):
    opale = emissif("Opaline", 2700, 9.0 if soir else 2.0)
    led = emissif("LED 2700 K", 2700, 18.0 if soir else 6.0)
    abat = emissif("Abat-jour", 2600, 2.5 if soir else 0.6)
    # suspensions globe (T01) : table d'hôtes, comptoir, salle de réunion
    for (x, y) in ((4.45, 2.10), (5.25, 2.10), (1.88, 1.2), (1.88, 1.8), (0.9, 3.28), (2.1, 3.28)):
        globe((x, y, 2.05 if x > 3 else 2.15), 0.14, opale, 40 if soir else 10)
    # lignes LED dans le plafond en lames
    for x in (3.75, 4.85, 5.95):
        for (ya, yb) in ((0.6, 3.2), (4.4, 7.0)):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, (ya + yb) / 2, 2.985))
            o = bpy.context.active_object
            o.scale = (0.03, yb - ya, 0.01)
            o.data.materials.append(led)
            o.visible_shadow = False
    # rail lumineux du mur de la collection (éclaire les livres)
    for (p, q) in (((6.28, 0.4), (6.28, 3.2)), ((6.28, 4.3), (6.28, 7.1)), ((3.4, 7.13), (6.2, 7.13))):
        l = bpy.data.lights.new("rail", "AREA")
        l.shape = "RECTANGLE"
        l.size = max(abs(q[0] - p[0]), 0.05)
        l.size_y = max(abs(q[1] - p[1]), 0.05)
        l.energy = 120 if soir else 40
        l.color = kelvin_rgb(2700)
        o = bpy.data.objects.new("rail", l)
        o.location = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, 2.9)
        bpy.context.collection.objects.link(o)
    for (x, y) in ((4.30, 5.65), (6.30, 5.65), (6.15, 0.75)):
        lampadaire(x, y, MAT["Laiton"], abat)
    # WC
    for x in (0.62, 2.17):
        lampe((x, 6.6, 2.7), 25 if soir else 10, 3000)
    # terrasse : globes sous la pergola et guirlande
    for x in (0.2, 2.3, 4.5, 6.6):
        for y in (-1.6, -3.6):
            globe((x, y, 2.45), 0.13, opale, 35 if soir else 0.1)
    if soir:
        pts = [(-0.9, -4.9), (1.25, -4.6), (3.4, -4.9), (5.55, -4.6), (7.7, -4.9)]
        ampoule = emissif("Guirlande", 2400, 25)
        for (a, b) in zip(pts, pts[1:]):
            for k in range(7):
                u = k / 7
                x = a[0] + (b[0] - a[0]) * u
                y = a[1] + (b[1] - a[1]) * u
                z = 2.55 - 0.18 * math.sin(math.pi * u)
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(x, y, z), segments=12, ring_count=6)
                bpy.context.active_object.data.materials.append(ampoule)


def environnement(soir, MAT):
    """Contexte hors maquette, figuré simplement : sol du quartier, immeuble au-dessus, grand arbre."""
    # sol au-delà de la terrasse
    bpy.ops.mesh.primitive_plane_add(size=60, location=(3.5, -20, -0.16))
    herbe = uni("Sol du quartier", "#6f6a58", 0.95, 0, 0.15, 0.8, 0)
    bpy.context.active_object.data.materials.append(herbe)
    # étages de l'immeuble habité au-dessus du local (volume simple)
    enduit = uni("Façade immeuble", "#d8cfc0", 0.9, 0, 0.05, 1.5, 0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(3.4, 4.0, 3.30 + 4.5))
    o = bpy.context.active_object
    o.scale = (10.0, 8.6, 9.0)
    o.data.materials.append(enduit)
    fen = emissif("Fenêtre habitée", 2900, 1.6) if soir else verre("Vitre étage")
    noire = uni("Vitre sombre", "#1d2226", 0.15, 0, 0.0, 1, 0)
    rng = np.random.default_rng(7)
    for etage in range(3):
        for x in (-0.6, 1.4, 3.4, 5.4, 7.4):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.31, 4.6 + etage * 3.0))
            w = bpy.context.active_object
            w.scale = (1.2, 0.02, 1.5)
            w.data.materials.append(fen if rng.random() < 0.45 else noire)
    # grand arbre (badamier) au-delà du muret
    tronc = uni("Écorce", "#4a3b2e", 0.9, 0, 0.2, 8)
    for (cx, cy, h) in ((-4.2, -8.5, 6.5), (10.5, -9.5, 5.5)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=h, location=(cx, cy, h / 2 - 0.15))
        bpy.context.active_object.data.materials.append(tronc)
        r = np.random.default_rng(int(cx * 10) % 97)
        for k in range(70):
            a, d = r.uniform(0, 2 * math.pi), r.uniform(0, 3.2)
            z = h - 0.6 + r.uniform(-0.8, 0.9) - 0.15 * d
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r.uniform(0.4, 0.8), location=(cx + d * math.cos(a), cy + d * math.sin(a), z))
            f = bpy.context.active_object
            f.scale = (1.0, 1.0, 0.55)
            f.data.materials.append(MAT["Végétal"])


def monde(soir):
    w = bpy.data.worlds.new("ciel")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    if soir:
        sky = nt.nodes.new("ShaderNodeTexSky")
        sky.sky_type = "MULTIPLE_SCATTERING" if hasattr(sky, "sky_type") and "MULTIPLE_SCATTERING" in [i.identifier for i in sky.bl_rna.properties["sky_type"].enum_items] else sky.sky_type
        try:
            sky.sun_elevation = math.radians(-2.5)
        except Exception:
            pass
        nt.links.new(sky.outputs[0], bg.inputs[0])
        bg.inputs[1].default_value = 0.08
    else:
        sky = nt.nodes.new("ShaderNodeTexSky")
        try:
            sky.sun_elevation = math.radians(52)
            sky.sun_rotation = math.radians(200)
        except Exception:
            pass
        nt.links.new(sky.outputs[0], bg.inputs[0])
        bg.inputs[1].default_value = 0.35
        s = bpy.data.lights.new("soleil", "SUN")
        s.energy = 3.2
        s.angle = math.radians(1.5)
        s.color = (1.0, 0.96, 0.9)
        o = bpy.data.objects.new("soleil", s)
        o.rotation_euler = (math.radians(38), 0, math.radians(200))
        bpy.context.collection.objects.link(o)


def camera(vue, res, ratio=1.5):
    oeil, cible, fov = VUES[vue]
    c = bpy.data.cameras.new("cam")
    c.sensor_fit = "HORIZONTAL"
    c.angle = math.radians(fov)
    c.clip_start = 0.05
    o = bpy.data.objects.new("cam", c)
    o.location = oeil
    d = Vector(cible) - Vector(oeil)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(o)
    sc = bpy.context.scene
    sc.camera = o
    sc.render.resolution_x = res
    sc.render.resolution_y = int(res / ratio)


def regler(echantillons, soir):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = echantillons
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 4
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 8
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    sc.view_settings.exposure = -1.3 if soir else -2.2
    sc.render.image_settings.file_format = "PNG"
    sc.render.threads_mode = "AUTO"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vue", default="P1")
    ap.add_argument("--ambiance", default="soir", choices=["soir", "jour"])
    ap.add_argument("--res", type=int, default=1600)
    ap.add_argument("--echantillons", type=int, default=128)
    ap.add_argument("--sortie", default=None)
    ap.add_argument("--exposition", type=float, default=None)
    a = ap.parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    soir = a.ambiance == "soir"
    MAT = materiaux()
    construire(MAT)
    eclairage(soir, MAT)
    environnement(soir, MAT)
    monde(soir)
    camera(a.vue, a.res)
    regler(a.echantillons, soir)
    if a.exposition is not None:
        bpy.context.scene.view_settings.exposure = a.exposition
    sortie = a.sortie or os.path.join(ICI, "..", "rendus", f"R_{a.vue}_{a.ambiance}.png")
    bpy.context.scene.render.filepath = os.path.abspath(sortie)
    bpy.ops.render.render(write_still=True)
    print("rendu :", os.path.abspath(sortie))


if __name__ == "__main__":
    main()
