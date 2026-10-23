"""課題4-1：ジャンプ1試行のZ軸に3種類のフィルタを適用する。"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, sosfiltfilt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", nargs="?", type=Path,
                        default=Path("data/raw/02-data-collection/jump1.csv"))
    parser.add_argument("--output", type=Path,
                        default=Path("lessons/04-preprocessing/output/4-1.png"))
    args = parser.parse_args()
    with args.csv_file.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    timestamps = np.array([int(row["timestamp_us"]) for row in rows])
    time = (timestamps - timestamps[0]) / 1_000_000
    signal = np.array([float(row["acc_z"]) for row in rows])
    if not np.isfinite(signal).all() or np.any(np.diff(time) <= 0):
        raise ValueError("加速度または時刻が不正です。")

    # 公称サンプリング周波数30Hz。時刻間隔が著しく異なる場合は止める。
    fs = 30.0
    intervals = np.diff(time)
    if abs(np.median(intervals) - 1 / fs) > 0.003 or intervals.max() >= 2 / fs:
        raise ValueError("時刻間隔が30Hzから大きく外れています。再サンプリングを検討してください。")
    size = 5
    padded = np.pad(signal, size // 2, mode="reflect")
    moving_average = np.convolve(padded, np.ones(size) / size, mode="valid")
    median = np.median(np.lib.stride_tricks.sliding_window_view(padded, size), axis=1)
    # 4次Butterworth、カットオフ3Hz。前後方向に適用し位相ずれを抑える。
    sos = butter(4, 3.0, btype="lowpass", fs=fs, output="sos")
    lowpass = sosfiltfilt(sos, signal)
    curves = [(moving_average, "Moving average (5 samples)", "#0072B2"),
              (median, "Median (5 samples)", "#009E73"),
              (lowpass, "Low-pass (Butterworth, 3 Hz)", "#D55E00")]
    fig, axes = plt.subplots(4, 1, figsize=(11, 11.5), sharex=True, sharey=True,
                             layout="constrained")
    all_values = np.concatenate([signal] + [values for values, _, _ in curves])
    padding = np.ptp(all_values) * 0.06
    axes[0].plot(time, signal, color="#777777", alpha=0.65, linewidth=1,
                 label="Original", marker="o", markersize=2, markevery=15)
    for (values, label, color), style in zip(curves, ("-", "--", ":")):
        axes[0].plot(time, values, color=color, linewidth=1.5,
                     linestyle=style, label=label)
    axes[0].legend(loc="lower left", bbox_to_anchor=(0, 1.01), ncol=2, fontsize=9)
    for ax, (values, label, color) in zip(axes[1:], curves):
        ax.plot(time, signal, color="#777777", alpha=0.65, linewidth=1,
                label="Original", marker="o", markersize=2, markevery=15)
        ax.plot(time, values, color=color, linewidth=1.5, label=label)
        ax.legend(loc="upper right", fontsize=9)
    for ax in axes:
        ax.set(ylabel="Acceleration [m/s²]", xlim=(0, time[-1]),
               ylim=(all_values.min() - padding, all_values.max() + padding))
        ax.grid(alpha=0.25)
    axes[-1].set_xlabel("Time [s]")
    fig.suptitle(f"{args.csv_file.stem}: filtering gravity-removed Z acceleration")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)
    with args.output.with_name("4-1-filtered.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("time_s", "original", "moving_average", "median", "lowpass"))
        writer.writerows(zip(time, signal, moving_average, median, lowpass))
    print(f"Saved: {args.output}; {len(signal)} samples, nominal fs={fs} Hz")


if __name__ == "__main__":
    main()
