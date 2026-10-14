import sys, logging, collections
import ifcopenshell, ifcopenshell.validate, ifcopenshell.geom, ifcopenshell.util.element as ue
import numpy as np
f = ifcopenshell.open(sys.argv[1])
log = logging.getLogger("v"); h = ifcopenshell.validate.json_logger(); 
ifcopenshell.validate.validate(f, h, express_rules=False)
st = collections.Counter(s.get("message","")[:90] for s in h.statements)
print("validation:", len(h.statements), "problèmes"); [print("  ", n, m) for m, n in st.most_common(12)]
for d in f.by_type("IfcDoor"):
    print("porte", d.Name, "| baie:", [r.RelatingOpeningElement.Name for r in d.FillsVoids],
          "| hôte:", [r.RelatingOpeningElement.VoidsElements[0].RelatingBuildingElement.Name for r in d.FillsVoids])
for o in f.by_type("IfcOpeningElement"):
    print("baie", o.Name, "->", [r.RelatingBuildingElement.Name for r in o.VoidsElements], "| remplie:", bool(o.HasFillings))
s = ifcopenshell.geom.settings(); s.set("use-world-coords", True)
it = ifcopenshell.geom.iterator(s, f); it.initialize(); n = 0; bad = []
seen = set()
while True:
    sh = it.get(); seen.add(sh.id); n += 1
    if not it.next(): break
prods = [p for p in f.by_type("IfcProduct") if p.Representation and not p.is_a("IfcOpeningElement")]
missing = [p.Name for p in prods if p.id() not in seen]
print("géométries calculées:", n, "| sans géométrie:", missing)
print("orphelins (sans conteneur):", [p.Name for p in f.by_type("IfcElement") if not p.is_a("IfcOpeningElement") and ue.get_container(p) is None])
print("projet:", f.by_type("IfcProject")[0].Name)
