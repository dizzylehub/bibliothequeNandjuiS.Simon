// Dossier de présentation V8 (Fabrice Sawegnon, rôle IA). Sans nom ni logo d’agence, à la demande du maître d’œuvre.
// Usage, depuis la racine du dépôt :
//   NODE_PATH=<dossier contenant pptxgenjs> node v8/scripts/dossier_v8.js
// Produit v8/dossier/NANDJUI_V8_Dossier_A3.pptx (format A3 paysage), puis conversion PDF par LibreOffice.
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const RACINE = path.resolve(__dirname, "..", "..");
const IMG = path.join(RACINE, "v8", "dossier", "img");
const DIMS = JSON.parse(fs.readFileSync(path.join(IMG, "dims.json"), "utf8"));
const SORTIE = path.join(RACINE, "v8", "dossier", "NANDJUI_V8_Dossier_A3.pptx");

const N = " "; // espace insécable
// palette propre au projet (mid-century) : brun noyer pour les titres, cognac pour les accents, olive pour les en-têtes
const K = { noir: "231C17", gris: "5E5047", vert: "A85F2C", entete: "56613A", blanc: "FFFFFF", grisClair: "F4EFE6", rouge: "B5432C",
            noyer: "7A4A2A", cognac: "A85F2C", olive: "56613A", moutarde: "C9962E", laiton: "C9A227", creme: "EFE4CC" };
const FONT = "Century Gothic";
const W = 16.54, H = 11.69; // A3 paysage, en pouces

const pres = new pptxgen();
pres.defineLayout({ name: "A3", width: W, height: H });
pres.layout = "A3";
pres.author = "L’équipe architecturale (rôles IA)";
pres.title = "Café-bibliothèque Nandjui · esquisse V8";
pres.theme = { headFontFace: FONT, bodyFontFace: FONT };

const PIED = `Café-bibliothèque Nandjui${N}·${N}Abidjan${N}·${N}Esquisse V8 indice B${N}·${N}16 octobre 2026`;
pres.defineSlideMaster({
  title: "CONTENU",
  background: { color: K.blanc },
  objects: [
    { text: { text: PIED, options: { x: 0.6, y: H - 0.66, w: 9, h: 0.3, fontFace: FONT, fontSize: 10, color: K.gris, margin: 0 } } },
    { placeholder: { options: { name: "titre", type: "title", x: 0.6, y: 0.45, w: W - 1.2, h: 0.75, fontFace: FONT, fontSize: 26, bold: true, color: K.gris, margin: 0, valign: "top", align: "left" }, text: "" } },
  ],
  slideNumber: { x: W / 2 - 0.3, y: H - 0.66, w: 0.6, h: 0.3, fontFace: FONT, fontSize: 10, color: K.gris, align: "center" },
});
pres.defineSlideMaster({ title: "COUVERTURE", background: { color: K.blanc }, objects: [] });

