# User provided Legend data (index 0 to 11)
legend_vals = [4398, 8797, 13196, 17595, 21993,
               26392, 30791, 35190, 39588, 43987, 48368, 52784]

# Quality ratios:
# Legend = 1.30 * Rare
# Mythic = 1.17 * Rare
# Epic = 1.08 * Rare

# Derived Rare from Legend:
rare_vals = [round(v / 1.30) for v in legend_vals]
mythic_vals = [round((v / 1.30) * 1.17) for v in legend_vals]
epic_vals = [round((v / 1.30) * 1.08) for v in legend_vals]

data_final = {
    "稀有": rare_vals,
    "史詩": epic_vals,
    "神話": mythic_vals,
    "傳奇": legend_vals
}

for q, vals in data_final.items():
    print(f"{q}:{', '.join(map(str, vals))}")
