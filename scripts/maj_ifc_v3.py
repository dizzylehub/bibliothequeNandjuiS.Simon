"""Met à jour DECIMO_ESQ_V2.ifc -> DECIMO_ESQ_V3.ifc (remarques du 14/10/2026).

Unités du modèle : centimètres. Les coordonnées ci-dessous sont en mètres (monde) et
converties en cm pour la géométrie ; tous les nouveaux objets sont placés à l'origine
du repère monde (matrice identité), leur géométrie est donc exprimée en coordonnées monde.
"""
import sys, time
import numpy as np
import ifcopenshell, ifcopenshell.api, ifcopenshell.guid
import ifcopenshell.util.placement as up
import ifcopenshell.api.owner.settings as owner_settings

SRC, DST = sys.argv[1], sys.argv[2]
f = ifcopenshell.open(SRC)
owner_settings.get_user = lambda f: f.by_type("IfcPersonAndOrganization")[0]
owner_settings.get_application = lambda f: f.by_type("IfcApplication")[0]
api = ifcopenshell.api.run

CM = 100.0
rdc = next(s for s in f.by_type("IfcBuildingStorey") if "RDC" in s.Name)
body = next(c for c in f.by_type("IfcGeometricRepresentationSubContext") if c.ContextIdentifier == "Body")

def by_tag(tag):
    r = [e for e in f.by_type("IfcProduct") if (e.Name or "").split(":")[-1] == tag]
    assert len(r) == 1, (tag, r)
    return r[0]

# --- primitives géométriques ---------------------------------------------------
P3 = lambda x, y, z: f.createIfcCartesianPoint((float(x), float(y), float(z)))
P2 = lambda x, y: f.createIfcCartesianPoint((float(x), float(y)))
DZ = f.createIfcDirection((0., 0., 1.))

def box(x0, y0, x1, y1, z0, z1):
    """Parallélépipède aligné sur les axes (mètres, repère monde)."""
    x0, x1, y0, y1, z0, z1 = (v * CM for v in (min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1))
    prof = f.createIfcRectangleProfileDef("AREA", None, f.createIfcAxis2Placement2D(P2((x0 + x1) / 2, (y0 + y1) / 2), None),
                                          x1 - x0, y1 - y0)
    return f.createIfcExtrudedAreaSolid(prof, f.createIfcAxis2Placement3D(P3(0, 0, z0), None, None), DZ, z1 - z0)

def cyl(cx, cy, r, z0, z1):
    prof = f.createIfcCircleProfileDef("AREA", None, f.createIfcAxis2Placement2D(P2(cx * CM, cy * CM), None), r * CM)
    return f.createIfcExtrudedAreaSolid(prof, f.createIfcAxis2Placement3D(P3(0, 0, z0 * CM), None, None), DZ, (z1 - z0) * CM)

def surface_style(name, rgb, transparency=0.0):
    col = f.createIfcColourRgb(None, *rgb)
    ren = f.createIfcSurfaceStyleRendering(col, transparency, None, None, None, None, None, None, "NOTDEFINED")
    return f.createIfcSurfaceStyle(name, "BOTH", [ren])
BOIS = surface_style("KDA - Bois clair (lames)", (0.73, 0.63, 0.49))
BLANC = surface_style("KDA - Laqué blanc", (0.93, 0.93, 0.92))
NOIR = surface_style("KDA - Noir mat", (0.10, 0.10, 0.11))
VERT = surface_style("KDA - Vert végétal", (0.42, 0.62, 0.30))
PLACO = surface_style("KDA - Placo peint", (0.90, 0.89, 0.86))
TABLEAU = surface_style("KDA - Tableau blanc", (0.97, 0.97, 0.97))

def styled(items, style):
    for it in items:
        f.createIfcStyledItem(it, [f.createIfcPresentationStyleAssignment([style])], None)
    return items

PSET_ORIGINE = {"Indice": "V3", "Origine": "Remarques du 14/10/2026 sur le plan RDC V2"}

