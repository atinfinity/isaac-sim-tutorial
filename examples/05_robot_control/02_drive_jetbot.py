"""差動二輪の制御で Jetbot を走らせる: 直進 → 左に 90 度旋回 → 直進。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/05_robot_control/02_drive_jetbot.py
    # Web ビューアで画面を見る場合
    /isaac-sim/python.sh /workspace/examples/05_robot_control/02_drive_jetbot.py --livestream

公式サンプル standalone_examples/api/isaacsim.robot.wheeled_robots.examples/
jetbot_differential_move.py (v6.1.0) をもとにしている。
"""

import argparse
import math

parser = argparse.ArgumentParser()
parser.add_argument("--livestream", action="store_true", help="Web ビューアで画面を表示する")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True, "hide_ui": not args.livestream})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.objects import DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.storage.native import get_assets_root_path

if args.livestream:
    simulation_app.set_setting("/app/window/drawMouse", True)
    app_utils.enable_extension("omni.kit.livestream.app")

PHYSICS_DT = 1.0 / 60.0

# Jetbot の寸法 (公式サンプルの値)
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


assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")

# シーン: 地面・ライト・Jetbot
stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# WheeledRobot は Articulation に「車輪の関節」を扱う機能を足したクラス
jetbot = WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)

# 差動二輪のコントローラ: (直進速度, 旋回速度) → (左車輪, 右車輪) の角速度
controller = DifferentialController(wheel_radius=WHEEL_RADIUS, wheel_base=WHEEL_BASE)

SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")

if args.livestream:
    # ブラウザで接続してから動きを見られるように、再生 (▶) が押されるまで待つ
    print("[drive_jetbot] Web ビューアで再生 (▶) を押すと始まります", flush=True)
    while simulation_app.is_running() and not app_utils.is_playing():
        simulation_app.update()
else:
    app_utils.play()
app_utils.update_app(steps=10)  # 物理エンジンの初期化と、Jetbot の着地を待つ


def print_pose(label: str) -> None:
    positions, orientations = jetbot.get_world_poses()
    x, y, _ = positions.numpy()[0]
    yaw = yaw_from_quaternion(*orientations.numpy()[0])
    print(f"{label:<14} x = {x:6.3f} m  y = {y:6.3f} m  向き = {math.degrees(yaw):7.1f} 度")


print_pose("スタート")
for label, linear_speed, angular_speed, duration in PLAN:
    wheel_velocities = controller.forward([linear_speed, angular_speed])
    print(f"--- {label}: 左右の車輪の角速度 = {wheel_velocities.round(2)} rad/s")
    for _ in range(round(duration / PHYSICS_DT)):
        jetbot.apply_wheel_actions(wheel_velocities)
        simulation_app.update()
    print_pose(f"{label} の後")

# livestream のときは、ブラウザを閉じるまで (またはアプリが終了するまで) 表示を続ける
while args.livestream and simulation_app.is_running():
    simulation_app.update()

app_utils.stop()
simulation_app.close()
