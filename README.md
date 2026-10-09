# 人工知能プログラミング

授業の演習と最終プロジェクトを管理するリポジトリです。

## ディレクトリ構成

```text
lessons/      各回の演習コード・ノート
data/         演習で共通して使うデータと計測条件
project/      最終課題の実装・発表資料・レポート
submissions/  提出用にまとめたファイル
```

`lessons/` は授業の進行に合わせてフォルダを追加します。
元のデータは `data/raw/` に残し、ラベル付与・前処理後のデータは `data/processed/` に保存します。
提出用ファイルは課題番号（例：`2-3.py`、`2-2.zip`）で命名します。

## Python環境の準備（Windows / PowerShell）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

必要なライブラリは `requirements.txt` に追加します。
演習プログラムは、リポジトリのルートから実行する想定です。

```powershell
python lessons/02-data-collection/2-3.py
```

上記の演習ファイルは、課題に取り組む際に作成してください。

## 授業メモ

- 第1回：概論と環境構築
- 第2回：データ取得
- 第3回：可視化
- 第4回：前処理・特徴量抽出
- 第5回：機械学習・回帰分析
- 第6回：検証
- 第7回：深層学習
- 第8回：実世界システム構築
- 第9回以降：プロジェクト課題・総合的議論

講義PDFはOneDriveで管理します。
