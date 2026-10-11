"""Jetbot を目標地点まで自動で走らせる (障害物なし)。

現在の位置・向きと目標地点から、直進速度と旋回速度を毎ステップ計算する (比例制御)。
7 章のミニプロジェクトでは、ここに LiDAR による障害物回避を加える。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/05_robot_control/03_go_to_goal.py
    # 目標地点を変える / Web ビューアで画面を見る場合
    /isaac-sim/python.sh /workspace/examples/05_robot_control/03_go_to_goal.py \
        --goal -1.0 1.5 --livestream
"""

import argparse
import math

parser = argparse.ArgumentParser()
parser.add_argument("--goal", type=float, nargs=2, default=[1.5, 1.0], help="目標地点 x y [m]")
parser.add_argument("--livestream", action="store_true", help="Web ビューアで画面を表示する")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True, "hide_ui": not args.livestream})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cylinder, DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.storage.native import get_assets_root_path

if args.livestream:
    simulation_app.set_setting("/app/window/drawMouse", True)
    app_utils.enable_extension("omni.kit.livestream.app")

PHYSICS_DT = 1.0 / 60.0
TIMEOUT = 30.0  # これ以上かかったらあきらめる [秒]

GOAL_TOLERANCE = 0.05  # 目標地点にこの距離まで近づいたら到着とする [m]
MAX_LINEAR_SPEED = 0.25  # [m/s]
MAX_ANGULAR_SPEED = 1.5  # [rad/s]
K_LINEAR = 0.5  # 距離に対する比例ゲイン
K_ANGULAR = 2.0  # 向きのずれに対する比例ゲイン


def yaw_from_quaternion(w: float, x: float, y: float, z: float) -> float:
    """四元数 (w, x, y, z) から z 軸まわりの回転角 (ヨー角) [rad] を求める。"""
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def wrap_angle(angle: float) -> float:
    """角度を -pi 〜 pi の範囲に収める。"""
    return math.atan2(math.sin(angle), math.cos(angle))


def compute_command(x: float, y: float, yaw: float, goal: list[float]) -> tuple[float, float]:
    """現在の位置・向きと目標地点から (直進速度, 旋回速度) を求める。"""
    dx, dy = goal[0] - x, goal[1] - y
    distance = math.hypot(dx, dy)
    heading_error = wrap_angle(math.atan2(dy, dx) - yaw)  # 目標の方向と今の向きの差

    angular_speed = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, K_ANGULAR * heading_error))
    # 目標が横や後ろにあるうちは、前に進まずにその場で向きを変える
    linear_speed = min(MAX_LINEAR_SPEED, K_LINEAR * distance) * max(0.0, math.cos(heading_error))
    return linear_speed, angular_speed


assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")

stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# 目標地点の目印 (見た目だけの円柱。物理を付けていないので、ぶつかってもすり抜ける)
goal_marker = Cylinder(
    "/World/GoalMarker",
    positions=[args.goal[0], args.goal[1], 0.005],
    radii=GOAL_TOLERANCE,
    heights=0.01,
)
green = PreviewSurfaceMaterial("/World/Materials/green")
green.set_input_values("diffuseColor", [0.1, 0.8, 0.2])
goal_marker.apply_visual_materials(green)

jetbot = WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)
controller = DifferentialController(wheel_radius=0.03, wheel_base=0.1125)

SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")
if args.livestream:
    # ブラウザで接続してから動きを見られるように、再生 (▶) が押されるまで待つ
    print("[go_to_goal] Web ビューアで再生 (▶) を押すと始まります", flush=True)
    while simulation_app.is_running() and not app_utils.is_playing():
        simulation_app.update()
else:
    app_utils.play()
app_utils.update_app(steps=10)

print(f"[go_to_goal] 目標地点: ({args.goal[0]:.2f}, {args.goal[1]:.2f})")
reached = False
step = 0
while step * PHYSICS_DT < TIMEOUT and simulation_app.is_running():
    positions, orientations = jetbot.get_world_poses()
    x, y, _ = positions.numpy()[0]
    yaw = yaw_from_quaternion(*orientations.numpy()[0])

    distance = math.hypot(args.goal[0] - x, args.goal[1] - y)
    if distance < GOAL_TOLERANCE:
        reached = True
        break

    linear_speed, angular_speed = compute_command(x, y, yaw, args.goal)
    jetbot.apply_wheel_actions(controller.forward([linear_speed, angular_speed]))
    simulation_app.update()

    if step % 60 == 0:  # 1 秒ごとに表示する
        print(
            f"t = {step * PHYSICS_DT:4.1f} 秒  位置 = ({x:5.2f}, {y:5.2f})  "
            f"向き = {math.degrees(yaw):6.1f} 度  残り = {distance:.2f} m"
        )
    step += 1

jetbot.apply_wheel_actions(controller.forward([0.0, 0.0]))  # 止める
if reached:
    print(f"[go_to_goal] 到着しました ({step * PHYSICS_DT:.1f} 秒)")
else:
    print(f"[go_to_goal] {TIMEOUT:.0f} 秒以内に到着できませんでした")

while args.livestream and simulation_app.is_running():
    simulation_app.update()

app_utils.stop()
simulation_app.close()
