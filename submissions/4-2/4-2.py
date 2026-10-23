"""課題4-2：30Hzのデータを1秒窓・50%重複で分割する。"""

import argparse
import csv
from statistics import median
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", nargs="?", type=Path,
                        default=Path("data/raw/02-data-collection"))
    parser.add_argument("--file", default="walk1.csv", help="1試行を選択（既定はwalk1）")
    parser.add_argument("--all", action="store_true", help="比較用に全15試行へ適用する")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("data/processed/04-preprocessing/windows"))
    args = parser.parse_args()
    if args.data_dir.resolve() == args.output_dir.resolve():
        parser.error("入力と出力は別フォルダにしてください。")
    files = ([args.data_dir / f"{action}{trial}.csv"
              for action in ("walk", "jump", "squat") for trial in range(1, 6)]
             if args.all else [args.data_dir / args.file])
    # 30Hzで1秒=30サンプル、50%重複=15サンプル刻み。
    window, step = 30, 15
    prepared = []
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            header = next(reader)
            rows = [row for row in reader if row]
        if len(rows) < window or any(len(row) != len(header) for row in rows):
            raise ValueError(f"行数または列数が不正です: {path.name}")
        times = [int(row[header.index("timestamp_us")]) for row in rows]
        intervals = [(b - a) / 1_000_000 for a, b in zip(times, times[1:])]
        if (any(dt <= 0 or dt >= 2 / 30 for dt in intervals)
                or abs(median(intervals) - 1 / 30) > 0.003):
            raise ValueError(f"30Hzから大きく外れた時刻間隔があります: {path.name}")
        prepared.append((path, header, rows))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for path, header, rows in prepared:
        count = 0
        for index, start in enumerate(range(0, len(rows) - window + 1, step), start=1):
            target = args.output_dir / f"{path.stem}_window{index:03d}.csv"
            with target.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(rows[start:start + window])
            count += 1
        print(f"{path.name}: {count} windows; 30 samples/window, 15 samples/step")


if __name__ == "__main__":
    main()
