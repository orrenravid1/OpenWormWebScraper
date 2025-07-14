import os

# Paste in (or load) your list of 134 bases:
frameset_bases = [
    "ADA","ADE","ADF","ADL","AFD","AIA","AIB","AIM","AIN","AIY","AIZ",
    "ALA","ALM","ALN","AQR","AS","ASE","ASG","ASH","ASI","ASJ","ASK",
    "AUA","AVA","AVB","AVD","AVE","AVF","AVG","AVH","AVJ","AVK","AVL",
    "AVM","AWA","AWB","AWC","BAG","BDU","CAN","CEP","DA","DB","DD",
    "DVA","DVB","DVC","FLP","HSN","I1","I2","I3","I4","I5","I6","IL1",
    "IL2","LUA","M1","M2","M3","M4","M5","MC","MI","NSM","OLL","OLQ",
    "PDA","PDB","PDE","PHA","PHB","PHC","PLM","PLN","PQR","PVC","PVD",
    "PVM","PVN","PVP","PVQ","PVR","PVT","PVW","RIA","RIB","RIC","RID",
    "RIF","RIG","RIH","RIM","RIP","RIR","RIS","RIV","RMD","RME","RMF",
    "RMG","RMH","SAA","SAB","SDQ","SIA","SIB","SMB","SMD","URA","URB",
    "URX","URY","VA","VB","VC","VD"
]

OUT_DIR = "output/pages"

saved = { fn[:-5] for fn in os.listdir(OUT_DIR) if fn.endswith(".html") }
missing = sorted(set(frameset_bases) - saved)

print("Expected frameset bases:", len(frameset_bases))
print("Actual files saved:    ", len(saved))
print("Missing bases:")
for m in missing:
    print("  ", m)

# ———————————————————————————————
# 7) Final sanity check
# ———————————————————————————————

import glob

# what you expected to fetch
expected = set(frameset_bases)

# what you actually saved
saved = { os.path.splitext(os.path.basename(p))[0]
          for p in glob.glob(os.path.join(OUT_DIR, "*.html")) }

print(f"\n⟳ Validation: expected {len(expected)} bases, found {len(saved)} files on disk.")

missing = expected - saved
extra   = saved - expected

if missing:
    print("⚠️  Missing files for these bases:")
    for b in sorted(missing):
        print("   ", b)
else:
    print("✅ No missing files.")

if extra:
    print("⚠️  Unexpected extra files for these bases:")
    for b in sorted(extra):
        print("   ", b)
else:
    print("✅ No extra files.")