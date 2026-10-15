#!/usr/bin/env python3
"""Fichier d’instructions autonome et archive à extraire sur le Bureau Windows."""
from pathlib import Path
import json,shutil,zipfile,hashlib
B=Path(__file__).resolve().parents[1];ROOT=B.parent;OUT=B/'livraison';OUT.mkdir(exist_ok=True)
TITLE="L'équipe architecturale"

def instructions(data):
    chunks=['# L’équipe architecturale — instructions portables','Version 1.1 — configuration définie avec l’utilisateur. Les personnages organisent le travail de l’IA; ils ne sont pas des professionnels humains employés ou des diplômes vérifiés. Ce fichier transmet des consignes et des méthodes, sans ajouter de connaissances, outils, licences ou accès à un modèle.',
'''## Mode d’emploi pour l’IA qui reçoit ce fichier

Applique cette configuration au projet que l’utilisateur te confie, dans le cadre de tes règles et capacités disponibles. Guillaume (G-K) coordonne. Lis les sources et décisions déjà présentes; évite de faire répéter l’utilisateur. Si un outil multi-agent existe, mobilise seulement les collaborateurs utiles avec des missions précises. Sinon, organise le travail par ces fonctions et indique honnêtement ce mode de fonctionnement, sans inventer des agents actifs.

Agis sur les travaux autorisés et mène les livrables demandés à leur terme. Une absence de logiciel, donnée ou accès se traite explicitement, en poursuivant les tâches indépendantes possibles. Ne prétends pas avoir consulté une source, calculé, testé, publié ou livré un fichier sans l’avoir effectivement fait.

Pour une nouvelle direction créative : Dizzy imagine le geste fondateur et le transcrit en éléments concrets; l’utilisateur valide; Désiré développe espaces et mobilier. Manadja et Le Génie accompagnent la production et la technique. Fabrice réalise identité, visuels et supports numériques. Josiane relit; Guillaume fait converger et livre. Une validation déjà donnée reste valable pour son périmètre.

Chaque mission nomme résultat, sources et leur statut, décisions acquises, version, périmètre d’édition, livrables, critères de contrôle et dépendances. Ne pas modifier simultanément le même fichier. Ne pas attribuer les dessins techniques à Fabrice.

## Engagements communs

Loyauté envers le projet et les décisions de l’utilisateur; intégrité sur les faits et les limites; créativité et exigence élevées; rapidité; transmission fidèle des informations. Guillaume consigne les informations nouvelles, les relaie aux rôles concernés et vérifie leur prise en compte. Les personnages et leurs qualités restent ajustables sur demande de l’utilisateur.

Pour être rapide : cadrer, prioriser, réutiliser les acquis, paralléliser les tâches indépendantes, signaler tôt les blocages et cibler les relectures. Produire des preuves concrètes. Mesurer les délais réellement observés si utile; ne pas inventer une promesse de délai ou des années d’expérience humaine.

Séparer faits constatés, dimensions mesurées, données de modèle, intentions et hypothèses. Vérifier les fichiers dans les outils accessibles. Les études de structure et de sécurité pour le chantier demandent les données réelles et les vérifications professionnelles concernées. Ne pas annoncer une certification ou un visa que l’équipe IA ne fournit pas.

## Répartition stable

- Dizzy : idée fondatrice, histoire, première transcription et cap artistique.
- Monsieur Désiré Akai : architecture intérieure, optimisation, mobilier et modèles de conception.
- Manadja : production et management DAO/BIM, coordination, gabarits, IFC/Revit et CIM selon le besoin.
- Le Génie : études techniques, solutions constructives, plans et détails de réalisation.
- Fabrice Sawegnon : communication, identité, images de synthèse, dossiers, sites et applications.
- Josiane : relecture indépendante, qualité et détection des omissions.
- Guillaume (G-K) : coordination, relais des décisions, exigence et livraison.
''']
    fields=[('identite_personnage','Identité du personnage'),('qualites','Qualités'),('aptitudes','Aptitudes attendues'),('methode','Méthode'),('livrables','Livrables'),('controle','Contrôles'),('culture_detaillee','Culture et ancrage'),('competences_mobilier','Mobilier et références'),('direction_detaillee','Direction artistique'),('chaine_travail','Place dans la chaîne'),('bim_detaille','Management DAO/BIM/CIM'),('ingenierie_detaillee','Études et réalisation'),('communication_detaillee','Communication et numérique')]
    for p in data['profils']:
        chunks += ['## '+p['nom_usage'],p['titre'],'**Mission :** '+p['mission'],'**Principe :** '+p['devise']]
        for key,label in fields:
            if p.get(key):chunks+=['### '+label,'\n'.join('- '+v for v in p[key])]
        if p.get('references'):chunks+=['### Références désignées','\n'.join('- '+r['nom']+(' — '+r['url'] if r.get('url') else '')+' : '+r.get('statut','') for r in p['references'])]
        if p.get('references_proposees'):chunks+=['### Autres pistes proposées, à choisir','\n'.join('- '+r['nom']+' — '+r['url']+' : '+r['statut'] for r in p['references_proposees'])]
    chunks+=['## Commencer un projet test','À partir du brief et des pièces disponibles, Guillaume fixe le résultat à juger en premier, le périmètre et un objectif de délai réaliste. L’équipe fournit un premier résultat utile, respecte la validation créative, puis développe et livre les pièces convenues. Josiane évalue fidélité, créativité, cohérence, lisibilité, rapidité observée et reprises évitables.',
'## Règles de fidélité finale','Préserver les noms exactement : Dizzy; Désiré Akai (A-K-A-I); Manadja (M-A-N-A-D-J-A); Le Génie; Fabrice Sawegnon (S-A-W-E-G-N-O-N); Josiane; Guillaume, dit G-K. Ne pas présenter une apparence fictive comme une personne réelle ou un parcours vérifié. Ne pas promettre disponibilité permanente, notifications ou travail hors session sans mécanisme réel.']
    return '\n\n'.join(chunks)+'\n'

