"""Met à jour DECIMO_ESQ_V3.ifc -> DECIMO_ESQ_V4.ifc (proposition V4 K&Démi).

- arbre à livres, niches cintrées, rails raccourcis, salon recentré ;
- façade : baies cintrées à claustra terre cuite, portail et porte d'entrée cintrée, jardinières ;
- pergola relevée à +2,90, poutre côté façade reculée, lames dégagées autour du portail ;
- matériaux et textures de la palette K&Démi (IfcMaterial, styles de surface, textures image).

Unités du modèle : cm, degrés. Coordonnées ci-dessous en mètres, repère monde.
"""
import sys, time
import numpy as np
import ifcopenshell, ifcopenshell.api, ifcopenshell.guid
import ifcopenshell.util.placement as up
import ifcopenshell.api.owner.settings as owner_settings
from matplotlib.path import Path

SRC, DST = sys.argv[1], sys.argv[2]
f = ifcopenshell.open(SRC)
owner_settings.get_user = lambda f: f.by_type("IfcPersonAndOrganization")[0]
owner_settings.get_application = lambda f: f.by_type("IfcApplication")[0]
api = ifcopenshell.api.run
CM = 100.0
rdc = next(s for s in f.by_type("IfcBuildingStorey") if "RDC" in s.Name)
body = next(c for c in f.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier == "Body")
OH = f.by_type("IfcOwnerHistory")[0]

def by_tag(tag):
    r = [e for e in f.by_type("IfcProduct") if (e.Name or "").split(":")[-1] == tag and not e.is_a("IfcOpeningElement")]
    assert len(r) == 1, (tag, r)
    return r[0]

def by_name(name):
    r = [e for e in f.by_type("IfcProduct") if e.Name == name]
    assert len(r) == 1, (name, r)
    return r[0]

# ============================ 0. charte : styles, matériaux ======================
for ps in f.by_type("IfcPropertySet"):
    if ps.Name == "KDA_Esquisse":
        ps.Name = "KDEMI_Esquisse"

