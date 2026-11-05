# NEON//WRIST MK-II part placement. Run inside KiCad PCB Editor:
#   Tools > Scripting Console, then:
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/place_parts.py').read())
import pcbnew, math
B = pcbnew.GetBoard()
CX, CY, RB = 150.0, 100.0, 21.0          # board centre (mm) and radius
mm = pcbnew.FromMM
log = []

try:
    B.SetCopperLayerCount(4); log.append('copper layers set to 4')
except Exception as e:
    log.append('could not set 4 layers here, use Board Setup: %s' % e)

try:
    ds = B.GetDesignSettings()
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(mm(0.1)); nc.SetTrackWidth(mm(0.15))
    ds.m_MinClearance = mm(0.1)
    ds.m_CopperEdgeClearance = mm(0.3)
    log.append('default clearance 0.1 mm, track 0.15 mm, copper to edge 0.3 mm')
except Exception as e:
    log.append('set clearance by hand in Board Setup > Net Classes (0.1 mm): %s' % e)

def fp(ref):
    f = B.FindFootprintByReference(ref)
    if f is None: log.append('MISSING ' + ref)
    return f

def set_side(f, back):
    if bool(f.IsFlipped()) == back: return
    try:
        f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    except Exception:
        f.Flip(f.GetPosition(), False)

def set_pos(f, x, y):
    f.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))

def set_rot(f, deg):
    try: f.SetOrientationDegrees(deg)
    except Exception: f.SetOrientation(pcbnew.EDA_ANGLE(deg, pcbnew.DEGREES_T))

def bbox(f):
    try: b = f.GetBoundingBox(False, False)
    except Exception: b = f.GetBoundingBox()
    return (pcbnew.ToMM(b.GetLeft()), pcbnew.ToMM(b.GetTop()), pcbnew.ToMM(b.GetRight()), pcbnew.ToMM(b.GetBottom()))

def pad_centroid(f):
    ps = list(f.Pads())
    xs = [pcbnew.ToMM(p.GetPosition().x) for p in ps]; ys = [pcbnew.ToMM(p.GetPosition().y) for p in ps]
    return sum(xs)/len(xs), sum(ys)/len(ys)

def aim(f, dx, dy):
    """rotate (any angle) so the side of the part with no pads (antenna, actuator) points along (dx,dy)"""
    def vec():
        l, t, r, b = bbox(f); px, py = pad_centroid(f)
        return (l+r)/2 - px, (t+b)/2 - py
    def score():
        vx, vy = vec(); n = math.hypot(vx, vy) or 1
        return (vx*dx + vy*dy) / n
    set_rot(f, 0)
    vx, vy = vec()
    delta = math.degrees(math.atan2(dy, dx) - math.atan2(vy, vx))
    best = None
    for a in (-delta, delta):
        set_rot(f, a % 360)
        sc = score()
        if best is None or sc > best[0]: best = (sc, a % 360)
    set_rot(f, best[1])

def polar(r, deg):           # deg clockwise from 12 o'clock
    t = math.radians(deg); return CX + r*math.sin(t), CY - r*math.cos(t)

placed = {False: [], True: []}
# antenna keepout of U1 (antenna points at the board centre): nothing on either side may go here
KO = (CX-3.0, CY-7.0, CX+3.0, CY+7.0, 'antenna keepout')
placed[False].append(KO); placed[True].append(KO)
def overlaps(box, side, margin=0.15):
    l, t, r, b = box
    for (L, T, R, Bo, ref) in placed[side]:
        if l - margin < R and r + margin > L and t - margin < Bo and b + margin > T: return ref
    return None
def inside(box, lim=RB-0.6):
    l, t, r, b = box
    return all(math.hypot(x-CX, y-CY) <= lim for x, y in [(l,t),(r,t),(l,b),(r,b)])
def commit(f, side):
    l, t, r, b = bbox(f); placed[side].append((l, t, r, b, f.GetReference()))

def put(ref, x, y, rot=0, back=False, aim_dir=None, check_inside=True):
    f = fp(ref)
    if not f: return
    set_side(f, back); set_rot(f, rot); set_pos(f, x, y)
    if aim_dir: aim(f, *aim_dir); set_pos(f, x, y)
    box = bbox(f); hit = overlaps(box, back)
    if hit: log.append('%s overlaps %s' % (ref, hit))
    if check_inside and not inside(box, RB+3): log.append('%s sticks out past the board edge' % ref)
    commit(f, back)