// ---------------------------------------------------------------- outils
function fit(key, x, y, w, h, align = "c") {
  const [iw, ih] = DIMS[key];
  const r = Math.min(w / iw, h / ih);
  const ww = iw * r, hh = ih * r;
  let xx = x + (w - ww) / 2, yy = y + (h - hh) / 2;
  if (align === "l") xx = x;
  if (align === "t") yy = y;
  if (align === "lt") { xx = x; yy = y; }
  return { path: path.join(IMG, key + ".jpg"), x: xx, y: yy, w: ww, h: hh };
}
function img(s, key, x, y, w, h, align, nom) {
  const o = fit(key, x, y, w, h, align);
  s.addImage({ ...o, altText: nom || key, objectName: "image " + key });
  return o;
}
function fr(x) { return x.replace(/« /g, "«" + N).replace(/ »/g, N + "»").replace(/ ([:;!?])/g, N + "$1"); }
function t(s, text, o) {
  text = typeof text === "string" ? fr(text) : text.map(r => ({ ...r, text: fr(r.text) }));
  s.addText(text, { isTextBox: true, fontFace: FONT, color: K.noir, fontSize: 14, margin: 0, valign: "top", paraSpaceAfter: 6, ...o });
}
function puces(s, items, o) {
  const runs = items.map((it, i) => {
    const arr = Array.isArray(it) ? it : [it];
    return { text: arr[0], options: { bullet: { code: "2014" }, breakLine: i < items.length - 1, ...(arr[1] || {}) } };
  });
  t(s, runs, { paraSpaceAfter: 8, ...o });
}
function legende(s, text, x, y, w) {
  t(s, text, { x, y, w, h: 0.5, fontSize: 11, color: K.gris, italic: true });
}
function nouvelle(titre, section) {
  const s = pres.addSlide({ masterName: "CONTENU", sectionTitle: section });
  s.addText(fr(titre), { placeholder: "titre" });
  return s;
}
function eyebrow(s, text, x, y, w) {
  t(s, text.toUpperCase(), { x, y, w: w || 8, h: 0.3, fontSize: 11, bold: true, color: K.vert, charSpacing: 1 });
}
function chiffre(s, valeur, libelle, x, y, w) {
  t(s, valeur, { x, y, w, h: 0.75, fontSize: 40, bold: true, color: K.vert });
  t(s, libelle, { x, y: y + 0.8, w, h: 0.6, fontSize: 13, color: K.gris });
}

// ---------------------------------------------------------------- 1. couverture
pres.addSection({ title: "Présentation" });
{
  const s = pres.addSlide({ masterName: "COUVERTURE", sectionTitle: "Présentation" });
  img(s, "P1", 6.3, 0.5, W - 6.9, H - 1.6, "c", "Perspective depuis l’entrée");
  t(s, "Café-bibliothèque Nandjui", { x: 0.6, y: 3.2, w: 5.4, h: 1.6, fontSize: 40, bold: true, color: K.gris });
  t(s, "Esquisse d’aménagement intérieur et de terrasse", { x: 0.6, y: 4.95, w: 5.4, h: 0.9, fontSize: 18, color: K.vert });
  t(s, `Dossier de présentation à Madame Nandjui`, { x: 0.6, y: 5.9, w: 5.4, h: 0.5, fontSize: 14, color: K.noir });
  t(s, `Abidjan${N}·${N}16 octobre 2026${N}·${N}V8 indice B`, { x: 0.6, y: H - 1.4, w: 5.4, h: 0.4, fontSize: 11, color: K.gris });
  t(s, "Document d’esquisse : cotes à confirmer par un relevé, études techniques de principe.", { x: 0.6, y: H - 1.0, w: 5.4, h: 0.4, fontSize: 10, color: K.gris, italic: true });
}

// ---------------------------------------------------------------- 2. le projet en bref
{
  const s = nouvelle("Un cocon mid-century, ouvert sur une terrasse du soir", "Présentation");
  eyebrow(s, "Le projet en bref", 0.6, 1.45);
  t(s, [
    { text: "Madame Nandjui ouvre sa bibliothèque personnelle au quartier. ", options: { bold: true } },
    { text: "On vient y lire, y travailler et y prendre un café. Le soir, la terrasse couverte accueille la musique et la famille, sous une lumière tamisée." },
  ], { x: 0.6, y: 1.9, w: 7.2, h: 1.5, fontSize: 17 });
  puces(s, [
    "Un seul volume ouvert : l’accueil-café à gauche, la bibliothèque à droite, sans cloison.",
    `Une salle de réunion vitrée à louer, 9${N}places, avec son propre WC.`,
    "Le mur de la collection, une bibliothèque « Kente » du sol au plafond.",
    "Une palette mid-century : noyer, velours cognac et olive, laiton, crème.",
    "Dehors, des assises basses sous une pergola, dont les chaises d’Issa Diabaté.",
  ], { x: 0.6, y: 3.6, w: 7.2, h: 3.6, fontSize: 14 });
  const xs = [0.6, 3.1, 5.6];
  chiffre(s, `49,2${N}m²`, "intérieur (profondeur estimée)", xs[0], 7.5, 2.4);
  chiffre(s, `≈${N}50${N}m²`, "terrasse proposée, 42 m² sous pergola", xs[1], 7.5, 2.4);
  chiffre(s, "9", "places en salle de réunion", xs[2], 7.5, 2.4);
  chiffre(s, "6", "places de travail (table, poteau) + abattants", xs[0], 9.0, 2.4);
  chiffre(s, "4", "fauteuils de lecture au salon", xs[1], 9.0, 2.4);
  chiffre(s, "2", "WC : un pour la salle louée, un public", xs[2], 9.0, 2.4);
  { const o = img(s, "P3", 8.4, 1.45, W - 9.0, 8.9, "t", "La terrasse sous pergola");
    legende(s, "La terrasse-salon depuis le portillon. Perspective calculée depuis la maquette IFC.", o.x, o.y + o.h + 0.12, Math.max(o.w, 6)); }
}

