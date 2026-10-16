"""第3回の提出用ZIPを更新する。未記入の考察は提出用ZIPにしない。"""

from pathlib import Path
from shutil import copyfile
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[2]
    for task in ("3-1", "3-2", "3-3", "3-4"):
        folder = root / "submissions" / task
        copyfile(root / "lessons/03-visualization" / f"{task}.py", folder / f"{task}.py")
        if task == "3-3":
            for source in (root / "data/processed/03-visualization/6-seconds").glob("*.csv"):
                copyfile(source, folder / source.name)
        else:
            copyfile(root / "lessons/03-visualization/output" / f"{task}.png",
                     folder / f"{task}.png")
        readme = folder / "README.md"
        if "【未記入】" in readme.read_text(encoding="utf-8"):
            print(f"{task}: READMEの記入後にZIPを作成できます。")
            continue
        files = sorted(path for path in folder.iterdir() if path.is_file())
        assert (folder / f"{task}.py").is_file()
        if task == "3-3":
            assert len(list(folder.glob("*.csv"))) == 15
        else:
            assert (folder / f"{task}.png").is_file()
        with ZipFile(root / "submissions" / f"{task}.zip", "w", ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.name)
        with ZipFile(root / "submissions" / f"{task}.zip") as archive:
            assert archive.testzip() is None
            assert set(archive.namelist()) == {path.name for path in files}
            for path in files:
                assert archive.read(path.name) == path.read_bytes()
        print(f"{task}.zip: 作成しました。")


if __name__ == "__main__":
    main()
