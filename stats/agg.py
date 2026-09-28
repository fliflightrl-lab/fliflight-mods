import json

cf = [
 ("CrossX-Better Crosshair Sniper", 6092),
 ("Crossy - CrossX", 2729),
 ("Custom Crosshair PvP", 74),
 ("Low Fire - Lowered Flame", 8515),
 ("PvP Essentials", 412),
 ("PvP HUD", 89),
 ("Clear Pumpkin", 3310),
 ("Everything in Diamonds Dimension", 749),
 ("Pvp sword (little sword)", 6189),
 ("CrosshairX-Better Crosshair", 6117),
 ("Bigger Dot Crosshair", 7626),
 ("Visible Ores (+netherite)", 14041),
 ("CrossX - Better Crosshair !", 9707),
 ("CrossX - CROSSX", 17093),
 ("Dot Crosshair - CrossX", 29558),
]
mr = [
 ("crossx", 263), ("diamond-dimension", 1), ("dot-crosshair", 84),
 ("pvp-essentials", 5), ("visible-ores", 212), ("bigger-dot", 38),
 ("pvphud", 0), ("clear-pumpkin", 0), ("crossx-crossx", 111),
 ("crossy", 16), ("short-sword", 15), ("crossx-better", 68),
 ("custom-crosshair", 0), ("crosshairx", 31), ("low-fire", 20),
]

cf_total = sum(x[1] for x in cf)
mr_total = sum(x[1] for x in mr)
gh_total = 5  # sum of the few non-zero asset downloads
grand = cf_total + mr_total + gh_total

print("CF total:", cf_total)
print("MR total:", mr_total)
print("GH total:", gh_total)
print("GRAND:", grand)
print("CF share: %.2f%%" % (cf_total/grand*100))
print("MR share: %.2f%%" % (mr_total/grand*100))

print("\n=== CF sorted by downloads ===")
for name, d in sorted(cf, key=lambda x:-x[1]):
    print(f"{d:6d}  {d/cf_total*100:5.2f}%  {name}")

print("\n=== MR sorted by downloads ===")
for name, d in sorted(mr, key=lambda x:-x[1]):
    print(f"{d:6d}  {name}")
