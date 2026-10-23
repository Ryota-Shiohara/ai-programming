"""課題4-5：FFTのピーク周波数を追加し、特徴量の分布を比較する。"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("features_csv", nargs="?", type=Path,
                        default=Path("data/processed/04-preprocessing/features.csv"))
    parser.add_argument("--windows-dir", type=Path,
                        default=Path("data/processed/04-preprocessing/windows"))
    parser.add_argument("--features-output", type=Path,
                        default=Path("data/processed/04-preprocessing/features-with-frequency.csv"))
    parser.add_argument("--output", type=Path,
                        default=Path("lessons/04-preprocessing/output/4-5.png"))
    args = parser.parse_args()
    if args.features_csv.resolve() == args.features_output.resolve():
        parser.error("追加前と追加後の表は別ファイルにしてください。")
    with args.features_csv.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        features = list(reader)
    if not features or "fft_peak_hz" in columns:
        parser.error("入力表が空、またはすでに周波数特徴量が追加されています。")
    if {row["label"] for row in features} != {"walk", "jump", "squat"}:
        parser.error("比較する3動作が揃っていません。")

    fs = 30.0
    for row in features:
        source = Path(row["source_file"]).stem
        index = int(row["window_id"])
        path = args.windows_dir / f"{source}_window{index:03d}.csv"
        with path.open(encoding="utf-8-sig", newline="") as file:
            records = list(csv.DictReader(file))
        xyz = np.array([[float(record[f"acc_{axis}"]) for axis in "xyz"]
                        for record in records])
        if len(xyz) != 30 or not np.isfinite(xyz).all():
            raise ValueError(f"30サンプルではないか、値が不正です: {path.name}")
        magnitude = np.sqrt(np.sum(xyz ** 2, axis=1))
        # 平均を引いて直流成分を抑え、Hann窓で端の不連続の影響を抑える。
        centered = magnitude - np.mean(magnitude)
        spectrum = np.abs(np.fft.rfft(centered * np.hanning(len(centered))))
        frequencies = np.fft.rfftfreq(len(centered), d=1 / fs)
        # 0Hzは候補から除外。窓長30、fs=30Hzなので刻みは1Hz。
        peak_index = 1 + int(np.argmax(spectrum[1:]))
        peak = 0.0 if np.max(np.abs(centered)) < 1e-12 else float(frequencies[peak_index])
        row["fft_peak_hz"] = peak

    args.features_output.parent.mkdir(parents=True, exist_ok=True)
    output_columns = [column for column in columns if column != "label"] + ["fft_peak_hz", "label"]
    with args.features_output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(features)

    fig = plt.figure(figsize=(18, 6), layout="constrained")
    before = fig.add_subplot(1, 3, 1)
    frequency_view = fig.add_subplot(1, 3, 2)
    after = fig.add_subplot(1, 3, 3, projection="3d")
    for action, color, marker in zip(("walk", "jump", "squat"),
                                    ("#0072B2", "#D55E00", "#009E73"), ("o", "^", "s")):
        points = np.array([[float(row["std"]), float(row["max"]), float(row["fft_peak_hz"])]
                           for row in features if row["label"] == action])
        label = f"{action.capitalize()} (n={len(points)})"
        style = dict(color=color, marker=marker, s=24, alpha=0.65, edgecolors="none", label=label)
        before.scatter(points[:, 0], points[:, 1], **style)
        frequency_view.scatter(points[:, 0], points[:, 2], **style)
        after.scatter(points[:, 0], points[:, 1], points[:, 2], depthshade=False, **style)
    std_max = max(float(row["std"]) for row in features) * 1.05
    acc_max = max(float(row["max"]) for row in features) * 1.05
    peak_max = max(float(row["fft_peak_hz"]) for row in features)
    before.set(title="Before: 2 time-domain features", xlabel="Standard deviation [m/s²]",
               ylabel="Maximum [m/s²]", xlim=(0, std_max), ylim=(0, acc_max))
    frequency_view.set(title="Frequency view: std vs peak frequency",
                       xlabel="Standard deviation [m/s²]", ylabel="FFT peak frequency [Hz]",
                       xlim=(0, std_max), ylim=(0, max(3, peak_max + 0.6)))
    after.set(title="After: all 3 features", xlabel="Std [m/s²]", ylabel="Max [m/s²]",
              zlabel="FFT peak [Hz]", xlim=(0, std_max), ylim=(0, acc_max),
              zlim=(0, max(3, peak_max + 0.6)))
    after.view_init(elev=22, azim=-55)
    for ax in (before, frequency_view):
        ax.grid(alpha=0.25)
    before.legend(loc="upper left", fontsize=9)
    fig.suptitle("Adding FFT peak frequency: same 331 windows\nMean removal + Hann window; nominal fs = 30 Hz; frequency bins = 1 Hz")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)
    print(f"Saved {len(features)} windows with FFT peak frequency: {args.features_output}")
    print(f"Saved comparison: {args.output}")
    for action in ("walk", "jump", "squat"):
        peaks = [float(row["fft_peak_hz"]) for row in features if row["label"] == action]
        values, counts = np.unique(peaks, return_counts=True)
        print(action, dict(zip(values.tolist(), counts.tolist())))


if __name__ == "__main__":
    main()
