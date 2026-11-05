# NEON//WRIST ground join: finds GND copper groups not tied to main ground and stitches them in.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/gnd_join.py').read())
import pcbnew, math
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
CX, CY = 150.0, 100.0
gnd = B.FindNet('GND') or B.FindNet('/GND'); G = gnd.GetNetCode()
zones = [z for z in B.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == G]
rules = [z for z in B.Zones() if z.GetIsRuleArea()]
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
filler = pcbnew.ZONE_FILLER(B)
VR, VD, CL = 0.225, 0.2, 0.12
V = lambda x, y: pcbnew.VECTOR2I(mm(x), mm(y))

def islands():
    isl = []  # (layer, poly, idx, area)
    for z in zones:
        L = z.GetLayer(); poly = z.GetFilledPolysList(L)
        for i in range(poly.OutlineCount()):
            isl.append((L, poly, i, abs(poly.Outline(i).Area())))
    return isl
def build():
    isl = islands(); par = list(range(len(isl)))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    def u(a, b): par[f(a)] = f(b)
    def hits(L, p):
        return [k for k, (l, poly, i, a) in enumerate(isl) if l == L and poly.Contains(p, i)]
    for t in B.GetTracks():
        if t.GetNetCode() != G: continue
        if t.GetClass() == 'PCB_VIA':
            h = sum((hits(L, t.GetPosition()) for L in CU), [])
            for k in h[1:]: u(h[0], k)
        else:
            h = hits(t.GetLayer(), t.GetStart()) + hits(t.GetLayer(), t.GetEnd())
            for k in h[1:]: u(h[0], k)
    pads = {}
    for fp in B.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() != G: continue
            h = sum((hits(L, p.GetPosition()) for L in CU if p.IsOnLayer(L)), [])
            for k in h[1:]: u(h[0], k)
    area = {}
    for k in range(len(isl)): r = f(k); area[r] = area.get(r, 0) + isl[k][3]
    main = max(area, key=area.get)
    return isl, f, main

def obstacles():
    segs, boxes = [], []
    for t in B.GetTracks():
        if t.GetNetCode() == G: continue
        if t.GetClass() == 'PCB_VIA':
            p = t.GetPosition(); r = um(t.GetWidth())/2; boxes.append((um(p.x)-r, um(p.y)-r, um(p.x)+r, um(p.y)+r))
        else:
            a, b = t.GetStart(), t.GetEnd(); segs.append((um(a.x), um(a.y), um(b.x), um(b.y), um(t.GetWidth())/2))
    for fp in B.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() != G:
                bb = p.GetBoundingBox(); boxes.append((um(bb.GetLeft()), um(bb.GetTop()), um(bb.GetRight()), um(bb.GetBottom())))
    return segs, boxes
def segdist(px, py, s):
    x1, y1, x2, y2, w = s; dx, dy = x2-x1, y2-y1; L = dx*dx+dy*dy
    u = 0 if L == 0 else max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/L))
    return math.hypot(px-(x1+u*dx), py-(y1+u*dy)) - w
def free(px, py, segs, boxes):
    if math.hypot(px-CX, py-CY) > 19.5: return False
    for z in rules:
        try:
            if z.GetDoNotAllowVias() and z.Outline().Contains(V(px, py)): return False
        except Exception: pass
    for (l, t, r, b) in boxes:
        if px > l-VR-CL and px < r+VR+CL and py > t-VR-CL and py < b+VR+CL: return False
    for s in segs:
        if min(abs(px-s[0]), abs(px-s[2])) < 8 and segdist(px, py, s) < VR+CL: return False
    return True

total = 0; stuck = []
for rnd in range(4):
    isl, f, main = build(); segs, boxes = obstacles()
    mainisl = [k for k in range(len(isl)) if f(k) == main]
    loose = [k for k in range(len(isl)) if f(k) != main]
    if not loose: break
    done_groups = set(); added = 0; stuck = []
    for k in sorted(loose, key=lambda k: -isl[k][3]):
        g = f(k)
        if g in done_groups: continue
        L, poly, i, a = isl[k]; bb = poly.Outline(i).BBox()
        x0, y0, x1, y1 = um(bb.GetLeft()), um(bb.GetTop()), um(bb.GetRight()), um(bb.GetBottom())
        best = None; y = y0
        while y <= y1 and not best:
            x = x0
            while x <= x1:
                p = V(x, y)
                if poly.Contains(p, i) and free(x, y, segs, boxes) and \
                   any(isl[m][0] != L and isl[m][1].Contains(p, isl[m][2]) for m in mainisl):
                    best = (x, y); break
                x += 0.1
            y += 0.1
        if best:
            v = pcbnew.PCB_VIA(B); v.SetPosition(V(*best)); v.SetWidth(mm(2*VR)); v.SetDrill(mm(VD)); v.SetNetCode(G); B.Add(v)
            boxes.append((best[0]-VR, best[1]-VR, best[0]+VR, best[1]+VR)); done_groups.add(g); added += 1
        else:
            stuck.append('%s island near (%.2f, %.2f)' % (B.GetLayerName(L), um(bb.Centre().x), um(bb.Centre().y)))
    total += added
    filler.Fill(B.Zones())
    if not added: break
print('stitching vias added: %d' % total)
for s in stuck: print('could not reach:', s)
try:
    B.BuildConnectivity(); print('unrouted connections left: %d' % B.GetConnectivity().GetUnconnectedCount(False))
except Exception: pass
pcbnew.Refresh(); print('Now: B, Cmd+S, DRC')
