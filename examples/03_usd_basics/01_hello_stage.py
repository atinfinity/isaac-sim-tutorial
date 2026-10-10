"""Stage を作り、Prim を定義して .usda ファイルに保存する。

実行方法:
    ホスト (uv):
        uv run python examples/03_usd_basics/01_hello_stage.py
    コンテナ内:
        cd /tmp
        /isaac-sim/python.sh /workspace/examples/03_usd_basics/01_hello_stage.py
"""

from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
stage_path = output_dir / "hello_stage.usda"

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
sphere.GetDisplayColorAttr().Set([Gf.Vec3f(0.2, 0.5, 0.9)])

# 独自の Attribute を追加することもできる
cube.GetPrim().CreateAttribute("tutorial:note", Sdf.ValueTypeNames.String).Set("はじめての Prim")

# 4. Stage の中身を確認する
for prim in stage.Traverse():
    print(f"{prim.GetPath()}  (型: {prim.GetTypeName()})")
    for attr in prim.GetAuthoredAttributes():
        print(f"    {attr.GetName()} = {attr.Get()}")

# 5. 保存する
stage.Save()
print(f"保存しました: {stage_path.resolve()}")
