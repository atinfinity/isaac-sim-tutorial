"""自作ロボットの URDF (my_diffbot.urdf) を、URDF Importer の Python API で USD に変換する。

URDF は「リンク (部品) と関節のつながり」を書いた XML ファイルで、ROS でよく使われる。
Isaac Sim で動かすには USD に変換する必要がある。変換の設定は URDFImporterConfig で指定する。
既定の設定のままでは、ロボットが床に固定され、車輪の駆動も効かないので、
次の 2 つを変える (--default を付けると、比較のために既定の設定のまま変換する)。

- fix_base=False: ロボットを床に固定せず、自由に動けるようにする
- joint_target_type="velocity" と override_joint_damping: 関節を速度で動かす駆動にする

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/appendix_e_urdf/01_import_urdf.py
    # USD は /isaac-sim/.local/share/ov/data/output/appendix_e_urdf/my_diffbot/ に保存される
    # (ホストでは ~/docker/isaac-sim/data/output/appendix_e_urdf/my_diffbot/)

公式サンプル standalone_examples/api/isaacsim.asset.importer.urdf/urdf_import.py (v6.1.0)
をもとにしている。
"""

import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    "--urdf",
    default=str(Path(__file__).resolve().parent / "my_diffbot.urdf"),
    help="変換する URDF ファイル",
)
parser.add_argument(
    "--output",
    default="/isaac-sim/.local/share/ov/data/output/appendix_e_urdf",
    help="USD の保存先 (この下に <ロボット名>/<ロボット名>.usda ができる)",
)
parser.add_argument("--default", action="store_true", help="既定の設定のまま変換する")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

from isaacsim.asset.importer.urdf import URDFImporter, URDFImporterConfig

config = URDFImporterConfig(urdf_path=args.urdf, usd_path=args.output)
if not args.default:
    config.fix_base = False  # 床に固定しない (車輪で走るロボットなので)
    config.joint_target_type = "velocity"  # 関節を速度で動かす
    config.override_joint_damping = 10000.0  # 速度の駆動の強さ [N·m·s/rad] (Jetbot と同じ値)

# 同じ名前のフォルダがすでにあると、別の名前 (my_diffbot_1 など) で保存されるので、先に消す
robot_dir = Path(args.output) / Path(args.urdf).stem
if robot_dir.exists():
    print(f"[import_urdf] 前回の出力を削除します: {robot_dir}", flush=True)
    shutil.rmtree(robot_dir)

usd_path = URDFImporter(config).import_urdf()
print(f"[import_urdf] 変換しました: {usd_path}", flush=True)
for path in sorted(robot_dir.rglob("*.usda")):
    print(f"[import_urdf]   {path.relative_to(robot_dir)}", flush=True)

simulation_app.close()
