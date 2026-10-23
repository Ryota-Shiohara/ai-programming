"""第4回の必要ファイルを整理し、考察記入済みの課題をZIPにする。"""

from pathlib import Path
from shutil import copyfile
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[2]
    lesson = root / "lessons/04-preprocessing"
    data = root / "data/processed/04-preprocessing"
    for task in ("4-1", "4-2", "4-3", "4-4", "4-5"):
        folder = root / "submissions" / task
        folder.mkdir(parents=True, exist_ok=True)
        code = folder / f"{task}.py"
        copyfile(lesson / code.name, code)
        files = [code]
        if task in ("4-1", "4-4", "4-5"):
            image = folder / f"{task}.png"
            copyfile(lesson / "output" / image.name, image)
            readme = folder / "README.md"
            files.extend((image, readme))
            if task == "4-5":
                # 表への追加結果も同梱する。4-3の元の表は変更しない。
                table = folder / "features-with-frequency.csv"
                copyfile(data / table.name, table)
                files.append(table)
            if "【未記入】" in readme.read_text(encoding="utf-8"):
                print(f"{task}: README記入待ち。グラフとコードは準備済みです。")
                continue
        elif task == "4-2":
            source = root / "data/raw/02-data-collection/walk1.csv"
            copyfile(source, folder / source.name)
            files.append(folder / source.name)
            windows = sorted((data / "windows").glob("walk1_window*.csv"))
            if not windows:
                raise ValueError("先に4-2.pyを実行してください。")
            for source in windows:
                copyfile(source, folder / source.name)
                files.append(folder / source.name)
        else:
            copyfile(data / "features.csv", folder / "features.csv")
            files.append(folder / "features.csv")
        target = root / "submissions" / f"{task}.zip"
        with ZipFile(target, "w", ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.name)
        with ZipFile(target) as archive:
            assert archive.testzip() is None
            assert set(archive.namelist()) == {path.name for path in files}
            for path in files:
                assert archive.read(path.name) == path.read_bytes()
        print(f"{task}.zip: 作成・確認済み（{len(files)}ファイル）")


if __name__ == "__main__":
    main()
