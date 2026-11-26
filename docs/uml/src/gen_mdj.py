"""Generate a StarUML (.mdj) Use Case model from uc_model.py.

View objects are cloned from a real StarUML file (sample.mdj) so that every
compartment/label StarUML expects is present; ids are regenerated and all
references are remapped.
"""
import base64, copy, json, math, os, sys
from uc_model import *

SX = 1.35  # horizontal stretch: StarUML ellipses do not wrap text


def X(x):
    return SUBJECT["x0"] + (x - SUBJECT["x0"]) * SX if x >= SUBJECT["x0"] else x


_counter = [0]


def nid():
    _counter[0] += 1
    raw = b"CWBK" + _counter[0].to_bytes(8, "big") + os.urandom(0)
    return base64.b64encode(raw.ljust(12, b"\0")).decode()


sample = json.load(open("sample.mdj"))
smodel = sample["ownedElements"][1]
sdiag = smodel["ownedElements"][0]
TPL = {}
for v in sdiag["ownedViews"]:
    TPL.setdefault(v["_type"], v)


def all_refs(o, fn):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if isinstance(v, dict) and set(v) == {"$ref"}:
                o[k] = {"$ref": fn(v["$ref"])}
            else:
                all_refs(v, fn)
    elif isinstance(o, list):
        for x in o:
            all_refs(x, fn)


def clone_view(tpl_type, parent_id, model_map, head=None, tail=None):
    v = copy.deepcopy(TPL[tpl_type])
    idmap = {}

    def reid(o):
        if isinstance(o, dict):
            if "_id" in o:
                idmap[o["_id"]] = nid()
                o["_id"] = idmap[o["_id"]]
            for x in o.values():
                reid(x)
        elif isinstance(o, list):
            for x in o:
                reid(x)

    old_root = v["_id"]
    old_head = v.get("head", {}).get("$ref")
    old_tail = v.get("tail", {}).get("$ref")
    reid(v)

    def fn(r):
        if r == old_head and head:
            return head
        if r == old_tail and tail:
            return tail
        if r in idmap:
            return idmap[r]
        if r in model_map:
            return model_map[r]
        return parent_id  # diagram parent
    all_refs(v, fn)
    v["_parent"] = {"$ref": parent_id}
    return v


def name_label(view):
    comp = view["subViews"][0]
    return next(l for l in comp["subViews"] if l.get("font") == "Arial;13;1")


def text_w(s):
    return 7.4 * len(s) + 10


project = {"_type": "Project", "_id": nid(), "name": "CoWork Booking System", "ownedElements": []}
model = {"_type": "UMLModel", "_id": nid(), "_parent": {"$ref": project["_id"]}, "name": "Use Case Model", "ownedElements": []}
project["ownedElements"].append(model)
diag = {"_type": "UMLUseCaseDiagram", "_id": nid(), "_parent": {"$ref": model["_id"]},
        "name": "Use Case — CoWork Booking System", "defaultDiagram": True, "ownedViews": []}
model["ownedElements"].append(diag)
D = diag["_id"]

elem, view = {}, {}

# subject (system boundary)
subj = {"_type": "UMLUseCaseSubject", "_id": nid(), "_parent": {"$ref": model["_id"]}, "name": SUBJECT["name"]}
model["ownedElements"].append(subj)
tpl = TPL["UMLUseCaseSubjectView"]
sv = clone_view("UMLUseCaseSubjectView", D, {tpl["model"]["$ref"]: subj["_id"]})
L, T = SUBJECT["x0"], SUBJECT["y0"]
Wd = X(SUBJECT["x1"]) - L + 60
Ht = SUBJECT["y1"] - T
sv.update(left=L, top=T, width=Wd, height=Ht)
nc = sv["subViews"][0]
nc.update(left=L, top=T, width=Wd, height=25)
nl = name_label(sv)
nl.update(text=SUBJECT["name"], left=L + 5, top=T + 7, width=Wd - 10)
diag["ownedViews"].append(sv)

for k, (label, cx, cy) in ACTORS.items():
    e = {"_type": "UMLActor", "_id": nid(), "_parent": {"$ref": model["_id"]}, "name": label, "ownedElements": []}
    model["ownedElements"].append(e)
    elem[k] = e
    tpl = TPL["UMLActorView"]
    v = clone_view("UMLActorView", D, {tpl["model"]["$ref"]: e["_id"]})
    cx = X(cx) + (60 if cx > SUBJECT["x1"] else 0)
    w = max(40, text_w(label))
    v.update(left=cx - w / 2, top=cy - 45, width=w, height=80)
    nc = v["subViews"][0]
    nc.update(left=cx - w / 2, top=cy + 40, width=w, height=25)
    name_label(v).update(text=label, left=cx - w / 2 + 5, top=cy + 47, width=w - 10)
    view[k] = v
    diag["ownedViews"].append(v)

for k, (label, cx, cy) in USE_CASES.items():
    e = {"_type": "UMLUseCase", "_id": nid(), "_parent": {"$ref": model["_id"]}, "name": label, "ownedElements": []}
    model["ownedElements"].append(e)
    elem[k] = e
    tpl = TPL["UMLUseCaseView"]
    v = clone_view("UMLUseCaseView", D, {tpl["model"]["$ref"]: e["_id"]})
    cx = X(cx)
    w, h = text_w(label) + 30, 45
    v.update(left=cx - w / 2, top=cy - h / 2, width=w, height=h)
    nc = v["subViews"][0]
    nc.update(left=cx - w / 2 + 15, top=cy - 12, width=w - 30, height=25)
    name_label(v).update(text=label, left=cx - w / 2 + 20, top=cy - 6, width=w - 40)
    view[k] = v
    diag["ownedViews"].append(v)


