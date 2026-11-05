# NEON//WRIST after re-route: reconnects R7 (LED_EN pulldown), trims dead stubs, redoes ground cleanup.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/after_route.py').read())
import pcbnew, os
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
V = lambda x, y: pcbnew.VECTOR2I(mm(x), mm(y))
en = B.FindNet('/LED_EN') or B.FindNet('LED_EN'); E = en.GetNetCode()
def trk(layer, a, b):
    t = pcbnew.PCB_TRACK(B); t.SetStart(V(*a)); t.SetEnd(V(*b)); t.SetWidth(mm(0.15)); t.SetLayer(layer); t.SetNetCode(E); B.Add(t)
trk(pcbnew.In1_Cu, (154.46, 88.4586), (154.65, 88.5))
trk(pcbnew.In1_Cu, (154.65, 88.5), (154.9, 88.25))
v = pcbnew.PCB_VIA(B); v.SetPosition(V(154.9, 88.25)); v.SetWidth(mm(0.45)); v.SetDrill(mm(0.2)); v.SetNetCode(E); B.Add(v)
trk(pcbnew.In2_Cu, (154.9, 88.25), (154.826, 88.1556))
print('R7 pulldown reconnected')
# trim the two dead stubs left by the rip-up
STUBS = [(152.787, 88.9663), (158.408, 92.3296)]
cut = 0
for t in list(B.GetTracks()):
    if t.GetClass() == 'PCB_VIA': continue
    for p in (t.GetStart(), t.GetEnd()):
        if any(abs(um(p.x)-x) < 0.01 and abs(um(p.y)-y) < 0.01 for x, y in STUBS):
            B.Remove(t); cut += 1; break
print('dead stubs trimmed: %d' % cut)
d = '/Users/sreevardhankondapalli/neonwrist/pcb/scripts/'
for s in ('gnd_fixup.py', 'gnd_islands.py', 'gnd_join.py'):
    print('--', s); exec(open(d + s).read())
print('ALL DONE. Now: B, Cmd+S, DRC')
