"""URDF から変換した自作ロボットを、5 章の Jetbot と同じ手順で走らせる。

走らせ方は 5 章と同じで、直進 → 左に 90 度旋回 → 直進。

URDF には摩擦の情報がないので、変換した USD では、補助輪 (caster) も床との摩擦で引きずられる。
そこで、Jetbot のアセットと同じように、補助輪に摩擦 0 の物理マテリアルを割り当てる
(--no-caster-material を付けると、割り当てずに走らせて比べられる)。

実行方法 (コンテナ内。先に 01_import_urdf.py で変換しておく):
    /isaac-sim/python.sh /workspace/examples/appendix_e_urdf/03_drive_my_robot.py
    # 補助輪の摩擦をそのままにして比べる場合は、最後に --no-caster-material を付ける

5 章のサンプル examples/05_robot_control/02_drive_jetbot.py をもとにしている。
"""

import argparse
import math

parser = argparse.ArgumentParser()
parser.add_argument(
    "--usd",
    default="/isaac-sim/.local/share/ov/data/output/appendix_e_urdf/my_diffbot/my_diffbot.usda",
    help="01_import_urdf.py で変換した USD",
)
parser.add_argument(
    "--no-caster-material",
    action="store_true",
    help="補助輪に摩擦 0 の物理マテリアルを割り当てない",
)
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.objects import DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from pxr import PhysxSchema, UsdPhysics, UsdShade

PHYSICS_DT = 1.0 / 60.0

# my_diffbot.urdf の寸法 (Jetbot に合わせてある)
WHEEL_RADIUS = 0.03  # 車輪の半径 [m]
WHEEL_BASE = 0.1125  # 左右の車輪の間隔 [m]

# 走行の予定: (説明, 直進速度 [m/s], 旋回速度 [rad/s], 時間 [秒])
PLAN = [
    ("直進", 0.2, 0.0, 3.0),
    ("左に 90 度旋回", 0.0, math.pi / 4, 2.0),  # pi/4 rad/s x 2 秒 = pi/2 rad = 90 度
    ("直進", 0.2, 0.0, 3.0),
    ("停止", 0.0, 0.0, 1.0),
]


def yaw_from_quaternion(w: float, x: float, y: float, z: float) -> float:
    """四元数 (w, x, y, z) から z 軸まわりの回転角 (ヨー角) [rad] を求める。"""
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


# シーン: 地面・ライト・自作ロボット
stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# 物理の設定 (variant "Physics") を選んで読み込む。WheeledRobot の usd_path では
# variant を選べないので、先に参照を追加してから、その Prim を WheeledRobot で包む
stage_utils.add_reference_to_stage(args.usd, "/World/MyBot", variants=[("Physics", "physx")])
robot = WheeledRobot(
    "/World/MyBot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    positions=[0.0, 0.0, 0.04],
)

if not args.no_caster_material:
    # 摩擦 0 の物理マテリアルを作り、補助輪のコリジョンに割り当てる
    stage = stage_utils.get_current_stage()
    material = UsdShade.Material.Define(stage, "/World/Physics/CasterMaterial")
    material_api = UsdPhysics.MaterialAPI.Apply(material.GetPrim())
    material_api.CreateStaticFrictionAttr(0.0)
    material_api.CreateDynamicFrictionAttr(0.0)
    # 摩擦は接している 2 つの物の値を組み合わせて決まる (既定は平均)。
    # "min" にすると小さいほう (ここでは 0) が使われる
    PhysxSchema.PhysxMaterialAPI.Apply(material.GetPrim()).CreateFrictionCombineModeAttr("min")
    caster_collision = stage.GetPrimAtPath("/World/MyBot/Geometry/base_link/caster/sphere_1")
    UsdShade.MaterialBindingAPI.Apply(caster_collision).Bind(
        material, UsdShade.Tokens.weakerThanDescendants, "physics"
    )
    print("[drive_my_robot] 補助輪に摩擦 0 の物理マテリアルを割り当てました", flush=True)

controller = DifferentialController(wheel_radius=WHEEL_RADIUS, wheel_base=WHEEL_BASE)

SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")
app_utils.play()
app_utils.update_app(steps=10)  # 物理エンジンの初期化と、ロボットの着地を待つ


def print_pose(label: str) -> None:
    positions, orientations = robot.get_world_poses()
    x, y, _ = positions.numpy()[0]
    yaw = yaw_from_quaternion(*orientations.numpy()[0])
    print(f"{label:<14} x = {x:6.3f} m  y = {y:6.3f} m  向き = {math.degrees(yaw):7.1f} 度")


print_pose("スタート")
for label, linear_speed, angular_speed, duration in PLAN:
    wheel_velocities = controller.forward([linear_speed, angular_speed])
    print(f"--- {label}: 左右の車輪の角速度 = {wheel_velocities.round(2)} rad/s")
    for _ in range(round(duration / PHYSICS_DT)):
        robot.apply_wheel_actions(wheel_velocities)
        simulation_app.update()
    print_pose(f"{label} の後")
    print(f"{'':<14} 車輪の角速度 (実際) = {robot.get_dof_velocities().numpy()[0].round(2)} rad/s")

app_utils.stop()
simulation_app.close()
