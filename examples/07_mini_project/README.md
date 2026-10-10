# 7 章: ミニプロジェクト

> [!WARNING]
> **未検証**: このディレクトリのスクリプトは、Isaac Sim 6.1.0 の公式サンプルとソースコードをもとに書いた下書きです。まだ実機で動かしていません。
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

## 検証で確認したいこと

- [ ] エラーなく最後まで実行できる
- [ ] 「結果: 到着」と表示される。かかった時間を記録する (2D シミュレーションでは約 25 秒)
- [ ] 障害物にぶつからない (一番近づいた距離が 0.1 m 以上)
- [ ] `output/07_mini_project/trajectory.png` で、箱を避けてゴールに向かう経路が描かれている
- [ ] `--goal 3.0 0.8` と `--goal 2.5 -1.0` でも到着する
- [ ] `--livestream`: 走行の様子を短い動画で撮る (7 章の冒頭に載せる)
