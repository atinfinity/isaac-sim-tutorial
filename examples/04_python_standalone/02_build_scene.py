"""Python からシーンを組み立てる: 地面・ライト・見た目だけの立方体・物理付きの立方体。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/04_python_standalone/02_build_scene.py
    # Web ビューアで画面を見る場合
    /isaac-sim/python.sh /workspace/examples/04_python_standalone/02_build_scene.py --livestream

公式サンプル standalone_examples/api/isaacsim.core.experimental.api/add_cubes.py (v6.1.0)
をもとにしている。
"""

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--livestream", action="store_true", help="Web ビューアで画面を表示する")
parser.add_argument("--steps", type=int, default=300, help="シミュレーションするステップ数")
parser.add_argument("--save", default="/tmp/output/04_scene.usda", help="シーンの保存先")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True, "hide_ui": not args.livestream})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube, DistantLight, GroundPlane
from isaacsim.core.experimental.prims import GeomPrim, RigidPrim

if args.livestream:
    simulation_app.set_setting("/app/window/drawMouse", True)
    app_utils.enable_extension("omni.kit.livestream.app")

# 1. 新しい Stage を作る
stage_utils.create_new_stage()

# 2. 地面とライトを置く
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# 3. 色 (マテリアル) を作る
red = PreviewSurfaceMaterial("/World/Materials/red")
red.set_input_values("diffuseColor", [1.0, 0.2, 0.2])
blue = PreviewSurfaceMaterial("/World/Materials/blue")
blue.set_input_values("diffuseColor", [0.2, 0.4, 1.0])

# 4. 見た目だけの立方体 (物理なし: 空中に浮いたまま)
visual_cube = Cube(paths="/World/VisualCube", positions=[0.0, -0.5, 1.0], sizes=0.3)
visual_cube.apply_visual_materials(blue)

# 5. 物理付きの立方体 (剛体 + コリジョン: 落下して地面で止まる)
dynamic_cube = Cube(paths="/World/DynamicCube", positions=[0.0, 0.5, 1.0], sizes=0.3)
dynamic_cube.apply_visual_materials(red)
RigidPrim(paths="/World/DynamicCube")  # 剛体にする (重力を受ける)
GeomPrim(paths="/World/DynamicCube", apply_collision_apis=True)  # 衝突判定を付ける

# 6. Stage のツリーを表示し、USD ファイルとして保存する (3 章で学んだ .usda で中身を確認できる)
print(stage_utils.generate_stage_representation())
Path(args.save).parent.mkdir(parents=True, exist_ok=True)
stage_utils.save_stage(args.save)
print(f"[build_scene] シーンを保存しました: {args.save}")

# 7. シミュレーションを再生し、指定ステップだけ進める
app_utils.play()
for _ in range(args.steps):
    simulation_app.update()

# livestream のときは、ブラウザを閉じるまで (またはアプリが終了するまで) 表示を続ける
while args.livestream and simulation_app.is_running():
    simulation_app.update()

app_utils.stop()
simulation_app.close()
