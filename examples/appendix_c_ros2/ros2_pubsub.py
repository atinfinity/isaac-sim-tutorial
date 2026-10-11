"""ROS 2 のトピックを配信・購読する: /clock を配信し、/move_cube (std_msgs/msg/Empty) を購読する。

- 配信: OmniGraph の ROS2PublishClock ノードで、シミュレーション時刻を /clock に流す
- 購読: Isaac Sim に同梱の rclpy でノードを作り、/move_cube を受け取るたびに表示する

実行方法 (コンテナ内):
    export FASTRTPS_DEFAULT_PROFILES_FILE=/workspace/examples/appendix_c_ros2/fastdds.xml
    /isaac-sim/python.sh /workspace/examples/appendix_c_ros2/ros2_pubsub.py

公式サンプル standalone_examples/api/isaacsim.ros2.bridge/clock.py と
subscriber.py (v6.1.0) をもとにしている。
"""

import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("--duration", type=float, default=60.0, help="動かす時間 [秒]")
args, _ = parser.parse_known_args()

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import omni.graph.core as og
from isaacsim.core.simulation_manager import SimulationManager

# ROS 2 Bridge を有効にする。同梱の rclpy もこのときに読み込まれる
app_utils.enable_extension("isaacsim.ros2.bridge")
simulation_app.update()

import rclpy
from std_msgs.msg import Empty

# 配信: 再生中は毎フレーム、シミュレーション時刻を /clock に配信する
og.Controller.edit(
    {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
    {
        og.Controller.Keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
        ],
        og.Controller.Keys.CONNECT: [
            ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"),
            ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
        ],
    },
)

# 購読: /move_cube を受け取った回数を数える
rclpy.init()
node = rclpy.create_node("isaac_sim_tutorial")
received = 0


def on_move_cube(msg: Empty) -> None:
    global received
    received += 1
    print(f"[ros2_pubsub] /move_cube を受信しました ({received} 回目)", flush=True)


node.create_subscription(Empty, "move_cube", on_move_cube, 10)

stage_utils.set_stage_units(meters_per_unit=1.0)
SimulationManager.setup_simulation(dt=1.0 / 60.0, device="cpu")
app_utils.play()
print(f"[ros2_pubsub] 開始します ({args.duration:.0f} 秒間)", flush=True)

start = time.time()
while simulation_app.is_running() and time.time() - start < args.duration:
    simulation_app.update()
    rclpy.spin_once(node, timeout_sec=0.0)  # 届いたメッセージのコールバックを呼ぶ

print(f"[ros2_pubsub] 終了します (/move_cube の受信: {received} 回)", flush=True)
node.destroy_node()
rclpy.shutdown()
app_utils.stop()
simulation_app.close()
