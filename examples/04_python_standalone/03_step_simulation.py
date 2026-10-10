"""シミュレーションを 1 ステップずつ進め、落下する立方体の高さを観察する。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/04_python_standalone/03_step_simulation.py

公式サンプル standalone_examples/api/isaacsim.core.experimental.api/add_cubes.py と
simulation_callbacks.py (v6.1.0) をもとにしている。
"""

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.objects import Cube, GroundPlane
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim
from isaacsim.core.simulation_manager import SimulationManager

PHYSICS_DT = 1.0 / 60.0  # 1 ステップ = 1/60 秒
INITIAL_HEIGHT = 2.0

# シーン: 地面と、高さ 2 m に置いた物理付きの立方体
stage_utils.create_new_stage()
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
Cube(paths="/World/Cube", positions=[0.0, 0.0, INITIAL_HEIGHT], sizes=0.2)
cube = RigidPrim(paths="/World/Cube")
GeomPrim(paths="/World/Cube", apply_collision_apis=True)

# 物理ステップの時間幅 (dt) を設定する
SimulationManager.set_physics_dt(PHYSICS_DT)

# タイムラインを再生する (GUI の ▶ ボタンに相当)
app_utils.play()
simulation_app.update()  # 物理エンジンを初期化する


def cube_height() -> float:
    positions, _ = cube.get_world_poses()  # 戻り値は warp の配列
    return float(positions.numpy()[0, 2])


for episode in range(2):
    # 立方体を初期位置に戻す (リセット)
    cube.set_world_poses(
        positions=[[0.0, 0.0, INITIAL_HEIGHT]],
        orientations=[[1.0, 0.0, 0.0, 0.0]],  # 回転なし (w, x, y, z)
    )
    cube.set_velocities(linear_velocities=[0, 0, 0], angular_velocities=[0, 0, 0])
    print(f"--- エピソード {episode} ---")

    for step in range(120):  # 120 ステップ = 2 秒
        SimulationManager.step()  # 物理だけを 1 ステップ進める (描画はしない)
        if step % 10 == 0:
            t = (step + 1) * PHYSICS_DT
            print(f"t = {t:4.2f} 秒  高さ = {cube_height():.3f} m")

print(f"シミュレーション時間の合計: {SimulationManager.get_simulation_time():.2f} 秒")

app_utils.stop()
simulation_app.close()
