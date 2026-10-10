# 4 章: Python スタンドアロン入門

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) で実行して動作を確認しました。

| ファイル | 内容 |
| --- | --- |
| `01_hello_simulation_app.py` | SimulationApp を起動・終了するだけの最小のスクリプト |
| `02_build_scene.py` | 地面・ライト・立方体を配置してシーンを保存する。`--livestream` を付けると Web ビューアで画面を見られる |
| `03_step_simulation.py` | 物理を 1 ステップずつ進め、落下する立方体の高さを表示する |

## 実行方法

リポジトリのルートで実行します。

### ヘッドレスで実行する

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/04_python_standalone/01_hello_simulation_app.py
```

`01_hello_simulation_app.py` の部分を `02_build_scene.py` や `03_step_simulation.py` に変えれば、ほかのスクリプトも実行できます。

### Web ビューアで画面を見ながら実行する

`isaac-sim` サービスとスクリプトが同じストリーミング用ポートを使うため、先に `isaac-sim` サービスを止めておきます。

```bash
docker compose -f docker/compose.yml stop isaac-sim
docker compose -f docker/compose.yml up -d --no-deps web-viewer

docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/04_python_standalone/02_build_scene.py --livestream
```

ブラウザで `http://localhost:8210` を開きます。スクリプトを終了するには `Ctrl+C` を押します。

## 検証で確認したこと

- [x] 3 本とも、エラーなく最後まで実行できる
- [x] `01`: Kit のバージョン (`110.3.0`) と起動時間 (38.2 秒) が表示される
- [x] `02`: Stage のツリーが表示され、`/tmp/output/04_scene.usda` が保存される
- [x] `02 --livestream`: Web ビューアで、赤い立方体が地面の上にあり、青い立方体が浮いたままになっている。Stage に `PhysicsScene` がある
- [x] `03`: 立方体の高さが 1.997 m から減っていき、0.100 m (立方体の半分の大きさ) で止まる。2 回目のエピソードでも 1.997 m から始まる
