# 7 章: ミニプロジェクト

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) で、ヘッドレスで実行して動作を確認しました。`--livestream` での表示はまだ確認していません。
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

`--goal 3.0 0.8` のようにゴールを変えたり、`--livestream` で Web ビューアから見たりできます。

## 検証で確認したこと

- [x] エラーなく最後まで実行できる
- [x] 「結果: 到着」と表示される (29.7 秒。2D シミュレーションでは約 25 秒)
- [x] 障害物にぶつからない (一番近づいた距離 0.16 m)
- [x] `output/07_mini_project/trajectory.png` で、箱を避けてゴールに向かう経路が描かれている
- [x] `--goal 3.0 0.8` (16.7 秒) と `--goal 2.5 -1.0` (13.8 秒) でも到着する

同じ設定でも、到着までの時間は実行するたびに少し変わります。
- [ ] `--livestream`: 走行の様子を短い動画で撮る (7 章の冒頭に載せる)
