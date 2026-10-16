"""Vues axonométriques et modèle GLB calculés depuis l'IFC V8 (Manadja, pour Fabrice Sawegnon).

Rendu logiciel (matplotlib), sans OpenGL : ombrage par l'orientation des faces.
Usage : python3 v8/scripts/vues_ifc_v8.py
  -> v8/vues/V01_axo_coupe_2m60.png, v8/vues/V02_axo_terrasse.png, v8/vues/NANDJUI_V8.glb
"""
import os

import ifcopenshell
import ifcopenshell.geom
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
IFC = os.path.join(ICI, "..", "NANDJUI_ESQ_V8.ifc")
SORTIE = os.path.join(ICI, "..", "vues")

f = ifcopenshell.open(IFC)
reg = ifcopenshell.geom.settings()
reg.set("use-world-coords", True)


def maillages():
    out = []
    for p in f.by_type("IfcProduct"):
        if not p.Representation or p.is_a("IfcSpace"):
            continue
        sh = ifcopenshell.geom.create_shape(reg, p)
        g = sh.geometry
        v = np.array(g.verts).reshape(-1, 3)
        t = np.array(g.faces).reshape(-1, 3)
        mids = np.array(g.material_ids) if len(g.material_ids) else np.zeros(len(t), int)
        cols = []
        for m in g.materials:
            d = m.diffuse
            rgb = (d.r(), d.g(), d.b()) if hasattr(d, "r") else tuple(d)[:3]
            tr = m.transparency if m.transparency == m.transparency else 0.0
            cols.append((*rgb, 1 - (tr or 0)))
        if not cols:
            cols = [(0.8, 0.8, 0.8, 1)]
        c = np.array([cols[i] if 0 <= i < len(cols) else cols[0] for i in mids])
        out.append((p, v, t, c))
    return out


MAILL = maillages()
LUM = np.array([-0.45, -0.6, 0.85])
LUM = LUM / np.linalg.norm(LUM)


