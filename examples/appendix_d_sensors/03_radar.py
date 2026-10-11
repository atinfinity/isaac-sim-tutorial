"""Jetbot にレーダを後付けし、前方の箱までの距離と、近づく速さ (ドップラー速度) を測る。

Jetbot を前方の箱に向かって走らせ、レーダの検出結果 (距離・方位角・相対速度) を記録する。
正解 (箱の面までの距離と Jetbot の速さ) と並べて、CSV と図に保存する。

RTX Radar は Motion BVH (動きを含めた光線追跡の仕組み) を必要とする。
検証環境 (RTX 2080 Ti) では Motion BVH が有効にならず、そのままでは起動時に止まるため、
--without-motion-bvh で、Motion BVH なしでの実行を強制できるようにしている。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/appendix_d_sensors/03_radar.py
    # Motion BVH が有効にならない GPU (検証環境の RTX 2080 Ti など) では
    /isaac-sim/python.sh /workspace/examples/appendix_d_sensors/03_radar.py --without-motion-bvh
    # 記録は /tmp/output/appendix_d_radar/radar.csv と radar.png に保存される

公式サンプル standalone_examples/api/isaacsim.sensors.experimental.rtx/
create_radar_basic.py と inspect_radar_gmo.py (v6.1.0) をもとにしている。
"""

import argparse
import csv
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="/tmp/output/appendix_d_radar", help="記録の保存先")
parser.add_argument(
    "--without-motion-bvh",
    action="store_true",
    help="Motion BVH なしでレーダを動かす (サポート外の設定)",
)
args, _ = parser.parse_known_args()

if args.without_motion_bvh:
    # 起動時の設定 (Kit の引数) として渡す
    sys.argv.append("--/app/sensors/nv/radar/runWithoutMBVH=true")

from isaacsim import SimulationApp

# RTX Radar には enable_motion_bvh=True が必須
simulation_app = SimulationApp({"headless": True, "enable_motion_bvh": True})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import matplotlib.pyplot as plt
import numpy as np
from isaacsim.core.experimental.objects import Cube, DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.sensors.experimental.rtx import Radar, RadarSensor, parse_generic_model_output_data
from isaacsim.storage.native import get_assets_root_path

app_utils.enable_extension("isaacsim.sensors.rtx.nodes")

PHYSICS_DT = 1.0 / 60.0
BOX_FACE_X = 1.75  # 前方の箱の、Jetbot 側の面の x 座標 [m]

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")

stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# 前方 2.0 m に一辺 0.5 m の箱を置く (Jetbot 側の面は x = 1.75 m)
Cube("/World/BoxFront", positions=[BOX_FACE_X + 0.25, 0.0, 0.25], sizes=0.5)

jetbot = WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)

# レーダを車体 (chassis) の子として作る。前方 (+X) を向く
#   aux_output_level="BASIC": 相対速度 (rv_ms) などの追加の値も出力する
radar = Radar(
    "/World/Jetbot/chassis/radar",
    translations=[0.0, 0.0, 0.12],  # 車体の上 12 cm に取り付ける
    aux_output_level="BASIC",
)
sensor = RadarSensor(radar, annotators=["generic-model-output"])
controller = DifferentialController(wheel_radius=0.03, wheel_base=0.1125)

SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")
app_utils.play()

rows = []
frame = 0
previous_x = 0.0
plan = [("停止", 0.0, 1.0), ("前進", 0.2, 4.0)]  # (名前, 前進速度 [m/s], 時間 [秒])
for name, speed, duration in plan:
    wheel_actions = controller.forward([speed, 0.0])
    for step in range(round(duration / PHYSICS_DT)):
        jetbot.apply_wheel_actions(wheel_actions)
        simulation_app.update()
        frame += 1
        x = float(jetbot.get_world_poses()[0].numpy()[0][0])
        true_speed = (x - previous_x) / PHYSICS_DT  # 正解の速さ (位置の変化から求める)
        previous_x = x
        data, _ = sensor.get_data("generic-model-output")
        if data is None:
            continue
        gmo = parse_generic_model_output_data(data)
        n = gmo.numElements
        if n == 0:
            continue
        # 既定の座標の形式 (球座標) では、x = 方位角 [度]、y = 仰角 [度]、z = 距離 [m]
        # rv_ms は相対速度 [m/s] (近づくときは負)
        ranges = np.asarray(gmo.z)[:n]
        i = int(np.argmin(ranges))  # 一番近い検出を使う
        azimuth, rng, rv = float(gmo.x[i]), float(ranges[i]), float(gmo.rv_ms[i])
        true_range = BOX_FACE_X - x  # 正解の距離 (箱の面まで)
        t = frame * PHYSICS_DT
        rows.append([t, name, n, azimuth, rng, rv, true_range, true_speed])
        if step % 30 == 29:
            print(
                f"[radar] {name} 検出数={n} 距離={rng:.2f} m (正解 {true_range:.2f} m) "
                f"方位角={azimuth:5.2f} 度 相対速度={rv:6.3f} m/s (正解 {-true_speed:6.3f} m/s)",
                flush=True,
            )

if not rows:
    raise RuntimeError("レーダの検出結果が一度も得られませんでした")

output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "radar.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "time",
            "phase",
            "num_detections",
            "azimuth_deg",
            "range",
            "rv_ms",
            "true_range",
            "true_speed",
        ]
    )
    writer.writerows(rows)

# 距離と相対速度を、正解と並べて図にする
values = np.array([[r[0], r[4], r[5], r[6], r[7]] for r in rows])
fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
axes[0].plot(values[:, 0], values[:, 1], label="radar")
axes[0].plot(values[:, 0], values[:, 3], "--", label="ground truth")
axes[0].set_ylabel("range [m]")
axes[1].plot(values[:, 0], values[:, 2], label="radar")
axes[1].plot(values[:, 0], -values[:, 4], "--", label="ground truth")
axes[1].set_ylabel("radial velocity [m/s]")
axes[1].set_xlabel("time [s]")
for ax in axes:
    ax.grid(True)
    ax.legend(loc="upper right")
fig.tight_layout()
fig.savefig(output_dir / "radar.png", dpi=100)
print(f"[radar] 記録を保存しました: {output_dir / 'radar.csv'}, {output_dir / 'radar.png'}")

app_utils.stop()
simulation_app.close()
