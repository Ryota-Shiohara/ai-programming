"""課題3-1：1動作・1試行の加速度XYZを表示する。"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", nargs="?", type=Path,
                        default=Path("data/raw/02-data-collection/jump1.csv"))
    parser.add_argument("--output", type=Path,
                        default=Path("lessons/03-visualization/output/3-1.png"))
    args = parser.parse_args()
    with args.csv_file.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    time_us = np.array([int(row["timestamp_us"]) for row in rows])
    time = (time_us - time_us[0]) / 1_000_000
    acceleration = np.array([[float(row[f"acc_{axis}"]) for axis in "xyz"]
                             for row in rows])
    if not np.isfinite(acceleration).all() or np.any(np.diff(time) <= 0):
        raise ValueError("加速度の欠損・非有限値、または時刻の逆転・重複があります。")

    fig, ax = plt.subplots(figsize=(11, 4.6), layout="constrained")
    for i, (axis, color) in enumerate(zip("XYZ", ("#0072B2", "#009E73", "#D55E00"))):
        ax.plot(time, acceleration[:, i], label=axis, color=color,
                linewidth=1.2, marker="o", markersize=2.5, markevery=15)
    ax.set(title=f"{args.csv_file.stem}: gravity-removed acceleration",
           xlabel="Time [s]", ylabel="Acceleration [m/s²]", xlim=(0, time[-1]))
    ax.legend(ncol=3, loc="upper right")
    ax.grid(alpha=0.25)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)
    for i, axis in enumerate("XYZ"):
        print(f"{axis}: min={acceleration[:, i].min():.3f}, "
              f"max={acceleration[:, i].max():.3f} m/s²")
    print(f"Duration: {time[-1]:.3f} s; saved: {args.output}")


if __name__ == "__main__":
    main()
