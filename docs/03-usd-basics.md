# 3. USD の基礎

!!! info "この章で学ぶこと"
    Isaac Sim のシーンを表現している USD の基本概念 (Stage・Prim・Attribute・Xform・Reference) を、Python で実際にファイルを作りながら理解します。

    - **所要時間**: 30 分
    - **前提**: 2 章
    - **対象バージョン**: Isaac Sim 6.1.0

## USD とは

**USD (Universal Scene Description)** は、Pixar が開発した 3D シーンの記述形式です。Isaac Sim で扱うシーンやロボット、環境は、すべて USD で表現されています。2 章で GUI から保存したファイルも USD です。

USD を理解しておくと、次のことが分かるようになります。

- GUI の **Stage** パネルに並んでいるツリーが何を表しているのか
- Python から物体の位置や色を変えるとき、何を操作しているのか
- ロボットのアセットをシーンに「読み込む」とは、何をしているのか

USD のファイルには主に次の拡張子があります。

| 拡張子 | 形式 | 用途 |
| --- | --- | --- |
| `.usda` | テキスト | 人が読める。学習やデバッグ向き |
| `.usdc` | バイナリ | 読み込みが速く、サイズが小さい |
| `.usd` | どちらでもよい | 中身はテキストかバイナリのどちらか |

この章では、中身を読めるように `.usda` を使います。

!!! tip "この章のサンプルは Isaac Sim なしでも動きます"
    USD は Isaac Sim とは独立したライブラリなので、この章のサンプルは Pixar の `usd-core` パッケージだけで動きます。GPU のない PC でも試せます。

    === "ホスト (uv)"

        ```bash
        uv sync
        uv run python examples/03_usd_basics/01_hello_stage.py
        ```

    === "コンテナ内"

        ```bash
        cd /tmp
        /isaac-sim/python.sh /workspace/examples/03_usd_basics/01_hello_stage.py
        ```

        `examples/` は読み取り専用でマウントしているので、出力先を書き込み可能な `/tmp` にしています。

    どちらの場合も、カレントディレクトリの `output/` に `.usda` ファイルが保存されます。

## Stage と Prim

### Stage

**Stage** は、1 つのシーン全体を表す入れ物です。Isaac Sim の GUI で開いているシーンが 1 つの Stage にあたります。

### Prim

**Prim** (Primitive) は、Stage の中に置かれる要素です。ロボット、床、ライト、カメラ、それらをまとめるグループなど、シーンに置かれるものはすべて Prim です。

Prim は次の 2 つの情報を持ちます。

- **パス**: `/World/Cube` のように、ファイルシステムと同じ形で階層を表す
- **型**: `Xform` (グループ化と座標変換)、`Cube`、`Sphere`、`Camera` など

GUI の Stage パネルに表示されているツリーは、この Prim の階層そのものです。

### Attribute

**Attribute** (属性) は、Prim が持つ値です。立方体の大きさ (`size`)、球の半径 (`radius`)、色 (`primvars:displayColor`) などがあります。

### コードで確かめる

`examples/03_usd_basics/01_hello_stage.py` で、Stage を作って Prim を 3 つ定義します。

```python title="examples/03_usd_basics/01_hello_stage.py (抜粋)"
# 1. 新しい Stage を作る
stage = Usd.Stage.CreateNew(str(stage_path))

# Isaac Sim と同じく Z 軸を上、1 単位 = 1 m にする
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)

# 2. Prim を定義する (パス + 型)
world = UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(world.GetPrim())

cube = UsdGeom.Cube.Define(stage, "/World/Cube")
sphere = UsdGeom.Sphere.Define(stage, "/World/Sphere")

# 3. Attribute (属性) を設定する
cube.GetSizeAttr().Set(0.5)
cube.GetDisplayColorAttr().Set([Gf.Vec3f(0.9, 0.3, 0.2)])
sphere.GetRadiusAttr().Set(0.25)
```

実行すると、Stage 内の Prim とその Attribute が表示されます。