// ---------------------------------------------------------------- 3. le site
{
  const s = nouvelle("Le lieu aujourd’hui", "Présentation");
  const ph = [["photo_facade", "La façade, le muret à grille et le parvis dallé."], ["photo_salle", "La grande salle : profonde, une seule baie haute au fond."],
              ["photo_bleue", "La pièce bleue, future salle de réunion, et son volume haut."], ["photo_arbre", "Au-delà du muret : dallage, pelouse et grand arbre."]];
  ph.forEach(([k, l], i) => {
    const x = 0.6 + i * 3.9;
    { const o = img(s, k, x, 1.5, 3.7, 2.8, "t", l);
      legende(s, l, o.x, o.y + o.h + 0.12, 3.7); }
  });
  eyebrow(s, "Ce que l’équipe retient", 0.6, 5.4);
  puces(s, [
    "Un rez-de-chaussée d’immeuble habité : les logements au-dessus imposent une musique douce le soir.",
    "Un ancien local de restauration, aux réseaux vétustes (fils nus, appareillage en applique) : tout est refait.",
    "Deux bandes parallèles : 3,00 m à gauche, 3,60 m à droite, séparées par un mur et marquées par un poteau de 90 × 90 cm.",
    "Un parvis de 2,75 m clos par un muret ; au-delà, un espace qui semble commun à la résidence.",
  ], { x: 0.6, y: 5.85, w: 9.2, h: 4.2 });
  eyebrow(s, "Ce qui reste à confirmer", 10.4, 5.4, 5.5);
  puces(s, [
    "La profondeur totale (estimée à 7,60 m).",
    "Le caractère porteur du mur à démolir.",
    "Le statut de l’espace devant le muret.",
    "La hauteur sous plafond et les réseaux existants.",
  ], { x: 10.4, y: 5.85, w: 5.5, h: 4.2, color: K.gris });
}

