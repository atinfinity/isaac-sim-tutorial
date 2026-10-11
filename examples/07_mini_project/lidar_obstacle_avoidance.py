"""ミニプロジェクト: LiDAR で障害物を避けながら、Jetbot をゴールへ向かわせる。

5 章の「目標地点へ向かう制御」と、6 章の「LiDAR で周囲の距離を測る」を組み合わせる。
毎ステップ、次の手順で進む方向を決める。

1. ゴールの方向 (ロボットから見た角度) を求める
2. 前方 -90〜+90 度の候補の方向のうち、ロボットの幅の「通路」が十分先まで空いている方向を探す
3. 空いている方向のうち、ゴールの方向に一番近いものへ向かう
4. 空いている方向がなければ、その場で空いている側へ回転する

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/07_mini_project/lidar_obstacle_avoidance.py
    # 走った経路の図は /tmp/output/07_mini_project/trajectory.png に保存される
    # Web ビューアで画面を見る場合
    /isaac-sim/python.sh /workspace/examples/07_mini_project/lidar_obstacle_avoidance.py \
        --livestream
"""

import argparse
import math
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--goal", type=float, nargs=2, default=[3.0, 0.0], help="ゴール x y [m]")
parser.add_argument("--output", default="/tmp/output/07_mini_project", help="図の保存先")
parser.add_argument("--livestream", action="store_true", help="Web ビューアで画面を表示する")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True, "hide_ui": not args.livestream})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import matplotlib.pyplot as plt
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube, Cylinder, DistantLight, GroundPlane
from isaacsim.core.experimental.prims import GeomPrim
from isaacsim.core.rendering_manager import ViewportManager
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.sensors.experimental.rtx import Lidar, LidarSensor, parse_generic_model_output_data
from isaacsim.storage.native import get_assets_root_path

app_utils.enable_extension("isaacsim.sensors.rtx.nodes")
if args.livestream:
    simulation_app.set_setting("/app/window/drawMouse", True)
    app_utils.enable_extension("omni.kit.livestream.app")

PHYSICS_DT = 1.0 / 60.0
TIMEOUT = 60.0  # [秒]

# 障害物: (x, y, 一辺の長さ) [m]
OBSTACLES = [
    (1.0, 0.0, 0.3),
    (1.9, 0.45, 0.3),
    (2.1, -0.4, 0.3),
]

# 制御のパラメータ
GOAL_TOLERANCE = 0.1  # ゴールにこの距離まで近づいたら到着 [m]
MAX_LINEAR_SPEED = 0.2  # [m/s]
MAX_ANGULAR_SPEED = 1.5  # [rad/s]
K_ANGULAR = 2.0  # 向きのずれに対する比例ゲイン
SAFE_DISTANCE = 0.5  # 通路がこの距離より先まで空いていれば「空いている方向」とみなす [m]
STOP_DISTANCE = 0.15  # 正面の通路の物体がこの距離より近ければ前に進まない [m]
CORRIDOR_WIDTH = 0.3  # 通路の幅 [m] (Jetbot の幅 約 0.15 m + 左右の余裕)
CANDIDATE_STEP = 5.0  # 候補の方向の間隔 [度]
CANDIDATES = np.arange(-90.0, 90.0 + CANDIDATE_STEP, CANDIDATE_STEP)  # ロボットから見た角度 [度]


class LidarScan:
    """LiDAR の点を方位角 1 度ごとの区画にまとめる (06_sensors/02_lidar.py と同じもの)。"""

    def __init__(self, num_bins: int = 360, expire_time: float = 0.3) -> None:
        self.num_bins = num_bins
        self.expire_time = expire_time
        self._ranges = np.full(num_bins, np.inf)
        self._stamps = np.full(num_bins, -np.inf)
        self._now = 0.0

    def update(self, azimuths_deg: np.ndarray, ranges: np.ndarray, now: float) -> None:
        valid = ranges > 0.05
        bins = (np.floor(azimuths_deg[valid]) % 360).astype(int) * self.num_bins // 360
        frame_ranges = np.full(self.num_bins, np.inf)
        np.minimum.at(frame_ranges, bins, ranges[valid])
        hit = np.isfinite(frame_ranges)
        self._ranges[hit] = frame_ranges[hit]
        self._stamps[hit] = now
        self._now = now

    @property
    def ranges(self) -> np.ndarray:
        fresh = (self._now - self._stamps) <= self.expire_time
        return np.where(fresh, self._ranges, np.inf)

    def min_range(self, center_deg: float, width_deg: float) -> float:
        offsets = np.arange(-width_deg / 2, width_deg / 2 + 1)
        bins = (np.floor(center_deg + offsets) % 360).astype(int) * self.num_bins // 360
        return float(self.ranges[bins].min())

    def points(self) -> np.ndarray:
        ranges = self.ranges
        angles = np.radians(np.arange(self.num_bins) * 360 / self.num_bins)
        hit = np.isfinite(ranges)
        return np.column_stack(
            [ranges[hit] * np.cos(angles[hit]), ranges[hit] * np.sin(angles[hit])]
        )