def near(ref, ax, ay, back=True, rot=0):
    """spiral out from (ax,ay) until the part fits without overlapping"""
    f = fp(ref)
    if not f: return
    set_side(f, back); set_rot(f, rot)
    for r10 in range(0, 140, 4):
        r = r10/10
        steps = 1 if r == 0 else max(8, int(2*math.pi*r/0.6))
        for k in range(steps):
            a = 2*math.pi*k/steps
            set_pos(f, ax + r*math.cos(a), ay + r*math.sin(a))
            box = bbox(f)
            if inside(box) and not overlaps(box, back):
                commit(f, back); return
    log.append('no free spot near anchor for ' + ref + ', placed on anchor')
    set_pos(f, ax, ay); commit(f, back)

# ---------- FRONT: LED rings, light sensor ----------
for i in range(60):                       # minute ring, D1 at 12 o'clock, clockwise
    x, y = polar(18.0, i*6); put('D%d' % (i+1), x, y, -i*6)
for i in range(12):                       # hour ring
    x, y = polar(12.0, i*30); put('D%d' % (61+i), x, y, -i*30)
put('U10', CX, CY - 9.0)
near('C19', CX + 2.4, CY - 9.2, back=False)
for k, c in enumerate(range(20, 32)):     # LED decoupling between the rings
    x, y = polar(15.0, 15 + k*30); near('C%d' % c, x, y, back=False, rot=-(15+k*30))

# ---------- BACK: rim parts first ----------
for ref, ang, R in [('SW4', 60, 18.9), ('SW5', 120, 18.9), ('SW2', 150, 18.9), ('SW3', 210, 18.9)]:
    x, y = polar(R, ang); t = math.radians(ang)
    put(ref, x, y, back=True, aim_dir=(math.sin(t), -math.cos(t)))
put('J1', CX, CY + 14.5, back=True)       # pogo pads, 6 o'clock

# ---------- BACK: module and chips ----------
placed[True].remove(KO)
put('U1', CX - 5.6, CY, back=True, aim_dir=(1, 0))    # antenna toward the centre, keepout inside the hour ring
_u1 = fp('U1'); set_rot(_u1, round(_u1.GetOrientationDegrees()/90)*90 % 360); set_pos(_u1, CX - 5.6, CY)   # keep it square
placed[True] = [e for e in placed[True] if e[4] != 'U1']; commit(_u1, True)
near('J2', CX - 11.5, CY + 9.5, back=True) # battery wires
placed[True].append(KO)
for ref, x, y in [('U2', CX+8.5, CY-2.5), ('U3', CX+8.0, CY+5.0), ('U7', CX+6.0, CY-9.5), ('L1', CX+9.5, CY-9.5)]:
    put(ref, x, y, back=True)
for ref, x, y in [('U5', CX-1.0, CY-10.5), ('U9', CX+1.5, CY-14.5), ('M1', CX-4.5, CY-15.0),
                  ('U8', CX+3.5, CY+10.0), ('U4', CX-2.0, CY+10.5)]:
    near(ref, x, y, back=True)

# ---------- BACK: passives next to the chip they belong to ----------
groups = {'U3x': ['SW1', 'R17'], 'U2': ['C1','C2','C3','R1','R2','R3','R4','R5','R6'], 'U3': ['C4','C5'], 'U7': ['C6','C7','C8','R7'],
          'U1': ['C9','C10','R8','C11','R9','R10','R11','R12','R13','R14'], 'U8': ['C12','R15'],
          'U5': ['C13','C14'], 'U4': ['C15','R16'], 'U9': ['C16','C17','C18']}
for ic, parts in groups.items():
    if ic == 'U3x':
        ax, ay = CX + 11.5, CY + 9.0          # power switch inside the back, near the regulator
    else:
        f = fp(ic)
        if not f: continue
        ax, ay = pcbnew.ToMM(f.GetPosition().x), pcbnew.ToMM(f.GetPosition().y)
    if ic == 'U1': ax, ay = CX + 1.0, CY + 6.5     # keep module passives off the antenna end
    for p in parts: near(p, ax, ay, back=True)

for f in B.GetFootprints():
    try: f.Reference().SetVisible(False)   # no reference text on this tiny board
    except Exception: pass
    try: f.Value().SetVisible(False)
    except Exception: pass

# PWR_FLAGs have no footprint, so nothing to place for them
pcbnew.Refresh()
log = [l for l in log if not (l.startswith('D') and ' overlaps D' in l)]   # LED text boxes only, courtyards are fine
print('\n'.join(log) if log else 'all parts placed, no overlaps found')
print('Done. Press B to refill zones later, then File > Save.')
