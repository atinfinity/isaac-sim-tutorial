"""動作確認用スクリプト: Jetbot を読み込み、ヘッドレスで数秒間前進させる。

コンテナ内で実行する:
    /isaac-sim/python.sh /workspace/examples/00_smoke_test/smoke_test.py

公式サンプル standalone_examples/api/isaacsim.robot.wheeled_robots.examples/
jetbot_differential_move.py (Isaac Sim v6.1.0) をもとにしている。
"""

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import isaacsim.core.experimental.utils.app as app_utils
from isaacsim.core.experimental.objects import DomeLight
from isaacsim.core.experimental.utils import stage as stage_utils
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import (
    DifferentialController,
)
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.storage.native import get_assets_root_path

NUM_STEPS = 300  # 60 Hz で 5 秒

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットが見つかりません")
print(f"[smoke_test] assets root: {assets_root_path}")

stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
stage_utils.add_reference_to_stage(
    usd_path=assets_root_path + "/Isaac/Environments/Grid/default_environment.usd",
    path="/World/ground",
)
DomeLight("/World/DomeLight").set_intensities(500)

jetbot = WheeledRobot(
    paths="/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)
controller = DifferentialController(wheel_radius=0.03, wheel_base=0.1125)

SimulationManager.setup_simulation(dt=1.0 / 60.0, device="cpu")
SimulationManager.get_physics_scenes()[0].set_enabled_gpu_dynamics(False)
app_utils.play()
app_utils.update_app(steps=10)

print(f"[smoke_test] start pose: {jetbot.get_world_poses()[0]}")
for _ in range(NUM_STEPS):
    jetbot.apply_wheel_actions(controller.forward([0.1, 0.0]))
    simulation_app.update()
print(f"[smoke_test] end pose:   {jetbot.get_world_poses()[0]}")
print("[smoke_test] OK")

app_utils.stop()
simulation_app.close()