def style(name, hexc, transparency=0.0, method="MATT", spec=None, texture=None):
    rgb = [int(hexc[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    col = f.createIfcColourRgb(None, *rgb)
    ren = f.createIfcSurfaceStyleRendering(
        col, transparency, None, None, None, None,
        f.createIfcColourRgb(None, *([spec] * 3)) if spec else None,
        f.createIfcSpecularRoughness(0.3 if spec else 1.0) if spec else None, method)
    styles = [ren]
    if texture:
        styles.append(f.createIfcSurfaceStyleWithTextures(
            [f.createIfcImageTexture(True, True, "TEXTURE", None, "textures/" + texture)]))
    return f.createIfcSurfaceStyle(name, "BOTH", styles)

S = {
    "blanc": style("KDEMI - Enduit chaux blanc", "#F3EFE6", texture="enduit_chaux_blanc.png"),
    "terre": style("KDEMI - Enduit terre cuite", "#B4583E", texture="enduit_terre_cuite.png"),
    "claustra": style("KDEMI - Claustra terre cuite", "#A9533A", texture="claustra_terre_cuite.png"),
    "acier": style("KDEMI - Acier noir mat", "#1E1E1E", method="METAL", spec=0.25, texture="acier_noir_mat.png"),
    "iroko": style("KDEMI - Bois iroko huilé", "#9A6B43", method="PLASTIC", spec=0.15, texture="iroko_huile.png"),
    "sable": style("KDEMI - Enduit chaux sable", "#E6D6BF", texture="enduit_chaux_sable.png"),
    "gres": style("KDEMI - Grès cérame sable", "#D9CDB8", texture="gres_cerame_sable.png"),
    "tissu": style("KDEMI - Tissu terre cuite", "#A9533A", texture="tissu_terre_cuite.png"),
    "vegetal": style("KDEMI - Végétal", "#5E8C4A", texture="vegetal.png"),
    "vitre": style("KDEMI - Vitrage clair", "#CFE3EA", transparency=0.7, method="GLASS", spec=0.6),
    "livres": style("KDEMI - Livres", "#B07A55", texture="livres.png"),
    "terreau": style("KDEMI - Terre végétale", "#4A3A2C"),
    "led": style("KDEMI - Enseigne lumineuse", "#FFF6E0", method="PLASTIC", spec=0.4),
}
# remplacement global des styles existants (tous les éléments qui les portent)
SWAP = {"Enduit interieur": "sable", "Placo": "sable", "KDA - Placo peint": "sable",
        "DECIMO - Chêne fumé": "iroko", "KDA - Bois clair (lames)": "iroko",
        "DECIMO - Grès sable": "gres", "DECIMO - Tissu olive": "tissu",
        "KDA - Noir mat": "acier", "KDA - Vert végétal": "vegetal"}
old = {s.Name: s for s in f.by_type("IfcSurfaceStyle")}
for psa in f.by_type("IfcPresentationStyleAssignment"):
    new = [S[SWAP[s.Name]] if getattr(s, "Name", None) in SWAP else s for s in psa.Styles]
    psa.Styles = new
for nm in ("KDA - Laqué blanc", "KDA - Tableau blanc"):
    if nm in old:
        old[nm].Name = nm.replace("KDA", "KDEMI")
RENAME_MAT = {"DECIMO - Chêne fumé": "KDEMI - Bois iroko huilé", "DECIMO - Grès sable": "KDEMI - Grès cérame sable",
              "DECIMO - Tissu olive": "KDEMI - Tissu terre cuite", "Enduit interieur": "KDEMI - Enduit chaux sable",
              "Placo": "Placo (fini KDEMI - Enduit chaux sable)"}
for m in f.by_type("IfcMaterial"):
    if m.Name in RENAME_MAT:
        m.Name = RENAME_MAT[m.Name]

MATS = {}
def material(key):
    """IfcMaterial portant le style de surface (lu par les visionneuses), créé à la demande."""
    if key not in MATS:
        st = S[key]
        m = f.createIfcMaterial(st.Name)
        si = f.createIfcStyledItem(None, [f.createIfcPresentationStyleAssignment([st])], None)
        f.createIfcMaterialDefinitionRepresentation(None, None, [f.createIfcStyledRepresentation(body, "Style", "Material", [si])], m)
        MATS[key] = f.createIfcRelAssociatesMaterial(ifcopenshell.guid.new(), OH, None, None, [], m)
    return MATS[key]

def set_material(el, key):
    for rel in list(el.HasAssociations):
        if rel.is_a("IfcRelAssociatesMaterial"):
            objs = [o for o in rel.RelatedObjects if o != el]
            if objs:
                rel.RelatedObjects = objs
            else:
                f.remove(rel)
    rel = material(key)
    rel.RelatedObjects = list(rel.RelatedObjects) + [el]

def body_items(el):
    out = []
    for rep in (el.Representation.Representations if el.Representation else []):
        if rep.RepresentationIdentifier != "Body":
            continue
        for it in rep.Items:
            out += list(it.MappingSource.MappedRepresentation.Items) if it.is_a("IfcMappedItem") else [it]
    return out

def restyle(el, key, only_from=None):
    for it in body_items(el):
        for si in it.StyledByItem or []:
            names = [s.Name for a in si.Styles for s in a.Styles]
            if only_from is None or only_from in names:
                si.Styles = [f.createIfcPresentationStyleAssignment([S[key]])]
        if not it.StyledByItem and only_from is None:
            f.createIfcStyledItem(it, [f.createIfcPresentationStyleAssignment([S[key]])], None)

# ============================ helpers géométriques ===============================
P3 = lambda x, y, z: f.createIfcCartesianPoint((float(x), float(y), float(z)))
P2 = lambda x, y: f.createIfcCartesianPoint((float(x), float(y)))
D3 = lambda *v: f.createIfcDirection(tuple(float(a) for a in v))
DZ = D3(0, 0, 1)

def styled(items, key):
    for it in items:
        f.createIfcStyledItem(it, [f.createIfcPresentationStyleAssignment([S[key]])], None)
    return items

def box(x0, y0, x1, y1, z0, z1):
    x0, x1, y0, y1, z0, z1 = (v * CM for v in (min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1))
    prof = f.createIfcRectangleProfileDef("AREA", None, f.createIfcAxis2Placement2D(P2((x0 + x1) / 2, (y0 + y1) / 2), None), x1 - x0, y1 - y0)
    return f.createIfcExtrudedAreaSolid(prof, f.createIfcAxis2Placement3D(P3(0, 0, z0), None, None), DZ, z1 - z0)

def rbox(cx, cy, L, W, ang, z0, z1):
    """Boîte de longueur L (selon l'angle ang, degrés) et largeur W, centrée en (cx, cy)."""
    a = np.radians(ang)
    pos = f.createIfcAxis2Placement2D(P2(cx * CM, cy * CM), f.createIfcDirection((float(np.cos(a)), float(np.sin(a)))))
    prof = f.createIfcRectangleProfileDef("AREA", None, pos, L * CM, W * CM)
    return f.createIfcExtrudedAreaSolid(prof, f.createIfcAxis2Placement3D(P3(0, 0, z0 * CM), None, None), DZ, (z1 - z0) * CM)

def cyl(cx, cy, r, z0, z1):
    prof = f.createIfcCircleProfileDef("AREA", None, f.createIfcAxis2Placement2D(P2(cx * CM, cy * CM), None), r * CM)
    return f.createIfcExtrudedAreaSolid(prof, f.createIfcAxis2Placement3D(P3(0, 0, z0 * CM), None, None), DZ, (z1 - z0) * CM)

def ring(cx, cy, r, t, z0, z1):
    prof = f.createIfcCircleHollowProfileDef("AREA", None, f.createIfcAxis2Placement2D(P2(cx * CM, cy * CM), None), r * CM, t * CM)
    return f.createIfcExtrudedAreaSolid(prof, f.createIfcAxis2Placement3D(P3(0, 0, z0 * CM), None, None), DZ, (z1 - z0) * CM)

# profils dans le plan vertical XZ, extrudés selon -Y (de y1 vers y0)
def xz_pos(y1):
    return f.createIfcAxis2Placement3D(P3(0, y1 * CM, 0), D3(0, -1, 0), D3(1, 0, 0))

def polyline(pts):
    pts = list(pts)
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    return f.createIfcPolyline([P2(x * CM, z * CM) for x, z in pts])

def xz_solid(outer, y0, y1, voids=()):
    if voids:
        prof = f.createIfcArbitraryProfileDefWithVoids("AREA", None, polyline(outer), [polyline(v) for v in voids])
    else:
        prof = f.createIfcArbitraryClosedProfileDef("AREA", None, polyline(outer))
    return f.createIfcExtrudedAreaSolid(prof, xz_pos(y1), DZ, (y1 - y0) * CM)

def xz_rect(x0, z0, x1, z1, y0, y1):
    return xz_solid([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1)

def xz_ring(cx, cz, r, t, y0, y1):
    prof = f.createIfcCircleHollowProfileDef("AREA", None, f.createIfcAxis2Placement2D(P2(cx * CM, cz * CM), None), r * CM, t * CM)
    return f.createIfcExtrudedAreaSolid(prof, xz_pos(y1), DZ, (y1 - y0) * CM)

def arch(x0, x1, z0, zs, n=24):
    r = (x1 - x0) / 2; c = (x0 + x1) / 2
    return ([(x0, z0), (x1, z0), (x1, zs)] + [(c + r * np.cos(a), zs + r * np.sin(a)) for a in np.linspace(0, np.pi, n)[1:-1]]
            + [(x0, zs)])

def pill(x0, x1, z0, z1, n=20):
    r = (x1 - x0) / 2; c = (x0 + x1) / 2
    return ([(c + r * np.cos(a), z1 - r + r * np.sin(a)) for a in np.linspace(0, np.pi, n)]
            + [(c + r * np.cos(a), z0 + r + r * np.sin(a)) for a in np.linspace(np.pi, 2 * np.pi, n)[:-1]])

def rounded_tl(x0, x1, z0, z1, r, n=10):
    return ([(x0, z0), (x1, z0), (x1, z1), (x0 + r, z1)]
            + [(x0 + r + r * np.cos(a), z1 - r + r * np.sin(a)) for a in np.linspace(np.pi / 2, np.pi, n)[1:]])

PSET = {"Indice": "V4", "Origine": "Proposition V4 K&Démi — arbre à livres et façade cintrée"}

def new_product(ifc_class, name, items, description=None, rep_type="SweptSolid", mat=None, predefined_type=None, **attrs):
    p = api("root.create_entity", f, ifc_class=ifc_class, name=name, predefined_type=predefined_type)
    p.Description = description
    p.OwnerHistory = OH
    for k, v in attrs.items():
        setattr(p, k, v)
    api("spatial.assign_container", f, products=[p], relating_structure=rdc)
    api("geometry.edit_object_placement", f, product=p, matrix=np.eye(4), is_si=True)
    rep = f.createIfcShapeRepresentation(body, "Body", rep_type, items)
    api("geometry.assign_representation", f, product=p, representation=rep)
    pset = api("pset.add_pset", f, product=p, name="KDEMI_Esquisse")
    api("pset.edit_pset", f, pset=pset, properties=PSET)
    if mat:
        set_material(p, mat)
    return p

def tag_modified(p, note):
    pset = next((d.RelatingPropertyDefinition for d in p.IsDefinedBy if d.is_a("IfcRelDefinesByProperties")
                 and d.RelatingPropertyDefinition.Name == "KDEMI_Esquisse"), None)
    if pset is None:
        pset = api("pset.add_pset", f, product=p, name="KDEMI_Esquisse")
    api("pset.edit_pset", f, pset=pset, properties={**PSET, "Modification": note})

def opening_xz(name, host, outer, y0=-0.15, y1=0.15):
    o = new_product("IfcOpeningElement", name, [xz_solid(outer, y0, y1)])
    api("feature.add_feature", f, feature=o, element=host)
    return o

def move_world(p, dx=0.0, dy=0.0, dz=0.0):
    m = up.get_local_placement(p.ObjectPlacement).copy()
    m[:3, 3] /= CM
    m[0, 3] += dx; m[1, 3] += dy; m[2, 3] += dz
    api("geometry.edit_object_placement", f, product=p, matrix=m, is_si=True)

# ============================ 1. suppressions ===================================
REMOVE = ["4350680", "4350681", "4350682", "4350683", "4350684", "4350685",     # bureau du fond + chaises
          "4350661", "4350665",                                                 # rayonnages
          "4350596", "4350597", "4350598", "4350599", "4350600", "4350601",     # anciennes baies de façade
          "4350602", "4350603", "4350604",
          "4350686", "4350691", "4350689", "4350690", "4350694", "4350695",     # rails lumineux (raccourcis)
          "4350708", "4350709"]                                                 # poteaux de pergola (rallongés)
for t in REMOVE:
    api("root.remove_product", f, product=by_tag(t))
for nm in ("Claustra bois paramétrique - mur du fond", "Pergola bois paramétrique (inspiration Kengo Kuma)"):
    api("root.remove_product", f, product=by_name(nm))
facade = by_tag("4350590")
for rel in list(facade.HasOpenings):
    api("root.remove_product", f, product=rel.RelatedOpeningElement)

# ============================ 2. déplacements ===================================
for t, d in {"4350677": (0.07, -0.26), "4350679": (0.07, -0.45), "4350678": (0.07, -0.56),
             "4350739": (1.0, 0), "4350740": (1.0, 0), "4350741": (1.0, 0)}.items():
    move_world(by_tag(t), dx=d[0], dy=d[1])
    tag_modified(by_tag(t), "Déplacé (salon recentré / axe d'entrée en terrasse)")
move_world(by_tag("4350710"), dy=-0.15, dz=0.25)
move_world(by_tag("4350711"), dz=0.25)
for t in ("4350710", "4350711"):
    restyle(by_tag(t), "iroko"); set_material(by_tag(t), "iroko")
    tag_modified(by_tag(t), "Poutre de pergola relevée à +2,90")

# ============================ 3. façade ==========================================
restyle(facade, "blanc")
tag_modified(facade, "Baies cintrées à claustra, entrée cintrée ; finition enduit chaux blanc")
BAIES = {"A": arch(0.55, 1.75, 0.45, 1.95), "B": pill(2.00, 2.70, 0.90, 2.40), "C": pill(5.15, 6.25, 0.60, 2.50)}
DOOR = arch(3.35, 4.85, 0.0, 2.05)

def inset(kind, k):
    if kind == "A":
        return arch(0.55 + k, 1.75 - k, 0.45 + k, 1.95)
    if kind == "B":
        return pill(2.00 + k, 2.70 - k, 0.90 + k, 2.40 - k)
    return pill(5.15 + k, 6.25 - k, 0.60 + k, 2.50 - k)

for kname, shape in BAIES.items():
    o = opening_xz(f"Baie cintrée {kname}", facade, shape)
    win = new_product("IfcWindow", f"Vitrage baie cintrée {kname}", styled([xz_solid(shape, 0.0, 0.012)], "vitre"),
                      description="Vitrage fixe en retrait, derrière le claustra", mat="vitre")
    api("feature.add_filling", f, opening=o, element=win)
    # claustra terre cuite : cadre + anneaux de 20 cm reliés par des pontets
    path = Path(inset(kname, 0.035) + [inset(kname, 0.035)[0]])
    items = [xz_solid(shape, -0.09, -0.03, voids=[inset(kname, 0.035)])]
    xs_ = [p[0] for p in shape]; zs_ = [p[1] for p in shape]
    s_, ro, t_ = 0.20, 0.075, 0.025
    nx = int((max(xs_) - min(xs_)) // s_) + 2; nz = int((max(zs_) - min(zs_)) // s_) + 2
    cx0 = (min(xs_) + max(xs_)) / 2 - (nx - 1) / 2 * s_
    cz0 = min(zs_) + 0.035 + ro
    inside = lambda cx, cz: all(path.contains_point((cx + ro * np.cos(a), cz + ro * np.sin(a))) for a in np.linspace(0, 2 * np.pi, 12))
    keep = {(i, j) for i in range(nx) for j in range(nz) if inside(cx0 + i * s_, cz0 + j * s_)}
    for i, j in keep:
        cx, cz = cx0 + i * s_, cz0 + j * s_
        items.append(xz_ring(cx, cz, ro, t_, -0.09, -0.03))
        if (i + 1, j) in keep:
            items.append(xz_rect(cx + ro - 0.005, cz - 0.017, cx + s_ - ro + 0.005, cz + 0.017, -0.09, -0.03))
        if (i, j + 1) in keep:
            items.append(xz_rect(cx - 0.017, cz + ro - 0.005, cx + 0.017, cz + s_ - ro + 0.005, -0.09, -0.03))
    new_product("IfcBuildingElementProxy", f"Claustra terre cuite baie {kname}", styled(items, "claustra"),
                description="Claustra terre cuite, motif anneaux, module 20 x 20 cm, ép. 6 cm", mat="claustra")

# portail terre cuite + porte d'entrée cintrée
o = opening_xz("Baie entrée principale", facade, DOOR)
new_product("IfcBuildingElementProxy", "Portail d'entrée terre cuite",
            styled([xz_solid(rounded_tl(3.20, 5.00, 0.0, 3.30, 0.45), -0.21, -0.09, voids=[DOOR])], "terre"),
            description="Portail en saillie de 12 cm, enduit teinté terre cuite, angle supérieur arrondi R 45", mat="terre")
inner = arch(3.40, 4.80, 0.0, 2.05)
door_items = styled([xz_solid(DOOR, -0.02, 0.04, voids=[inner]),
                     xz_rect(4.225, 0.0, 4.275, 2.05, -0.02, 0.04), xz_rect(3.40, 2.025, 4.80, 2.075, -0.02, 0.04),
                     xz_rect(4.17, 0.95, 4.19, 1.20, -0.08, -0.02), xz_rect(4.31, 0.95, 4.33, 1.20, -0.08, -0.02)], "acier")
door_items += styled([xz_solid(inner, 0.004, 0.016)], "vitre")
d = new_product("IfcDoor", "Porte d'entrée cintrée double (0,90 + 0,60)", door_items,
                description="Double porte vitrée cintrée, acier noir, ouvrant vers l'extérieur, seuil plat",
                OverallHeight=280.0, OverallWidth=150.0, mat="acier")
api("feature.add_filling", f, opening=o, element=d)
new_product("IfcBuildingElementProxy", "Enseigne lumineuse DECIMO", styled([box(3.62, -0.225, 4.58, -0.21, 2.86, 3.10)], "led"),
            description="Lettres découpées rétroéclairées LED 2700 K sur le portail")

# jardinières maçonnées
for k, (x0, x1) in enumerate(((0.35, 2.95), (5.05, 6.45)), 1):
    its = styled([box(x0, -0.49, x1, -0.44, 0, 0.45), box(x0, -0.44, x0 + 0.05, -0.09, 0, 0.45),
                  box(x1 - 0.05, -0.44, x1, -0.09, 0, 0.45), box(x0, -0.44, x1, -0.09, 0, 0.05)], "blanc")
    its += styled([box(x0 + 0.05, -0.44, x1 - 0.05, -0.09, 0.05, 0.38)], "terreau")
    its += styled([cyl(xx, -0.27, 0.14, 0.38, 0.38 + 0.45 + 0.25 * np.sin(xx * 7) ** 2)
                   for xx in np.arange(x0 + 0.22, x1 - 0.1, 0.42)], "vegetal")
    new_product("IfcBuildingElementProxy", f"Jardinière maçonnée {k}", its,
                description="Jardinière maçonnée enduite, h 45 cm, plantations, LED rasante en pied", mat="blanc")

# ============================ 4. pergola relevée =================================
def spacing(x, attractors, smin, smax, reach):
    dd = min(abs(x - a) for a in attractors)
    return smin + (smax - smin) * (1 - np.exp(-(dd / reach) ** 2))
DZP = 0.25
for xx in (0.25, 6.25):
    new_product("IfcBuildingElementProxy", "Poteau de pergola", styled([box(xx, -2.50, xx + 0.08, -2.42, 0.0, 2.65 + DZP)], "iroko"),
                description="Poteau bois rallongé (pergola relevée à +2,90)", mat="iroko")
xa, x = [], 0.05
while x < 6.56:
    xa.append(x); x += spacing(x, [1.375, 4.80], 0.07, 0.24, 1.3)
ya, y = [], -0.24
while y > -2.45:
    ya.append(y); y -= 0.08 + 0.20 * (abs(y) / 2.5) ** 1.4
PX0, PX1, PYF = 3.15, 5.05, -0.27        # dégagement du portail (lames reculées)
perg = []
for y in ya:
    if y + 0.04 > PYF:
        perg += [box(-0.05, y, PX0, y + 0.04, 2.75 + DZP, 2.81 + DZP), box(PX1, y, 6.65, y + 0.04, 2.75 + DZP, 2.81 + DZP)]
    else:
        perg.append(box(-0.05, y, 6.65, y + 0.04, 2.75 + DZP, 2.81 + DZP))
for x in xa:
    yend = -2.52 - 0.30 * (0.5 + 0.5 * np.sin(2 * np.pi * (x - 0.6) / 3.3))
    hz = 0.10 + 0.16 * (0.5 + 0.5 * np.cos(2 * np.pi * (x - 1.375) / 3.4))
    y_start = PYF if PX0 - 0.02 <= x <= PX1 + 0.02 else -0.17
    perg.append(box(x - 0.017, yend, x + 0.017, y_start, 2.81 + DZP, 2.81 + DZP + hz))
new_product("IfcBuildingElementProxy", "Pergola bois paramétrique (inspiration Kengo Kuma)", styled(perg, "iroko"),
            description=f"2 nappes de lames iroko, relevées à +2,90 ; {len(ya)} lames basses, {len(xa)} lames hautes ; "
                        "lames reculées de 27 cm au droit du portail", mat="iroko")

# ============================ 5. intérieur =======================================
CX, CY = 4.75, 5.61
tree = styled([cyl(CX, CY, 0.40, 0.0, 0.10), cyl(CX, CY, 0.20, 0.10, 2.40)]
              + [cyl(CX, CY, 0.45, z, z + 0.03) for z in 0.10 + 0.33 * np.arange(7)]
              + [ring(CX, CY, 0.47, 0.06, 2.37, 2.41)]
              + [rbox(CX + 0.325 * np.cos(np.radians(a)), CY + 0.325 * np.sin(np.radians(a)), 0.25, 0.02, a, 0.10, 2.37)
                 for a in np.arange(22.5, 360, 45)], "iroko")
tree += styled([ring(CX, CY, 0.43, 0.21, z + 0.03, z + 0.30) for z in 0.10 + 0.33 * np.arange(7)], "livres")
zc = np.linspace(2.40, 3.28, 24)
rc = 0.45 + 0.85 * ((zc - 2.40) / 0.88) ** 2.2
prof_pts = [(r, z) for r, z in zip(rc, zc)] + [(r - 0.05, z) for r, z in zip(rc[::-1], zc[::-1])]
canopy = f.createIfcRevolvedAreaSolid(
    f.createIfcArbitraryClosedProfileDef("AREA", None, polyline(prof_pts)),
    f.createIfcAxis2Placement3D(P3(CX * CM, CY * CM, 0), D3(0, -1, 0), D3(1, 0, 0)),
    f.createIfcAxis1Placement(P3(0, 0, 0), D3(0, 1, 0)), 360.0)
tree += styled([canopy], "iroko")
new_product("IfcFurnishingElement", "DECIMO_L01_Arbre_a_livres:ESQ - sur mesure", tree, rep_type="SweptSolid",
            description="Arbre à livres Ø 90 : 7 plateaux, noyau Ø 40, canopée bois cintrée Ø 260 avec anneau LED", mat="iroko")

# doublage cintré du mur du fond
NICHES = [(3.20, 4.10, 1.95), (4.18, 5.43, 1.80), (5.51, 6.41, 1.95)]
new_product("IfcCovering", "Doublage cintré des niches",
            styled([xz_solid([(3.09, 0.0), (6.51, 0.0), (6.51, 3.30), (3.09, 3.30)], 7.06, 7.41,
                             voids=[arch(x0, x1, 0.0, zs) for x0, x1, zs in NICHES])], "sable"),
            predefined_type="CLADDING", description="Doublage cintré 35 cm, enduit chaux sable ciré", mat="sable")

def under_arch(x0, x1, zs, z):
    r = (x1 - x0) / 2; c = (x0 + x1) / 2
    if z <= zs:
        return x0, x1
    if z >= zs + r - 0.02:
        return None
    hw = np.sqrt(r * r - (z - zs) ** 2)
    return c - hw, c + hw

for k, (x0, x1, zs) in enumerate((NICHES[0], NICHES[2]), 1):
    it = styled([box(x0, 7.06, x1, 7.41, 0.0, 0.10), xz_solid(arch(x0, x1, 0.10, zs), 7.38, 7.41)], "iroko")
    bk = []
    for z in np.arange(0.10, zs + 0.45, 0.36):
        w = under_arch(x0, x1, zs, z + 0.025)
        if w:
            it += styled([box(w[0], 7.08, w[1], 7.38, z, z + 0.025)], "iroko")
            w2 = under_arch(x0, x1, zs, z + 0.31)
            if w2 and w2[1] - w2[0] > 0.1:
                bk.append(box(w2[0] + 0.02, 7.12, w2[1] - 0.02, 7.38, z + 0.025, z + 0.31))
    new_product("IfcFurnishingElement", "DECIMO_N01_Niche_bibliotheque:ESQ - sur mesure", it + styled(bk, "livres"),
                description="Niche cintrée bibliothèque, tablettes iroko tous les 36 cm", mat="iroko")
x0, x1, zs = NICHES[1]
r_ = (x1 - x0) / 2; c_ = (x0 + x1) / 2
it = styled([box(x0, 7.06, x1, 7.41, 0.0, 0.10), box(x0, 6.96, x1, 7.41, 0.10, 0.43),
             box(x0, 7.16, x1, 7.41, 1.50, 1.525)]
            + [box(xx - 0.015, 7.38, xx + 0.015, 7.41, 0.10, zs + np.sqrt(max(r_ ** 2 - (xx - c_) ** 2, 0)) - 0.01)
               for xx in np.arange(x0 + 0.03, x1 - 0.02, 0.05)], "iroko")
it += styled([box(x0 + 0.02, 6.98, x1 - 0.02, 7.36, 0.43, 0.53), box(x0 + 0.05, 7.26, x1 - 0.05, 7.36, 0.53, 0.83)], "tissu")
it += styled([box(x0 + 0.05, 7.18, x0 + 0.50, 7.38, 1.525, 1.80)], "livres")
new_product("IfcFurnishingElement", "DECIMO_N02_Niche_banquette:ESQ - sur mesure", it,
            description="Niche cintrée banquette de lecture, coussins tissu terre cuite, fond en lames bois", mat="iroko")

for xx in (3.65, 5.35):
    new_product("IfcBuildingElementProxy", "Rail lumineux (raccourci)", styled([box(xx - 0.015, 0.40, xx + 0.015, 4.20, 3.10, 3.14)], "acier"),
                description="Rail lumineux arrêté avant la canopée de l'arbre à livres", mat="acier")

# ============================ 6. matériaux des éléments conservés ================
for t in ("4350673", "4350674", "4350675"):
    set_material(by_tag(t), "iroko")
m01 = by_name("DECIMO_M01_Console_Vinyles_P40:ESQ - sur mesure")
restyle(m01, "iroko", only_from="KDEMI - Laqué blanc"); set_material(m01, "iroko")
pouf = by_name("DECIMO_P01_Pouf:ESQ - sur mesure")
restyle(pouf, "tissu"); set_material(pouf, "tissu")
for t in ("4350632", "4350707", "4350634"):
    restyle(by_tag(t), "gres"); set_material(by_tag(t), "gres")

# ============================ 7. nettoyage, projet, en-tête ======================
for e in f.by_type("IfcRoot"):
    if e.OwnerHistory is None:
        e.OwnerHistory = OH
changed = True
while changed:
    changed = False
    for lp in f.by_type("IfcLocalPlacement"):
        if not lp.PlacesObject and not lp.ReferencedByPlacements:
            f.remove(lp); changed = True
for rel in list(f.by_type("IfcRelAssociatesMaterial")):
    if not rel.RelatedObjects:
        f.remove(rel)
for st in list(f.by_type("IfcSurfaceStyle")):          # anciens styles KDA devenus inutilisés
    if "KDA" in (st.Name or "") and not f.get_inverse(st):
        for sub in st.Styles:
            col = getattr(sub, "SurfaceColour", None)
            f.remove(sub)
            if col is not None and not f.get_inverse(col):
                f.remove(col)
        f.remove(st)
proj = f.by_type("IfcProject")[0]
proj.Name = "Bibliothèque Decimo - étude intérieure V4"
proj.Description = "Esquisse V4 K&Démi : arbre à livres, niches cintrées, façade à claustra, palette matériaux"
f.header.file_name.name = DST.split("/")[-1]
f.header.file_name.time_stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
f.write(DST)
print("ok", DST)
