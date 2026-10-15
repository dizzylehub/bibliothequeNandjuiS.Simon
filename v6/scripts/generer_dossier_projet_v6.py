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
from matplotlib.patches import Polygon as MplPolygon, Arc
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
    if obj["class"] == "IfcBuildingElementProxy" and obj["old"]:
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


def draw_plan(fig, ax, objects, cut_z=1.0, legend=True, space_labels=True):
    objects = [o for o in objects if in_project_view(o)]
    section_plot(ax, objects, 2, cut_z, 0, 1, f"Plan du RDC · coupe horizontale à z={cut_z:.2f} m (IFC V6)", projection=True, cut_z=cut_z)
    # Color/projection of modeled furniture helps distinguish table/shelf positions when below cut.
    for obj in objects:
        if obj["space"]:
            hull = projection_hull(obj, 0, 1)
            if hull is not None:
                p = hull.centroid
                label = obj["name"].split("—")[-1].strip()
                # Exclure les espaces hors emprise intérieure (terrasse / extérieurs) du cartouche plan.
                if space_labels and 0 <= p.x <= 7 and 0 <= p.y <= 7.5:
                    ax.text(p.x, p.y, label[:25], fontsize=5.5, ha="center", va="center", color=MID, zorder=5,
                            bbox={"facecolor": WHITE, "edgecolor": "none", "alpha": .65, "pad": 1})
            continue
        if obj["old"] or obj["class"] not in ("IfcFurnishingElement", "IfcFurniture"):
            continue
        hull = projection_hull(obj, 0, 1, 2.2)
        if hull is not None:
            x, y = hull.exterior.xy
            ax.fill(x, y, facecolor=ORANGE, edgecolor=ORANGE, alpha=.09, linewidth=.8, zorder=1)
    if legend:
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


# Gabarit architectural développé : feuille blanche, dessin principal à gauche,
# panneau de lecture à droite. Les dimensions sont toujours explicitement liées à l’IFC.
def arch_frame(fig, code, title, subtitle):
    fig.patch.set_facecolor(WHITE)
    fig.text(.035,.955,"K&DÉMI   /   BIBLIOTHÈQUE DECIMO",fontsize=12,weight="bold",color=INK)
    fig.text(.035,.923,f"{code}   {title}",fontsize=15,weight="bold",color=ORANGE)
    fig.text(.035,.899,subtitle,fontsize=7.2,color=MID)
    fig.add_artist(plt.Line2D([.035,.965],[.88,.88],transform=fig.transFigure,color=INK,lw=.6))
    fig.add_artist(plt.Line2D([.705,.705],[.06,.88],transform=fig.transFigure,color=INK,lw=.65))
    fig.add_artist(plt.Line2D([.035,.965],[.052,.052],transform=fig.transFigure,color=INK,lw=.45))
    fig.text(.035,.029,"ESQUISSE V6 · IFC V6 / IFC V5 · LES VALEURS DE MAQUETTE NE SONT PAS UN RELEVÉ DE SITE",fontsize=6.2,color=MID)
    fig.text(.965,.029,code,fontsize=7,ha="right",color=ORANGE,weight="bold")
    fig.text(.725,.845,"BIBLIOTHÈQUE DECIMO",fontsize=8.2,weight="bold",color=INK)
    fig.text(.725,.824,"Option C · Abidjan",fontsize=7,color=MID)


def panel_title(fig,y,title):
    fig.text(.725,y,title.upper(),fontsize=7.1,weight="bold",color=ORANGE)


def panel_text(fig,y,text,size=7.1,color=INK):
    fig.text(.725,y,text,fontsize=size,color=color,va="top",linespacing=1.36,wrap=True)


def north_arrow(ax,x,y):
    ax.annotate("N",(x,y),xytext=(x,y-.55),ha="center",va="top",fontsize=8,weight="bold",color=INK,arrowprops={"arrowstyle":"-|>","lw":.8,"color":INK})


def dimension(ax,p1,p2,label,offset=(0,0),color=MID,fs=6.5):
    x1,y1=p1; x2,y2=p2; ox,oy=offset
    a=(x1+ox,y1+oy); b=(x2+ox,y2+oy)
    ax.annotate("",b,a,arrowprops={"arrowstyle":"<->","lw":.65,"color":color,"shrinkA":0,"shrinkB":0})
    ax.plot([x1,a[0]],[y1,a[1]],color=color,lw=.45); ax.plot([x2,b[0]],[y2,b[1]],color=color,lw=.45)
    ax.text((a[0]+b[0])/2,(a[1]+b[1])/2,label,fontsize=fs,color=color,ha="center",va="bottom",bbox={"facecolor":WHITE,"edgecolor":"none","pad":.7})


def add_scale_person(ax,x,y,height=1.7,color=MID):
    """Gabarit conventionnel affiché comme repère graphique, jamais comme relevé."""
    r=height*.047
    ax.add_patch(plt.Circle((x,y+height-r),r,fill=False,ec=color,lw=.65,zorder=8))
    ax.plot([x,x],[y+height-2*r,y+height*.42],color=color,lw=.8,zorder=8)
    ax.plot([x-height*.16,x+height*.16],[y+height*.70,y+height*.70],color=color,lw=.8,zorder=8)
    ax.plot([x,x-height*.13],[y+height*.42,y],color=color,lw=.8,zorder=8)
    ax.plot([x,x+height*.13],[y+height*.42,y],color=color,lw=.8,zorder=8)


