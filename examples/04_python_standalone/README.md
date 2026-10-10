# 4 章: Python スタンドアロン入門

> [!WARNING]
> **未検証**: このディレクトリのスクリプトは、Isaac Sim 6.1.0 の公式サンプルとソースコードをもとに書いた下書きです。まだ実機で動かしていません。

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

## 検証で確認したいこと

- [ ] 3 本とも、エラーなく最後まで実行できる
- [ ] `01`: Kit のバージョンと起動時間が表示される
- [ ] `02`: Stage のツリーが表示され、`/tmp/output/04_scene.usda` が保存される
- [ ] `02 --livestream`: Web ビューアで、赤い立方体が落下し、青い立方体が浮いたままになる様子が見える
- [ ] `03`: 立方体の高さが 2.0 m から減っていき、約 0.1 m (立方体の半分の大きさ) で止まる。2 回目のエピソードでも 2.0 m から始まる
