# NEON//WRIST DRC polish: nudge D38 ground via off its data trace, set via ring minimum to the fab's real limit.
#   exec(open('/Users/sreevardhankondapalli/neonwrist/pcb/scripts/drc_polish.py').read())
import pcbnew
B = pcbnew.GetBoard(); mm = pcbnew.FromMM; um = pcbnew.ToMM
moved = 0
for t in B.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        p = t.GetPosition()
        if abs(um(p.x)-138.49) < 0.01 and abs(um(p.y)-113.335) < 0.01:
            t.SetPosition(pcbnew.VECTOR2I(mm(138.52), mm(113.34))); moved += 1
ds = B.GetDesignSettings()
ok = False
for attr in ('m_ViasMinAnnularWidth', 'm_MinRingWidth'):
    try: setattr(ds, attr, mm(0.075)); ok = True; break
    except Exception: pass
pcbnew.ZONE_FILLER(B).Fill(B.Zones())
print('D38 via nudged: %d' % moved)
print('min via ring set to 0.075 mm: %s' % ('yes' if ok else 'NO - set it by hand'))
pcbnew.Refresh(); print('Now: B, Cmd+S, DRC')