def hatching(rect, ax, hatch="////"):
    ax.add_patch(plt.Rectangle((rect[0],rect[1]),rect[2],rect[3],facecolor="#F5F3EE",edgecolor="#A9ADA8",lw=.45,hatch=hatch,zorder=0))


def make_arch_pages(model,objects,failures,scale):
    local=[o for o in objects if in_project_view(o)]
    new=[o for o in objects if not o["old"] and in_project_view(o)]
    hypotheses=[o for o in new if classify(o)=="hypothesis"]
    walls=[o for o in local if o["class"].startswith("IfcWall")]
    wallverts=np.concatenate([o["verts"] for o in walls]) if walls else np.concatenate([o["verts"] for o in local])
    xmin,ymin,zmin=wallverts.min(0); xmax,ymax,zmax=wallverts.max(0)
    pages=[]
    fmt=(16.54,11.69)

    # 00 — éditorial, état des lieux et quatre temps de conception.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"00","Lire le lieu avant de dessiner","Repères photographiques et démarche de conception · les photos restent des documents de l’existant.")
    photos=[
      ("photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (4).jpeg","01 · SEUIL / grille et accès visibles"),
      ("photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (22).jpeg","02 · PIÈCE BLEUE / identité à confirmer sur plan"),
      ("photos/LE SITE/WhatsApp Image 2026-10-13 at 5.50.23 PM (5).jpeg","03 · ABORD / arbre et chemin vus en photo"),
    ]
    for i,(fpath,label) in enumerate(photos):
        x=.04+i*.215; ax=fig.add_axes([x,.43,.205,.34]); im=Image.open(ROOT/fpath).convert("RGB"); ax.imshow(im); ax.set_axis_off()
        ax.text(.02,.96,label,transform=ax.transAxes,fontsize=6.2,color=INK,va="top",bbox={"facecolor":WHITE,"edgecolor":"none","alpha":.88,"pad":2})
        ax.text(.02,.04,"PHOTO D’ÉTAT DES LIEUX · NON COTÉE",transform=ax.transAxes,fontsize=5.3,color=INK,bbox={"facecolor":WHITE,"edgecolor":"none","alpha":.86,"pad":1.5})
    # quatre étapes, dessinées comme une séquence plutôt qu’une liste de principes.
    stages=[("01","OBSERVER","Photos, seuil, pièce bleue, ombre de l’arbre."),("02","CONSERVER","Grilles, enveloppe et réseaux existants à relever."),("03","IMPLANTER","Accueil, salle, rayonnages et parcours de lecture."),("04","VÉRIFIER","Cotes, structure, lumière et limites de terrasse.")]
    for i,(n,t,d) in enumerate(stages):
        x=.05+i*.16
        fig.text(x,.32,n,fontsize=15,weight="bold",color=ORANGE)
        fig.text(x,.28,t,fontsize=7.2,weight="bold",color=INK)
        fig.text(x,.245,d,fontsize=6.5,color=MID,wrap=True)
        if i<3: fig.text(x+.13,.293,"→",fontsize=14,color=ORANGE)
    fig.text(.05,.13,"INTENTION",fontsize=7.2,weight="bold",color=ORANGE)
    fig.text(.05,.095,"Un lieu clair et traversant :\ncomptoir visible dès l’entrée · pièce bleue\ntransformée en salle vitrée · rayonnages\nlinéaires · usages calmes dans la grande salle.\nJardin et limites extérieures à documenter.",fontsize=7.2,color=INK,linespacing=1.35)
    panel_title(fig,.77,"Statut des documents"); panel_text(fig,.742,"NOIR / GRIS\nEnveloppe et mobilier conservés de la maquette V5.\n\nORANGE\nAjouts de mobilier et éléments projetés V6.\n\nORANGE TIRETÉ\nHypothèse ou emprise optionnelle portée par l’IFC.\n\nPHOTOGRAPHIE\nObservation visuelle; aucune cote ni limite foncière n’en est déduite.",6.7)
    pages.append(fig)

    # A00 — analyse du site et parcours, schéma explicitement sans échelle.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"A00","Analyse du site et parcours","Lecture photo + diagrammes d’usage · schéma non topographique, sans limites cadastrales ni distances mesurées.")
    for i,(fpath,label) in enumerate([
      ("photos/LE SITE/WhatsApp Image 2026-10-13 at 5.50.23 PM (5).jpeg","Arbre existant observé; position exacte à relever."),
      ("photos/interieur/WhatsApp Image 2026-10-13 at 6.12.46 PM (4).jpeg","Entrée photographiée; seuil et passage à mesurer."),
    ]):
        ax=fig.add_axes([.045+i*.32,.52,.30,.28]); ax.imshow(Image.open(ROOT/fpath).convert("RGB")); ax.set_axis_off()
        ax.text(.02,.02,label,transform=ax.transAxes,fontsize=6,color=INK,bbox={"facecolor":WHITE,"alpha":.9,"edgecolor":"none","pad":2})
        ax.text(.03,.94,"OBSERVÉ EN PHOTO",transform=ax.transAxes,fontsize=6,color=ORANGE,weight="bold",bbox={"facecolor":WHITE,"alpha":.9,"edgecolor":"none","pad":2})
    # schéma d'accès intérieur depuis le plan IFC : flèches de parcours = intention, pas circulation réglementaire.
    ax=fig.add_axes([.06,.10,.58,.35]); draw_plan(fig,ax,local,cut_z=1.0,legend=False,space_labels=False)
    ax.set_xlim(-.35,6.9); ax.set_ylim(-.35,7.75)
    for a,b,n in [((3.3,.18),(1.65,.45),"1"),((1.65,.45),(1.8,3.5),"2"),((1.8,3.5),(4.7,3.0),"3")]:
        ax.annotate("",b,a,arrowprops={"arrowstyle":"-|>","lw":1.6,"color":ORANGE,"linestyle":"--","connectionstyle":"arc3,rad=-.12"})
        ax.text(*b,n,fontsize=7,weight="bold",color=WHITE,ha="center",va="center",bbox={"boxstyle":"circle,pad=.28","fc":ORANGE,"ec":"none"},zorder=10)
    panel_title(fig,.77,"Lire les séquences"); panel_text(fig,.742,"1 · ENTRER\nRepérer le comptoir depuis le seuil.\n\n2 · S’ORIENTER\nTraverser vers salle vitrée ou rayonnages.\n\n3 · S’INSTALLER\nChoisir lecture, table de travail ou terrasse.\n\nLes flèches décrivent des parcours de projet. Les dégagements, l’accessibilité et la sécurité restent à valider après relevé.")
    panel_title(fig,.44,"À relever sur place"); panel_text(fig,.412,"Limites et niveaux extérieurs · seuil · pièce bleue · ombres et écoulement des eaux.",6.5)
    site=fig.add_axes([.715,.055,.26,.27]); site.set_xlim(0,1); site.set_ylim(0,1); site.set_aspect("auto"); site.axis("off")
    site.text(.5,.98,"SITE EXTÉRIEUR · SCHÉMA NON COTÉ",ha="center",va="top",fontsize=4.8,color=ORANGE,weight="bold")
    # Relation spatiale illustrative, sans orientation ni limites parcellaires : bâtiment au nord,
    # seuil et garde-corps à relever, puis dallages et cheminement observés / projetés.
    site.add_patch(plt.Rectangle((.04,.64),.48,.25,fc="#F1F0EB",ec=INK,lw=.7)); site.text(.28,.78,"LOCAL · IFC",ha="center",va="center",fontsize=5.0,color=INK)
    site.add_patch(plt.Rectangle((.04,.48),.48,.15,fc="#DED9CF",ec=MID,lw=.6)); site.text(.28,.555,"TERRASSE COUVERTE\nexistante · IFC V5",ha="center",va="center",fontsize=4.4,color=INK)
    site.plot([.025,.55],[.455,.455],color=MID,lw=1.2,ls="--")
    site.text(.29,.425,"CLÔTURE / GARDE-CORPS À CONFIRMER",ha="center",va="top",fontsize=4.0,color=MID)
    site.add_patch(plt.Rectangle((.56,.48),.38,.15,fc="#E36A3D",ec=ORANGE,lw=.8,ls="--",alpha=.23)); site.text(.75,.555,"EXTENSION\noption V6",ha="center",va="center",fontsize=4.4,color=ORANGE)
    site.add_patch(plt.Rectangle((.05,.10),.37,.23,fc="#D8D4CC",ec=MID,lw=.55)); site.text(.235,.215,"DALLAGE EXISTANT\nobservé en photo",ha="center",va="center",fontsize=4.2,color=INK)
    site.add_patch(plt.Rectangle((.43,.10),.51,.32,fc="#DCE5D5",ec="#91A287",lw=.55,alpha=.75)); site.text(.68,.28,"PELOUSE",ha="center",va="center",fontsize=4.7,color=INK)
    site.plot([.16,.24,.31,.28],[.05,.11,.24,.47],color=ORANGE,lw=1.0,ls=(0,(2,1)))
    site.annotate("",xy=(.28,.47),xytext=(.28,.35),arrowprops={"arrowstyle":"-|>","color":ORANGE,"lw":.9})
    site.text(.12,.045,"PARCOURS",ha="center",va="center",fontsize=4.0,color=ORANGE)
    fig.text(.06,.075,"Arbre et chemin : observations photographiques; symboles et parcours non géolocalisés.",fontsize=6.2,color=MID)
    pages.append(fig)

    # A01 — plan coté de maquette avec nomenclature et statut de chaque couche.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"A01","Plan RDC · implantation Option C","Géométrie issue de l’IFC V6 · cotes d’emprise de maquette uniquement, à contrôler au relevé.")
    ax=fig.add_axes([.035,.09,.65,.77]); draw_plan(fig,ax,local,cut_z=1.0,legend=False)
    ax.set_xlim(-.55,7.05); ax.set_ylim(-.35,7.85)
    dimension(ax,(xmin,ymin),(xmax,ymin),f"{xmax-xmin:.2f} m · emprise IFC",offset=(0,-.28))
    dimension(ax,(xmin,ymin),(xmin,ymax),f"{ymax-ymin:.2f} m · emprise IFC",offset=(-.28,0))
    # Repères de coupe reportés sur le plan; la ligne pointillée indique le plan de coupe.
    ax.plot([2.0,2.0],[.1,5.0],color=ORANGE,lw=.85,ls=(0,(4,2)),zorder=8)
    ax.plot([.1,6.5],[4.35,4.35],color="#8D593D",lw=.85,ls=(0,(4,2)),zorder=8)
    for x,y,label,col in [(2,5.05,"A",ORANGE),(2,.1,"A",ORANGE),(.05,4.35,"B","#8D593D"),(6.55,4.35,"B","#8D593D")]:
        ax.text(x,y,label,fontsize=6.5,weight="bold",color=WHITE,ha="center",va="center",bbox={"boxstyle":"circle,pad=.24","fc":col,"ec":"none"},zorder=9)
    north_arrow(ax,6.65,7.25)
    panel_title(fig,.77,"Programme / repères"); panel_text(fig,.742,"01  Grande salle · coworking et lecture\n02  Accueil-café · poste unique\n03  Pièce bleue présumée · salle vitrée\n04–07  Locaux de service hérités V5\n08  Terrasse couverte héritée de la maquette",6.4)
    panel_title(fig,.48,"Légende")
    legend=[("#242824","Existant IFC V5"),(ORANGE,"Mobilier / ajout V6"),(ORANGE,"Hypothèse V6 · tirets")]
    for i,(c,l) in enumerate(legend):
        yy=.45-i*.03; fig.add_artist(plt.Line2D([.728,.755],[yy,yy],transform=fig.transFigure,color=c,lw=1.5,ls="--" if i==2 else "-")); fig.text(.762,yy-.008,l,fontsize=6.4,color=INK)
    panel_title(fig,.33,"Terrasse / limite à vérifier"); panel_text(fig,.302,f"Emprise des murs IFC : {xmax-xmin:.2f} × {ymax-ymin:.2f} m.\n\nTERRASSE COUVERTE EXISTANTE → CLÔTURE / GARDE-CORPS À CONFIRMER ET À RELEVER → DALLAGE EXTÉRIEUR OPTIONNEL V6.\n\nAucune cote de parcelle ou distance extérieure n’est connue.",6.0)
    pages.append(fig)

    # A02 — plan réfléchi et diagramme de zonage / usages.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"A02","Plafond, lumière et logique des usages","Plan réfléchi de maquette V5/V6; les zones colorées et parcours sont des diagrammes de conception, sans recaler les équipements.")
    ax=fig.add_axes([.045,.10,.63,.75]); draw_lighting(ax,local); ax.set_xlim(-.35,7.05); ax.set_ylim(-.35,7.8)
    for (x,y,w,h),label,col,a in [((.1,.1,2.7,2.25),"ACCUEIL",ORANGE,.12),((.1,2.55,2.8,2.55),"SALLE VITRÉE",BLUE,.25),((3.1,.1,3.4,7.25),"LECTURE / COWORKING",BROWN,.08)]:
        ax.add_patch(plt.Rectangle((x,y),w,h,fc=col,ec=col,lw=.8,alpha=a,zorder=1)); ax.text(x+w/2,y+h/2,label,fontsize=6.4,color=INK,ha="center",va="center",weight="bold",zorder=6,bbox={"fc":WHITE,"ec":"none","alpha":.85,"pad":1.5})
    ax.annotate("",(1.45,.45),(3.3,.1),arrowprops={"arrowstyle":"-|>","lw":1.2,"color":ORANGE,"linestyle":"--"})
    ax.annotate("",(4.8,3.3),(1.45,.45),arrowprops={"arrowstyle":"-|>","lw":1.2,"color":ORANGE,"linestyle":"--","connectionstyle":"arc3,rad=-.15"})
    # Symboles orange : intention de lumière, séparée des points gris de l’IFC hérité.
    for x,y in [(3.8,1.0),(5.2,1.0),(3.8,2.5),(5.2,2.5),(4.6,4.8),(1.2,1.1)]:
        ax.add_patch(plt.Circle((x,y),.13,fill=False,ec=ORANGE,lw=1.05,ls=(0,(3,2)),zorder=8))
        ax.plot([x-.08,x+.08],[y,y],color=ORANGE,lw=.6,zorder=8); ax.plot([x,x],[y-.08,y+.08],color=ORANGE,lw=.6,zorder=8)
    panel_title(fig,.77,"Deux statuts graphiques")
    panel_text(fig,.742,"POINT GRIS · appareil présent dans l’IFC V5, position héritée et non vérifiée.\n\nCERCLE ORANGE TIRETÉ · intention de lumière V6, position indicative non modélisée dans l’IFC.",6.2)
    panel_title(fig,.51,"Scénario de conception")
    panel_text(fig,.482,"Lumière générale diffuse dans la grande salle; accent au comptoir et lumière de tâche aux tables. Les symboles ne fixent ni quantité, ni circuit, ni niveau d’éclairement.",6.2)
    panel_title(fig,.27,"À coordonner")
    panel_text(fig,.242,"Faux plafond · retombées · climatisation / condensats · circuits et protections · ventilation · lumière naturelle.",6.0)
    pages.append(fig)

    # A04/A05 — grandes coupes composites avec niveaux, hachures et personnage conventionnel.
    reserve=next((o for o in hypotheses if "plateforme" in o["name"].lower()),None)
    for code,axis,val,u,v,title,sub in [
      ("A03",0,2.0,1,2,"Coupe A–A · accueil et salle","Coupe verticale réelle du maillage IFC, position x = 2,00 m (à relever sur site)."),
      ("A04",1,4.35,0,2,"Coupe B–B transversale · pièce bleue et réserve","Coupe transversale réelle du maillage IFC à y = 4,35 m; plateforme orange tiretée = hypothèse V6."),
    ]:
        fig=plt.figure(figsize=fmt); arch_frame(fig,code,title,sub)
        ax=fig.add_axes([.045,.14,.63,.69]); section_plot(ax,local,axis,val,u,v,"Coupe IFC V6 · existant, projet et hypothèse")
        if axis==0:
            ax.set_xlim(-.55,7.85); ax.set_ylim(-.18,3.58)
            # Hachures de coupe schématiques sur plancher haut et murs périphériques, séparées du trait IFC.
            hatching((-.08,3.28,6.74,.18),ax,"///"); ax.plot([-.08,6.66],[3.28,3.28],color=INK,lw=.8,zorder=7)
            hatching((-.08,0,.16,3.28),ax,"///"); hatching((6.53,0,.16,3.28),ax,"///")
            levelxs=[.0,6.58]
            add_scale_person(ax,6.05,0,1.70)
            dimension(ax,(6.18,0),(6.18,1.70),"1,70 m · gabarit indicatif",offset=(.23,0),fs=5.6)
            ax.text(.18,3.36,"NIVEAU HAUT IFC V5 · +3,30 m · HYPOTHÈSE DE MODÈLE",fontsize=6.2,color=MID)
            ax.text(.2,.08,"±0,00 RDC IFC · niveau de modèle, non relevé",fontsize=6.0,color=MID)
            ax.axhline(0,color=MID,lw=.45,ls=(0,(2,2)),zorder=6); ax.axhline(3.3,color=MID,lw=.45,ls=(0,(2,2)),zorder=6)
            dimension(ax,(6.78,0),(6.78,3.3),"3,30 m · modèle",offset=(.26,0),fs=6.0)
            ax.annotate("D01 · comptoir V6",xy=(.48,.7),xytext=(1.15,1.18),fontsize=5.2,color=ORANGE,arrowprops={"arrowstyle":"->","lw":.6,"color":ORANGE},bbox={"fc":WHITE,"ec":"none","alpha":.9})
            ax.annotate("D02 · table réunion V6",xy=(3.55,.76),xytext=(4.35,1.08),fontsize=5.2,color=ORANGE,arrowprops={"arrowstyle":"->","lw":.6,"color":ORANGE},bbox={"fc":WHITE,"ec":"none","alpha":.9})
            panel_title(fig,.77,"Éléments traversés"); panel_text(fig,.742,"Le plan coupe le comptoir et la table de réunion dans leur géométrie V6. Les traits noirs décrivent le modèle hérité; les traits orange décrivent les ajouts V6.",6.5)
            panel_title(fig,.48,"Niveaux à confirmer"); panel_text(fig,.452,"±0,00 et +3,30 m sont des niveaux de modèle, pas des cotes de chantier. Épaisseur et appuis de la dalle haute restent à vérifier par relevé et avis structure.",6.4)
            # Principe de cloison vitrée demandé au programme, absent de la géométrie IFC V6.
            panel_title(fig,.26,"Interface salle vitrée · intention")
            inset=fig.add_axes([.735,.105,.22,.125]); inset.set_xlim(0,1); inset.set_ylim(0,1); inset.axis("off")
            inset.add_patch(plt.Rectangle((.08,.10),.84,.72,fc="none",ec=ORANGE,lw=.85,ls="--"))
            inset.plot([.50,.50],[.10,.82],color=ORANGE,lw=.55,ls="--"); inset.plot([.08,.92],[.10,.10],color=INK,lw=1.1)
            inset.add_patch(Arc((.50,.10),.35,.35,theta1=0,theta2=90,color=ORANGE,lw=.6,ls="--"))
            inset.text(.5,.48,"verre clair",ha="center",fontsize=5.7,color=MID)
            fig.text(.735,.075,"SCHÉMA NON COTÉ · cloison et porte non modélisées dans l’IFC V6.",fontsize=5.5,color=MID,wrap=True)
        else:
            ax.set_xlim(-.35,7.05); ax.set_ylim(-.18,3.58)
            hatching((-.08,3.28,6.74,.18),ax,"///"); ax.plot([-.08,6.66],[3.28,3.28],color=INK,lw=.8,zorder=7)
            hatching((-.08,0,.16,3.28),ax,"///"); hatching((6.53,0,.16,3.28),ax,"///")
            add_scale_person(ax,5.4,0,1.70)
            if reserve is not None:
                ax.annotate("PLATEFORME · HYPOTHÈSE V6\nface inf. +2,08 / sup. +2,28 m",xy=(1.6,2.18),xytext=(3.5,2.55),fontsize=6.2,color=ORANGE,arrowprops={"arrowstyle":"->","color":ORANGE,"lw":.7},bbox={"fc":WHITE,"ec":"none","alpha":.85})
            ax.text(.2,.08,"±0,00 RDC IFC · niveau de modèle, non relevé",fontsize=6.0,color=MID)
            ax.text(.18,3.36,"NIVEAU HAUT IFC V5 · +3,30 m · À CONFIRMER",fontsize=6.2,color=MID)
            ax.axhline(0,color=MID,lw=.45,ls=(0,(2,2)),zorder=6); ax.axhline(3.3,color=MID,lw=.45,ls=(0,(2,2)),zorder=6)
            dimension(ax,(6.73,0),(6.73,3.3),"3,30 m · modèle",offset=(.25,0),fs=6.0)
            panel_title(fig,.77,"Hypothèse de réserve"); panel_text(fig,.742,"La plateforme est un objet IFC de projet, pas un plancher validé. L’IFC ne montre ni escalier, ni garde-corps, ni appuis vérifiés. Aucun stockage ni accès n’est présumé.",6.5)
            panel_title(fig,.48,"À obtenir"); panel_text(fig,.452,"Relevé altimétrique et structurel · avis d’un BET · stratégie d’accès et de protection · validation de la correspondance de la pièce bleue avec l’espace 03.",6.4)
            # Zoom 1: interface de réserve, dimensions uniquement issues du maillage.
            panel_title(fig,.25,"Zoom / objet IFC V6")
            axin=fig.add_axes([.735,.105,.22,.145],projection="3d"); draw_component(axin,reserve) if reserve is not None else axin.set_axis_off()
            fig.text(.735,.075,"Plateforme hypothétique · appuis, accès et garde-corps non définis.",fontsize=5.5,color=MID,wrap=True)
        fig.text(.06,.09,"Silhouette conventionnelle 1,70 m pour lecture graphique uniquement · aucune personne ni hauteur humaine relevée.",fontsize=5.8,color=MID)
        pages.append(fig)

    # A05 — façade (état de référence) avec note claire de non-intervention V6.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"A05","Élévation sur rue · état existant","Élévation héritée de l’IFC V5; aucune transformation de façade n’est modélisée en V6.")
    ax=fig.add_axes([.04,.11,.64,.74]); section_plot(ax,local,1,float(ymin+.05),0,2,"Élévation sud · projection de la maquette")
    ax.set_xlim(-.7,7.4); ax.set_ylim(-.3,4.0)
    # arbre d'alignement seulement repéré d'après photo, sans géolocalisation ni gabarit coté.
    ax.text(0.02,.88,"ARBRES ET ABORDS NON MODÉLISÉS / À RELEVER",transform=ax.transAxes,fontsize=6.2,color=MID,bbox={"fc":WHITE,"ec":"none","alpha":.9})
    panel_title(fig,.77,"État de référence"); panel_text(fig,.742,"Les baies et arches visibles sont celles de la maquette V5. Leur conformité à l’existant photographié et les dimensions de l’entrée restent à vérifier.",6.5)
    panel_title(fig,.50,"Aucune intervention V6"); panel_text(fig,.472,"Grilles, enseigne, menuiseries, seuil, arbres et mobilier extérieur ne sont pas modifiés par cette proposition IFC.",6.5)
    pages.append(fig)

    # A06 — élévations intérieures avec rayonnages cotés depuis l'IFC.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"A06","Élévations intérieures · rayonnages","Élévations au droit des objets V6; dimensions de maquette, pas dimensions de fabrication.")
    ax1=fig.add_axes([.045,.51,.63,.31]); section_plot(ax1,local,1,6.83,0,2,"Nord · rayonnage droit V6")
    ax2=fig.add_axes([.045,.13,.63,.31]); section_plot(ax2,local,0,6.30,1,2,"Est · rayonnage droit V6")
    panel_title(fig,.77,"Dimensions de maquette")
    r_n=next((o for o in new if "rayonnage droit nord" in o["name"].lower()),None)
    r_e=next((o for o in new if "rayonnage droit est" in o["name"].lower()),None)
    def dims(o):
        d=o["verts"].max(0)-o["verts"].min(0); return d
    if r_n is not None:
        d=dims(r_n); panel_text(fig,.742,f"Nord-est · enveloppe IFC {d[0]:.2f} × {d[1]:.2f} × {d[2]:.2f} m.\n\nEst : rayonnage V6 prolongé contre le mur.\n\nAppuis, fixations, charge admissible et profondeur utile ne sont pas définis par la géométrie.",6.4)
    panel_title(fig,.48,"Coordination")
    panel_text(fig,.452,"Relever niches, prises et passages. Vérifier la stabilité et l’ancrage au support. Contrôler l’accessibilité aux ouvrages et l’emprise des portes.",6.4)
    pages.append(fig)

    # A07 — axonométrie intérieure/extérieure + schéma de situation non cadastral.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"A07","Axonométrie d’implantation","Enveloppe filaire + mobilier IFC · la bande extérieure orange est une option de dallage, non une limite de propriété.")
    ax=fig.add_axes([.025,.12,.66,.72],projection="3d"); draw_axon(ax,local,False)
    # Repères d’objets du projet dans l’axo; positions pointées depuis les maillages V6.
    for number,start,end in [
      ("1",(1.6,.5,1.1),(1.0,-1.1,2.1)),
      ("2",(4.7,6.8,1.8),(5.4,7.65,2.7)),
      ("3",(6.3,5.2,1.6),(6.9,4.5,2.5)),
      ("4",(1.6,4.5,2.2),(.2,5.4,3.0)),
      ("5",(3.2,-3.2,.1),(2.7,-3.95,1.2)),
    ]:
        ax.plot([start[0],end[0]],[start[1],end[1]],[start[2],end[2]],color=ORANGE,lw=.7)
        ax.scatter([start[0]],[start[1]],[start[2]],s=9,color=ORANGE)
        ax.text(end[0],end[1],end[2],number,color=WHITE,fontsize=5,weight="bold",bbox={"boxstyle":"circle,pad=.25","fc":ORANGE,"ec":"white","lw":.4})
    panel_title(fig,.77,"Séquence d’implantation")
    panel_text(fig,.742,"Entrée et accueil → salle vitrée à gauche → lecture / coworking à droite → terrasse existante et extension optionnelle.",6.5)
    site_ax=fig.add_axes([.735,.39,.23,.24]); site_ax.set_aspect("equal"); site_ax.axis("off")
    site_ax.add_patch(plt.Rectangle((.18,.18),.58,.62,fc="#F0F0ED",ec=INK,lw=.8))
    site_ax.add_patch(plt.Rectangle((.18,.02),.58,.16,fc="#E36A3D",ec=ORANGE,lw=.8,alpha=.25,linestyle="--"))
    site_ax.text(.47,.5,"LOT /\nLOCAL\nIFC",ha="center",va="center",fontsize=7,color=INK,weight="bold")
    site_ax.text(.47,.1,"EXTENSION\nOPTION",ha="center",va="center",fontsize=6,color=ORANGE)
    # tree icon with explicit documentary status; its location is schematic.
    site_ax.add_patch(plt.Circle((.86,.23),.08,fill=False,ec=MID,lw=.8)); site_ax.plot([.86,.86],[.12,.21],color=MID,lw=.8)
    site_ax.text(.86,.07,"arbre vu\nen photo*",ha="center",fontsize=5.5,color=MID)
    site_ax.text(.45,.92,"SCHÉMA SANS ÉCHELLE",ha="center",fontsize=6,color=ORANGE,weight="bold")
    panel_title(fig,.30,"Repères sur l’axo"); panel_text(fig,.272,"1 Comptoir V6 · 2 Rayonnage nord · 3 Rayonnage est · 4 Plateforme haute hypothétique · 5 Dallage extérieur optionnel. Le retour WC optionnel apparaît sur A01/A08.",6.0)
    fig.text(.74,.09,"*Position de l’arbre non géolocalisée.",fontsize=5.8,color=MID)
    pages.append(fig)

    # A08 — détails utiles, vues réelles, enveloppes mesurées dans IFC et principe à développer.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"A08","Détails de conception · mobilier","Vues rapprochées des objets IFC et repères dimensionnels issus de leurs maillages; non exécutoires.")
    specs=[
      (next((o for o in new if "comptoir accueil" in o["name"].lower()),None),"D01 · COMPTOIR ACCUEIL"),
      (next((o for o in new if "table de réunion" in o["name"].lower()),None),"D02 · TABLE DE RÉUNION"),
      (r_n,"D03 · RAYONNAGE NORD-EST"),
      (next((o for o in new if "retour opaque wc" in o["name"].lower()),None),"D04 · ÉCRAN WC / OPTION"),
    ]
    boxes=[(.055,.51,.30,.30),(.37,.51,.30,.30),(.055,.13,.30,.30),(.37,.13,.30,.30)]
    for (obj,label),rect in zip(specs,boxes):
        if obj is None: continue
        ax=fig.add_axes(rect,projection="3d"); draw_component(ax,obj)
        fig.text(rect[0],rect[1]+rect[3]+.008,label,fontsize=6.7,weight="bold",color=INK)
        d=dims(obj)
        fig.text(rect[0],rect[1]-.026,f"Enveloppe IFC (L × P × H) : {d[0]:.2f} × {d[1]:.2f} × {d[2]:.2f} m",fontsize=5.8,color=ORANGE)
        fig.text(rect[0],rect[1]-.047,"Géométrie de principe · raccords, sections, fixations et tolérances à définir.",fontsize=5.5,color=MID)
    panel_title(fig,.77,"Principes constructifs à développer")
    panel_text(fig,.742,"Comptoir · corps menuisé, plinthe protégée, plateau résistant à l’eau; réservations café et alimentation non positionnées.\n\nRayonnage · tablettes répétitives et ancrage à dimensionner selon support et charges.\n\nÉcran WC · retour opaque optionnel dans l’IFC; une finition ajourée est une variante de conception, non modélisée.\n\nTable · plateau et piètements sont des volumes de maquette, sans assemblage fabricant.",6.0)
    panel_title(fig,.33,"Statut des cotes")
    panel_text(fig,.302,"Ces longueurs sont les limites des maillages IFC, pas des mesures prises sur site. Vérifier les jeux, débattements, passage libre et support avant fabrication.",6.0)
    principle=fig.add_axes([.735,.105,.22,.115]); principle.set_xlim(0,1); principle.set_ylim(0,1); principle.axis("off")
    principle.add_patch(plt.Rectangle((.08,.66),.84,.16,fc="#9A7050",ec=INK,lw=.65))
    principle.add_patch(plt.Rectangle((.08,.28),.84,.36,fc="#EEEAE3",ec=INK,lw=.65,hatch="xx"))
    principle.plot([.1,.9],[.18,.18],color=INK,lw=1.0)
    principle.annotate("",(.93,.66),(.93,.82),arrowprops={"arrowstyle":"<->","lw":.55,"color":ORANGE})
    principle.text(.04,.02,"PRINCIPE DE PLATEAU / CAISSON / PLINTHE · SCHÉMA SANS COTES",fontsize=4.8,color=MID)
    pages.append(fig)

    # T00 — palette, nomenclature et points ouverts.
    fig=plt.figure(figsize=fmt); arch_frame(fig,"T00","Palette, nomenclature et validations","Matières indicatives · quantités = comptage d’objets IFC, pas métrés de fabrication.")
    sw=[("Bois / mobilier",BROWN),("Enduit clair","#EDE9DF"),("Terre cuite",ORANGE),("Métal sombre",INK),("Verre",BLUE)]
    for i,(label,c) in enumerate(sw):
        x=.05+i*.122; ax=fig.add_axes([x,.73,.105,.09]); ax.set_facecolor(c); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_color(INK)
        fig.text(x,.705,label,fontsize=5.8,color=INK)
    # nomenclature concise par famille V6
    table_ax=fig.add_axes([.05,.16,.62,.48]); table_ax.axis("off")
    rows=[("01","Comptoir accueil-café","1","IFC V6 / projet"),("02","Siège du poste accueil","1","IFC V6 / projet"),("03","Table réunion 6 places","1","IFC V6 / projet"),("04","Sièges de réunion","1 ensemble","IFC V6 / projet"),("05","Rayonnages droits nord et est","2","IFC V6 / projet"),("06","Retour opaque WC","1","IFC V6 / option à valider"),("07","Plateforme réserve haute","1","IFC V6 / hypothèse structure"),("08","Dallage extension terrasse","1","IFC V6 / emprise optionnelle"),("09","Luminaires hérités","27","IFC V5 / non recalés")]
    yy=.655
    for j,row in enumerate(rows):
        color="#F4F3F0" if j%2==0 else WHITE
        table_ax.add_patch(plt.Rectangle((0,yy-.045),1,.045,transform=table_ax.transAxes,fc=color,ec="none"))
        table_ax.text(.02,yy-.029,row[0],transform=table_ax.transAxes,fontsize=6.2,color=ORANGE,weight="bold")
        table_ax.text(.09,yy-.029,row[1],transform=table_ax.transAxes,fontsize=6.1,color=INK)
        table_ax.text(.66,yy-.029,row[2],transform=table_ax.transAxes,fontsize=6.1,color=INK)
        table_ax.text(.76,yy-.029,row[3],transform=table_ax.transAxes,fontsize=5.7,color=MID)
        yy-=.05
    panel_title(fig,.77,"Avant APS / fabrication")
    panel_text(fig,.742,"1 · Relever l’enveloppe, les baies, les seuils et niveaux.\n2 · Confirmer pièce bleue ↔ IFC 03.\n3 · Recalculer éclairage, ventilation, prises et évacuations.\n4 · Faire vérifier plateforme, charges et accès par un BET.\n5 · Confirmer limites, pentes et eaux de terrasse.\n6 · Échantillonner les finitions et consulter les menuisiers.",6.0)
    panel_title(fig,.40,"Contrôles IFC")
    panel_text(fig,.372,f"{len(objects)} géométries calculées; {len(new)} produits V6 ajoutés; {len(failures)} échec(s) de calcul.\n\nLa validation IFC contrôle le fichier, pas la conformité réglementaire ni la constructibilité.",6.0)
    pages.append(fig)
    return pages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ifc", type=Path, default=V6_IFC, help="IFC V6 à lire (par défaut: v6/DECIMO_ESQ_V6_OPTION_C.ifc)")
    parser.add_argument("--check-only", action="store_true", help="Calcule le maillage et les comptes sans générer le PDF")
    args = parser.parse_args()
    model, objects, failures, scale = load_geometry(args.ifc)
    if args.check_only:
        print(f"IFC: {args.ifc}; produits géométriques: {len(objects)}; nouveaux V6: {sum(not o['old'] for o in objects)}; échecs: {len(failures)}")
        return
    figs = make_arch_pages(model, objects, failures, scale)
    PREVIEW.mkdir(exist_ok=True)
    with PdfPages(OUT) as pdf:
        for i, fig in enumerate(figs, 1):
            pdf.savefig(fig, bbox_inches=None)
            fig.savefig(PREVIEW / f"page_{i:02d}.png", dpi=150, facecolor=fig.get_facecolor())
            plt.close(fig)
    print(f"PDF: {OUT}")
    print(f"Planches générées: {len(figs)}; géométries: {len(objects)}; V6: {sum(not o['old'] for o in objects)}; échecs: {len(failures)}")
    for name, error in failures:
        print(f"ÉCHEC GEO {name}: {error[:180]}")


if __name__ == "__main__":
    main()