```text
/World  (型: Xform)
/World/Cube  (型: Cube)
    primvars:displayColor = [(0.9, 0.3, 0.2)]
    size = 0.5
    tutorial:note = はじめての Prim
/World/Sphere  (型: Sphere)
    primvars:displayColor = [(0.2, 0.5, 0.9)]
    radius = 0.25
```

保存された `output/hello_stage.usda` をテキストエディタで開いてみましょう。

```usda title="output/hello_stage.usda"
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Z"
)

def Xform "World"
{
    def Cube "Cube"
    {
        color3f[] primvars:displayColor = [(0.9, 0.3, 0.2)]
        double size = 0.5
        custom string tutorial:note = "はじめての Prim"
    }

    def Sphere "Sphere"
    {
        color3f[] primvars:displayColor = [(0.2, 0.5, 0.9)]
        double radius = 0.25
    }
}
```

- 先頭の `( ... )` は Stage 全体の設定 (メタデータ) です
- `def <型> "<名前>"` が Prim の定義で、`{ }` の入れ子がそのまま階層になっています
- `{ }` の中に Attribute が `型 名前 = 値` の形で並んでいます

!!! note "Isaac Sim の座標系と単位"
    Isaac Sim では **Z 軸が上**、**1 単位 = 1 m** を標準としています。USD 自体は Y 軸が上の Stage も扱えるため、自分で Stage を作るときは `upAxis` と `metersPerUnit` を明示しておくと安全です。

## Xform と座標系

### Xform

**Xform** は、子の Prim をまとめて、位置・回転・スケールを与える Prim です。ロボット全体を動かしたいときは、ロボットのルートにある Xform を動かします。

位置や回転は **xformOp** という Attribute で表します。

| xformOp | 意味 |
| --- | --- |
| `xformOp:translate` | 平行移動 |
| `xformOp:rotateXYZ`、`xformOp:rotateZ` など | 回転 (度) |
| `xformOp:orient` | 回転 (クォータニオン) |
| `xformOp:scale` | 拡大縮小 |

複数の xformOp をどの順で適用するかは、`xformOpOrder` という Attribute で決まります。

### 親子関係とローカル・ワールド座標

子の Prim の位置は、**親から見た位置** (ローカル座標) で書かれます。Stage 全体から見た位置 (ワールド座標) は、親の変換をすべて掛け合わせて求めます。

`examples/03_usd_basics/02_xform_hierarchy.py` では、台車 (`Cart`) の上にセンサ (`Sensor`) を載せています。

```python title="examples/03_usd_basics/02_xform_hierarchy.py (抜粋)"
# 親: 台車 (x 方向に 1 m 移動し、z 軸まわりに 90 度回転)
cart = UsdGeom.Xform.Define(stage, "/World/Cart")
cart.AddTranslateOp().Set(Gf.Vec3d(1.0, 0.0, 0.0))
cart.AddRotateZOp().Set(90.0)

# 子: 台車の上に載ったセンサ (親から見て x 方向に 0.2 m、z 方向に 0.1 m)
sensor = UsdGeom.Cube.Define(stage, "/World/Cart/Sensor")
sensor.AddTranslateOp().Set(Gf.Vec3d(0.2, 0.0, 0.1))
```

実行結果は次のとおりです。

```text
Cart の xformOpOrder: [xformOp:translate, xformOp:rotateZ]
Sensor のローカル位置: (0.2, 0, 0.1)
Sensor のワールド位置: (1, 0.2, 0.1)
Cart を x = 2.0 に動かした後の Sensor のワールド位置: (2, 0.2, 0.1)
```

- センサは台車から見ると x 方向に 0.2 m の位置にあります
- 台車が 90 度回転しているので、ワールド座標では y 方向に 0.2 m ずれた位置になります
- 台車を動かすと、センサも一緒に動きます

この考え方は、5 章でロボットを動かすときや、6 章でロボットにセンサを取り付けるときにそのまま使います。

## Reference でアセットを読み込む

### Reference とは