// ---------------------------------------------------------------- 4. relevé et cotes
{
  const s = nouvelle("Le relevé et les cotes retenues", "Présentation");
  { const o = img(s, "releve", 0.6, 1.4, 4.6, 9.0, "t", "Croquis de relevé du 14 octobre");
    legende(s, "Croquis de relevé du 14 octobre, tourné façade en bas.", o.x, o.y + o.h + 0.12, 4.6); }
  const rows = [
    ["ÉLÉMENT", "VALEUR", "STATUT"].map(v => ({ text: v.normalize("NFD").replace(/[̀-ͯ]/g, ""), options: { bold: true, color: K.blanc, fill: { color: K.entete } } })),
    ["Bande gauche (accueil, réunion, WC)", "3,00 m", "Mesuré"], ["Grande salle (bibliothèque)", "3,60 m", "Mesuré"],
    ["Mur de séparation", "0,15 m", "Estimé"], ["Largeur intérieure", "6,75 m", "Calculé"],
    ["Façade → face avant du poteau", "3,30 m", "Mesuré"], ["Poteau", "0,90 × 0,90 m", "Mesuré"],
    ["Fond → bloc WC", "2,40 m", "Mesuré"], ["Profondeur totale", "7,60 m (7,20 à 8,00)", "Estimé"],
    ["Parvis existant", "2,75 m", "Mesuré"], ["Mesure prise sur la terrasse", "5,50 m", "À rattacher"],
  ].map((r, i) => i === 0 ? r : r.map((v, j) => ({ text: v, options: { color: j === 2 && ["Estimé", "À rattacher"].includes(v) ? K.rouge : K.noir, bold: j === 2 && ["Estimé", "À rattacher"].includes(v) } })));
  s.addTable(rows, { x: 5.8, y: 1.5, w: 10.1, colW: [4.9, 3.0, 2.2], fontFace: FONT, fontSize: 13, border: { type: "solid", pt: 0.5, color: "BFBFBF" },
                     rowH: 0.48, valign: "middle" });
  eyebrow(s, "Comment la profondeur a été estimée", 5.8, 7.1);
  t(s, `Sur le croquis, le poteau à 3,30${N}m tombe à 46${N}% de la profondeur dessinée (≈${N}7,2${N}m) et le bloc WC de 2,40${N}m en occupe 30${N}% (≈${N}8,0${N}m). L’ancienne maquette V7 retenait 7,68${N}m. Les photos confirment une salle longue sans donner de cote fiable. L’esquisse retient 7,60${N}m, à mesurer au laser avant les plans d’exécution.`,
    { x: 5.8, y: 7.55, w: 10.1, h: 2.5, fontSize: 14 });
}

// ---------------------------------------------------------------- 5. parti
{
  const s = nouvelle("Le parti : le salon de Madame, un cocon mid-century", "Présentation");
  { const o = img(s, "A1", 0.6, 1.4, 9.8, 6.3, "t", "Croquis A1, le cocon mid-century");
    legende(s, "Croquis A1 de Dizzy : entrer dans le cocon.", o.x, o.y + o.h + 0.12, Math.max(o.w, 6)); }
  eyebrow(s, "Le geste fondateur", 10.9, 1.45, 5);
  t(s, "« Et si l’on entrait dans la bibliothèque de Madame Nandjui comme on entre chez elle ? »", { x: 10.9, y: 1.9, w: 5.0, h: 1.6, fontSize: 18, italic: true, color: K.gris });
  puces(s, [
    "Un intérieur années 50-70 : bois chaud, velours, laiton, lumière basse.",
    "Tout est refait ; la peinture bleue disparaît.",
    "Le mur entre la pièce bleue et la grande salle tombe : la salle de réunion se ferme en baies vitrées.",
    "La terrasse prolonge le salon : assises basses sous une pergola, pas de grande table.",
  ], { x: 10.9, y: 3.7, w: 5.0, h: 4.6, fontSize: 14 });
  eyebrow(s, "La palette", 0.6, 8.4);
  [["noyer", "Noyer"], ["cognac", "Velours cognac"], ["olive", "Velours olive"], ["moutarde", "Moutarde"], ["laiton", "Laiton"], ["creme", "Crème"]].forEach(([c, l], i) => {
    const x = 0.6 + i * 2.55;
    s.addShape(pres.shapes.OVAL, { x, y: 8.9, w: 0.75, h: 0.75, fill: { color: K[c] }, line: { color: "BFBFBF", width: 0.5 }, objectName: "teinte " + l });
    t(s, l, { x: x + 0.9, y: 9.12, w: 1.6, h: 0.4, fontSize: 12, color: K.gris });
  });
  t(s, "Direction B « Sous le badamier » (modernisme tropical) étudiée et non retenue ; son claustra en dos de livres reste une option.", { x: 0.6, y: 10.0, w: 15.3, h: 0.4, fontSize: 11, color: K.gris, italic: true });
}

