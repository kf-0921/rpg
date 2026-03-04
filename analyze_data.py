import numpy as np

# A, B, C, D data
data = {
    "A": [15000, 18300, 22200, 26850, 32400, 39000, 46950, 56400, 67650, 81150, 97350, 116700],
    "B": [16200, 19650, 23850, 28800, 34650, 41700, 50100, 60150, 72150, 86550, 103800, 124500],
    "C": [17550, 21300, 25800, 31200, 37650, 45300, 54450, 65400, 78450, 94200, 112950, 135450],
    "D": [19500, 23700, 28650, 34500, 41550, 49950, 60000, 72000, 86400, 103650, 124350, 149100]
}


def analyze_ratios(values):
    ratios = []
    for i in range(len(values) - 1):
        ratios.append(values[i+1] / values[i])
    return ratios


for key, values in data.items():
    ratios = analyze_ratios(values)
    avg_ratio = np.mean(ratios)
    print(f"{key}: Avg Ratio = {avg_ratio:.4f}, Min = {min(ratios):.4f}, Max = {max(ratios):.4f}")
    # Check if ratio is exactly 1.2
    exact_match = all(abs(r - 1.2) < 0.1 for r in ratios)
    if exact_match:
        print(f"  Suggests Exponential Growth with factor ~1.2")
