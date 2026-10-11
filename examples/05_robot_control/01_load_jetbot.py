"""Jetbot を読み込み、Articulation としての構造 (リンク・関節) を調べる。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/05_robot_control/01_load_jetbot.py

公式サンプル standalone_examples/api/isaacsim.robot.wheeled_robots.examples/
jetbot_differential_move.py (v6.1.0) をもとにしている。
"""

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.objects import DistantLight, GroundPlane
from isaacsim.core.experimental.prims import Articulation
from isaacsim.storage.native import get_assets_root_path
from pxr import Usd

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")
jetbot_usd = assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda"
print(f"[load_jetbot] アセット: {jetbot_usd}")

# シーン: 地面・ライト・Jetbot
stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# Jetbot の USD を Reference として読み込む (3 章の Reference と同じ仕組み)
stage_utils.add_reference_to_stage(usd_path=jetbot_usd, path="/World/Jetbot")
jetbot = Articulation(
    "/World/Jetbot",
    positions=[[0.0, 0.0, 0.05]],  # 車輪が地面にめり込まない高さに置く
    reset_xform_op_properties=True,
)

# Stage 上の Jetbot の Prim の構造を、深さ 3 まで表示する
stage = stage_utils.get_current_stage()
for prim in Usd.PrimRange(stage.GetPrimAtPath("/World/Jetbot")):
    depth = prim.GetPath().pathElementCount - 2  # /World/Jetbot を深さ 0 とする
    if depth <= 3:
        print(f"{'  ' * depth}{prim.GetName()} ({prim.GetTypeName()})")

# 関節やリンクの情報は、物理エンジンが初期化されてから (再生後に) 取得できる
app_utils.play()
simulation_app.update()

print(f"リンク ({jetbot.num_links} 個): {jetbot.link_names}")
print(f"関節 ({jetbot.num_joints} 個): {jetbot.joint_names}")
print(f"自由度 DOF ({jetbot.num_dofs} 個): {jetbot.dof_names}")

# 何も指令を与えずに 1 秒 (60 ステップ) 進め、位置が変わらないことを確かめる
for _ in range(60):
    simulation_app.update()

positions, orientations = jetbot.get_world_poses()
print(f"位置 (x, y, z) [m]: {positions.numpy()[0].round(3)}")
print(f"姿勢 (w, x, y, z): {orientations.numpy()[0].round(3)}")
print(f"車輪の角速度 [rad/s]: {jetbot.get_dof_velocities().numpy()[0].round(3)}")

app_utils.stop()
simulation_app.close()
