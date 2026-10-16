"""課題3-3：15試行を各試行の開始から共通の時間長に切り出す。"""

import argparse
import csv
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", nargs="?", type=Path,
                        default=Path("data/raw/02-data-collection"))
    parser.add_argument("--seconds", type=float, default=6.0)
    parser.add_argument("--output-dir", type=Path,
                        default=Path("data/processed/03-visualization/6-seconds"))
    args = parser.parse_args()
    if not 0 < args.seconds < float("inf"):
        parser.error("時間長は有限の正の値にしてください。")
    if args.data_dir.resolve() == args.output_dir.resolve():
        parser.error("元データと出力先は別のフォルダにしてください。")

    # 全15試行の長さを先に確認し、短い試行があれば出力前に停止する。
    prepared = []
    for action in ("walk", "jump", "squat"):
        for trial in range(1, 6):
            path = args.data_dir / f"{action}{trial}.csv"
            with path.open(encoding="utf-8-sig", newline="") as file:
                reader = csv.reader(file)
                header = next(reader)
                rows = [row for row in reader if row]
            column = header.index("timestamp_us")
            times = [int(row[column]) for row in rows]
            if any(b <= a for a, b in zip(times, times[1:])):
                raise ValueError(f"時刻の逆転・重複があります: {path.name}")
            start = times[0]
            if (times[-1] - start) / 1_000_000 < args.seconds:
                raise ValueError(f"{args.seconds}秒に足りません: {path.name}")
            # 半開区間 [0, seconds) を使い、元の値・時刻・列は保持する。
            clipped = [row for row, time in zip(rows, times)
                       if 0 <= time - start < args.seconds * 1_000_000]
            prepared.append((path.name, header, clipped))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, header, rows in prepared:
        with (args.output_dir / name).open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)
        print(f"{name}: {len(rows)} rows, interval=[0, {args.seconds}) s")


if __name__ == "__main__":
    main()
