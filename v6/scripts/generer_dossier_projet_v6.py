"""Génère un dossier de conception V6 à partir de la géométrie IFC V6.

Les planches sont des vues directement calculées depuis l’IFC courant. Les pièces V5
ne sont pas reprises ici. Toute cote affichée est une valeur de maquette, non un relevé.
"""
from pathlib import Path
import math
import argparse
import os

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element as element_util
import ifcopenshell.util.unit as unit_util
os.environ.setdefault("MPLCONFIGDIR", "/tmp/decimo-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/decimo-cache")
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon as MplPolygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from PIL import Image
from shapely.geometry import MultiPoint


ROOT = Path(__file__).resolve().parents[2]
V5_IFC = ROOT / "v5" / "DECIMO_ESQ_V5.ifc"
V6_IFC = ROOT / "v6" / "DECIMO_ESQ_V6_OPTION_C.ifc"
OUT = ROOT / "v6" / "DOSSIER_PROJET_OPTION_C_V6.pdf"
PREVIEW = ROOT / "v6" / "apercus_projet_v6"
PHOTOS = ROOT / "photos"

INK = "#202421"
ORANGE = "#E36A3D"
MID = "#7C817A"
LIGHT = "#D9DCD8"
PALE = "#F5F4F0"
BLUE = "#C9DFE2"
BROWN = "#9A7050"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MID,
    "ytick.color": MID,
    "figure.facecolor": PALE,
    "axes.facecolor": WHITE,
    "pdf.fonttype": 42,
})


def load_geometry(ifc_path=V6_IFC):
    if not ifc_path.exists():
        raise FileNotFoundError(f"L’IFC V6 est attendu ici : {ifc_path}")
    model = ifcopenshell.open(str(ifc_path))
    old = ifcopenshell.open(str(V5_IFC))
    old_ids = {p.GlobalId for p in old.by_type("IfcProduct")}
    scale = unit_util.calculate_unit_scale(model)
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    data = []
    failures = []
    for prod in model.by_type("IfcProduct"):
        if prod.Representation is None or prod.is_a("IfcOpeningElement"):
            continue
        try:
            body = next((r for r in prod.Representation.Representations if r.RepresentationIdentifier == "Body"), None)
            if body is None:
                continue
            shape = ifcopenshell.geom.create_shape(settings, prod, body)
            geo = shape.geometry
            # IfcOpenShell returns geometry in SI coordinates even when the file is in cm.
            verts = np.asarray(geo.verts, dtype=float).reshape((-1, 3))
            faces = np.asarray(geo.faces, dtype=np.int64).reshape((-1, 3))
            if len(verts) and len(faces):
                data.append({
                    "id": prod.GlobalId,
                    "name": prod.Name or prod.is_a(),
                    "class": prod.is_a(),
                    "old": prod.GlobalId in old_ids,
                    "space": prod.is_a("IfcSpace"),
                    "verts": verts,
                    "faces": faces,
                    "zmin": float(verts[:, 2].min()),
                    "zmax": float(verts[:, 2].max()),
                    "psets": element_util.get_psets(prod),
                })
        except Exception as exc:
            failures.append((prod.Name or prod.GlobalId, str(exc)))
    if not data:
        raise RuntimeError("Aucune géométrie exploitable trouvée dans l’IFC V6.")
    return model, data, failures, scale


def classify(obj):
    name = obj["name"].lower()
    if not obj["old"] and (obj["class"] == "IfcSlab" and "plateforme" in name or "hypoth" in str(obj["psets"]).lower() or "optionnelle" in name):
        return "hypothesis"
    if not obj["old"]:
        return "project"
    if obj["class"].startswith("IfcWall") or obj["class"] in ("IfcColumn", "IfcSlab", "IfcBeam"):
        return "existing"
    if obj["class"] in ("IfcLightFixture", "IfcPipeSegment", "IfcCableCarrierSegment", "IfcPump"):
        return "inherited_tech"
    return "existing"


def in_project_view(obj):
    """Écarte le contexte IFC des logements voisins, hors du lot présenté."""
    if obj["class"] == "IfcBuildingElementProxy":
        return False
    v = obj["verts"]
    lo, hi = v.min(axis=0), v.max(axis=0)
    return bool(hi[0] >= -.35 and lo[0] <= 7.0 and hi[1] >= -4.1 and lo[1] <= 7.9 and lo[2] <= 4.25)


