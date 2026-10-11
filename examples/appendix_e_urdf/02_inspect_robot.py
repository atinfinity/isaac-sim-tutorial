"""URDF から変換した USD を読み込み、リンク・コリジョン・質量・関節を表示する。

変換した USD が URDF のとおりになっているかを確かめる。
変換した USD には物理の設定の切り替え (variant "Physics") があり、選ばないと物理の設定が
読み込まれない。ここでは Jetbot のアセットと同じ "physx" を選ぶ。

実行方法 (コンテナ内。先に 01_import_urdf.py で変換しておく):
    /isaac-sim/python.sh /workspace/examples/appendix_e_urdf/02_inspect_robot.py
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--usd",
    default="/isaac-sim/.local/share/ov/data/output/appendix_e_urdf/my_diffbot/my_diffbot.usda",
    help="01_import_urdf.py で変換した USD",
)
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import isaacsim.core.experimental.utils.stage as stage_utils
from pxr import UsdGeom, UsdPhysics

stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
prim = stage_utils.add_reference_to_stage(args.usd, "/World/MyBot", variants=[("Physics", "physx")])
stage = stage_utils.get_current_stage()

variant_sets = prim.GetVariantSets()
for name in variant_sets.GetNames():
    variant_set = variant_sets.GetVariantSet(name)
    print(
        f"variant {name}: {variant_set.GetVariantNames()} のうち "
        f"{variant_set.GetVariantSelection()!r} を選択"
    )

print("\n== リンク (剛体) と質量")
for p in stage.Traverse():
    if p.HasAPI(UsdPhysics.RigidBodyAPI):
        mass = UsdPhysics.MassAPI(p).GetMassAttr().Get()
        print(f"{p.GetPath()}  質量 = {mass} kg")

print("\n== コリジョン (衝突判定の形)")
for p in stage.Traverse():
    if p.HasAPI(UsdPhysics.CollisionAPI):
        size = ""
        if p.IsA(UsdGeom.Cylinder):
            cylinder = UsdGeom.Cylinder(p)
            radius, height = cylinder.GetRadiusAttr().Get(), cylinder.GetHeightAttr().Get()
            size = f"半径 {radius} m、長さ {height} m"
        elif p.IsA(UsdGeom.Sphere):
            size = f"半径 {UsdGeom.Sphere(p).GetRadiusAttr().Get()} m"
        print(f"{p.GetPath()}  {p.GetTypeName()}  {size}")

print("\n== 関節")
for p in stage.Traverse():
    if not p.IsA(UsdPhysics.Joint):
        continue
    joint = UsdPhysics.Joint(p)
    body0 = joint.GetBody0Rel().GetTargets()[0].name
    body1 = joint.GetBody1Rel().GetTargets()[0].name
    line = f"{p.GetName()}  {p.GetTypeName()}  {body0} → {body1}"
    if p.IsA(UsdPhysics.RevoluteJoint):
        line += f"  回転軸 = {UsdPhysics.RevoluteJoint(p).GetAxisAttr().Get()}"
        drive = UsdPhysics.DriveAPI(p, "angular")
        # USD では、回転関節の駆動の強さは「度」あたりの値で保存される
        line += (
            f"\n    駆動: stiffness = {drive.GetStiffnessAttr().Get()}, "
            f"damping = {drive.GetDampingAttr().Get()}, "
            f"maxForce = {drive.GetMaxForceAttr().Get()}"
        )
    print(line)

simulation_app.close()
