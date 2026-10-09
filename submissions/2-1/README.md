# 課題2-1：センサの挙動

LCLab Streamでセンサの挙動を確認したスクリーンショットを保存します。

## 操作の順序

各センサについて、横揺れ → 縦揺れ → 高さ揺れを連続で行い、グラフをスクリーンショットに記録します。
この順序は操作の順序であり、センサのX・Y・Z軸との対応を示すものではありません。

## 保存先

- `motion/`：動き
- `orientation/`：姿勢・向き
- `sound/`：音
- `gps/`：位置・GPS（提出は任意）

## 保存済みの画像

- `motion/linear-acceleration.png`：加速度（重力分離）。横揺れ → 縦揺れ → 高さ揺れを連続で実施。
- `motion/total-acceleration.png`：全加速度（重力含む全値）。
- `motion/gyroscope.png`：角速度。
- `orientation/gravity-vector.png`：推定重力ベクトル。
- `orientation/attitude-quaternion.png`：姿勢（クォータニオン）。
- `orientation/euler-angles.png`：姿勢オイラー角。
- `orientation/compass-heading.png`：コンパス方位角。
- `sound/microphone-level.png`：マイク信号レベルと振幅実効値（RMS）。
