# 第3回：可視化

第2回の元データを使い、課題3-1〜3-4のグラフと切り出しデータを作成します。
提出用READMEには、本人がグラフを見て考えた特徴・共通点・相違点・考察を反映済みです。

## 実行方法

リポジトリのルートから実行します。

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe lessons/03-visualization/3-1.py
.\.venv\Scripts\python.exe lessons/03-visualization/3-2.py
.\.venv\Scripts\python.exe lessons/03-visualization/3-3.py
.\.venv\Scripts\python.exe lessons/03-visualization/3-4.py
```

仮想環境がない場合は、先に `python -m venv .venv` を実行してください。
グラフは画面表示せずPNGとして `output/` に保存します。
CSVの入力先や画像の出力先は各プログラムの `--help` で確認できます。

## 使用データ・計算方法

| 課題 | 使用データ | 処理 |
| --- | --- | --- |
| 3-1 | `jump1.csv` 全体 | 加速度XYZの時系列グラフ |
| 3-2 | `jump1.csv`〜`jump5.csv` 全体 | 合成加速度を共通の軸範囲で5段に表示 |
| 3-3 | Walk / Jump / Squat 全15試行 | 各試行の開始から6秒間を切り出す |
| 3-4 | 3-3で切り出した15試行 | 各試行の合成加速度の標準偏差を求め、動作別の箱ひげ図にする |

- 加速度は重力分離済みの `acc_x`・`acc_y`・`acc_z` を使用します。
- 時間は `timestamp_us` の先頭値を引き、1,000,000で割って秒に変換します。
- 合成加速度は `sqrt(acc_x**2 + acc_y**2 + acc_z**2)` です。
- 標準偏差は各試行の合成加速度の全サンプルに対して `numpy.std(..., ddof=0)` で計算します。
- 箱ひげ図の1点は「1試行の標準偏差」です。1動作に5点あります。
- 3-3は `[0, 6)` 秒を採用し、元の列・値・タイムスタンプを保持します。補間や水増しはしません。
- 第2回の記録時間の不揃いは元データに残っています。今回の6秒への切り出しで、第2回の「各10秒」の条件を満たすことにはなりません。

## 自分で考察を書く

1. グラフを開き、まず目で確認します。
2. `観察メモ.md` を参考に、気づいた位置・軸・違いをメモします。
3. `submissions/3-1/README.md`、`3-2/README.md`、`3-4/README.md` に自分の言葉でまとめます（今回分は記入済み）。
4. 修正後に以下を実行すると、READMEを含めて提出用ZIPを更新できます。

```powershell
.\.venv\Scripts\python.exe lessons/03-visualization/package_submissions.py
```

`【未記入】` が残っている場合は、その課題のZIPを作成しない仕組みです。