// ---------------------------------------------------------------- 6. plan
pres.addSection({ title: "Aménagement" });
{
  const s = nouvelle("Plan d’aménagement", "Aménagement");
  img(s, "E01", 0.6, 1.3, 11.4, 9.5, "lt", "Plan d’aménagement E01");
  eyebrow(s, "À retenir", 12.3, 1.45, 3.6);
  puces(s, [
    `Une seule grande porte de 1,60${N}m ; l’ancienne porte devient vitrine.`,
    "Accueil ouvert à gauche, meuble « Secrétaire » face aux livres.",
    `Salle de réunion de 8,4${N}m², 9${N}places, table « Pirogue ».`,
    "Deux WC au nord : l’un ouvre sur la salle louée, l’autre sur la bibliothèque.",
    "Bibliothèque « Kente » sur trois murs, échelle laiton.",
    "Table d’hôtes, « Arbre à travail » au poteau, salon de lecture au fond.",
    "Terrasse prolongée, pergola, chaises ÖVERALLT.",
  ], { x: 12.3, y: 1.9, w: 3.65, h: 8.6, fontSize: 13 });
}
{
  const s = nouvelle("Le volume, coupé à 2,60 m", "Aménagement");
  { const o = img(s, "V01", 0.6, 1.3, 15.3, 8.9, "t", "Axonométrie coupée");
    legende(s, "Axonométrie calculée depuis la maquette IFC4. Le mur à démolir apparaît en orange transparent. Rendu de contrôle, sans textures.", o.x, o.y + o.h + 0.12, Math.max(o.w, 6)); }
}
{
  const s = nouvelle("En entrant", "Aménagement");
  { const o = img(s, "P1", 0.6, 1.3, 15.3, 9.0, "t", "Perspective depuis l’entrée");
    legende(s, "La bibliothèque « Kente », la table d’hôtes, l’« Arbre à travail » et le salon au fond ; à gauche, la salle de réunion vitrée. Perspective calculée depuis la maquette, sans textures.", o.x, o.y + o.h + 0.12, Math.max(o.w, 6)); }
}
{
  const s = nouvelle("Depuis le salon de lecture", "Aménagement");
  img(s, "P2", 0.6, 1.3, 10.6, 9.0, "lt", "Perspective depuis le salon");
  eyebrow(s, "La salle de réunion", 11.6, 1.45, 4.3);
  puces(s, [
    "Baies vitrées sur deux faces, rideaux en lin pour l’intimité.",
    `9${N}places : banquette de 5 le long de la baie, 4 chaises en face.`,
    `Circulation de 0,90${N}m vers la porte et le WC réunion.`,
    `Sans table, environ 12${N}chaises pour une présentation.`,
  ], { x: 11.6, y: 1.9, w: 4.3, h: 6, fontSize: 13 });
}
{
  const s = nouvelle("La terrasse-salon sous pergola", "Aménagement");
  img(s, "A2", 0.6, 1.3, 7.6, 5.0, "lt", "Croquis A2");
  { const o = img(s, "V02", 8.5, 1.3, 7.4, 5.0, "t", "Axonométrie depuis la terrasse");
    legende(s, "Croquis A2 de Dizzy et vue calculée depuis la maquette.", o.x, o.y + o.h + 0.12, Math.max(o.w, 6)); }
  puces(s, [
    `Terrasse prolongée d’environ 2,65${N}m au-delà du muret actuel, close par un claustra bas, des jardinières et un portillon.`,
    `Pergola en acier noir et lames de bois sur chant ; globes opalins pour une lumière tamisée.`,
    "Deux salons : banquettes en L, tables basses, chaises ÖVERALLT d’Issa Diabaté et Kevin Gouriou, et tabourets.",
    "Les lames ajourées ne protègent pas de la pluie : une couverture translucide est à décider.",
    "L’emprise au-delà du muret doit être autorisée par écrit avant tout chiffrage.",
  ], { x: 0.6, y: 7.0, w: 15.3, h: 3.4, fontSize: 14 });
}

