"""Export de consultation depuis les mêmes maillages que l’axonométrie IFC.

L'IFC reste le fichier de travail. Le GLB et la page HTML sont des compléments
de lecture : coupe d'affichage à +2,40 m, façades sud/est abaissées à +1,00 m,
plafonds et options de réserve/extension masqués. Aucun IFC n'est modifié.
"""
from pathlib import Path
import base64
import hashlib
import json
import sys
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from render_maquette import load_scene, render_arrays


def main():
    folder = ROOT / 'v7'
    source = folder / 'DECIMO_PROPOSITION_V7.ifc'
    scene = load_scene(source)
    triangles, colors, ids, excluded, kept = render_arrays(scene, 'axo')
    out = trimesh.Scene()
    rotation = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    for index in np.unique(ids):
        select = ids == index
        t = triangles[select]
        rgba = np.rint(np.clip(colors[select], 0, 1) * 255).astype(np.uint8)
        for k, color in enumerate(np.unique(rgba, axis=0)):
            part = t[np.all(rgba == color, axis=1)]
            if not len(part):
                continue
            mesh = trimesh.Trimesh(vertices=part.reshape(-1, 3),
                faces=np.arange(len(part) * 3).reshape(-1, 3), process=False)
            material = trimesh.visual.material.PBRMaterial(
                name=f'mat_{int(index)}_{k}', baseColorFactor=color,
                roughnessFactor=.82, metallicFactor=.04,
                alphaMode='BLEND' if color[3] < 250 else 'OPAQUE',
                doubleSided=True)
            mesh.visual = trimesh.visual.TextureVisuals(material=material)
            mesh.apply_transform(rotation)
            label = kept[int(index)]['nom'] or f'Produit {index}'
            out.add_geometry(mesh, node_name=f'{label} / {k}', geom_name=f'{index}_{k}')
    glb = out.export(file_type='glb')
    (folder / 'MAQUETTE_V7_VISITE.glb').write_bytes(glb)
    poster = folder / 'assets/ifc/axo.png'
    poster_uri = 'data:image/png;base64,' + base64.b64encode(poster.read_bytes()).decode() if poster.exists() else ''
    model_uri = 'data:model/gltf-binary;base64,' + base64.b64encode(glb).decode()
    html = '''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bibliothèque Nandjui D. Simon — maquette V7</title>
<script type="module" src="https://unpkg.com/@google/model-viewer@4.0.0/dist/model-viewer.min.js"></script>
<style>*{box-sizing:border-box}body{margin:0;background:#f5f2ec;color:#292826;font:16px system-ui,sans-serif}header{padding:22px 5vw;background:#fff;border-bottom:1px solid #d8d2c9}h1{font-size:clamp(22px,4vw,34px);margin:0 0 6px}p{margin:5px 0;line-height:1.5}model-viewer{display:block;width:100%;height:70vh;min-height:400px;background:#f5f2ec}nav{padding:10px 5vw;display:flex;gap:10px;flex-wrap:wrap}button{border:1px solid #bd5b3b;border-radius:3px;background:#fff;padding:10px 14px;color:#7c3c27;font:inherit;cursor:pointer}footer{padding:15px 5vw;color:#68655e;font-size:14px;max-width:1000px}noscript{display:block;padding:20px}</style>
<header><h1>Une bibliothèque habitée</h1><p>Maquette V7 en coupe · tournez avec le doigt ou la souris, zoomez avec deux doigts.</p></header>
<model-viewer id="model" camera-controls touch-action="pan-y" shadow-intensity=".7" exposure="1.1" environment-image="neutral" src="__MODEL__" poster="__POSTER__" alt="Maquette du projet : accueil-café à gauche du seuil, salle vitrée, rangements périphériques et terrasse." camera-orbit="35deg 55deg auto"><img slot="poster" src="__POSTER__" alt="Aperçu statique de la maquette" style="width:100%;height:100%;object-fit:contain"></model-viewer>
<nav><button id="reset">Vue d’ensemble</button><button id="rotate">Faire tourner</button></nav>
<footer><p>Vue d’affichage issue de l’IFC : plafonds et options de réserve haute/extension masqués; parois sud et est abaissées pour lire l’intérieur. Le modèle complet reste dans le fichier IFC.</p><p>Les données 3D sont intégrées dans cette page. Une connexion Internet charge le lecteur 3D; l’aperçu reste disponible dans la galerie PNG.</p></footer>
<script>const m=document.querySelector('#model');m.addEventListener('load',()=>m.dismissPoster());document.querySelector('#reset').onclick=()=>{m.cameraOrbit='35deg 55deg auto';m.cameraTarget='auto auto auto';m.jumpCameraToGoal()};document.querySelector('#rotate').onclick=()=>{m.autoRotate=!m.autoRotate};</script></html>'''
    html = html.replace('__MODEL__', model_uri).replace('__POSTER__', poster_uri)
    (folder / 'VISITE_MAQUETTE_V7.html').write_text(html, encoding='utf-8')
    meta = {'source_ifc': str(source.relative_to(ROOT)),
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'geometries_glb': len(out.geometry), 'mode_affichage': 'axonometrie coupee',
        'masques': excluded, 'unites': 'metres',
        'note': 'Complément de consultation; utiliser IFC pour la modification.'}
    (folder / 'visite_3d_provenance.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n')
    print(f'GLB : {len(glb):,} octets; {len(out.geometry)} géométries; lecteur HTML créé')


if __name__ == '__main__':
    main()
