# 5 章: ロボットを動かす

> [!WARNING]
> **未検証**: このディレクトリのスクリプトは、Isaac Sim 6.1.0 の公式サンプルとソースコードをもとに書いた下書きです。まだ実機で動かしていません。

| ファイル | 内容 |
| --- | --- |
| `01_load_jetbot.py` | Jetbot を読み込み、Prim の構造・リンク・関節 (DOF) を表示する |
| `02_drive_jetbot.py` | 差動二輪のコントローラで、直進 → 左に 90 度旋回 → 直進 と走らせる |
| `03_go_to_goal.py` | 位置と向きから速度を計算し、目標地点まで自動で走らせる (障害物なし) |

## 実行方法

リポジトリのルートで実行します。

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/05_robot_control/01_load_jetbot.py
```

`02` と `03` は `--livestream` を付けると Web ビューアで画面を見られます。手順は [4 章の README](../04_python_standalone/README.md) と同じです (先に `isaac-sim` サービスを止め、`web-viewer` だけを起動します)。

## 検証で確認したいこと

- [ ] 3 本とも、エラーなく最後まで実行できる
- [ ] `01`: Prim の構造に `chassis`・`left_wheel`・`right_wheel` が表示される
- [ ] `01`: DOF が 2 個 (`left_wheel_joint`, `right_wheel_joint`) と表示される
- [ ] `01`: 指令なしで 1 秒進めても、位置がほぼ (0, 0) のまま
- [ ] `02`: 直進の後 x ≈ 0.6 m、旋回の後 向き ≈ 90 度、2 回目の直進の後 y ≈ 0.6 m になる (車輪の滑りでずれてもよい。ずれ幅を記録する)
- [ ] `02`: `simulation_app.update()` 1 回で物理が 1/60 秒進んでいるか (表示される移動距離から確かめる)
- [ ] `03`: 「到着しました」と表示される。かかった時間を記録する
- [ ] `--livestream`: Jetbot が走る様子が Web ビューアで見える (スクリーンショットか短い動画を撮る)