// ---------------------------------------------------------------- mobilier
// Toutes les variantes sont présentées, une page chacune : la cliente choisit sur un large éventail.
pres.addSection({ title: "Mobilier" });
const VAR = JSON.parse(fs.readFileSync(path.join(RACINE, "v8", "mobilier", "variantes.json"), "utf8"));
const FAMILLES = {
  V1_bibliotheque: ["La bibliothèque", "M02_bibliotheque_kente"],
  V2_accueil: ["Le meuble d’accueil", "M01_accueil_secretaire"],
  V3_table_reunion: ["La table de réunion", "M03_banquette_table_pirogue"],
  V4_postes_travail: ["Les postes de travail", "M08_poste_arbre_a_travail"],
};
{
  const s = nouvelle("Le mobilier : douze modèles au choix", "Mobilier");
  t(s, "Pour chaque meuble, trois modèles sont dessinés. L’équipe en recommande un, mais tous sont réalisables à Abidjan par un ébéniste, un tapissier et un métallier : Madame Nandjui choisit, et peut combiner des idées d’un modèle à l’autre.",
    { x: 0.6, y: 1.45, w: 15.3, h: 1.0, fontSize: 16 });
  VAR.forEach((f, r) => {
    const y = 2.75 + r * 1.95;
    t(s, FAMILLES[f.fichier][0], { x: 0.6, y: y + 0.6, w: 3.0, h: 0.6, fontSize: 15, bold: true, color: K.gris });
    f.variantes.forEach((v, c) => {
      const x = 3.8 + c * 4.05;
      img(s, v.cle, x, y, 1.9, 1.5, "c", v.nom);
      t(s, v.nom.replace(" · ", " "), { x: x + 2.0, y: y + 0.45, w: 2.0, h: 0.5, fontSize: 12, bold: v.recommande, color: K.noir });
      if (v.recommande) t(s, "recommandé", { x: x + 2.0, y: y + 0.9, w: 2.0, h: 0.3, fontSize: 10, italic: true, color: K.vert });
    });
  });
}
VAR.forEach(f => {
  const [famille, fiche] = FAMILLES[f.fichier];
  const s = nouvelle(famille + " : trois propositions", "Mobilier");
  img(s, f.fichier, 0.6, 1.3, 15.3, 9.1, "c", "Planche de variantes : " + famille);
  f.variantes.forEach(v => {
    const nom = v.nom.replace(/^[ABC] · /, "");
    const lettre = v.nom[0];
    const s = nouvelle(`${famille}, modèle ${lettre} ${nom}`, "Mobilier");
    img(s, v.cle, 0.6, 1.3, 9.8, 8.9, "c", nom);
    let y = 1.45;
    if (v.recommande) {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.9, y, w: 2.4, h: 0.42, rectRadius: 0.08, fill: { color: K.vert }, line: { color: K.vert }, objectName: "recommandé" });
      t(s, "RECOMMANDE PAR L’EQUIPE", { x: 10.9, y: y + 0.09, w: 2.4, h: 0.3, fontSize: 9, bold: true, color: K.blanc, align: "center" });
      y += 0.7;
    }
    t(s, v.idee, { x: 10.9, y, w: 5.0, h: 2.3, fontSize: 14 });
    eyebrow(s, "Pour", 10.9, y + 2.4, 5);
    puces(s, v.pour, { x: 10.9, y: y + 2.8, w: 5.0, h: 1.8, fontSize: 13 });
    eyebrow(s, "Contre", 10.9, y + 4.75, 5);
    puces(s, v.contre, { x: 10.9, y: y + 5.15, w: 5.0, h: 1.6, fontSize: 13, color: K.gris });
  });
  const s2 = nouvelle("Le modèle recommandé en détail : " + famille.toLowerCase(), "Mobilier");
  img(s2, fiche, 0.6, 1.3, 15.3, 8.9, "t", "Fiche " + famille);
  t(s2, f.reco, { x: 0.6, y: 10.35, w: 15.3, h: 0.5, fontSize: 12, color: K.gris, italic: true });
});
[["M04_fauteuil_lecture", "Les assises : le fauteuil de lecture « Madame »", "Pour le salon de lecture : quatre fauteuils bas, noyer et velours cognac ou olive."],
 ["M05_chaise", "Les assises : la chaise de table d’hôtes et de réunion", "La même chaise sert à la table d’hôtes et en salle de réunion."],
 ["M06_fauteuil_terrasse", "Les assises : le fauteuil bas de terrasse (variante)", "Variante dessinée par l’équipe pour la terrasse, si les chaises ÖVERALLT ne peuvent pas être fabriquées."],
 ["M07_chaise_overallt_issa_diabate", "Les assises : la chaise ÖVERALLT d’Issa Diabaté", "La chaise ÖVERALLT (Issa Diabaté et Kevin Gouriou, IKEA 2019) est une œuvre protégée par le droit d’auteur. Elle est figurée ici par son volume ; sa fabrication à Abidjan demande l’accord de ses auteurs et d’IKEA."],
].forEach(([k, titre, texte]) => {
  const s = nouvelle(titre, "Mobilier");
  const o = img(s, k, 0.6, 1.3, 15.3, 8.9, "t", titre);
  t(s, texte, { x: o.x, y: o.y + o.h + 0.12, w: 15.3, h: 0.5, fontSize: 12, color: K.gris, italic: true });
});