def centre(k):
    v = view[k]
    return v["left"] + v["width"] / 2, v["top"] + v["height"] / 2


def border(k, tx, ty):
    v = view[k]
    cx, cy = centre(k)
    a, b = v["width"] / 2, v["height"] / 2
    dx, dy = tx - cx, ty - cy
    if k in ACTORS:
        return cx + (a if dx > 0 else -a) * 0.6, cy - 5
    t = 1 / math.sqrt(dx * dx / (a * a) + dy * dy / (b * b))
    return cx + dx * t, cy + dy * t


def pts(tail_k, head_k):
    (tx, ty), (hx, hy) = centre(tail_k), centre(head_k)
    p1, p2 = border(tail_k, hx, hy), border(head_k, tx, ty)
    return f"{p1[0]:.0f}:{p1[1]:.0f};{p2[0]:.0f}:{p2[1]:.0f}"


# associations: owned by actor (end1 = actor, end2 = use case)
atpl = TPL["UMLAssociationView"]
amodel_old = atpl["model"]["$ref"]
old_end_ids = sorted({sv_["model"]["$ref"] for sv_ in atpl["subViews"]} - {amodel_old})
for a, u in ASSOCIATIONS:
    as_ = {"_type": "UMLAssociation", "_id": nid(), "_parent": {"$ref": elem[a]["_id"]}}
    as_["end1"] = {"_type": "UMLAssociationEnd", "_id": nid(), "_parent": {"$ref": as_["_id"]},
                   "reference": {"$ref": elem[a]["_id"]}, "navigable": False}
    as_["end2"] = {"_type": "UMLAssociationEnd", "_id": nid(), "_parent": {"$ref": as_["_id"]},
                   "reference": {"$ref": elem[u]["_id"]}}
    elem[a]["ownedElements"].append(as_)
    # in the template, which end id belongs to tail (actor) / head (use case)
    tail_end = next(s["model"]["$ref"] for s in atpl["subViews"] if s.get("edgePosition") == 2 and s["model"]["$ref"] != amodel_old)
    head_end = next(s["model"]["$ref"] for s in atpl["subViews"] if s["model"]["$ref"] not in (amodel_old, tail_end))
    mm = {amodel_old: as_["_id"], tail_end: as_["end1"]["_id"], head_end: as_["end2"]["_id"]}
    v = clone_view("UMLAssociationView", D, mm, head=view[u]["_id"], tail=view[a]["_id"])
    for s in v["subViews"]:
        s.pop("text", None)
    v["points"] = pts(a, u)
    diag["ownedViews"].append(v)


def dep_edge(kind, src, tgt):
    """include/extend: owned by source, view tail=source, head=target."""
    m = {"_type": kind, "_id": nid(), "_parent": {"$ref": elem[src]["_id"]},
         "source": {"$ref": elem[src]["_id"]}, "target": {"$ref": elem[tgt]["_id"]}}
    elem[src]["ownedElements"].append(m)
    tpl = TPL["UMLIncludeView"]
    v = clone_view("UMLIncludeView", D, {tpl["model"]["$ref"]: m["_id"]}, head=view[tgt]["_id"], tail=view[src]["_id"])
    v["_type"] = "UMLIncludeView" if kind == "UMLInclude" else "UMLExtendView"
    for s in v["subViews"]:
        if s.get("text"):
            s["text"] = "«include»" if kind == "UMLInclude" else "«extend»"
    v["points"] = pts(src, tgt)
    diag["ownedViews"].append(v)


for b, i in INCLUDES:
    dep_edge("UMLInclude", b, i)
for e, b in EXTENDS:
    dep_edge("UMLExtend", e, b)

gtpl = TPL["UMLGeneralizationView"]
for c, p in GENERALIZATIONS:
    g = {"_type": "UMLGeneralization", "_id": nid(), "_parent": {"$ref": elem[c]["_id"]},
         "source": {"$ref": elem[c]["_id"]}, "target": {"$ref": elem[p]["_id"]}}
    elem[c]["ownedElements"].append(g)
    v = clone_view("UMLGeneralizationView", D, {gtpl["model"]["$ref"]: g["_id"]}, head=view[p]["_id"], tail=view[c]["_id"])
    (cx, cy), (px, py) = centre(c), centre(p)
    v["points"] = f"{cx:.0f}:{view[c]['top']:.0f};{px:.0f}:{view[p]['top'] + view[p]['height'] + 28:.0f}"
    diag["ownedViews"].append(v)

for e in elem.values():
    if not e["ownedElements"]:
        del e["ownedElements"]

# integrity check: every $ref resolves
ids = set()


def collect(o):
    if isinstance(o, dict):
        if "_id" in o:
            ids.add(o["_id"])
        for x in o.values():
            collect(x)
    elif isinstance(o, list):
        for x in o:
            collect(x)


collect(project)
bad = []
all_refs(copy.deepcopy(project), lambda r: (bad.append(r) if r not in ids else None) or r)
assert not bad, bad[:5]
json.dump(project, open(sys.argv[1], "w"), ensure_ascii=False, indent="\t")
print("ok", len(ids), "objects")
