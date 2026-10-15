"""Validation d'un IFC : ifcopenshell.validate (schéma + règles EXPRESS) et génération de la
géométrie de chaque produit porteur d'une représentation.

Usage : python3 v5/scripts/valider_ifc.py FICHIER.ifc [rapport.txt]
Code retour 0 si 0 erreur de schéma et 0 échec géométrique.
"""
import sys, collections, logging
import ifcopenshell, ifcopenshell.validate, ifcopenshell.geom


def valider(path):
    f = ifcopenshell.open(path)
    log = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, log, express_rules=True)
    errors = [s for s in log.statements if s.get("level", "error") == "error"]
    warns = [s for s in log.statements if s.get("level") == "warning"]

    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", True)
    prods = [p for p in f.by_type("IfcProduct") if p.Representation is not None]
    ok, ko = 0, []
    for p in prods:
        reps = p.Representation.Representations
        rep = next((r for r in reps if r.RepresentationIdentifier == "Body"), reps[0])
        try:
            sh = ifcopenshell.geom.create_shape(s, p, rep)
            if len(sh.geometry.faces) == 0:
                ko.append((p, "maillage vide"))
            else:
                ok += 1
        except Exception as e:  # noqa
            ko.append((p, str(e)[:80]))

    lines = [f"Fichier : {path}", f"Schéma : {f.schema}", f"Entités : {len(list(f))}",
             f"ifcopenshell {ifcopenshell.version}",
             "", "== ifcopenshell.validate (schéma + règles EXPRESS) ==",
             f"Erreurs : {len(errors)}", f"Avertissements : {len(warns)}"]
    for k, n in collections.Counter(e["message"][:100] for e in errors).most_common(20):
        lines.append(f"  {n} x {k}")
    for e in errors[:20]:
        lines.append(f"  - {str(e.get('instance'))[:140]} : {e['message'][:120]}")
    lines += ["", "== Géométrie (ifcopenshell.geom, tous les IfcProduct avec représentation) ==",
              f"Produits avec représentation : {len(prods)}", f"Géométrie OK : {ok}", f"Échecs : {len(ko)}"]
    for p, why in ko:
        lines.append(f"  - #{p.id()} {p.is_a()} {p.Name} : {why}")
    cnt = collections.Counter(p.is_a() for p in prods)
    lines += ["", "Répartition : " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items()))]
    return "\n".join(lines), len(errors) == 0 and not ko


if __name__ == "__main__":
    logging.disable(logging.WARNING)
    txt, good = valider(sys.argv[1])
    print(txt)
    if len(sys.argv) > 2:
        open(sys.argv[2], "w", encoding="utf-8").write(txt + "\n")
    sys.exit(0 if good else 1)
