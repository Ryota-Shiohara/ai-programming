"""課題3-4：切り出し済み15試行の合成加速度の標準偏差を箱ひげ図で比較する。"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", nargs="?", type=Path,
                        default=Path("data/processed/03-visualization/6-seconds"))
    parser.add_argument("--output", type=Path,
                        default=Path("lessons/03-visualization/output/3-4.png"))
    args = parser.parse_args()
    actions = ("walk", "jump", "squat")
    groups, statistics = [], []
    for action in actions:
        deviations = []
        for trial in range(1, 6):
            path = args.data_dir / f"{action}{trial}.csv"
            with path.open(encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))
            xyz = np.array([[float(row[f"acc_{axis}"]) for axis in "xyz"] for row in rows])
            if not np.isfinite(xyz).all():
                raise ValueError(f"加速度に非有限値があります: {path.name}")
            magnitude = np.sqrt(np.sum(xyz ** 2, axis=1))
            # 各試行内の全サンプルを対象とする標準偏差（ddof=0）。
            deviation = float(np.std(magnitude, ddof=0))
            deviations.append(deviation)
            statistics.append((path.name, action, len(rows), deviation))
            print(f"{path.name}: standard deviation={deviation:.6f} m/s²")
        groups.append(deviations)

    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    boxes = ax.boxplot(groups, whis=1.5, patch_artist=True, showfliers=False,
                       medianprops={"color": "#222222", "linewidth": 1.6})
    for i, (patch, values, color) in enumerate(
        zip(boxes["boxes"], groups, ("#0072B2", "#D55E00", "#009E73")), start=1
    ):
        patch.set_facecolor(color)
        patch.set_alpha(0.3)
        # 各点は1試行の標準偏差。全5点を示し、外れ値も隠さない。
        ax.scatter(i + np.linspace(-0.07, 0.07, 5), values, color=color,
                   edgecolors="white", linewidths=0.6, s=45, zorder=3)
    ax.set_xticks((1, 2, 3), ("Walk", "Jump", "Squat"))
    ax.set(title="Standard deviation of acceleration magnitude\nFirst 6 seconds; 5 trials per action",
           xlabel="Action", ylabel="Standard deviation [m/s²]", ylim=(0, None))
    ax.grid(axis="y", alpha=0.25)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)
    with args.output.with_name("3-4-statistics.csv").open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(("file", "action", "samples", "std_m_s2"))
        writer.writerows(statistics)


if __name__ == "__main__":
    main()