def yaw_from_quaternion(w: float, x: float, y: float, z: float) -> float:
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def wrap_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def corridor_distance(points: np.ndarray, direction_deg: float) -> float:
    """direction_deg の方向に伸ばした通路 (幅 CORRIDOR_WIDTH) の中で、一番近い点までの距離。

    points はロボットから見た点の座標 (x = 前, y = 左)。通路に点がなければ無限大を返す。
    """
    if len(points) == 0:
        return math.inf
    angle = math.radians(direction_deg)
    along = points[:, 0] * math.cos(angle) + points[:, 1] * math.sin(angle)  # 通路に沿った距離
    across = -points[:, 0] * math.sin(angle) + points[:, 1] * math.cos(
        angle
    )  # 通路の中心からのずれ
    inside = (along > 0) & (np.abs(across) < CORRIDOR_WIDTH / 2)
    return float(along[inside].min()) if inside.any() else math.inf


def choose_direction(
    points: np.ndarray, goal_angle_deg: float, goal_distance: float
) -> float | None:
    """空いている方向のうち、ゴールの方向に一番近いものを返す。なければ None。"""
    free = [
        c
        for c in CANDIDATES
        # ゴールが SAFE_DISTANCE より近いときは、ゴールまで空いていれば十分
        if corridor_distance(points, c) > min(SAFE_DISTANCE, goal_distance)
    ]
    if not free:
        return None
    return min(free, key=lambda c: abs(c - goal_angle_deg))


def compute_command(scan: LidarScan, x: float, y: float, yaw: float) -> tuple[float, float, str]:
    """(直進速度, 旋回速度, 状態) を求める。"""
    dx, dy = args.goal[0] - x, args.goal[1] - y
    goal_distance = math.hypot(dx, dy)
    goal_angle = math.degrees(wrap_angle(math.atan2(dy, dx) - yaw))

    points = scan.points()
    direction = choose_direction(points, goal_angle, goal_distance)
    if direction is None:
        # 前がふさがっている: 左右のうち空いている側へその場で回転する
        left, right = scan.min_range(90, 60), scan.min_range(270, 60)
        return 0.0, MAX_ANGULAR_SPEED if left > right else -MAX_ANGULAR_SPEED, "回転"

    error = math.radians(direction)
    angular_speed = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, K_ANGULAR * error))
    # 正面の物体が近いほど、またゴールが近いほど速度を落とす
    front = corridor_distance(points, 0.0)
    slow_down = min(1.0, max(0.0, (front - STOP_DISTANCE) / (SAFE_DISTANCE - STOP_DISTANCE)))
    linear_speed = min(MAX_LINEAR_SPEED, 0.5 * goal_distance) * slow_down
    linear_speed *= max(0.0, math.cos(error))
    state = "ゴールへ" if abs(direction - goal_angle) <= CANDIDATE_STEP else "回避"
    return linear_speed, angular_speed, state


# ---------------------------------------------------------------------------
# シーンを作る
# ---------------------------------------------------------------------------
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")

stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

orange = PreviewSurfaceMaterial("/World/Materials/orange")
orange.set_input_values("diffuseColor", [1.0, 0.5, 0.1])
for i, (ox, oy, size) in enumerate(OBSTACLES):
    path = f"/World/Obstacles/Box{i}"
    box = Cube(path, positions=[ox, oy, size / 2], sizes=size)
    box.apply_visual_materials(orange)
    GeomPrim(path, apply_collision_apis=True)  # 衝突判定だけ付ける (剛体にしないので動かない)

green = PreviewSurfaceMaterial("/World/Materials/green")
green.set_input_values("diffuseColor", [0.1, 0.8, 0.2])
goal_marker = Cylinder(
    "/World/GoalMarker",
    positions=[args.goal[0], args.goal[1], 0.005],
    radii=GOAL_TOLERANCE,
    heights=0.01,
)
goal_marker.apply_visual_materials(green)

jetbot = WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)
controller = DifferentialController(wheel_radius=0.03, wheel_base=0.1125)

