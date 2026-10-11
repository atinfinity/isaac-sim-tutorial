"""Jetbot に 2D LiDAR を後付けし、周囲の物体までの距離を測る。

LiDAR は回転しながら少しずつ測るので、1 フレームで得られるのは一周の一部だけになる。
そこで、方向 (方位角) を 1 度ずつの区画に分け、区画ごとに最新の距離を覚えておく。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/06_sensors/02_lidar.py
    # 一周分の距離を描いた図は /tmp/output/06_lidar/scan.png に保存される
    # Web ビューアで点群を見る場合
    /isaac-sim/python.sh /workspace/examples/06_sensors/02_lidar.py --livestream

公式サンプル standalone_examples/api/isaacsim.sensors.experimental.rtx/
lidar_robot_integration.py と inspect_lidar_gmo.py (v6.1.0) をもとにしている。
"""

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="/tmp/output/06_lidar", help="図の保存先")
parser.add_argument("--livestream", action="store_true", help="Web ビューアで画面を表示する")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True, "hide_ui": not args.livestream})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import matplotlib.pyplot as plt
import numpy as np
from isaacsim.core.experimental.objects import Cube, DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.sensors.experimental.rtx import Lidar, LidarSensor, parse_generic_model_output_data
from isaacsim.storage.native import get_assets_root_path

app_utils.enable_extension("isaacsim.sensors.rtx.nodes")  # LiDAR の点群を描く機能
if args.livestream:
    simulation_app.set_setting("/app/window/drawMouse", True)
    app_utils.enable_extension("omni.kit.livestream.app")

PHYSICS_DT = 1.0 / 60.0


class LidarScan:
    """LiDAR の点を方位角 1 度ごとの区画にまとめ、区画ごとの距離を覚えておく。

    方位角はロボットの前方 (+X) を 0 度とし、左回り (+Y の方向) を正とする。
    しばらく点が届かない区画は「何もない (距離 = 無限大)」とみなす。
    """

    def __init__(self, num_bins: int = 360, expire_time: float = 0.3) -> None:
        self.num_bins = num_bins
        self.expire_time = expire_time
        self._ranges = np.full(num_bins, np.inf)
        self._stamps = np.full(num_bins, -np.inf)
        self._now = 0.0

    def update(self, azimuths_deg: np.ndarray, ranges: np.ndarray, now: float) -> None:
        valid = ranges > 0.05  # 近すぎる点 (自分自身など) は使わない
        bins = (np.floor(azimuths_deg[valid]) % 360).astype(int) * self.num_bins // 360
        frame_ranges = np.full(self.num_bins, np.inf)
        np.minimum.at(frame_ranges, bins, ranges[valid])  # 同じ区画の点は一番近いものを使う
        hit = np.isfinite(frame_ranges)
        self._ranges[hit] = frame_ranges[hit]
        self._stamps[hit] = now
        self._now = now

    @property
    def ranges(self) -> np.ndarray:
        """区画ごとの距離 [m]。古くなった区画は無限大にする。"""
        fresh = (self._now - self._stamps) <= self.expire_time
        return np.where(fresh, self._ranges, np.inf)

    def min_range(self, center_deg: float, width_deg: float) -> float:
        """center_deg を中心とした幅 width_deg の範囲で、一番近い物体までの距離 [m]。"""
        offsets = np.arange(-width_deg / 2, width_deg / 2 + 1)
        bins = (np.floor(center_deg + offsets) % 360).astype(int) * self.num_bins // 360
        return float(self.ranges[bins].min())

    def points(self) -> np.ndarray:
        """区画ごとの点を、ロボットから見た (x, y) 座標 [m] にして返す。"""
        ranges = self.ranges
        angles = np.radians(np.arange(self.num_bins) * 360 / self.num_bins)
        hit = np.isfinite(ranges)
        return np.column_stack(
            [ranges[hit] * np.cos(angles[hit]), ranges[hit] * np.sin(angles[hit])]
        )


assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")

stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# LiDAR で測る物体: 前方 1.0 m に箱、左 0.6 m に箱、後方 1.5 m に横長の壁
Cube("/World/BoxFront", positions=[1.0, 0.0, 0.15], sizes=0.3)
Cube("/World/BoxLeft", positions=[0.0, 0.6, 0.15], sizes=0.3)
Cube("/World/WallBack", positions=[-1.5, 0.0, 0.15], sizes=1.0, scales=[0.1, 2.0, 0.3])

WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)

# LiDAR を Jetbot の車体 (chassis) の子として作る。車体と一緒に動くようになる
#   Example_Rotary_2D: 水平方向の一周を測る 2D LiDAR の設定
lidar = Lidar.create(
    "/World/Jetbot/chassis/lidar",
    config="Example_Rotary_2D",
    translations=[0.0, 0.0, 0.12],  # 車体の上 12 cm に取り付ける
)
# Example_Rotary_2D のままだと、近い物体を検出しない
#   nearRangeM = 1: 1 m より近い点を捨てる
#   minDistBetweenEchosM = 0.4: 約 0.4 m より近い点も出てこない (検証環境で確認)
# Jetbot のまわりの近い物体も測れるように、この 2 つを変える。
# 最小距離は、Jetbot 自身 (約 8 cm 先のアンテナ) を測らないように 10 cm にする
lidar_prim = stage_utils.get_current_stage().GetPrimAtPath("/World/Jetbot/chassis/lidar")
lidar_prim.GetAttribute("omni:sensor:Core:nearRangeM").Set(0.1)
lidar_prim.GetAttribute("omni:sensor:Core:minDistBetweenEchosM").Set(0.0)
# generic-model-output: LiDAR の測定結果 (点ごとの方位角・仰角・距離など)
sensor = LidarSensor(lidar, annotators=["generic-model-output"])
if args.livestream:
    sensor.attach_writer("draw-point-cloud")  # 点群を画面に描く

SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")
if args.livestream:
    # ブラウザで接続してから動きを見られるように、再生 (▶) が押されるまで待つ
    print("[lidar] Web ビューアで再生 (▶) を押すと始まります", flush=True)
    while simulation_app.is_running() and not app_utils.is_playing():
        simulation_app.update()
else:
    app_utils.play()

scan = LidarScan()
for frame in range(120):  # 2 秒分
    simulation_app.update()
    data, _ = sensor.get_data("generic-model-output")
    if data is None:
        continue
    gmo = parse_generic_model_output_data(data)
    if gmo.numElements == 0:
        continue
    # 既定の座標の形式 (球座標) では、x = 方位角 [度]、y = 仰角 [度]、z = 距離 [m]
    azimuths, ranges = np.asarray(gmo.x), np.asarray(gmo.z)
    scan.update(azimuths, ranges, now=frame * PHYSICS_DT)
    if frame % 30 == 0:
        print(
            f"[lidar] フレーム {frame}: {gmo.numElements} 点 "
            f"(方位角 {azimuths.min():.0f}〜{azimuths.max():.0f} 度)"
        )

print("--- 各方向で一番近い物体までの距離 (幅 10 度) ---")
for label, center in [
    ("前 (0 度)", 0),
    ("左 (90 度)", 90),
    ("後 (180 度)", 180),
    ("右 (270 度)", 270),
]:
    print(f"{label:<12} {scan.min_range(center, 10):.2f} m")

# 一周分の距離を、ロボットを中心とした図 (上から見た図) に描く
output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)
points = scan.points()
fig, ax = plt.subplots(figsize=(5, 5))
ax.scatter(points[:, 0], points[:, 1], s=4)
ax.plot(0, 0, "r^", markersize=10)  # ロボットの位置 (前方 = +X)
ax.set_aspect("equal")
ax.set_xlabel("x [m]")
ax.set_ylabel("y [m]")
ax.grid(True)
fig.tight_layout()
fig.savefig(output_dir / "scan.png", dpi=100)
print(f"[lidar] 図を保存しました: {output_dir / 'scan.png'}")

while args.livestream and simulation_app.is_running():
    simulation_app.update()

app_utils.stop()
simulation_app.close()
