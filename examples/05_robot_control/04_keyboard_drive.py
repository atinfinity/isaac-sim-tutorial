"""Jetbot をキーボードの矢印キーで走らせる (Web ビューアで操作する)。

キーボードの入力は Web ビューアから送るため、このスクリプトは常に livestream で起動する。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/05_robot_control/04_keyboard_drive.py

操作 (先にビューポートを 1 回クリックして、キー入力を Isaac Sim に送れるようにする):
    ↑ / ↓: 前進 / 後退    ← / →: 左 / 右に旋回    (キーを離すと止まる)
    終了するには、実行したターミナルで Ctrl+C を押す
"""

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True, "hide_ui": False})

import carb.input
import isaacsim.core.experimental.utils.app as app_utils
import isaacsim.core.experimental.utils.stage as stage_utils
import omni.appwindow
from isaacsim.core.experimental.objects import DistantLight, GroundPlane
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot
from isaacsim.storage.native import get_assets_root_path

simulation_app.set_setting("/app/window/drawMouse", True)
app_utils.enable_extension("omni.kit.livestream.app")

PHYSICS_DT = 1.0 / 60.0
LINEAR_SPEED = 0.2  # ↑ / ↓ で出す直進速度 [m/s]
ANGULAR_SPEED = 1.0  # ← / → で出す旋回速度 [rad/s]

# キーごとの (直進速度, 旋回速度)。左回り (←) が旋回速度のプラス
KEY_COMMANDS = {
    carb.input.KeyboardInput.UP: (LINEAR_SPEED, 0.0),
    carb.input.KeyboardInput.DOWN: (-LINEAR_SPEED, 0.0),
    carb.input.KeyboardInput.LEFT: (0.0, ANGULAR_SPEED),
    carb.input.KeyboardInput.RIGHT: (0.0, -ANGULAR_SPEED),
}
pressed_keys = set()  # いま押されているキー


def on_keyboard_event(event, *args) -> bool:
    """キーが押された / 離されたときに呼ばれる。"""
    if event.input in KEY_COMMANDS:
        if event.type == carb.input.KeyboardEventType.KEY_PRESS:
            pressed_keys.add(event.input)
        elif event.type == carb.input.KeyboardEventType.KEY_RELEASE:
            pressed_keys.discard(event.input)
    return True


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
controller = DifferentialController(wheel_radius=0.03, wheel_base=0.1125)

# キーボードのイベントを受け取る関数を登録する
input_interface = carb.input.acquire_input_interface()
keyboard = omni.appwindow.get_default_app_window().get_keyboard()
keyboard_subscription = input_interface.subscribe_to_keyboard_events(keyboard, on_keyboard_event)

SimulationManager.setup_simulation(dt=PHYSICS_DT, device="cpu")
app_utils.play()
print("[keyboard_drive] ビューポートをクリックしてから矢印キーを押してください", flush=True)

step = 0
while simulation_app.is_running():
    if app_utils.is_playing():
        # 押されているキーの指令を足し合わせる (↑ と ← を同時に押すと、左に曲がりながら進む)
        linear_speed = sum(KEY_COMMANDS[key][0] for key in pressed_keys)
        angular_speed = sum(KEY_COMMANDS[key][1] for key in pressed_keys)
        jetbot.apply_wheel_actions(controller.forward([linear_speed, angular_speed]))
        if pressed_keys and step % 60 == 0:  # 走っている間は 1 秒ごとに位置を表示する
            positions, _ = jetbot.get_world_poses()
            x, y, _ = positions.numpy()[0]
            print(f"[keyboard_drive] 位置 = ({x:5.2f}, {y:5.2f})", flush=True)
        step += 1
    simulation_app.update()

input_interface.unsubscribe_to_keyboard_events(keyboard, keyboard_subscription)
app_utils.stop()
simulation_app.close()
