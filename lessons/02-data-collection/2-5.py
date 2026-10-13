"""課題2-5：移動・田植えのCSVに英語の動作ラベルを付与する。"""

import csv
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2]
    source_dir = root / "data/raw/02-data-collection-bonus"
    output_dir = root / "data/processed/02-data-collection-bonus"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 元ファイル名のtaueは、英語ラベルplantに対応する。
    for prefix, label in (("move", "move"), ("taue", "plant")):
        for trial in range(1, 6):
            source_path = source_dir / f"{prefix}{trial}.csv"
            with source_path.open(encoding="utf-8-sig", newline="") as source:
                reader = csv.reader(source)
                header = next(reader)
                if "label" in header:
                    raise ValueError(f"すでにlabel列があります: {source_path.name}")
                rows = [row for row in reader if row]
                if any(len(row) != len(header) for row in rows):
                    raise ValueError(f"列数が不揃いです: {source_path.name}")

            with (output_dir / source_path.name).open(
                "w", encoding="utf-8", newline=""
            ) as output:
                writer = csv.writer(output)
                writer.writerow(header + ["label"])
                writer.writerows(row + [label] for row in rows)
            print(f"{source_path.name}: {label} ({len(rows)}行)")


if __name__ == "__main__":
    main()
