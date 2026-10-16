"""課題3-2：1動作の5試行について合成加速度を共通の軸で比較する。"""

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
                        default=Path("data/raw/02-data-collection"))
    parser.add_argument("--action", choices=("walk", "jump", "squat"), default="jump")
    parser.add_argument("--output", type=Path,
                        default=Path("lessons/03-visualization/output/3-2.png"))
    args = parser.parse_args()
    trials = []
    for trial in range(1, 6):
        path = args.data_dir / f"{args.action}{trial}.csv"
        with path.open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        time_us = np.array([int(row["timestamp_us"]) for row in rows])
        time = (time_us - time_us[0]) / 1_000_000
        xyz = np.array([[float(row[f"acc_{axis}"]) for axis in "xyz"] for row in rows])
        if not np.isfinite(xyz).all() or np.any(np.diff(time) <= 0):
            raise ValueError(f"加速度または時刻が不正です: {path.name}")
        magnitude = np.sqrt(np.sum(xyz ** 2, axis=1))
        trials.append((time, magnitude))
        print(f"{path.name}: duration={time[-1]:.3f} s, "
              f"max={magnitude.max():.3f} m/s²")

    end = max(time[-1] for time, _ in trials)
    upper = max(magnitude.max() for _, magnitude in trials) * 1.08
    fig, axes = plt.subplots(5, 1, figsize=(11, 10), sharex=True, sharey=True,
                             layout="constrained")
    for trial, (ax, (time, magnitude)) in enumerate(zip(axes, trials), start=1):
        ax.plot(time, magnitude, color="#0072B2", linewidth=1.2,
                marker="o", markersize=2, markevery=15)
        ax.set(title=f"{args.action}{trial}", xlim=(0, end), ylim=(0, upper))
        ax.grid(alpha=0.25)
        ax.set_ylabel("Magnitude [m/s²]")
    axes[-1].set_xlabel("Time [s]")
    fig.suptitle(f"{args.action.capitalize()}: gravity-removed acceleration magnitude (5 trials)")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