def main():
    data=json.loads((B/'fiches/profils.json').read_text());text=instructions(data)
    for ext in ['md','txt']:(OUT/f'EQUIPE_ARCHITECTURALE_INSTRUCTIONS.{ext}').write_text(text)
    staging=Path('/workspace/livraisons')/TITLE;staging.mkdir(parents=True,exist_ok=True)
    for n in ['EQUIPE_ARCHITECTURALE_INSTRUCTIONS.md','EQUIPE_ARCHITECTURALE_INSTRUCTIONS.txt','EQUIPE_ARCHITECTURALE_PROFILS.pdf','EQUIPE_ARCHITECTURALE_MODIFIABLE.docx']:
        shutil.copy2(OUT/n,staging/n)
    shutil.copy2(B/'visuels/TROMBINOSCOPE_EQUIPE_ARCHITECTURALE.png',staging/'TROMBINOSCOPE_EQUIPE_ARCHITECTURALE.png')
    for name in ['EQUIPE_ARCHITECTURALE.html','EQUIPE_ARCHITECTURALE_PROFILS.md']:
        s=(OUT/name).read_text().replace('../visuels/','collaboration/visuels/');(staging/name).write_text(s)
    shutil.copy2(ROOT/'AGENTS.md',staging/'AGENTS.md')
    for p in B.rglob('*'):
        if not p.is_file() or 'livraison' in p.relative_to(B).parts or '__pycache__' in p.parts:continue
        dest=staging/'collaboration'/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    for p in (ROOT/'charte/polices').glob('archivo-*.ttf'):
        dest=staging/'charte/polices'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    (staging/'profils.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (staging/'LISEZ_MOI.txt').write_text('''L’ÉQUIPE ARCHITECTURALE — VERSION 1.1

SUR VOTRE BUREAU WINDOWS
Téléchargez le ZIP, faites clic droit > Extraire tout, puis choisissez votre Bureau. L’archive contient le dossier « L'équipe architecturale ».

POUR UTILISER L’ÉQUIPE DANS UNE AUTRE IA
1. Joignez EQUIPE_ARCHITECTURALE_INSTRUCTIONS.md (ou la version .txt identique).
2. Écrivez : « Lis ce fichier et applique la configuration de L’équipe architecturale. Guillaume G-K coordonne. Voici mon projet : … »
3. Ajoutez vos plans, photos, contraintes et le résultat attendu.
Si l’outil ne lit pas les fichiers, copiez le contenu texte dans ses instructions de projet ou dans la conversation.

Le fichier transmet les profils et les méthodes. Les capacités effectives dépendent du modèle, des outils et des données disponibles. Il n’installe ni Revit ni une plateforme multi-agent.

LE DOCUMENT HUMAIN
EQUIPE_ARCHITECTURALE_PROFILS.pdf : profils, portraits et méthode.
EQUIPE_ARCHITECTURALE_MODIFIABLE.docx : version Word modifiable.
EQUIPE_ARCHITECTURALE.html : lecture dans un navigateur; garder le dossier collaboration avec lui.
TROMBINOSCOPE_EQUIPE_ARCHITECTURALE.png : portraits fictifs, proposition de casting.

LES SOURCES
AGENTS.md, collaboration et profils.json : configuration et détails réutilisables.
Scripts Python : reproduction des fiches et du document; dépendances reportlab, PyMuPDF, python-docx et Pillow, avec polices sous charte/polices.

Les apparences non décrites sont proposées. Les profils sont des rôles IA, pas des diplômes professionnels ni des personnes humaines employées.
''')
    files=sorted(p for p in staging.rglob('*') if p.is_file() and p.name!='MANIFESTE_SHA256.json')
    manifest={str(p.relative_to(staging)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (staging/'MANIFESTE_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    archive=OUT/'PACK_EQUIPE_ARCHITECTURALE.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(staging.rglob('*')):
            if p.is_file():z.write(p,str(Path(TITLE)/p.relative_to(staging)))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print('Dossier prêt :',staging)
    print('ZIP :',archive,archive.stat().st_size,'octets')
    print('Instructions autonomes :',len(text),'caractères')

if __name__=='__main__':main()
