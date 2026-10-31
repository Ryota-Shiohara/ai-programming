# 第5回：機械学習・回帰分析

## 進め方

まずデータと散布図だけを準備します。

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe lessons/05-machine-learning/prepare.py
```

`事前予想.md` に5-1と5-4の予想を自分の言葉で記入してから、以下を実行します。
未記入の間は学習を停止します。結果を見てから事前予想を書き換えないでください。

```powershell
.\.venv\Scripts\python.exe lessons/05-machine-learning/5-1.py
.\.venv\Scripts\python.exe lessons/05-machine-learning/5-2.py
.\.venv\Scripts\python.exe lessons/05-machine-learning/5-3.py
.\.venv\Scripts\python.exe lessons/05-machine-learning/5-4.py
```

モデルごとのCSVや設定は `output/5-1/`〜`output/5-4/` に保存されます。
表示されるAccuracyは窓単位の正解率です。Accuracy=正解した窓数÷評価した窓数。

## データと分割

- `prepare.py` は元の15試行から、第4回と同じ条件で特徴量を再生成し、`trial_id` を明示した `data/processed/05-machine-learning/features.csv` を作成します。第4回の生成済み表には依存しません。
- 元データはWalk / Jump / Squat各5試行。1秒=30サンプル、50%重複=15サンプル刻み。
- 全331窓。学習：各動作の1〜4試行目。評価：各動作の5試行目。
- 試行IDの一覧・窓数・区分は `split.csv` に保存。
- 全課題で同じ分割を使用し、評価用の正解率に応じた再分割や設定の調整はしない。
- 元試行ID・窓ID・ラベルは入力特徴量に含めない。
- 前回のデータには動作ごとの装着条件の違いがある。結果を動作だけの識別性能と解釈しない。
- 重複窓は独立した試行ではない。評価用は各動作1試行なので、Accuracyの安定性は今後検証が必要。

## 各課題の条件

| 課題 | 条件 |
| --- | --- |
| 5-1 | 標準偏差・最大値の2特徴量、標準化なしのロジスティック回帰 |
| 5-2 | 同じ2特徴量・モデルを使い、標準化なし／ありを比較 |
| 5-3 | 標準化付きロジスティック回帰、決定木、ランダムフォレスト、XGBoostを比較 |
| 5-4 | 標準化付きロジスティック回帰に固定し、A=標準偏差・最大値、B=A＋平均・FFTピーク周波数を比較 |

標準化はPipelineを使い、`fit` は学習用データだけに対して実施します。
決定木・ランダムフォレストは標準化しません。
XGBoostも標準化せず、200ラウンド・深さ3・学習率0.1で固定します。学習用でのみ作った整数ラベルの対応を用い、予測CSVには元の動作名で保存します。
評価データによるearly stoppingや、評価Accuracyに応じたパラメータ調整は行いません。
モデル設定は `common.py` に固定し、実際に使用した設定も各出力のJSONに保存します。
5-2・5-4は標準化の平均・標準偏差もCSVに保存します。
標準偏差は分母n、標準化も学習用母分散（ddof=0）を使用します。

## 特徴量の定義

各窓の重力分離済み加速度XYZから合成加速度 `a=sqrt(X²+Y²+Z²)` を計算しています。

| 特徴量 | 定義 | 単位 |
| --- | --- | --- |
| std | aの標準偏差（ddof=0） | m/s² |
| max | aの最大値 | m/s² |
| mean | aの平均 | m/s² |
| fft_peak_hz | aの平均を引いてHann窓を掛け、0Hz以外でFFT振幅が最大となる周波数 | Hz |

FFTは30点・公称30Hzなので周波数刻みは1Hz。最大のスペクトル成分であり、必ず基本周波数になるわけではありません。
第4回と同じ定義のその他の特徴量も表に保持しますが、各モデルへ渡す列は上記の条件に限定します。

## 提出準備

学習後に結果と照らし合わせ、各 `submissions/5-x/README.md` の考察を自分で記入します。
予想の原文・分割・設定・正解と予測のCSVを残し、第6回でも利用できるようにします。
`package_submissions.py` は学習結果とREADMEが揃ってから提出用ZIPを作成します。
提出用ZIPには `RUN.md` と `requirements.txt` は同梱しません。
5-1には特徴量・分割・散布図を生成する `prepare.py` を同梱します。元CSV15個は提出物に含めず、必要に応じて課題2-2のデータを入力に指定します。学習・評価は同梱の `features.csv` と `split.csv` から再実行できます。

```powershell
.\.venv\Scripts\python.exe lessons/05-machine-learning/package_submissions.py
```
