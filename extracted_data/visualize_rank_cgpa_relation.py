import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# -----------------------
# Configuration
# -----------------------
DATABASE = "data.db"
YEAR = 2024                    # <-- Change this
OUTPUT = f"rank_range_{YEAR}.png"

# -----------------------
# Read data
# -----------------------
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
SELECT cgpa, min_rank, max_rank
FROM CgpaRankRange
WHERE year = ?
ORDER BY cgpa
""", (YEAR,))

rows = cursor.fetchall()
conn.close()

if not rows:
    raise ValueError(f"No data found for year {YEAR}")

cgpa = [r[0] for r in rows]
min_rank = [r[1] for r in rows]
max_rank = [r[2] for r in rows]

# -----------------------
# Plot
# -----------------------
plt.figure(figsize=(10, 6))

# Filled region
plt.fill_between(
    cgpa,
    min_rank,
    max_rank,
    color="#4E79A7",
    alpha=0.25,
    label="Possible Rank Range"
)

# Boundary lines
plt.plot(
    cgpa,
    min_rank,
    color="#2F5597",
    linewidth=2.5,
    label="Best Possible Rank"
)

plt.plot(
    cgpa,
    max_rank,
    color="#E15759",
    linewidth=2.5,
    label="Worst Possible Rank"
)

# Cosmetics
plt.gca().invert_yaxis()      # Rank 1 at top

plt.title(
    f"CGPA vs Rank Range ({YEAR})",
    fontsize=16,
    weight="bold"
)

plt.xlabel("CGPA", fontsize=12)
plt.ylabel("Rank", fontsize=12)



plt.xticks(np.arange(5, 10.5, 0.5))

plt.grid(True, linestyle="--", alpha=0.35)
plt.legend()

plt.tight_layout()

plt.savefig(OUTPUT, dpi=300)
plt.show()