lidar = Lidar.create(
    "/World/Jetbot/chassis/lidar",
    config="Example_Rotary_2D",
    translations=[0.0, 0.0, 0.12],
)
# Example_Rotary_2D のままだと、近い物体を検出しない
#   nearRangeM = 1: 1 m より近い点を捨てる
#   minDistBetweenEchosM = 0.4: 約 0.4 m より近い点も出てこない (検証環境で確認)
# Jetbot のまわりの近い物体も測れるように、この 2 つを変える。
# 最小距離は、Jetbot 自身 (約 8 cm 先のアンテナ) を測らないように 10 cm にする
lidar_prim = stage_utils.get_current_stage().GetPrimAtPath("/World/Jetbot/chassis/lidar")
lidar_prim.GetAttribute("omni:sensor:Core:nearRangeM").Set(0.1)
lidar_prim.GetAttribute("omni:sensor:Core:minDistBetweenEchosM").Set(0.0)
sensor = LidarSensor(lidar, annotators=["generic-model-output"])
if args.livestream:
    sensor.attach_writer("draw-point-cloud")
    # スタートからゴールまでが画面に収まるように、斜め上から見下ろす
    ViewportManager.set_camera_view(
        "/OmniverseKit_Persp", eye=[1.5, -2.2, 2.0], target=[1.5, 0.0, 0.0]
    )

# ---------------------------------------------------------------------------
# 走らせる
# ---------------------------------------------------------------------------
SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")
if args.livestream:
    # ブラウザで接続してから動きを見られるように、再生 (▶) が押されるまで待つ
    print("[mini_project] Web ビューアで再生 (▶) を押すと始まります", flush=True)
    while simulation_app.is_running() and not app_utils.is_playing():
        simulation_app.update()
else:
    app_utils.play()

scan = LidarScan()
trajectory = []
closest = math.inf  # 走行中に一番障害物に近づいた距離
result = "タイムアウト"
step = 0
print(f"[mini_project] ゴール: ({args.goal[0]:.2f}, {args.goal[1]:.2f})")
while step * PHYSICS_DT < TIMEOUT and simulation_app.is_running():
    simulation_app.update()
    now = step * PHYSICS_DT
    step += 1

    data, _ = sensor.get_data("generic-model-output")
    if data is not None:
        gmo = parse_generic_model_output_data(data)
        if gmo.numElements > 0:
            scan.update(np.asarray(gmo.x), np.asarray(gmo.z), now=now)

    positions, orientations = jetbot.get_world_poses()
    x, y, _ = positions.numpy()[0]
    yaw = yaw_from_quaternion(*orientations.numpy()[0])
    trajectory.append((x, y))
    closest = min(closest, float(scan.ranges.min()))

    if math.hypot(args.goal[0] - x, args.goal[1] - y) < GOAL_TOLERANCE:
        result = "到着"
        break

    # LiDAR のデータがそろうまで (最初の 0.5 秒) は動かない
    if now < 0.5:
        continue

    linear_speed, angular_speed, state = compute_command(scan, x, y, yaw)
    jetbot.apply_wheel_actions(controller.forward([linear_speed, angular_speed]))

    if step % 60 == 0:
        print(
            f"t = {now:4.1f} 秒  位置 = ({x:5.2f}, {y:5.2f})  状態 = {state}  "
            f"正面の通路の距離 = {corridor_distance(scan.points(), 0.0):.2f} m"
        )

jetbot.apply_wheel_actions(controller.forward([0.0, 0.0]))
print(f"[mini_project] 結果: {result} ({step * PHYSICS_DT:.1f} 秒)")
print(f"[mini_project] 障害物に一番近づいた距離: {closest:.2f} m")

# 走った経路を上から見た図に描く
output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(7, 4))
for ox, oy, size in OBSTACLES:
    ax.add_patch(plt.Rectangle((ox - size / 2, oy - size / 2), size, size, color="orange"))
ax.add_patch(plt.Circle(args.goal, GOAL_TOLERANCE, color="green", alpha=0.5))
path_xy = np.array(trajectory)
ax.plot(path_xy[:, 0], path_xy[:, 1], "b-", label="Jetbot")
ax.plot(0, 0, "ko", label="start")
ax.set_aspect("equal")
ax.set_xlabel("x [m]")
ax.set_ylabel("y [m]")
ax.grid(True)
ax.legend()
fig.savefig(output_dir / "trajectory.png", dpi=100)
print(f"[mini_project] 経路の図を保存しました: {output_dir / 'trajectory.png'}")

while args.livestream and simulation_app.is_running():
    simulation_app.update()

app_utils.stop()
simulation_app.close()
