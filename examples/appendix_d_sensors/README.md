# 付録 D: その他のセンサ

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) で、ヘッドレスで実行して動作を確認しました。`03_radar.py` は、検証環境では Motion BVH が有効にならないため、サポート外の設定 (`--without-motion-bvh`) で動かしています。

| ファイル | 内容 |
| --- | --- |
| `01_imu.py` | Jetbot に IMU を後付けし、回転・前進したときの加速度・角速度・姿勢を記録する |
| `02_contact.py` | Jetbot に接触センサを後付けし、壁にぶつかったことを検出する |
| `03_radar.py` | Jetbot にレーダを後付けし、前方の箱までの距離と近づく速さ (ドップラー速度) を測る |

## 実行方法

リポジトリのルートで実行します。記録 (CSV と図) は `--output` で指定した場所に保存されます。保存先の考え方は 6 章のサンプルと同じです。

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/appendix_d_sensors/01_imu.py --output /isaac-sim/.local/share/ov/data/output/appendix_d_imu
# 記録はホストの ~/docker/isaac-sim/data/output/appendix_d_imu/ にできる
```

`01_imu.py` は `--solver PGS` で、物理エンジンのソルバを PGS に変えて実行できます (既定は Jetbot のアセットと同じ TGS)。

`03_radar.py` は、Motion BVH が有効にならない GPU (検証環境の RTX 2080 Ti など) では、`--without-motion-bvh` を付けないと起動時に `Running radar without MotionBVH is disallowed` というエラーで止まります。

## 検証で確認したこと

- [x] 3 本とも、エラーなく最後まで実行できる (`03` は `--without-motion-bvh` を付けた場合)
- [x] `01`: 静止時の加速度が約 `[0.05, 0, 9.81]` m/s² になる。前進を始めた瞬間と止まった瞬間に x 方向の加速度が大きくなる
- [x] `01`: TGS (既定) では、左回転で向きが 74.9 度変わるのに対し、角速度 (z) の積分は 97.4 度になる。静止中も y 軸まわりの角速度が約 -0.4 rad/s のまま (車体の剛体の角速度も同じ値。速度の反復回数を 8 にしても変わらない)
- [x] `01 --solver PGS`: 向きの変化 70.4 度と角速度の積分 71.1 度がほぼ一致する。ただし静止中も加速度・角速度が振動する (加速度 z の標準偏差は約 5.9 m/s²。速度の反復回数を 8 にしても変わらない)
- [x] `02`: 走行中は床との接触だけ (力 約 4.28 N、接触点 6)。3.33 秒に `/World/Wall` との接触が現れ、力が約 22.7 N になる。Jetbot は x = 0.679 m で止まる
- [x] `03 --without-motion-bvh`: 距離が正解 (箱の面まで) と 0.01〜0.02 m の差で一致し、前進中の相対速度が -0.218 m/s (正解と同じ) になる。箱を遠く (`BOX_FACE_X = 3.75`) にしても同様
- [x] `03 --without-motion-bvh`: 箱を斜め前 (`positions=[2.0, 0.5, 0.25]`) に置くと検出されず、距離 100 m・`scalar` -60 の点が 1 個だけ返る
- [x] `03` (`--without-motion-bvh` なし): `Running radar without MotionBVH is disallowed` で止まる。公式サンプル `inspect_radar_gmo.py` も同じ
- [x] `03`: `--/renderer/raytracingMotion/enabled=true` などの引数を直接渡しても同じエラーで止まる。実行中の設定値 `/renderer/raytracingMotion/enabled` は `True`
- [x] `03`: 検証環境の GPU (RTX 2080 Ti) の Vulkan ドライバは `VK_NV_ray_tracing_motion_blur` を提供していない (`VK_KHR_ray_tracing_pipeline` などはある)。Isaac Sim の `libcarb.graphics-vulkan.plugin.so` はこの拡張機能の名前を含む
- [x] GPU メモリの使用量 (GPU 全体、最大): `01`・`02` は約 2.4GB、`03` は約 6.9GB。VRAM 11GB に収まる
- [ ] Motion BVH が有効になる GPU での `03` は試していない (手元にそのような GPU がない)
