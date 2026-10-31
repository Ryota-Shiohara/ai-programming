"""第5回の特徴量表・試行単位の固定分割・予想用散布図を準備する。学習はしない。"""

import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_dir", nargs="?", type=Path,
                        default=Path("data/raw/02-data-collection"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("data/processed/05-machine-learning"))
    parser.add_argument("--plot-dir", type=Path,
                        default=Path("lessons/05-machine-learning/output"))
    args = parser.parse_args()
    if args.raw_dir.resolve() == args.output_dir.resolve():
        parser.error("元CSVと出力先は別のフォルダにしてください。")
    # 第4回の生成物に依存せず、元15試行から同じ特徴量を再生成する。
    rows = []
    columns = ["source_file", "window_id", "mean", "std", "max", "min", "rms", "range", "fft_peak_hz", "label"]
    paths = sorted(args.raw_dir / f"{action}{trial}.csv"
                   for action in ("walk", "jump", "squat") for trial in range(1, 6))
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as file:
            records = list(csv.DictReader(file))
        timestamps = np.array([int(row["timestamp_us"]) for row in records])
        intervals = np.diff(timestamps) / 1_000_000
        if (len(records) < 30 or np.any(intervals <= 0) or np.any(intervals >= 2 / 30)
                or abs(np.median(intervals) - 1 / 30) > 0.003):
            raise ValueError(f"30Hzの試行として扱えません: {path.name}")
        xyz = np.array([[float(row[f"acc_{axis}"]) for axis in "xyz"] for row in records])
        if not np.isfinite(xyz).all():
            raise ValueError(f"加速度に欠損・非有限値があります: {path.name}")
        # 公称30Hzで30サンプル=1秒、15サンプル刻み=50%重複。試行境界をまたがない。
        for index, start in enumerate(range(0, len(records) - 30 + 1, 15), start=1):
            magnitude = np.sqrt(np.sum(xyz[start:start + 30] ** 2, axis=1))
            centered = magnitude - np.mean(magnitude)
            spectrum = np.abs(np.fft.rfft(centered * np.hanning(30)))
            frequencies = np.fft.rfftfreq(30, d=1 / 30)
            peak_index = 1 + int(np.argmax(spectrum[1:]))
            peak = 0.0 if np.max(np.abs(centered)) < 1e-12 else float(frequencies[peak_index])
            rows.append(dict(source_file=path.name, window_id=index,
                             mean=float(np.mean(magnitude)), std=float(np.std(magnitude, ddof=0)),
                             max=float(np.max(magnitude)), min=float(np.min(magnitude)),
                             rms=float(np.sqrt(np.mean(magnitude ** 2))), range=float(np.ptp(magnitude)),
                             fft_peak_hz=peak, label=path.stem.rstrip("0123456789")))
    target = args.output_dir
    target.mkdir(parents=True, exist_ok=True)
    expected = {f"{action}{trial}" for action in ("walk", "jump", "squat") for trial in range(1, 6)}
    for row in rows:
        row["trial_id"] = Path(row["source_file"]).stem
        if row["trial_id"] not in expected or row["label"] != row["trial_id"].rstrip("0123456789"):
            raise ValueError("試行IDまたはラベルが不正です。")
    counts = Counter(row["trial_id"] for row in rows)
    if set(counts) != expected:
        raise ValueError("全15試行が揃っていません。")
    with (target / "features.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["trial_id"] + columns)
        writer.writeheader()
        writer.writerows(rows)
    with (target / "split.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("trial_id", "source_file", "label", "split", "windows"))
        for action in ("walk", "jump", "squat"):
            for trial in range(1, 6):
                trial_id = f"{action}{trial}"
                writer.writerow((trial_id, trial_id + ".csv", action,
                                 "test" if trial == 5 else "train", counts[trial_id]))

    fig, ax = plt.subplots(figsize=(8.5, 6), layout="constrained")
    for action, color, marker in zip(("walk", "jump", "squat"),
                                    ("#0072B2", "#D55E00", "#009E73"), ("o", "^", "s")):
        group = [row for row in rows if row["label"] == action]
        # 事前の観察図。正解率やモデルの予測は表示しない。
        ax.scatter([float(row["std"]) for row in group], [float(row["max"]) for row in group],
                   color=color, marker=marker, s=28, alpha=0.65, edgecolors="none",
                   label=f"{action.capitalize()} (n={len(group)})")
    ax.set(title="Before training: standard deviation vs maximum\nAll 15 trials; 1-second windows, 50% overlap",
           xlabel="Standard deviation [m/s²]", ylabel="Maximum [m/s²]",
           xlim=(0, None), ylim=(0, None))
    ax.grid(alpha=0.25)
    ax.legend()
    output = args.plot_dir
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "5-1.png", dpi=180)
    plt.close(fig)
    # 追加特徴量の予想に使う観察図。5-4の学習結果は使わない。
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.3), layout="constrained")
    for action, color, marker in zip(("walk", "jump", "squat"),
                                    ("#0072B2", "#D55E00", "#009E73"), ("o", "^", "s")):
        group = [row for row in rows if row["label"] == action]
        for ax, feature in zip(axes, ("std", "max")):
            ax.scatter([float(row[feature]) for row in group],
                       [float(row["mean"]) for row in group], color=color,
                       marker=marker, s=28, alpha=0.65, edgecolors="none",
                       label=f"{action.capitalize()} (n={len(group)})")
    for ax, title, label in zip(axes, ("Standard deviation vs mean", "Maximum vs mean"),
                                ("Standard deviation [m/s²]", "Maximum [m/s²]")):
        ax.set(title=title, xlabel=label, ylabel="Mean [m/s²]", xlim=(0, None), ylim=(0, None))
        ax.grid(alpha=0.25)
    axes[0].legend(loc="upper left", fontsize=9)
    fig.suptitle("Before 5-4 training: inspecting the mean feature\nGravity-removed acceleration magnitude; 1-second windows, 50% overlap")
    fig.savefig(output / "5-4-mean.png", dpi=180)
    plt.close(fig)
    train = sum(count for trial, count in counts.items() if not trial.endswith("5"))
    test = sum(count for trial, count in counts.items() if trial.endswith("5"))
    print(f"Prepared {len(rows)} windows; train={train} windows / 12 trials; test={test} windows / 3 trials.")
    print("This preparation step does not fit models. Write predictions before running each experiment.")


if __name__ == "__main__":
    main()
