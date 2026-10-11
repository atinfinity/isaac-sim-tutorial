"""Xform の親子関係と、ローカル座標・ワールド座標の違いを確かめる。

実行方法:
    ホスト (uv):
        uv run python examples/03_usd_basics/02_xform_hierarchy.py
    コンテナ内:
        export PYTHONPATH=$(ls -d /isaac-sim/extscache/omni.usd.libs-*)
        export LD_LIBRARY_PATH=$PYTHONPATH/bin
        cd /tmp
        /isaac-sim/python.sh /workspace/examples/03_usd_basics/02_xform_hierarchy.py
"""

from pathlib import Path

from pxr import Gf, Usd, UsdGeom

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
stage_path = output_dir / "xform_hierarchy.usda"

stage = Usd.Stage.CreateNew(str(stage_path))
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
stage.SetDefaultPrim(UsdGeom.Xform.Define(stage, "/World").GetPrim())

# 親: 台車 (x 方向に 1 m 移動し、z 軸まわりに 90 度回転)
cart = UsdGeom.Xform.Define(stage, "/World/Cart")
cart.AddTranslateOp().Set(Gf.Vec3d(1.0, 0.0, 0.0))
cart.AddRotateZOp().Set(90.0)

# 子: 台車の上に載ったセンサ (親から見て x 方向に 0.2 m、z 方向に 0.1 m)
sensor = UsdGeom.Cube.Define(stage, "/World/Cart/Sensor")
sensor.GetSizeAttr().Set(0.05)
sensor.AddTranslateOp().Set(Gf.Vec3d(0.2, 0.0, 0.1))

# xformOpOrder: どの順番で変換を適用するか
print("Cart の xformOpOrder:", cart.GetXformOpOrderAttr().Get())

# ローカル変換 (親から見た位置) とワールド変換 (Stage 全体から見た位置)
time = Usd.TimeCode.Default()
local = sensor.GetLocalTransformation(time)
world = sensor.ComputeLocalToWorldTransform(time)
print("Sensor のローカル位置:", local.ExtractTranslation())
print("Sensor のワールド位置:", world.ExtractTranslation())

# 親を動かすと、子のワールド位置も一緒に動く
cart.GetPrim().GetAttribute("xformOp:translate").Set(Gf.Vec3d(2.0, 0.0, 0.0))
world = sensor.ComputeLocalToWorldTransform(time)
print("Cart を x = 2.0 に動かした後の Sensor のワールド位置:", world.ExtractTranslation())

stage.Save()
print(f"保存しました: {stage_path.resolve()}")
