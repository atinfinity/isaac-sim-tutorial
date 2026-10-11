# 7 章: ミニプロジェクト

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) で、ヘッドレスで実行して動作を確認しました。`--livestream` での表示も Web ビューアで確認しました。
> 回避の考え方 (候補の方向ごとに、ロボットの幅の通路が空いているかを調べる) は、Isaac Sim を使わない簡易な 2D シミュレーションで確かめてあります。

| ファイル | 内容 |
| --- | --- |
| `lidar_obstacle_avoidance.py` | LiDAR で障害物を避けながら、Jetbot をゴールへ向かわせる。走った経路を図に保存する |

## 実行方法

リポジトリのルートで実行します。

```bash
mkdir -p output
docker compose -f docker/compose.yml run --rm --no-deps -v "$PWD/output:/tmp/output" \
  --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/07_mini_project/lidar_obstacle_avoidance.py
```

`--goal 3.0 0.8` のようにゴールを変えたり、`--livestream` で Web ビューアから見たりできます。`--livestream` のときは、スタートからゴールまでを斜め上から見下ろす視点にし、LiDAR の点群も描きます。Web ビューアで再生 (▶) を押すと走り始めます。

## 検証で確認したこと

- [x] エラーなく最後まで実行できる
- [x] 「結果: 到着」と表示される (29.7 秒。2D シミュレーションでは約 25 秒)
- [x] 障害物にぶつからない (一番近づいた距離 0.16 m)
- [x] `output/07_mini_project/trajectory.png` で、箱を避けてゴールに向かう経路が描かれている
- [x] `--goal 3.0 0.8` (16.7 秒) と `--goal 2.5 -1.0` (13.8 秒) でも到着する
- [x] `--livestream`: 箱を避けてゴールに着く様子と、箱の面に描かれる LiDAR の点が Web ビューアで見える (25.9 秒・33.5 秒で到着、一番近づいた距離 0.16 m)。走行の動画を `docs/assets/07-mini-project/lidar-obstacle-avoidance.mp4` に置いた

同じ設定でも、到着までの時間は実行するたびに少し変わります。
