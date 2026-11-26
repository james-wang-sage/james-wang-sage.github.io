# /// script
# dependencies = ["matplotlib"]
# ///
# Source of ...-amdahl.svg (Section 11). Re-run: uv run <this file>
from pathlib import Path

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

BG, PANEL, TEXT, MUTED, BLUE, ACCENT = "#171f2b", "#202b3a", "#f0f4f8", "#a0adbe", "#8cc8ff", "#d8b58a"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 20, "svg.fonttype": "none"})

rows = [("Before AI", 75, 25), ("Coding 10x faster", 75, 2.5)]
fig, ax = plt.subplots(figsize=(6.4, 4.2), facecolor=BG)
ax.set_facecolor(BG)
for y, (label, other, coding) in zip([1, 0], rows):
    ax.barh(y, other, color=PANEL, edgecolor=BLUE, linewidth=1.5, height=0.5)
    ax.barh(y, coding, left=other, color=ACCENT, edgecolor=ACCENT, height=0.5)
    ax.text(other / 2, y, "Other stages", ha="center", va="center", color=TEXT, fontsize=17)
    ax.text(other + coding + 1.5, y, f"{other + coding:g}%", ha="left", va="center", color=TEXT)
    ax.text(0, y + 0.36, label, ha="left", color=TEXT)
ax.text(87.5, 1.36, "coding 25%", ha="center", color=ACCENT, fontsize=17)
ax.text(77.5, 0.36, "coding 2.5%", ha="center", color=ACCENT, fontsize=17)
ax.set_yticks([])
ax.set_xlim(0, 120)
ax.set_xticks([0, 50, 100], ["0", "50%", "100%"], color=MUTED)
ax.set_xlabel("Delivery time per item, as % of before", color=MUTED)
ax.tick_params(length=0)
for side in ax.spines.values():
    side.set_visible(False)
fig.tight_layout()
fig.savefig(Path(__file__).with_suffix(".svg"), facecolor=BG, bbox_inches="tight", pad_inches=0.25, metadata={"Date": None})
