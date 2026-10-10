# 6 章: センサ

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) で、ヘッドレスで実行して動作を確認しました。`--livestream` での表示はまだ確認していません。

| ファイル | 内容 |
| --- | --- |
| `01_camera.py` | Jetbot に付いているカメラから RGB 画像と Depth 画像を取得し、PNG で保存する |
| `02_lidar.py` | Jetbot に 2D LiDAR (`Example_Rotary_2D`) を後付けし、前後左右の物体までの距離を測る |

## 実行方法

リポジトリのルートで実行します。画像や図はコンテナの `/tmp/output/` に保存されるので、ホストから見られるようにボリュームを追加します。

```bash
mkdir -p output
docker compose -f docker/compose.yml run --rm --no-deps -v "$PWD/output:/tmp/output" \
  --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/06_sensors/01_camera.py
```

保存先のディレクトリはコンテナのユーザ (uid 1234) が書き込める必要があります。書き込めない場合は `sudo chown 1234:1234 output` を実行してください。

## 検証で確認したこと

- [x] 2 本とも、エラーなく最後まで実行できる
- [x] `01`: 何フレーム目でデータを取得できたかが表示される (3 フレーム目)
- [x] `01`: `output/06_camera/rgb.png` に赤と青の立方体が写っている (画像の上下は黒い帯になる)
- [x] `01`: `output/06_camera/depth.png` で、手前の赤い立方体が奥の青い立方体より近い色になっている
- [x] `02`: 点の数が 0 より大きい (約 14 万点。**RTX 2080 Ti でも RTX LiDAR は動く**)
- [x] `02`: 方位角が -180〜180 度の範囲で表示される
- [x] `02`: 距離が 前 0.85 m・左 0.45 m・後 1.45 m・右 inf になる (箱の面までの距離)
- [x] `02`: `output/06_lidar/scan.png` に 3 つの物体の形が見える

`Example_Rotary_2D` の設定のままでは、近い物体を検出しません (`nearRangeM = 1` と `minDistBetweenEchosM = 0.4` のため。前と左の箱が inf になる)。`02_lidar.py` では、この 2 つを変えています。終了時に `GMO magic number is not correct` という行が出ますが、結果には影響しません。
- [ ] `02 --livestream`: LiDAR の点群が Web ビューアに描かれる