// ---------------------------------------------------------------- technique
pres.addSection({ title: "Technique" });
[["T01", "Électricité et éclairage tamisé", [
    "Installation entièrement neuve, tableau près de l’entrée.",
    "Trois scènes : jour, soir tamisé (≈ 30 %), fermeture.",
    `Lumière 2${N}700${N}K gradable ; ≈${N}300${N}lux sur les tables.`,
    `≈${N}12${N}kW installés, ≈${N}8,5${N}kW foisonnés : abonnement à voir avec la CIE.`]],
 ["T02", "Plomberie", [
    "Les deux WC partagent une évacuation au fond.",
    `L’évier du café, à 6,3${N}m de la chute, passe par une pompe de relevage.`,
    "Évier, pompe et chauffe-eau seulement si l’on prépare et lave sur place."]],
 ["T03", "Climatisation et ventilation", [
    `Trois climatiseurs muraux (≈${N}11,5${N}kW de froid).`,
    "Extraction mécanique des WC ; brasseurs d’air sous la pergola.",
    "Groupes extérieurs proposés sur le mur nord : accès, bruit et accord de la copropriété à valider."]],
].forEach(([k, titre, items]) => {
  const s = nouvelle(titre, "Technique");
  img(s, k, 0.6, 1.3, 10.6, 9.3, "lt", "Plan " + k);
  eyebrow(s, "Principes", 11.6, 1.45, 4.3);
  puces(s, items, { x: 11.6, y: 1.9, w: 4.3, h: 7, fontSize: 14 });
  t(s, "Schéma de principe à faire valider par un bureau d’études et les concessionnaires.", { x: 11.6, y: 9.6, w: 4.3, h: 0.8, fontSize: 11, italic: true, color: K.gris });
});