def new_product(ifc_class, name, items, description=None, rep_type="SweptSolid", **attrs):
    p = api("root.create_entity", f, ifc_class=ifc_class, name=name)
    p.Description = description
    for k, v in attrs.items():
        setattr(p, k, v)
    api("spatial.assign_container", f, products=[p], relating_structure=rdc)
    api("geometry.edit_object_placement", f, product=p, matrix=np.eye(4), is_si=True)
    rep = f.createIfcShapeRepresentation(body, "Body", rep_type, items)
    api("geometry.assign_representation", f, product=p, representation=rep)
    pset = api("pset.add_pset", f, product=p, name="KDA_Esquisse")
    api("pset.edit_pset", f, pset=pset, properties=PSET_ORIGINE)
    return p

def tag_modified(p, note):
    pset = api("pset.add_pset", f, product=p, name="KDA_Esquisse")
    api("pset.edit_pset", f, pset=pset, properties={**PSET_ORIGINE, "Modification": note})

def opening(name, host, x0, y0, x1, y1, z0=0.0, z1=2.10):
    o = new_product("IfcOpeningElement", name, [box(x0, y0, x1, y1, z0, z1)])
    api("feature.add_feature", f, feature=o, element=host)
    return o

def move_world(p, dx=0.0, dy=0.0, rot_deg=0.0, about=(0.0, 0.0)):
    """Déplace un produit dans le repère monde (mètres) : rotation autour de `about`, puis translation."""
    m = up.get_local_placement(p.ObjectPlacement).copy()
    m[:3, 3] /= CM
    a = np.radians(rot_deg)
    R = np.eye(4); R[:2, :2] = [[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]
    T1 = np.eye(4); T1[:2, 3] = [-about[0], -about[1]]
    T2 = np.eye(4); T2[:2, 3] = [about[0] + dx, about[1] + dy]
    api("geometry.edit_object_placement", f, product=p, matrix=T2 @ R @ T1 @ m, is_si=True)

# --- 1. suppressions -------------------------------------------------------------
REMOVE = {
    "4350624": "WC 1 (un seul WC conservé)",
    "4350627": "lave-mains WC 1", "4350628": "vasque WC 1",
    "4350611": "porte vitrée salle de réunion", "4350610": "vitrage haut cloison salle de réunion",
    "4350617": "montant de la porte vitrée",
    "4350676": "console vinyles M01 (remplacée, voir nouvelle M01)",
    "4350662": "rayonnage B01 remplacé par une plante",
    **{str(i): "ancienne lame de pergola" for i in range(4350712, 4350732)},
}
for tag in REMOVE:
    api("root.remove_product", f, product=by_tag(tag))

# --- 2. portes déplacées (GUID et style de porte conservés) -----------------------
door_wc, door_reu = by_tag("4350623"), by_tag("4350622")
for d in (door_wc, door_reu):
    for rel in list(d.FillsVoids):
        api("root.remove_product", f, product=rel.RelatingOpeningElement)   # l'ancienne baie se referme

# porte de l'ex-WC 1 -> porte du WC unique, dans la cloison placo entre dégagement et WC
move_world(door_wc, dx=0.07, dy=1.20)
o = opening("Baie porte WC", by_tag("4350620"), 1.90, 6.22, 2.83, 6.38)
api("feature.add_filling", f, opening=o, element=door_wc)
door_wc.Name = door_wc.Name  # nom Revit conservé
tag_modified(door_wc, "Déplacée : porte du WC unique (ouvre vers le dégagement)")

# --- 3. nouvelles cloisons ---------------------------------------------------------
placo_type = next(t for t in f.by_type("IfcWallType") if "Placo" in (t.Name or ""))
placo_set = next(r.RelatingMaterial for r in by_tag("4350620").HasAssociations
                 if r.is_a("IfcRelAssociatesMaterial")).ForLayerSet

def new_wall(name, x0, y0, x1, y1, h=3.30):
    w = new_product("IfcWallStandardCase", name, styled([box(x0, y0, x1, y1, 0, h)], PLACO),
                    description="Cloison placo double BA13 (esquisse V3)")
    api("type.assign_type", f, related_objects=[w], relating_type=placo_type)
    f.createIfcRelAssociatesMaterial(ifcopenshell.guid.new(), w.OwnerHistory, None, None, [w], placo_set)
    return w

w_rgt = new_wall("Cloison rangement / dégagement", 1.76, 5.16, 1.88, 6.24)
w_reu = new_wall("Cloison pleine salle de réunion", 2.955, 2.82, 3.045, 5.04)

# porte de l'ex-WC 2 -> porte de la salle de réunion, en haut de la nouvelle cloison
move_world(door_reu, dx=-0.045, dy=-2.365)
o = opening("Baie porte salle de réunion", w_reu, 2.94, 4.07, 3.06, 5.00)
api("feature.add_filling", f, opening=o, element=door_reu)
tag_modified(door_reu, "Déplacée : porte de la salle de réunion (ex-porte WC 2)")

# baie libre entre salle de lecture et dégagement (mur agglos 4350608)
opening("Baie libre dégagement WC", by_tag("4350608"), 2.89, 5.30, 3.11, 6.14)

# porte coulissante du rangement
o = opening("Baie porte coulissante rangement", w_rgt, 1.74, 5.32, 1.90, 6.08)
d = new_product("IfcDoor", "Porte coulissante rangement", styled([box(1.90, 5.30, 1.93, 6.10, 0, 2.08)], BLANC),
                OverallHeight=208.0, OverallWidth=80.0)
api("feature.add_filling", f, opening=o, element=d)

# --- 4. éléments déplacés ----------------------------------------------------------
for tag in ("4350673", "4350674", "4350675"):         # comptoir d'accueil côté vitrine
    move_world(by_tag(tag), dx=1.76, dy=0.14)
    tag_modified(by_tag(tag), "Déplacé côté vitrine")
SINK_C = (1.575, 6.72)                                  # lave-mains contre l'ancienne porte WC 2
for tag in ("4350630", "4350631"):
    move_world(by_tag(tag), dx=2.72 - SINK_C[0], dy=6.86 - SINK_C[1], rot_deg=90, about=SINK_C)
    tag_modified(by_tag(tag), "Lave-mains reporté contre le mur est du WC")

# --- 5. nouveau mobilier et équipements --------------------------------------------
m01 = []
for i, (y0, y1) in enumerate([(1.86, 2.58), (2.58, 3.30), (3.30, 4.02)]):
    m01 += styled([box(3.09, y0 + 0.005, 3.49, y1 - 0.005, 0.0, 0.90)], BLANC)
    if i:
        m01 += styled([cyl(3.29, (y0 + y1) / 2, 0.15, 0.90, 0.95)], NOIR)
new_product("IfcFurnishingElement", "DECIMO_M01_Console_Vinyles_P40:ESQ - sur mesure", m01,
            description="Console vinyles 40 cm, 2 platines + 1 module rangement, contre la cloison de la salle de réunion")

new_product("IfcFurnishingElement", "DECIMO_TB01_Tableau_Mural:ESQ - sur mesure",
            styled([box(0.09, 2.95, 0.13, 4.75, 0.90, 2.10)], TABLEAU), description="Tableau mural salle de réunion, 180 x 120")
new_product("IfcFurnishingElement", "DECIMO_P01_Pouf:ESQ - sur mesure",
            styled([cyl(2.27, 1.18, 0.22, 0.0, 0.42)], VERT), description="Pouf coin lecture, diam. 45")
new_product("IfcFurnishingElement", "DECIMO_V01_Plante:ESQ",
            styled([cyl(6.18, 2.85, 0.16, 0.0, 0.45)], BLANC) + styled([cyl(6.18, 2.85, 0.32, 0.45, 1.60)], VERT),
            description="Plante en pot (remplace un rayonnage)")

# porte à galandage coin lecture / salle de lecture
new_product("IfcBuildingElementProxy", "Caisson porte à galandage",
            styled([box(3.09, 0.09, 3.23, 0.99, 0.0, 2.30)], PLACO), description="Caisson de doublage pour porte à galandage")
new_product("IfcDoor", "Porte à galandage coin lecture",
            styled([box(3.145, 0.12, 3.175, 0.97, 0.0, 2.08)], BLANC),
            description="Vantail coulissant (position ouverte, dans le caisson) ; fermé, il obture la baie y = 0,90 à 1,80",
            OverallHeight=208.0, OverallWidth=90.0)

# --- 6. claustra et pergola paramétriques (même loi que le plan V3) ------------------
def spacing(x, attractors, smin, smax, reach):
    d = min(abs(x - a) for a in attractors)
    return smin + (smax - smin) * (1 - np.exp(-(d / reach) ** 2))

XC, HW = 4.62, 1.50
offs, o_ = [0.0], 0.0
while True:
    o_ += spacing(XC + o_, [XC], 0.075, 0.16, 1.1)
    if o_ > 1.48:
        break
    offs.append(o_)
fins = []
for x in sorted({round(XC + k * o, 4) for o in offs for k in (-1, 1)}):
    u = np.clip((x - XC) / HW, -0.995, 0.995)
    d = 0.05 + 1.0 * (1 - np.sqrt(1 - u * u))
    if 3.50 <= x <= 5.88:      # au-dessus du bureau : tasseau plaqué + lame suspendue
        fins.append(box(x - 0.017, 7.36, x + 0.017, 7.41, 0.0, 3.30))
        if d > 0.06:
            fins.append(box(x - 0.017, 7.41 - d, x + 0.017, 7.36, 1.40, 3.30))
    else:
        fins.append(box(x - 0.017, 7.41 - d, x + 0.017, 7.41, 0.0, 3.30))
new_product("IfcBuildingElementProxy", "Claustra bois paramétrique - mur du fond", styled(fins, BOIS),
            description="Lames bois 34 mm, profondeur en arc autour du bureau (5 à 105 cm), espacement 7,5 à 16 cm")

xa, x = [], 0.05
while x < 6.56:
    xa.append(x); x += spacing(x, [1.375, 4.80], 0.07, 0.24, 1.3)
ya, y = [], -0.24
while y > -2.45:
    ya.append(y); y -= 0.08 + 0.20 * (abs(y) / 2.5) ** 1.4
perg = [box(-0.05, y, 6.65, y + 0.04, 2.75, 2.81) for y in ya]
for x in xa:
    yend = -2.52 - 0.30 * (0.5 + 0.5 * np.sin(2 * np.pi * (x - 0.6) / 3.3))
    hz = 0.10 + 0.16 * (0.5 + 0.5 * np.cos(2 * np.pi * (x - 1.375) / 3.4))
    perg.append(box(x - 0.017, yend, x + 0.017, -0.17, 2.81, 2.81 + hz))
new_product("IfcBuildingElementProxy", "Pergola bois paramétrique (inspiration Kengo Kuma)", styled(perg, BOIS),
            description=f"2 nappes de lames bois croisées : {len(ya)} lames basses (denses côté façade), "
                        f"{len(xa)} lames hautes (resserrées entrée/vitrine, hauteur et rive ondulées)")

# --- 7. nettoyage : historique obligatoire en IFC2X3, placements orphelins ----------
oh = f.by_type("IfcOwnerHistory")[0]
for e in f.by_type("IfcRoot"):
    if e.OwnerHistory is None:
        e.OwnerHistory = oh
changed = True
while changed:
    changed = False
    for lp in f.by_type("IfcLocalPlacement"):
        if not lp.PlacesObject and not lp.ReferencedByPlacements:
            f.remove(lp); changed = True

# --- 8. projet et en-tête ----------------------------------------------------------
proj = f.by_type("IfcProject")[0]
proj.Name = "Bibliothèque Decimo - étude intérieure V3"
proj.Description = "Esquisse V3 : remarques du 14/10/2026 sur le plan RDC intégrées"
f.header.file_name.name = DST.split("/")[-1]
f.header.file_name.time_stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
f.write(DST)
print("ok", DST, len(fins), "lames claustra,", len(ya) + len(xa), "lames pergola")
