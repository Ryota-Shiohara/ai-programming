"""課題4-3：各ウィンドウの合成加速度から時間領域の特徴量を6つ抽出する。"""

import argparse
import csv
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("windows_dir", nargs="?", type=Path,
                        default=Path("data/processed/04-preprocessing/windows"))
    parser.add_argument("--output", type=Path,
                        default=Path("data/processed/04-preprocessing/features.csv"))
    args = parser.parse_args()
    files = sorted(args.windows_dir.glob("*_window*.csv"))
    if not files:
        parser.error("ウィンドウCSVが見つかりません。先に4-2.pyを実行してください。")
    features = []
    for path in files:
        source, window_id = path.stem.rsplit("_window", 1)
        label = source.rstrip("0123456789")
        if label not in ("walk", "jump", "squat"):
            raise ValueError(f"ラベルを判定できません: {path.name}")
        with path.open(encoding="utf-8-sig", newline="") as file:
            records = list(csv.DictReader(file))
        xyz = np.array([[float(row[f"acc_{axis}"]) for axis in "xyz"] for row in records])
        if len(xyz) != 30 or not np.isfinite(xyz).all():
            raise ValueError(f"30サンプルではないか、加速度に欠損があります: {path.name}")
        magnitude = np.sqrt(np.sum(xyz ** 2, axis=1))
        # ラベル・元試行・窓番号は識別用情報。特徴量としてモデルへ入力しない。
        features.append((source + ".csv", int(window_id),
                         float(np.mean(magnitude)), float(np.std(magnitude, ddof=0)),
                         float(np.max(magnitude)), float(np.min(magnitude)),
                         float(np.sqrt(np.mean(magnitude ** 2))), float(np.ptp(magnitude)), label))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("source_file", "window_id", "mean", "std", "max", "min", "rms", "range", "label"))
        writer.writerows(features)
    print(f"Saved {len(features)} windows with 6 features to {args.output}")


if __name__ == "__main__":
    main()
