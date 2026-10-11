# 5 章: ロボットを動かす

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) で、ヘッドレスで実行して動作を確認しました。`--livestream` での表示も Web ビューアで確認しました。

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

`--livestream` のときは、Web ビューアで再生 (▶) を押すまで動き出しません (接続する前に動き終わらないようにするため)。接続した直後の画面が黒いままのときは、ビューポートの上でマウスを動かすと表示されます。

## 検証で確認したこと

- [x] 3 本とも、エラーなく最後まで実行できる
- [x] `01`: Prim の構造に `chassis`・`left_wheel`・`right_wheel` が表示される
- [x] `01`: DOF が 2 個 (`left_wheel_joint`, `right_wheel_joint`) と表示される
- [x] `01`: 指令なしで 1 秒進めても、位置がほぼ (0, 0) のまま (`[-0. 0. 0.033]`)
- [x] `02`: 直進の後 x = 0.646 m、旋回の後 向き = 74.0 度、2 回目の直進の後 (x, y) = (0.822, 0.617) m。**旋回は 90 度より 16 度ほど足りない** (車輪の滑りと思われる)
- [x] `02`: `simulation_app.update()` 1 回で物理が 1/60 秒進んでいる (直進 1 回の移動距離が 0.646 m で、0.2 m/s × 3 秒 = 0.6 m とほぼ一致する)
- [x] `03`: 「到着しました」と表示される (9.4 秒)
- [x] `02 --livestream`: 直進 → 旋回 → 直進 と走る様子が Web ビューアで見える (Jetbot は画面の中央に小さく映る)
- [x] `03 --livestream`: Jetbot が緑のゴールまで走って止まる様子が見える (9.4 秒)