def vue(nom, elev, azim, coupe=None, exclure=(), titre="", cadre=None, W=1800, H=1250, ss=2):
    """Rendu orthographique à tampon de profondeur, contours par discontinuités."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    a, e = np.radians(azim), np.radians(elev)
    avant = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])   # vers la caméra
    droite = np.array([-np.sin(a), np.cos(a), 0.0])
    haut = np.cross(avant, droite)
    tris, cols, ids, verre = [], [], [], []
    for k, (p, v, t, c) in enumerate(MAILL):
        if any(p.is_a(x) or (p.Name or "").startswith(x) for x in exclure):
            continue
        vv = v.copy()
        if coupe is not None:
            if vv[:, 2].min() >= coupe - 1e-6:
                continue
            vv[:, 2] = np.minimum(vv[:, 2], coupe)
        tri = vv[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nn = np.linalg.norm(n, axis=1)
        g = nn > 1e-9
        n = n[g] / nn[g, None]
        lum = 0.62 + 0.38 * np.clip(n @ LUM, -1, 1) * np.sign(n @ avant + 1e-9)
        cc = c[g].copy()
        cc[:, :3] = np.clip(cc[:, :3] * lum[:, None], 0, 1)
        tris.append(tri[g]); cols.append(cc); ids.append(np.full(g.sum(), k))
    T = np.concatenate(tris); Cc = np.concatenate(cols); I = np.concatenate(ids)
    P = np.stack([T @ droite, T @ haut, T @ avant], axis=-1)
    if cadre is None:
        umin, vmin = P[..., 0].min(), P[..., 1].min(); umax, vmax = P[..., 0].max(), P[..., 1].max()
    else:
        umin, umax, vmin, vmax = cadre
    Ws, Hs = W * ss, (H - 150) * ss
    ech = min((Ws - 120 * ss) / (umax - umin), (Hs - 80 * ss) / (vmax - vmin))
    ox = (Ws - (umax - umin) * ech) / 2 - umin * ech
    oy = (Hs - (vmax - vmin) * ech) / 2 + vmax * ech
    X = P[..., 0] * ech + ox; Y = oy - P[..., 1] * ech; Z = P[..., 2]
    zbuf = np.full((Hs, Ws), -1e9); img = np.zeros((Hs, Ws, 3)); idb = np.full((Hs, Ws), -1)
    fond = np.array([0.965, 0.945, 0.906])
    img[:] = fond
    transp = Cc[:, 3] < 0.95
    def raster(sel, blend):
        ordre = np.where(sel)[0]
        if blend:
            ordre = ordre[np.argsort(Z[ordre].mean(axis=1))]
        for q in ordre:
            xs, ys, zs = X[q], Y[q], Z[q]
            x0, x1 = int(max(np.floor(xs.min()), 0)), int(min(np.ceil(xs.max()), Ws - 1))
            y0, y1 = int(max(np.floor(ys.min()), 0)), int(min(np.ceil(ys.max()), Hs - 1))
            if x1 < x0 or y1 < y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(d) < 1e-12:
                continue
            l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
            l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
            l2 = 1 - l0 - l1
            m = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
            if not m.any():
                continue
            z = l0 * zs[0] + l1 * zs[1] + l2 * zs[2]
            zb = zbuf[y0:y1 + 1, x0:x1 + 1]
            m &= z > zb + 1e-5
            if not m.any():
                continue
            if blend:
                al = 1 - (1 - Cc[q, 3]) * 0 if False else Cc[q, 3]
                sub = img[y0:y1 + 1, x0:x1 + 1]
                sub[m] = sub[m] * (1 - al) + Cc[q, :3] * al
            else:
                zb[m] = z[m]
                img[y0:y1 + 1, x0:x1 + 1][m] = Cc[q, :3]
                idb[y0:y1 + 1, x0:x1 + 1][m] = I[q] * 8 + 0
    raster(~transp, False)
    # contours : changement d'objet ou saut de profondeur
    bord = np.zeros((Hs, Ws), bool)
    for dy, dx in ((0, 1), (1, 0)):
        a1, a2 = idb[: Hs - dy, : Ws - dx], idb[dy:, dx:]
        z1, z2 = zbuf[: Hs - dy, : Ws - dx], zbuf[dy:, dx:]
        b = (a1 != a2) | (np.abs(z1 - z2) > 0.04)
        bord[: Hs - dy, : Ws - dx] |= b
    img[bord] = img[bord] * 0.35 + np.array([0.16, 0.14, 0.12]) * 0.65
    raster(transp, True)
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((W, H - 150), Image.LANCZOS)
    page = Image.new("RGB", (W, H), tuple((fond * 255).astype(int)))
    page.paste(im, (0, 130))
    d = ImageDraw.Draw(page)
    try:
        ft = ImageFont.truetype(os.path.join(ICI, "..", "..", "charte", "polices", "archivo-latin-600-normal.ttf"), 34)
        fs = ImageFont.truetype(os.path.join(ICI, "..", "..", "charte", "polices", "archivo-latin-400-normal.ttf"), 19)
    except OSError:
        ft = fs = ImageFont.load_default()
    d.text((48, 36), titre, fill=(42, 38, 34), font=ft)
    d.text((48, 86), "Calculée depuis NANDJUI_ESQ_V8.ifc · rendu de contrôle sans textures · géométrie d'esquisse, profondeur estimée",
           fill=(107, 102, 96), font=fs)
    os.makedirs(SORTIE, exist_ok=True)
    chemin = os.path.join(SORTIE, nom)
    page.save(chemin)
    print(chemin, len(T), "triangles")


def glb():
    import trimesh
    scene = trimesh.Scene()
    for p, v, t, c in MAILL:
        m = trimesh.Trimesh(vertices=v[:, [0, 2, 1]] * np.array([1, 1, -1]), faces=t, process=False)
        m.visual.face_colors = (np.clip(c, 0, 1) * 255).astype(np.uint8)
        scene.add_geometry(m, node_name=f"{p.is_a()}_{p.id()}")
    chemin = os.path.join(SORTIE, "NANDJUI_V8.glb")
    scene.export(chemin)
    print(chemin)


if __name__ == "__main__":
    vue("V01_axo_coupe_2m60.png", 50, -125, coupe=2.6, titre="V01 · Axonométrie coupée à 2,60 m",
        exclure=("IfcMember", "Plancher de la réserve"))
    vue("V02_axo_terrasse.png", 22, -105, titre="V02 · Vue depuis la terrasse, pergola en place")
    vue("V03_axo_interieur.png", 48, 55, coupe=2.6, titre="V03 · Intérieur coupé à 2,60 m, vu depuis le fond",
        exclure=("IfcMember", "Plancher de la réserve", "Dallage", "Claustra", "Portillon", "Poteau de pergola", "Banquette extérieure",
                 "Table basse extérieure", "Fauteuil bas", "Pouf", "Jardinière", "Plante"))
    glb()
