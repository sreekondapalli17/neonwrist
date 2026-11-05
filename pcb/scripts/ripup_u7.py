# NEON//WRIST: rips up the traces boxed around the boost chip (U7) so Freerouting can redo that corner with the new FB divider.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/ripup_u7.py').read())
import pcbnew
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
gnd = B.FindNet('GND') or B.FindNet('/GND'); G = gnd.GetNetCode()
X0, X1, Y0, Y1 = 152.6, 158.2, 88.0, 94.0
def inbox(p): return X0 < um(p.x) < X1 and Y0 < um(p.y) < Y1
gone = 0
for t in list(B.GetTracks()):
    if t.GetNetCode() == G: continue
    if t.GetClass() == 'PCB_VIA':
        hit = inbox(t.GetPosition())
    else:
        hit = t.GetLayer() == pcbnew.B_Cu and (inbox(t.GetStart()) or inbox(t.GetEnd()))
    if hit: B.Remove(t); gone += 1
pcbnew.ZONE_FILLER(B).Fill(B.Zones())
pcbnew.Refresh(); print('traces/vias ripped up around U7: %d' % gone); print('Now: Cmd+S, then run Freerouting')
