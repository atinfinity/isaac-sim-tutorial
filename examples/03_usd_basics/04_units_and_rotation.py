"""座標系・単位・回転の表し方を確かめる。

実行方法:
    ホスト (uv):
        uv run python examples/03_usd_basics/04_units_and_rotation.py
    コンテナ内:
        cd /tmp
        /isaac-sim/python.sh /workspace/examples/03_usd_basics/04_units_and_rotation.py
"""

import math
from pathlib import Path

from pxr import Gf, Usd, UsdGeom

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. 回転: 同じ「z 軸まわりに 90 度」を 3 通りで表す
# ---------------------------------------------------------------------------
angle_deg = 90.0
angle_rad = math.radians(angle_deg)
print(f"角度: {angle_deg} 度 = {angle_rad:.4f} ラジアン")

# 四元数 (クォータニオン)。USD と Isaac Sim Core の API は (w, x, y, z) の順
quat = Gf.Rotation(Gf.Vec3d(0, 0, 1), angle_deg).GetQuat()
w, (x, y, z) = quat.GetReal(), quat.GetImaginary()
print(f"四元数 (w, x, y, z) = ({w:.4f}, {x:.4f}, {y:.4f}, {z:.4f})")

# x 軸方向の単位ベクトル (前方) を回すと、y 軸方向 (左) を向く
forward = Gf.Vec3d(1, 0, 0)
rotated = Gf.Rotation(quat).TransformDir(forward)
print(f"前方 (1, 0, 0) を回転すると: ({rotated[0]:.1f}, {rotated[1]:.1f}, {rotated[2]:.1f})")

# ---------------------------------------------------------------------------
# 2. USD での回転: 角度 (度) で書く rotateZ と、四元数で書く orient
# ---------------------------------------------------------------------------
stage = Usd.Stage.CreateNew(str(output_dir / "units_and_rotation.usda"))
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
stage.SetDefaultPrim(UsdGeom.Xform.Define(stage, "/World").GetPrim())

by_euler = UsdGeom.Xform.Define(stage, "/World/ByEuler")
by_euler.AddRotateZOp().Set(angle_deg)  # 度で指定

by_quat = UsdGeom.Xform.Define(stage, "/World/ByQuat")
by_quat.AddOrientOp().Set(Gf.Quatf(quat))  # 四元数で指定

time = Usd.TimeCode.Default()
same = Gf.IsClose(by_euler.GetLocalTransformation(time), by_quat.GetLocalTransformation(time), 1e-6)
print(f"rotateZ = 90 と orient (四元数) は同じ回転か: {same}")

# ---------------------------------------------------------------------------
# 3. 長さの単位: metersPerUnit
# ---------------------------------------------------------------------------
# センチメートル単位 (metersPerUnit = 0.01) で作られたアセットを想定する
cm_stage = Usd.Stage.CreateInMemory()
UsdGeom.SetStageMetersPerUnit(cm_stage, 0.01)
cube = UsdGeom.Cube.Define(cm_stage, "/Cube")
cube.GetSizeAttr().Set(30.0)  # 30 単位 = 30 cm

mpu = UsdGeom.GetStageMetersPerUnit(cm_stage)
size = cube.GetSizeAttr().Get()
print(f"metersPerUnit = {mpu} の Stage で size = {size} の立方体は {size * mpu:.2f} m")
print("メートル単位 (metersPerUnit = 1.0) の Stage にそのまま読み込むと 30 m の立方体になる")

stage.Save()