**Reference** は、別の USD ファイルの内容を、Stage の中の Prim として取り込む仕組みです。Isaac Sim でロボットや環境のアセットをシーンに「読み込む」ときは、内部でこの Reference を使っています。

Reference には次の特徴があります。

- 同じアセットを何度でも配置できる
- 元のファイルはコピーされず、参照されるだけ
- 読み込んだ側で値を上書き (オーバーライド) しても、元のファイルは変わらない

### コードで確かめる

`examples/03_usd_basics/03_reference.py` では、コーンのアセットファイルを作り、それをシーンに 2 つ配置します。さらに、2 つ目のコーンだけ色を上書きします。

```python title="examples/03_usd_basics/03_reference.py (抜粋)"
for i, x in enumerate([0.0, 1.0]):
    cone = UsdGeom.Xform.Define(stage, f"/World/Cone_{i}")
    # シーンファイルからの相対パスで参照する
    cone.GetPrim().GetReferences().AddReference(f"./{asset_path.name}")
    cone.AddTranslateOp().Set(Gf.Vec3d(x, 0.0, 0.25))

# 3. 2 つ目のコーンだけ色を上書きする (元のアセットファイルは変わらない)
override = UsdGeom.Cone(stage.GetPrimAtPath("/World/Cone_1/Body"))
override.GetDisplayColorAttr().Set([Gf.Vec3f(0.1, 0.8, 0.1)])
```

保存されたシーンファイルの中身は次のようになります。

```usda title="output/scene_with_references.usda (抜粋)"
def Xform "World"
{
    def Xform "Cone_0" (
        prepend references = @./traffic_cone.usda@
    )
    {
        double3 xformOp:translate = (0, 0, 0.25)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }

    def Xform "Cone_1" (
        prepend references = @./traffic_cone.usda@
    )
    {
        double3 xformOp:translate = (1, 0, 0.25)
        uniform token[] xformOpOrder = ["xformOp:translate"]

        over "Body"
        {
            color3f[] primvars:displayColor = [(0.1, 0.8, 0.1)]
        }
    }
}
```

- シーンファイルには、コーンの形 (`Cone` の高さや半径) は書かれていません。`references` で `traffic_cone.usda` を参照しているだけです
- 上書きした色は `over "Body"` として、差分だけが記録されています

!!! tip "Isaac Sim のアセットも同じ仕組み"
    4 章以降では、Jetbot のアセットを次のように読み込みます。

    ```python
    stage_utils.add_reference_to_stage(usd_path=jetbot_asset_path, path="/World/Jetbot")
    ```

    関数名のとおり、ここで行っているのは「Stage に Reference を追加すること」です。

<!-- TODO(実機検証待ち): 生成した .usda を Isaac Sim の GUI で開き、Stage パネルとの対応を示すスクリーンショットを追加する -->

## まとめ

- Isaac Sim のシーンは USD で表現されている
- **Stage** はシーン全体、**Prim** はその中の要素で、`/World/Cube` のようなパスで階層を表す
- Prim の値は **Attribute** として持つ
- **Xform** は位置・回転・スケールを与え、子の位置は親から見たローカル座標で表す
- **Reference** で別ファイルのアセットを取り込み、差分だけを上書きできる

## 演習

1. `01_hello_stage.py` に円柱 (`UsdGeom.Cylinder`) を追加し、保存された `.usda` にどう現れるかを確認してください。
2. `02_xform_hierarchy.py` で台車の回転を 180 度に変えると、センサのワールド位置はどうなるでしょうか。実行する前に予想してから確かめてください。
3. `03_reference.py` で、`traffic_cone.usda` 側のコーンの高さを変えて実行し、シーン側の 2 つのコーンが両方とも変わることを確認してください。

## 参考リンク

- [OpenUSD 公式ドキュメント](https://openusd.org/release/index.html)
- [OpenUSD Terms and Concepts (用語集)](https://openusd.org/release/glossary.html)
- [usd-core (PyPI)](https://pypi.org/project/usd-core/)
- [Isaac Sim ドキュメント](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/index.html)