def styler(obj):
    role = classify(obj)
    if role == "project":
        return ORANGE, 1.15, "-"
    if role == "hypothesis":
        return ORANGE, 1.0, "--"
    if role == "inherited_tech":
        return MID, 0.75, ":"
    return INK, 0.95, "-"


def base(fig, code, title, subtitle, source="IFC V6 · géométrie de la maquette"):
    fig.patch.set_facecolor(PALE)
    fig.text(.045, .962, "BIBLIOTHÈQUE DECIMO", fontsize=13, weight="bold", color=INK)
    fig.text(.045, .928, f"{code} · {title}", fontsize=17, weight="bold", color=ORANGE)
    fig.text(.045, .904, subtitle, fontsize=8.2, color=MID)
    fig.add_artist(plt.Line2D([.045, .955], [.889, .889], transform=fig.transFigure, color="#D5D6D2", lw=.8))
    fig.add_artist(plt.Line2D([.045, .955], [.047, .047], transform=fig.transFigure, color="#D5D6D2", lw=.8))
    fig.text(.045, .027, f"ESQUISSE DE CONCEPTION · {source} · COTES DE MAQUETTE À VÉRIFIER SUR SITE", fontsize=6.5, color=MID)
    fig.text(.955, .027, code, fontsize=7, color=ORANGE, ha="right", weight="bold")


def tri_segments(obj, axis, value, u, v, only=None):
    verts, faces = obj["verts"], obj["faces"]
    if only is not None and not only(obj):
        return []
    out = []
    for face in faces:
        t = verts[face]
        dist = t[:, axis] - value
        if dist.min() > 1e-7 or dist.max() < -1e-7:
            continue
        pts = []
        for j in range(3):
            a, b = t[j], t[(j + 1) % 3]
            da, db = dist[j], dist[(j + 1) % 3]
            if abs(da) <= 1e-7:
                pts.append(a)
            if da * db < -1e-14:
                pts.append(a + (b - a) * (da / (da - db)))
        uniq = []
        for p in pts:
            if not any(np.linalg.norm(p - q) < 1e-6 for q in uniq):
                uniq.append(p)
        if len(uniq) >= 2:
            p, q = uniq[:2]
            out.append([(p[u], p[v]), (q[u], q[v])])
    return out


def projection_hull(obj, u, v, z_limit=None):
    points = obj["verts"]
    if z_limit is not None:
        points = points[points[:, 2] <= z_limit + .08]
    if len(points) < 3:
        return None
    p2 = points[:, [u, v]]
    hull = MultiPoint(p2).convex_hull
    return hull if hull.geom_type == "Polygon" else None


def section_plot(ax, objects, axis, value, u, v, title, filter_fn=None, projection=False, cut_z=None):
    ax.set_title(title, loc="left", fontsize=8.5, weight="bold", color=INK, pad=8)
    for obj in objects:
        if obj["space"] or not in_project_view(obj):
            continue
        if filter_fn and not filter_fn(obj):
            continue
        color, width, style = styler(obj)
        seg = tri_segments(obj, axis, value, u, v)
        if seg:
            ax.add_collection(LineCollection(seg, colors=color, linewidths=width, linestyles=style, zorder=3 if color == ORANGE else 2))
        elif projection:
            hull = projection_hull(obj, u, v, cut_z)
            if hull is not None:
                x, y = hull.exterior.xy
                ax.plot(x, y, color=color, lw=width, ls=style, zorder=2)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)
    ax.set_xlabel({0: "x · m", 1: "y · m", 2: "z · m"}[u], fontsize=7)
    ax.set_ylabel({0: "x · m", 1: "y · m", 2: "z · m"}[v], fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)


def add_legend(fig):
    fig.text(.71, .865, "EXISTANT IFC V5", color=INK, fontsize=7, weight="bold")
    fig.text(.81, .865, "PROJET V6", color=ORANGE, fontsize=7, weight="bold")
    fig.text(.89, .865, "HYPOTHÈSE", color=ORANGE, fontsize=7, weight="bold", style="italic")


