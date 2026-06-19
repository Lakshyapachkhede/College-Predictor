import sqlite3
import matplotlib.pyplot as plt

# ---------------- Configuration ----------------

DB_PATH = "data.db"

# Set year to visualize
year = 2025

# CGPA bins
bins = {
    "5.0-5.5": 0,
    "5.5-6.0": 0,
    "6.0-6.5": 0,
    "6.5-7.0": 0,
    "7.0-7.5": 0,
    "7.5-8.0": 0,
    "8.0-8.5": 0,
    "8.5-9.0": 0,
    "9.0-9.5": 0,
    "9.5-10.0": 0,
}

# ---------------- Read from database ----------------

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
SELECT cgpa, min_rank, max_rank
FROM CgpaRankRange
WHERE year = ?
ORDER BY cgpa
""", (year,))

rows = cursor.fetchall()
conn.close()

# ---------------- Calculate Distribution ----------------

for cgpa, min_rank, max_rank in rows:

    students = max_rank - min_rank + 1

    if 5.0 <= cgpa < 5.5:
        bins["5.0-5.5"] += students
    elif 5.5 <= cgpa < 6.0:
        bins["5.5-6.0"] += students
    elif 6.0 <= cgpa < 6.5:
        bins["6.0-6.5"] += students
    elif 6.5 <= cgpa < 7.0:
        bins["6.5-7.0"] += students
    elif 7.0 <= cgpa < 7.5:
        bins["7.0-7.5"] += students
    elif 7.5 <= cgpa < 8.0:
        bins["7.5-8.0"] += students
    elif 8.0 <= cgpa < 8.5:
        bins["8.0-8.5"] += students
    elif 8.5 <= cgpa < 9.0:
        bins["8.5-9.0"] += students
    elif 9.0 <= cgpa < 9.5:
        bins["9.0-9.5"] += students
    elif 9.5 <= cgpa <= 10.0:
        bins["9.5-10.0"] += students

print(bins)

# ---------------- Plot ----------------

labels = list(bins.keys())
values = list(bins.values())

colors = [
    "#4E79A7",
    "#F28E2B",
    "#59A14F",
    "#E15759",
    "#AF7AA1",
    "#EDC948",
    "#76B7B2",
    "#FF9DA7",
    "#9C755F",
    "#BAB0AC",
]

plt.figure(figsize=(10, 5))

bars = plt.bar(
    labels,
    values,
    color=colors,
    edgecolor="black",
    linewidth=0.8
)

plt.title(f"CGPA Distribution ({year})", fontsize=16, weight="bold")
plt.xlabel("CGPA Range")
plt.ylabel("Number of Students")

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + max(values) * 0.01,
        str(int(height)),
        ha="center",
        fontsize=9,
        weight="bold"
    )

plt.grid(axis="y", linestyle="--", alpha=0.35)
plt.tight_layout()

plt.savefig(f"cgpa_distribution_{year}.png", dpi=300)
plt.show()