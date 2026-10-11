"""Jetbot に接触センサを後付けし、壁にぶつかったことを検出する。

Jetbot を前方の壁に向かって走らせ、接触センサの力と接触相手を記録する。
Jetbot は常に床と接しているので、「接触しているか」だけでは壁との衝突が分からない。
そこで、接触の一つひとつ (raw contact) から相手を調べ、床以外との接触を探す。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/appendix_d_sensors/02_contact.py
    # 記録は /tmp/output/appendix_d_contact/contact.csv と contact.png に保存される

公式サンプル standalone_examples/api/isaacsim.sensors.experimental.physics/
contact_sensor.py (v6.1.0) をもとにしている。
"""

import argparse
import csv
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="/tmp/output/appendix_d_contact", help="記録の保存先")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import matplotlib.pyplot as plt
import numpy as np
from isaacsim.core.experimental.objects import Cube, DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.sensors.experimental.physics import Contact, ContactSensor
from isaacsim.storage.native import get_assets_root_path
from pxr import UsdPhysics

PHYSICS_DT = 1.0 / 60.0

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")

stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# 前方 0.8 m に壁を置く。ぶつかれるように、コリジョン (衝突判定) を付ける
Cube("/World/Wall", positions=[0.8, 0.0, 0.15], sizes=1.0, scales=[0.1, 1.0, 0.3])
UsdPhysics.CollisionAPI.Apply(stage_utils.get_current_stage().GetPrimAtPath("/World/Wall"))

jetbot = WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)

# 接触センサを車体 (chassis) の子として作る。センサは剛体の子孫に置く必要があり、
# その剛体 (ここでは車体) が何かに触れたときの力を測る
contact = ContactSensor(Contact.create("/World/Jetbot/chassis/contact_sensor"))
contact.add_raw_contact_data_to_frame()  # 接触の一つひとつ (相手・位置など) も取得する
controller = DifferentialController(wheel_radius=0.03, wheel_base=0.1125)

SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")
app_utils.play()
app_utils.update_app(steps=10)  # 落下して接地するまで待つ

wheel_actions = controller.forward([0.2, 0.0])  # 0.2 m/s で前進する
rows = []
first_hit = None
for step in range(round(5.0 / PHYSICS_DT)):  # 5 秒分
    jetbot.apply_wheel_actions(wheel_actions)
    simulation_app.update()
    data = contact.get_data()
    # 床 (GroundPlane) 以外との接触だけを取り出す
    others = [c for c in data["contacts"] if "GroundPlane" not in c["body1"]]
    x = float(jetbot.get_world_poses()[0].numpy()[0][0])
    rows.append(
        [
            data["time"],
            x,
            data["in_contact"],
            data["force"],
            data["number_of_contacts"],
            len(others),
        ]
    )
    if others and first_hit is None:
        first_hit = data["time"]
        names = sorted({c["body1"] for c in others})
        print(f"[contact] t={data['time']:.2f} 床以外と接触しました: {names}", flush=True)
        print(f"[contact]   接触位置の例: {np.round(others[0]['position'], 3)}", flush=True)
    if step % 30 == 29:
        print(
            f"[contact] t={data['time']:4.2f} x={x:.3f} m 接触中={data['in_contact']} "
            f"力={data['force']:5.2f} N 接触点={data['number_of_contacts']:2d} "
            f"(床以外 {len(others)})",
            flush=True,
        )

output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "contact.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        ["time", "x", "in_contact", "force", "number_of_contacts", "contacts_not_ground"]
    )
    writer.writerows(rows)

# 力と位置を時系列の図にする。床以外と接触している時間を色付けする
t = np.array([r[0] for r in rows])
fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
axes[0].plot(t, [r[3] for r in rows])
axes[0].set_ylabel("force [N]")
axes[1].plot(t, [r[1] for r in rows])
axes[1].set_ylabel("x [m]")
axes[1].set_xlabel("time [s]")
hit = np.array([r[5] > 0 for r in rows])
for ax in axes:
    ax.fill_between(t, 0, 1, where=hit, transform=ax.get_xaxis_transform(), alpha=0.2, label="wall")
    ax.grid(True)
axes[0].legend(loc="upper left")
fig.tight_layout()
fig.savefig(output_dir / "contact.png", dpi=100)
print(f"[contact] 記録を保存しました: {output_dir / 'contact.csv'}, {output_dir / 'contact.png'}")

app_utils.stop()
simulation_app.close()