// ---------------------------------------------------------------- suite
pres.addSection({ title: "Suite" });
{
  const s = nouvelle("Avant de chiffrer et de construire", "Suite");
  eyebrow(s, "Points à valider", 0.6, 1.45);
  puces(s, [
    [`Mur à démolir : avis d’un ingénieur structure (immeuble habité au-dessus). S’il est porteur, une poutre de reprise d’environ 5${N}m reste possible.`, { color: K.noir }],
    "Copropriété : accord pour la démolition, la terrasse prolongée, la pergola fixée en façade et les groupes de climatisation.",
    "Relevé au laser : profondeur, façade d’angle à angle, hauteurs, réseaux et descentes existants.",
    "Réglementation locale : accueil du public, sens d’ouverture de la porte, accessibilité du seuil et du WC, licence de boissons, bruit du soir.",
    "Exploitation du café : évier, pompe et chauffe-eau seulement si l’on prépare et lave sur place.",
    "Chaises ÖVERALLT : œuvre protégée par le droit d’auteur ; accord d’Issa Diabaté, de Kevin Gouriou et d’IKEA avant toute fabrication locale.",
  ], { x: 0.6, y: 1.9, w: 7.6, h: 8.5, fontSize: 14 });
  eyebrow(s, "Prochaines étapes", 8.9, 1.45, 7);
  const etapes = [["1", "Validation de l’esquisse par Madame Nandjui", "plan E01, mobilier, terrasse"],
                  ["2", "Relevé et diagnostic structure", "laser, sondage du mur, réseaux"],
                  ["3", "Avant-projet", "plans cotés, détails du mobilier, maquette recalée"],
                  ["4", "Consultation des artisans", "ébéniste, tapissier, métallier, électricien, plombier"],
                  ["5", "Prototypes", "fauteuil, chaise, rideau à lattes, échelle"],
                  ["6", "Travaux et installation", "après autorisations"]];
  etapes.forEach(([n, a, b], i) => {
    const y = 1.95 + i * 1.38;
    s.addShape(pres.shapes.OVAL, { x: 8.9, y, w: 0.62, h: 0.62, fill: { color: K.vert }, line: { color: K.vert }, objectName: "étape " + n });
    t(s, n, { x: 8.9, y: y + 0.12, w: 0.62, h: 0.4, fontSize: 15, bold: true, color: K.blanc, align: "center" });
    t(s, a, { x: 9.75, y: y + 0.02, w: 6.2, h: 0.4, fontSize: 15, bold: true, color: K.gris });
    t(s, b, { x: 9.75, y: y + 0.5, w: 6.2, h: 0.4, fontSize: 13, color: K.noir });
  });
}
{
  const s = nouvelle("Méthode, maquette et sources", "Suite");
  eyebrow(s, "Une seule géométrie pour tout le dossier", 0.6, 1.45, 7.4);
  puces(s, [
    "Plans, coupes, vues 3D, perspectives et fiches mobilier sont calculés depuis les mêmes scripts.",
    `Maquette NANDJUI_ESQ_V8.ifc (IFC4) : 0${N}erreur à la validation, 112${N}objets géométriques, statut de chaque objet (mesuré, estimé, proposé, à démolir).`,
    "Ouverture dans Revit non testée ; objets en volumes simples, pas en familles natives.",
    "Les vues sont des rendus de maquette sans textures ni éclairage réaliste ; les croquis sont des dessins de principe.",
  ], { x: 0.6, y: 1.9, w: 7.4, h: 5, fontSize: 13 });
  eyebrow(s, "L’équipe architecturale (rôles IA)", 8.6, 1.45, 7.3);
  puces(s, [
    "Guillaume (G-K) : coordination.  Dizzy : direction artistique.",
    "Désiré Akai : aménagement et mobilier.  Manadja : maquette et contrôle DAO.",
    "Le Génie : études techniques.  Fabrice Sawegnon : dossier.  Josiane : relecture.",
  ], { x: 8.6, y: 1.9, w: 7.3, h: 2.2, fontSize: 13 });
  t(s, "Ces noms désignent des rôles de travail d’une IA, pas des personnes ; ils ne remplacent ni un architecte inscrit à l’Ordre, ni un bureau d’études agréé, ni les autorisations administratives.", { x: 8.6, y: 4.2, w: 7.3, h: 0.9, fontSize: 11, color: K.gris, italic: true });
  eyebrow(s, "Références mobilier consultées le 16 octobre 2026", 8.6, 5.4, 7.3);
  t(s, "Pierre Jeanneret (Vitra Design Museum, Merit) · Sergio Rodrigues (Metropolitan Museum of Art) · Charlotte Perriand (Cassina, Phillips) · Hans J. Wegner (Skandium) · George Nakashima (Baltimore Museum of Art) · Cheick Diallo (InCollect) · Jean Servais Somian (Forbes Afrique) · Issa Diabaté et IKEA ÖVERALLT (Dezeen, Domus, Chairish) · Pieter Peulen (Gubi). Liste complète et liens : v8/mobilier/REFERENCES.csv.",
    { x: 8.6, y: 5.85, w: 7.3, h: 3, fontSize: 12, color: K.noir });
}

pres.writeFile({ fileName: SORTIE }).then(() => console.log(SORTIE));