def draw_plan(fig, ax, objects, cut_z=1.0):
    objects = [o for o in objects if in_project_view(o)]
    section_plot(ax, objects, 2, cut_z, 0, 1, f"Plan du RDC · coupe horizontale à z={cut_z:.2f} m (IFC V6)", projection=True, cut_z=cut_z)
    # Color/projection of modeled furniture helps distinguish table/shelf positions when below cut.
    for obj in objects:
        if obj["space"]:
            hull = projection_hull(obj, 0, 1)
            if hull is not None:
                p = hull.centroid
                label = obj["name"].split("—")[-1].strip()
                ax.text(p.x, p.y, label[:25], fontsize=5.5, ha="center", va="center", color=MID, zorder=5,
                        bbox={"facecolor": WHITE, "edgecolor": "none", "alpha": .65, "pad": 1})
            continue
        if obj["old"] or obj["class"] not in ("IfcFurnishingElement", "IfcFurniture"):
            continue
        hull = projection_hull(obj, 0, 1, 2.2)
        if hull is not None:
            x, y = hull.exterior.xy
            ax.fill(x, y, facecolor=ORANGE, edgecolor=ORANGE, alpha=.09, linewidth=.8, zorder=1)
    add_legend(fig)


def draw_lighting(ax, objects):
    # Reflected plan at ceiling level; only geometry at/above 2.45 m is shown.
    ax.set_title("Plafond et éclairage · projection de la géométrie IFC V6", loc="left", fontsize=8.5, weight="bold", color=INK, pad=8)
    value = 2.95
    for obj in objects:
        if not in_project_view(obj):
            continue
        if obj["space"]:
            continue
        if obj["zmax"] < 2.35:
            continue
        color, width, style = styler(obj)
        seg = tri_segments(obj, 2, value, 0, 1)
        if seg:
            ax.add_collection(LineCollection(seg, colors=color, linewidths=width, linestyles=style))
        if obj["class"] == "IfcLightFixture":
            hull = projection_hull(obj, 0, 1, 3.3)
            if hull is not None:
                c = hull.centroid
                ax.scatter([c.x], [c.y], marker="o", s=11, facecolors="none", edgecolors=MID, linewidths=.7, zorder=4)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x · m"); ax.set_ylabel("y · m")
    ax.spines[["top", "right"]].set_visible(False)


