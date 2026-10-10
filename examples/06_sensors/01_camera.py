"""Jetbot に付いているカメラから RGB 画像と Depth 画像を取得し、PNG で保存する。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/06_sensors/01_camera.py
    # 保存した画像は /tmp/output/06_camera/ にある

公式サンプル standalone_examples/api/isaacsim.sensors.experimental.rtx/create_camera_basic.py
(v6.1.0) をもとにしている。
"""

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="/tmp/output/06_camera", help="画像の保存先")
parser.add_argument("--livestream", action="store_true", help="Web ビューアで画面を表示する")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True, "hide_ui": not args.livestream})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import matplotlib.pyplot as plt
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube, DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.sensors.experimental.rtx import CameraSensor
from isaacsim.storage.native import get_assets_root_path

if args.livestream:
    simulation_app.set_setting("/app/window/drawMouse", True)
    app_utils.enable_extension("omni.kit.livestream.app")

# Jetbot の USD の中にあるカメラの Prim のパス
JETBOT_CAMERA = "/World/Jetbot/chassis/rgb_camera/jetbot_camera"
RESOLUTION = (240, 320)  # (高さ, 幅) [ピクセル]

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise RuntimeError("Isaac Sim のアセットの場所が見つかりません")

stage_utils.create_new_stage()
stage_utils.set_stage_up_axis("Z")
stage_utils.set_stage_units(meters_per_unit=1.0)
GroundPlane("/World/GroundPlane", positions=[0, 0, 0])
DistantLight("/World/DistantLight").set_intensities(300)

# カメラに写す物体: 手前に赤、奥に青の立方体を置く
for name, position, color in [
    ("RedCube", [0.6, 0.15, 0.1], [1.0, 0.2, 0.2]),
    ("BlueCube", [1.2, -0.2, 0.1], [0.2, 0.4, 1.0]),
]:
    cube = Cube(f"/World/{name}", positions=position, sizes=0.2)
    material = PreviewSurfaceMaterial(f"/World/Materials/{name}")
    material.set_input_values("diffuseColor", color)
    cube.apply_visual_materials(material)

WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)

# 既存のカメラの Prim に「センサとしてデータを取り出す仕組み」を取り付ける
#   rgb: 色の画像 / distance_to_image_plane: 画像の面からの距離 [m] (Depth 画像)
camera = CameraSensor(
    JETBOT_CAMERA,
    resolution=RESOLUTION,
    annotators=["rgb", "distance_to_image_plane"],
)

SimulationManager.setup_simulation(dt=1.0 / 60.0, device="cpu")
app_utils.play()

# カメラのデータは、描画が何フレームか進んでから届く。届くまで待つ
rgb = depth = None
for frame in range(300):
    simulation_app.update()
    rgb_data, _ = camera.get_data("rgb")
    depth_data, _ = camera.get_data("distance_to_image_plane")
    if rgb_data is not None and depth_data is not None and rgb_data.size > 0:
        rgb = rgb_data.numpy()
        depth = depth_data.numpy().squeeze()  # (高さ, 幅, 1) → (高さ, 幅)
        print(f"[camera] {frame + 1} フレーム目でデータを取得しました")
        break

if rgb is None:
    raise RuntimeError("カメラのデータを取得できませんでした")

print(f"RGB   : shape = {rgb.shape}, dtype = {rgb.dtype}")
print(f"Depth : shape = {depth.shape}, dtype = {depth.dtype}")
center = depth[RESOLUTION[0] // 2, RESOLUTION[1] // 2]
print(f"Depth : 画像の中央までの距離 = {center:.2f} m")

output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)
plt.imsave(output_dir / "rgb.png", rgb)
# 何も写っていない画素 (空) は距離が無限大になるので、表示する範囲を 3 m までに区切る
plt.imsave(output_dir / "depth.png", depth.clip(0.0, 3.0), cmap="viridis")
print(f"[camera] 画像を保存しました: {output_dir}")

while args.livestream and simulation_app.is_running():
    simulation_app.update()

app_utils.stop()
simulation_app.close()
