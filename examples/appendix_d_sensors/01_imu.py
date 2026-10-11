"""Jetbot に IMU を後付けし、加速度・角速度・姿勢を記録する。

Jetbot を「止まる → その場で左に回る → 止まる → 前に進む → 止まる」の順に動かし、
IMU の値を CSV と図に保存する。最後に、姿勢から求めた向きの変化と、
角速度 (z 軸まわり) を足し合わせて求めた向きの変化を比べる。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/appendix_d_sensors/01_imu.py
    # 記録は /tmp/output/appendix_d_imu/imu.csv と imu.png に保存される
    # 物理エンジンのソルバを PGS に変えて比べる場合
    /isaac-sim/python.sh /workspace/examples/appendix_d_sensors/01_imu.py --solver PGS

公式サンプル standalone_examples/api/isaacsim.sensors.experimental.physics/
imu_sensor.py (v6.1.0) をもとにしている。
"""

import argparse
import csv
import math
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="/tmp/output/appendix_d_imu", help="記録の保存先")
parser.add_argument(
    "--solver",
    choices=["TGS", "PGS"],
    default="TGS",
    help="物理エンジンのソルバ (Jetbot のアセットの既定は TGS)",
)
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import matplotlib.pyplot as plt
import numpy as np
from isaacsim.core.experimental.objects import DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.sensors.experimental.physics import IMU, IMUSensor
from isaacsim.storage.native import get_assets_root_path

PHYSICS_DT = 1.0 / 60.0

# 動かし方: (名前, 前進速度 [m/s], 回転速度 [rad/s], 時間 [秒])
PLAN = [
    ("停止", 0.0, 0.0, 1.0),
    ("左回転", 0.0, math.pi / 4, 2.0),
    ("停止", 0.0, 0.0, 1.0),
    ("前進", 0.2, 0.0, 2.0),
    ("停止", 0.0, 0.0, 1.0),
]


def yaw_deg(orientation: np.ndarray) -> float:
    """クォータニオン (w, x, y, z) から、z 軸まわりの向き (ヨー角) [度] を求める。"""
    w, x, y, z = orientation
    return math.degrees(math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z)))


assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")

stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

jetbot = WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)

# IMU を車体 (chassis) の子として作る。IMU は剛体の子孫に置く必要がある
imu = IMUSensor(IMU.create("/World/Jetbot/chassis/imu"))
controller = DifferentialController(wheel_radius=0.03, wheel_base=0.1125)

SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")
if args.solver == "PGS":
    # Jetbot のアセットに含まれる物理シーンのソルバを書き換える
    for prim in stage_utils.get_current_stage().Traverse():
        attr = prim.GetAttribute("physxScene:solverType")
        if attr and attr.IsValid():
            attr.Set("PGS")
print(f"[imu] ソルバ: {args.solver}", flush=True)

app_utils.play()
app_utils.update_app(steps=10)  # 落下して接地するまで待つ

rows = []
for name, linear, angular, duration in PLAN:
    wheel_actions = controller.forward([linear, angular])
    start_yaw = yaw_deg(imu.get_data()["orientation"])
    integrated = 0.0  # 角速度 (z) を足し合わせた向きの変化 [rad]
    for step in range(round(duration / PHYSICS_DT)):
        jetbot.apply_wheel_actions(wheel_actions)
        simulation_app.update()
        data = imu.get_data()
        acc = np.asarray(data["linear_acceleration"])  # 加速度 [m/s^2] (IMU の座標系)
        gyro = np.asarray(data["angular_velocity"])  # 角速度 [rad/s] (IMU の座標系)
        yaw = yaw_deg(np.asarray(data["orientation"]))
        integrated += gyro[2] * PHYSICS_DT
        rows.append([data["time"], name, *acc, *gyro, yaw])
        if step % 30 == 29:
            print(
                f"[imu] t={data['time']:5.2f} {name:<4} 加速度={np.round(acc, 2)} "
                f"角速度={np.round(gyro, 2)} 向き={yaw:6.1f} 度",
                flush=True,
            )
    yaw_change = yaw_deg(imu.get_data()["orientation"]) - start_yaw
    print(
        f"[imu] == {name}: 向きの変化 {yaw_change:.1f} 度 / "
        f"角速度 (z) を足し合わせた値 {math.degrees(integrated):.1f} 度",
        flush=True,
    )

output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "imu.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        ["time", "phase", "acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z", "yaw_deg"]
    )
    writer.writerows(rows)

# 加速度・角速度・向きを時系列の図にする
t = np.array([r[0] for r in rows])
values = np.array([r[2:] for r in rows], dtype=float)
fig, axes = plt.subplots(3, 1, figsize=(7, 7), sharex=True)
for i, axis in enumerate("xyz"):
    axes[0].plot(t, values[:, i], label=f"acc {axis}")
    axes[1].plot(t, values[:, 3 + i], label=f"gyro {axis}")
axes[2].plot(t, values[:, 6], label="yaw")
axes[0].set_ylabel("[m/s^2]")
axes[1].set_ylabel("[rad/s]")
axes[2].set_ylabel("[deg]")
axes[2].set_xlabel("time [s]")
for ax in axes:
    ax.grid(True)
    ax.legend(loc="upper right")
fig.suptitle(f"IMU (solver: {args.solver})")
fig.tight_layout()
fig.savefig(output_dir / "imu.png", dpi=100)
print(f"[imu] 記録を保存しました: {output_dir / 'imu.csv'}, {output_dir / 'imu.png'}")

app_utils.stop()
simulation_app.close()
