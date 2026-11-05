# NEON//WRIST: puts back the one 5V_LED trace the stub cleaner removed by mistake, ending it on the new 5V via.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/fix_5v.py').read())
import pcbnew
B = pcbnew.GetBoard(); mm = pcbnew.FromMM
n = B.FindNet('/5V_LED') or B.FindNet('5V_LED')
t = pcbnew.PCB_TRACK(B); t.SetStart(pcbnew.VECTOR2I(mm(152.415), mm(87.0352))); t.SetEnd(pcbnew.VECTOR2I(mm(154.437), mm(89.0343)))
t.SetWidth(mm(0.15)); t.SetLayer(pcbnew.F_Cu); t.SetNetCode(n.GetNetCode()); B.Add(t)
pcbnew.ZONE_FILLER(B).Fill(B.Zones()); B.BuildConnectivity()
print('5V trace restored; unrouted connections: %d' % B.GetConnectivity().GetUnconnectedCount(False))
pcbnew.Refresh(); print('Now: B, Cmd+S, DRC')
