"""Reference で別ファイルのアセットを読み込み、読み込み先で値を上書きする。

実行方法:
    ホスト (uv):
        uv run python examples/03_usd_basics/03_reference.py
    コンテナ内:
        export PYTHONPATH=$(ls -d /isaac-sim/extscache/omni.usd.libs-*)
        export LD_LIBRARY_PATH=$PYTHONPATH/bin
        cd /tmp
        /isaac-sim/python.sh /workspace/examples/03_usd_basics/03_reference.py
"""

from pathlib import Path

from pxr import Gf, Usd, UsdGeom

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# 1. 部品となるアセットファイルを作る (簡単な「コーン」)
asset_path = output_dir / "traffic_cone.usda"
asset_stage = Usd.Stage.CreateNew(str(asset_path))
UsdGeom.SetStageUpAxis(asset_stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(asset_stage, 1.0)
root = UsdGeom.Xform.Define(asset_stage, "/TrafficCone")
asset_stage.SetDefaultPrim(root.GetPrim())
body = UsdGeom.Cone.Define(asset_stage, "/TrafficCone/Body")
body.GetHeightAttr().Set(0.5)
body.GetRadiusAttr().Set(0.15)
body.GetDisplayColorAttr().Set([Gf.Vec3f(1.0, 0.5, 0.0)])
asset_stage.Save()

# 2. シーンを作り、アセットを Reference で 2 つ配置する
scene_path = output_dir / "scene_with_references.usda"
stage = Usd.Stage.CreateNew(str(scene_path))
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
stage.SetDefaultPrim(UsdGeom.Xform.Define(stage, "/World").GetPrim())

for i, x in enumerate([0.0, 1.0]):
    cone = UsdGeom.Xform.Define(stage, f"/World/Cone_{i}")
    # シーンファイルからの相対パスで参照する
    cone.GetPrim().GetReferences().AddReference(f"./{asset_path.name}")
    cone.AddTranslateOp().Set(Gf.Vec3d(x, 0.0, 0.25))

# 3. 2 つ目のコーンだけ色を上書きする (元のアセットファイルは変わらない)
override = UsdGeom.Cone(stage.GetPrimAtPath("/World/Cone_1/Body"))
override.GetDisplayColorAttr().Set([Gf.Vec3f(0.1, 0.8, 0.1)])

for prim in stage.Traverse():
    if prim.IsA(UsdGeom.Cone):
        color = UsdGeom.Cone(prim).GetDisplayColorAttr().Get()
        print(f"{prim.GetPath()}  色 = {color}")

stage.Save()
print(f"保存しました: {scene_path.resolve()}")
print("--- シーンファイルの中身 ---")
print(stage.GetRootLayer().ExportToString())
