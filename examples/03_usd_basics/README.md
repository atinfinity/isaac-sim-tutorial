# 3 章: USD の基礎

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) と、ホストの `usd-core` (uv) の両方で実行して動作を確認しました。

| ファイル | 内容 |
| --- | --- |
| `01_hello_stage.py` | Stage を作り、Prim (Xform・Cube・Sphere) を定義して `.usda` に保存する |
| `02_xform_hierarchy.py` | Xform の親子関係と、ローカル座標・ワールド座標の違いを確かめる |
| `03_reference.py` | コーンのアセットを Reference で 2 つ読み込み、片方だけ色を上書きする |
| `04_units_and_rotation.py` | 角度と四元数、`rotateZ` と `orient`、`metersPerUnit` の違いを確かめる |

この章のスクリプトは `SimulationApp` を起動せず、USD のライブラリ (`pxr`) だけを使います。そのため GPU のない PC でも、ホストの Python で実行できます。

## 実行方法

どちらの方法でも、カレントディレクトリの `output/` に `.usda` ファイルが保存されます。

### ホストで実行する (uv)

リポジトリのルートで実行します。`usd-core` は `dev` グループに入っているので、`uv sync` で入ります。

```bash
uv sync
uv run python examples/03_usd_basics/01_hello_stage.py
```

`01_hello_stage.py` の部分を `02_xform_hierarchy.py` などに変えれば、ほかのスクリプトも実行できます。

### コンテナ内で実行する

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint bash isaac-sim
```

コンテナに入ったら、`pxr` の場所を設定してから実行します。

```bash
export PYTHONPATH=$(ls -d /isaac-sim/extscache/omni.usd.libs-*)
export LD_LIBRARY_PATH=$PYTHONPATH/bin
cd /tmp
/isaac-sim/python.sh /workspace/examples/03_usd_basics/01_hello_stage.py
```

- 最初の 2 行がないと `ModuleNotFoundError: No module named 'pxr'` になります (付録 B の「`No module named 'pxr'`」を参照)
- `examples/` は読み取り専用でマウントしているので、書き込める `/tmp` に移動してから実行します。保存したファイルはコンテナを抜けると消えます

## 検証で確認したこと

- [x] 4 本とも、ホスト (uv) とコンテナ内の両方で、エラーなく最後まで実行できる
- [x] `output/` に `hello_stage.usda`・`xform_hierarchy.usda`・`traffic_cone.usda`・`scene_with_references.usda`・`units_and_rotation.usda` ができる
- [x] `02`: Sensor のワールド位置が `(1, 0.2, 0.1)` になり、Cart を動かすと `(2, 0.2, 0.1)` になる
- [x] `03`: `Cone_0` はオレンジ `(1, 0.5, 0)`、`Cone_1` は上書きした緑 `(0.1, 0.8, 0.1)` になる
- [x] `04`: `rotateZ = 90` と四元数 `(0.7071, 0, 0, 0.7071)` が同じ回転と判定される
- [x] コンテナ内で `PYTHONPATH` と `LD_LIBRARY_PATH` を設定しないと、実行に失敗する