def draw_axon(ax, objects, exploded=False):
    ax.set_axis_off()
    groups = []
    for obj in objects:
        if not in_project_view(obj):
            continue
        if obj["space"]:
            continue
        # Montrer le mobilier et les ajouts V6; l’enveloppe reste un repère filaire.
        is_new_site_piece = not obj["old"] and obj["class"] in ("IfcSlab", "IfcCovering", "IfcBuildingElementProxy")
        if obj["class"] not in ("IfcFurnishingElement", "IfcFurniture") and not is_new_site_piece:
            continue
        role = classify(obj)
        if exploded:
            if role in ("existing", "inherited_tech"):
                zoff = 0
            elif role == "project":
                zoff = 1.3
            else:
                zoff = 2.6
        else:
            zoff = 0
        if role in ("project", "hypothesis"):
            color = ORANGE
            alpha = .62 if role == "project" else .42
        elif role == "inherited_tech":
            color, alpha = "#AEB4AE", .24
        elif obj["class"] in ("IfcWall", "IfcSlab", "IfcBeam", "IfcColumn", "IfcCovering"):
            color, alpha = "#AEB4AE", .16
        else:
            color, alpha = "#69716B", .65
        verts, faces = obj["verts"], obj["faces"]
        # Keep the project/model view light enough to render and inspect in A3.
        if len(faces) > 4500:
            faces = faces[::max(1, len(faces) // 3000)]
        polys = []
        for face in faces:
            tri = verts[face].copy()
            tri[:, 2] += zoff
            polys.append(tri)
        if polys:
            groups.append((polys, color, role, alpha))
    for polys, color, role, alpha in groups:
        edge = "none" if alpha < .3 else color
        ax.add_collection3d(Poly3DCollection(polys, facecolors=color, edgecolors=edge, linewidths=.018, alpha=alpha))
    x0, x1, y0, y1, z0, z1 = -.09, 6.69, -.09, 7.59, 0.0, 3.3
    edges = [
        ((x0,y0,z0),(x1,y0,z0)),((x1,y0,z0),(x1,y1,z0)),((x1,y1,z0),(x0,y1,z0)),((x0,y1,z0),(x0,y0,z0)),
        ((x0,y0,z1),(x1,y0,z1)),((x1,y0,z1),(x1,y1,z1)),((x1,y1,z1),(x0,y1,z1)),((x0,y1,z1),(x0,y0,z1)),
        ((x0,y0,z0),(x0,y0,z1)),((x1,y0,z0),(x1,y0,z1)),((x1,y1,z0),(x1,y1,z1)),((x0,y1,z0),(x0,y1,z1)),
    ]
    for a,b in edges:
        ax.plot([a[0],b[0]],[a[1],b[1]],[a[2],b[2]],color="#9EA49F",lw=.65,alpha=.8)
    ax.view_init(elev=28, azim=-55)
    ax.set_box_aspect((1, 1, .55))
    ax.set_xlim(-.4, 7.0); ax.set_ylim(-4.1, 7.9); ax.set_zlim(-.2, 5.4 if exploded else 3.8)
    ax.set_xlabel("x · m"); ax.set_ylabel("y · m"); ax.set_zlabel("z · m")
    if exploded:
        ax.set_title("Axonométrie éclatée · couches séparées à titre explicatif", loc="left", fontsize=8.5, weight="bold")
    else:
        ax.set_title("Axonométrie IFC V6 · existant conservé + aménagement modélisé", loc="left", fontsize=8.5, weight="bold")


def draw_component(ax, obj):
    """Vue rapprochée du maillage réel d’un objet IFC."""
    verts, faces = obj["verts"], obj["faces"]
    if len(faces) > 5000:
        faces = faces[::max(1, len(faces)//3500)]
    polys = [verts[f] for f in faces]
    role = classify(obj)
    face = "#F4D9CE" if role in ("project", "hypothesis") else "#E4E6E2"
    edge = ORANGE if role in ("project", "hypothesis") else INK
    ax.add_collection3d(Poly3DCollection(polys, facecolors=face, edgecolors=edge, linewidths=.28, alpha=.9))
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    mid, span = (lo+hi)/2, np.maximum(hi-lo, .02)
    ax.set_xlim(mid[0]-span[0]*.62,mid[0]+span[0]*.62)
    ax.set_ylim(mid[1]-span[1]*.62,mid[1]+span[1]*.62)
    ax.set_zlim(max(0,lo[2]-span[2]*.15),hi[2]+span[2]*.45)
    ax.set_box_aspect(span)
    ax.view_init(elev=25,azim=-55)
    ax.set_axis_off()


def add_photo(fig, photo, rect, title):
    ax = fig.add_axes(rect)
    if photo.exists():
        im = Image.open(photo).convert("RGB")
        ax.imshow(im)
    ax.set_axis_off()
    ax.set_title(title, loc="left", fontsize=8, color=INK, pad=4)


def simple_page(fig, code, title, subtitle, text, photos=()):
    base(fig, code, title, subtitle)
    add_legend(fig)
    fig.text(.08, .72, text, fontsize=10, color=INK, va="top", linespacing=1.7)
    for rect, photo, label in photos:
        add_photo(fig, photo, rect, label)


def create_pages(model, objects, failures, scale):
    view_objects = [o for o in objects if in_project_view(o)]
    dimensions = [o["verts"] for o in view_objects if o["class"].startswith("IfcWall")]
    xyz = np.concatenate(dimensions) if dimensions else np.concatenate([o["verts"] for o in view_objects])
    xmin, ymin, zmin = xyz.min(0)
    xmax, ymax, zmax = xyz.max(0)
    v6_new = [o for o in objects if not o["old"]]
    hypotheses = [o for o in v6_new if classify(o) == "hypothesis"]
    light_count = sum(o["class"] == "IfcLightFixture" for o in objects)
    figlist = []

    # 01 — opening statement and photo evidence.
    fig = plt.figure(figsize=(16.54, 11.69))
    base(fig, "00", "Une bibliothèque pour lire, se rencontrer et travailler", "Option C · projet de conception V6 généré depuis la maquette IFC V6")
    fig.text(.06, .73, "Accueil-café · salle vitrée · rayonnages · coworking · terrasse", fontsize=18, weight="bold", color=INK)
    fig.text(.06, .66, "Repère graphique : noir = existant hérité de la V5; orange = projet V6; orange interrompu = hypothèse identifiée dans l’IFC.", fontsize=9, color=MID)
    photo_paths = [
        PHOTOS / "interieur" / "WhatsApp Image 2026-10-13 at 6.12.46 PM (4).jpeg",
        PHOTOS / "interieur" / "WhatsApp Image 2026-10-13 at 6.12.46 PM (22).jpeg",
        PHOTOS / "LE SITE" / "WhatsApp Image 2026-10-13 at 5.50.23 PM (5).jpeg",
    ]
    for rect, path, label in zip(((.07,.22,.26,.37),(.37,.22,.26,.37),(.67,.22,.26,.37)), photo_paths,
                                 ("Entrée et seuil · observé en photo", "Pièce bleue et fond · observé en photo", "Avant-cour · limites à vérifier")):
        add_photo(fig, path, rect, label)
    fig.text(.07, .14, f"IFC : {len(objects)} géométries calculées · {len(v6_new)} produits V6 ajoutés · {light_count} luminaires hérités dans le modèle.", fontsize=8.5, color=INK)
    fig.text(.07, .105, "Les photos orientent le programme; elles ne donnent pas de cotes et ne valident pas la structure du volume haut.", fontsize=8.5, color=ORANGE)
    figlist.append(fig)

    # 02 — floor plan from actual IFC meshes.
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    base(fig, "A01", "Plan RDC · Option C V6", "Plan géométrique issu de l’IFC V6; zones et mobilier correspondent aux objets présents dans le fichier.")
    ax.set_position([.08,.12,.62,.73]); draw_plan(fig, ax, view_objects)
    fig.text(.74,.75,"PROGRAMME",fontsize=10,weight="bold",color=ORANGE)
    texts = [
        ("Accueil-café", "Comptoir droit et poste unique; raccordements café à confirmer."),
        ("Réunion", "Table six places modélisée; vérifier l’implantation réelle de la pièce bleue."),
        ("Bibliothèque", "Rayonnages droits et modules répétitifs; dégagements à contrôler."),
        ("Réserve haute", "Objet IFC hypothétique; usage suspendu à la vérification structurelle."),
        ("Terrasse", "Extension extérieure codée comme option; emprise foncière et niveaux à confirmer."),
    ]
    y=.70
    for h,t in texts:
        fig.text(.74,y,h,fontsize=8.5,weight="bold",color=INK); y-=.025
        fig.text(.74,y,t,fontsize=7.2,color=MID,wrap=True); y-=.068
    figlist.append(fig)

    # 03 — ceiling/light plan based on real model geometry.
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    base(fig, "A02", "Plafond, lumière et réseaux hauts", "Projection calculée depuis l’IFC V6; équipements techniques conservés en gris pointillé = héritage V5.")
    ax.set_position([.07,.13,.68,.70]); draw_lighting(ax, view_objects)
    fig.text(.78,.72,f"Luminaires IfcLightFixture trouvés : {light_count}.",fontsize=9,weight="bold",color=INK)
    fig.text(.78,.66,"Le modèle V6 conserve les luminaires et réseaux de la V5. Leur adéquation au comptoir-café et à la nouvelle salle de réunion reste à vérifier; aucun nouveau circuit V6 n’est supposé.",fontsize=8,color=MID,wrap=True)
    fig.text(.78,.52,"Contrôles avant APS",fontsize=9,weight="bold",color=ORANGE)
    fig.text(.78,.48,"Relever le faux-plafond, les retombées, les suspentes, les arrivées électriques et la ventilation. Recalculer les circuits et l’éclairage après validation du programme café.",fontsize=8,color=INK,wrap=True)
    figlist.append(fig)

    # 04 — primary section through room center.
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    base(fig, "A03", "Coupe A–A · salle et bibliothèque", "Coupe vraie du maillage IFC V6, regard vers le sud; niveau de coupe choisi depuis les objets de projet.")
    cut_x = 2.0
    ax.set_position([.08,.15,.82,.69]); section_plot(ax, view_objects, 0, cut_x, 1, 2, f"Plan vertical x = {cut_x:.2f} m (valeur IFC, à contrôler sur site)", filter_fn=lambda o: "extension terrasse" not in o["name"].lower())
    add_legend(fig)
    figlist.append(fig)

    # 05 — the rear blue-room / upper reserve section.
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    base(fig, "A04", "Coupe B–B · fond de la pièce bleue et réserve", "La réserve haute est montrée car elle figure dans l’IFC; sa structure, son accès et son usage ne sont pas validés.")
    reserve = [o for o in hypotheses if "plateforme" in o["name"].lower()]
    cut_y = 4.35 if reserve else ymax-.55
    ax.set_position([.07,.15,.65,.69]); section_plot(ax, view_objects, 1, cut_y, 0, 2, f"Plan vertical y = {cut_y:.2f} m · niveau de maquette à confirmer", filter_fn=lambda o: "extension terrasse" not in o["name"].lower())
    fig.text(.76,.76,"VOLUME HAUT",fontsize=10,weight="bold",color=ORANGE)
    fig.text(.76,.71,"La géométrie orange en tirets désigne une hypothèse de réserve. Les photos ne montrent ni appuis, ni accès, ni garde-corps de façon suffisante.",fontsize=8,color=INK,wrap=True)
    fig.text(.76,.54,"À obtenir",fontsize=9,weight="bold",color=ORANGE)
    fig.text(.76,.49,"Relevé complet des niveaux et appuis; avis du BET structure avant tout stockage ou accès.",fontsize=8,color=INK,wrap=True)
    add_legend(fig)
    figlist.append(fig)

    # 06 — street entrance elevation from actual IFC meshes.
    fig, ax = plt.subplots(figsize=(16.54, 11.69))
    base(fig, "A05", "Élévation entrée et façade", "État de façade hérité de la maquette V5; aucun changement de baie n’est proposé dans l’IFC V6.")
    ax.set_position([.08,.14,.82,.70]); section_plot(ax, view_objects, 1, float(ymin+.05), 0, 2, "Façade sud · projection du modèle", filter_fn=lambda o: "extension terrasse" not in o["name"].lower())
    add_legend(fig)
    figlist.append(fig)

    # 07 — interior elevations generated from current model.
    fig = plt.figure(figsize=(16.54, 11.69)); base(fig,"A06","Élévations intérieures","Élévations projetées depuis le modèle V6; traits orange = nouveaux objets IFC.")
    ax1=fig.add_axes([.07,.50,.40,.33]); section_plot(ax1,view_objects,1,6.83,0,2,"Mur nord · vue au droit des rayonnages",filter_fn=lambda o: "extension terrasse" not in o["name"].lower())
    ax2=fig.add_axes([.53,.50,.40,.33]); section_plot(ax2,view_objects,0,6.30,1,2,"Mur est · vue au droit du rayonnage",filter_fn=lambda o: "extension terrasse" not in o["name"].lower())
    fig.text(.08,.39,"Ouvertures et niveaux visibles hérités de la V5; vérifier les dimensions sur site.",fontsize=8,color=MID)
    figlist.append(fig)

    # 08 — axonometric model view and separated layers.
    fig=plt.figure(figsize=(16.54,11.69)); base(fig,"A07","Axonométrie du projet","Axonométrie calculée depuis la géométrie V6; formes et positions lisibles dans le fichier source.")
    ax=fig.add_axes([.05,.12,.58,.72],projection="3d"); draw_axon(ax,view_objects,False)
    ax2=fig.add_axes([.63,.17,.32,.62],projection="3d"); draw_axon(ax2,view_objects,True)
    fig.text(.68,.79,"AXONOMÉTRIE ÉCLATÉE",fontsize=8,weight="bold",color=ORANGE)
    fig.text(.68,.13,"Les couches sont écartées verticalement pour lecture seulement; ce n’est pas une position construite.",fontsize=7,color=MID,wrap=True)
    figlist.append(fig)

    # 09 — targeted details, cut directly through IFC at their actual locations.
    fig=plt.figure(figsize=(16.54,11.69)); base(fig,"A08","Détails · mobilier et menuiseries","Vues axonométriques des objets réellement modélisés; assemblages et fixations restent à concevoir.")
    detail_specs = [
        (next((o for o in v6_new if "comptoir accueil" in o["name"].lower()), None), "D01 · Comptoir accueil-café"),
        (next((o for o in v6_new if "table de réunion" in o["name"].lower()), None), "D02 · Table de réunion"),
        (next((o for o in v6_new if "rayonnage droit nord" in o["name"].lower()), None), "D03 · Rayonnage nord-est"),
        (next((o for o in v6_new if "retour opaque wc" in o["name"].lower()), None), "D04 · Retour WC · option à valider"),
    ]
    cells=[(.07,.52,.39,.30),(.54,.52,.39,.30),(.07,.13,.39,.30),(.54,.13,.39,.30)]
    for idx,((obj,label),rect) in enumerate(zip(detail_specs,cells),1):
        if obj is None:
            continue
        ax=fig.add_axes(rect,projection="3d")
        ax.set_title(label,loc="left",fontsize=8.5,weight="bold",color=INK,pad=8)
        draw_component(ax,obj)
        fig.text(rect[0],rect[1]-.018,"Forme générale IFC · sans détail de fabrication",fontsize=6.8,color=MID)
    figlist.append(fig)

    # 10 — materials and technical assumptions registered in IFC.
    fig=plt.figure(figsize=(16.54,11.69)); base(fig,"T00","Matières et notes techniques","Synthèse liée aux objets IFC V6; l’état de site et les raccordements restent à relever.")
    swatches=[("Bois iroko huilé",BROWN),("Enduit clair", "#EDE9DF"),("Terre cuite",ORANGE),("Acier noir",INK),("Vitrage",BLUE)]
    for i,(label,col) in enumerate(swatches):
        x=.08+i*.17
        ax=fig.add_axes([x,.66,.11,.10]); ax.set_facecolor(col); ax.set_xticks([]);ax.set_yticks([])
        for sp in ax.spines.values():sp.set_edgecolor(INK)
        fig.text(x,.62,label,fontsize=7.3,color=INK)
    fig.text(.08,.51,"NOTES DE CONCEPTION",fontsize=10,weight="bold",color=ORANGE)
    notes=[
        f"Maquette IFC : unités SI calculées depuis le fichier; emprise analysée x={xmin:.2f} à {xmax:.2f} m, y={ymin:.2f} à {ymax:.2f} m. Valeurs à confirmer au relevé.",
        f"Éléments V6 ajoutés au modèle : {len(v6_new)} produits géométriques; réserves/extension identifiées comme hypothèses : {len(hypotheses)}.",
        "Raccordements café, électricité, ventilation, évacuations et charges des rayonnages non validés par cette esquisse.",
        "La plateforme haute et l’extension de terrasse ne constituent pas une approbation structurelle ou foncière.",
    ]
    for i,t in enumerate(notes): fig.text(.09,.46-i*.055,"•  "+t,fontsize=8.5,color=INK,wrap=True)
    if failures:
        fig.text(.08,.17,f"Géométries non calculées par IfcOpenShell : {len(failures)} (voir journal de génération).",fontsize=7.5,color=ORANGE)
    else:
        fig.text(.08,.17,"Toutes les géométries représentées dans ce dossier ont été calculées par IfcOpenShell.",fontsize=7.5,color=MID)
    figlist.append(fig)

    return figlist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ifc", type=Path, default=V6_IFC, help="IFC V6 à lire (par défaut: v6/DECIMO_ESQ_V6_OPTION_C.ifc)")
    parser.add_argument("--check-only", action="store_true", help="Calcule le maillage et les comptes sans générer le PDF")
    args = parser.parse_args()
    model, objects, failures, scale = load_geometry(args.ifc)
    if args.check_only:
        print(f"IFC: {args.ifc}; produits géométriques: {len(objects)}; nouveaux V6: {sum(not o['old'] for o in objects)}; échecs: {len(failures)}")
        return
    figs = create_pages(model, objects, failures, scale)
    PREVIEW.mkdir(exist_ok=True)
    with PdfPages(OUT) as pdf:
        for i, fig in enumerate(figs, 1):
            pdf.savefig(fig, bbox_inches=None)
            fig.savefig(PREVIEW / f"page_{i:02d}.png", dpi=90, facecolor=fig.get_facecolor())
            plt.close(fig)
    print(f"PDF: {OUT}")
    print(f"Planches générées: {len(figs)}; géométries: {len(objects)}; V6: {sum(not o['old'] for o in objects)}; échecs: {len(failures)}")
    for name, error in failures:
        print(f"ÉCHEC GEO {name}: {error[:180]}")


if __name__ == "__main__":
    main()
