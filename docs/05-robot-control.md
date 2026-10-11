# 5. ロボットを動かす

!!! info "この章で学ぶこと"
    Jetbot を Python から読み込み、関節の構造を調べてから、差動二輪の制御で走らせます。最後に、キーボードで操作する方法と、目標地点まで自動で走らせる方法を学びます。

    - **所要時間**: 45 分
    - **前提**: 4 章
    - **対象バージョン**: Isaac Sim 6.1.0

2 章の [ホイールを回して走らせる](02-gui-basics.md#drive-wheels) では、Property パネルで左右のホイールの `Target Velocity` を変えて Jetbot を走らせました。この章では同じことを Python から行い、「どれくらいの速さで進み、どれくらいの速さで曲がるか」から左右のホイールの速度を計算して走らせます。

この章のサンプルは `examples/05_robot_control/` にあります。実行のしかたは 4 章の [スクリプトをコンテナで実行する](04-python-standalone.md#run-in-container) と同じです。

| ファイル | 内容 |
| --- | --- |
| `01_load_jetbot.py` | Jetbot を読み込み、Prim の構造・リンク・関節を表示する |
| `02_drive_jetbot.py` | 直進 → 左に 90 度旋回 → 直進 と走らせる |
| `03_go_to_goal.py` | 目標地点まで自動で走らせる |
| `04_keyboard_drive.py` | Web ビューアから矢印キーで操作する |

## Jetbot のアセットを読み込む {#load-jetbot}

Jetbot の USD ファイルは、NVIDIA が公開しているアセットの置き場所 (アセットルート) にあります。2 章では Asset Browser の `Robots_Multiphysics > NVIDIA > Jetbot` からドラッグ&ドロップしました。Python では、アセットルートのパスを `get_assets_root_path()` で取得し、その後ろにファイルの場所をつなげます。

```python title="examples/05_robot_control/01_load_jetbot.py (抜粋)"
from isaacsim.core.experimental.prims import Articulation
from isaacsim.storage.native import get_assets_root_path

assets_root_path = get_assets_root_path()
jetbot_usd = assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda"

# Jetbot の USD を Reference として読み込む (3 章の Reference と同じ仕組み)
stage_utils.add_reference_to_stage(usd_path=jetbot_usd, path="/World/Jetbot")
jetbot = Articulation(
    "/World/Jetbot",
    positions=[[0.0, 0.0, 0.05]],  # 車輪が地面にめり込まない高さに置く
    reset_xform_op_properties=True,
)
```

検証環境では、アセットルートは次の URL でした。アセットはインターネット上にあり、初回の読み込み時にダウンロードされてキャッシュに残ります。

```text
[load_jetbot] アセット: https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.1/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda
```

`add_reference_to_stage()` は、3 章の [Reference](03-usd-basics.md#reference) と同じ仕組みで、Jetbot の USD ファイルを `/World/Jetbot` に取り込みます。ファイルの中身をコピーするのではなく、参照するだけです。

## Articulation と関節 {#articulation}

`01_load_jetbot.py` を実行すると、まず `/World/Jetbot` の下の Prim の構造が表示されます (深さ 3 まで)。

```text
Jetbot (Xform)
  chassis (Xform)
    left_wheel_joint (PhysicsRevoluteJoint)
    right_wheel_joint (PhysicsRevoluteJoint)
    geometry (Xform)
      left_antenna (Xform)
      ...
    rgb_camera (Xform)
      camera_base (Xform)
      jetbot_camera (Camera)
  left_wheel (Xform)
    left_wheel (Xform)
    Collision (Sphere)
  right_wheel (Xform)
    right_wheel (Xform)
    Collision (Sphere)
  Looks (Scope)
  ...
```

続いて、リンクと関節の情報が表示されます。

```text
リンク (3 個): ['chassis', 'left_wheel', 'right_wheel']
関節 (2 個): ['left_wheel_joint', 'right_wheel_joint']
自由度 DOF (2 個): ['left_wheel_joint', 'right_wheel_joint']
```

### リンク・関節・DOF {#links-and-joints}

ロボットは、いくつかの剛体を関節でつないだものとして表されます。

| 用語 | 意味 | Jetbot の場合 |
| --- | --- | --- |
| **リンク** (link) | ロボットを構成する剛体 | 車体 (`chassis`)、左右の車輪 (`left_wheel`・`right_wheel`) |
| **関節** (joint) | 2 つのリンクをつなぎ、動ける方向を決める | 車体と車輪をつなぐ `left_wheel_joint`・`right_wheel_joint` |
| **DOF** (自由度) | 独立して動かせる量の数 | 2 (左右の車輪の回転) |

Jetbot の関節の型は `PhysicsRevoluteJoint` (回転関節) です。1 つの軸のまわりに回転だけができる関節で、1 つあたり 1 DOF を持ちます。車体の前後にあるキャスター (`caster_ball_...`) は関節を持たず、車体 (`chassis`) の一部として扱われます。

このように、関節でつながったリンクの集まりを、物理エンジンでは **Articulation** として扱います。`isaacsim.core.experimental.prims` の `Articulation` クラスを使うと、関節の名前や数を調べたり、関節の位置・速度を読み書きしたりできます。

!!! warning "関節の情報は再生してから取得する"
    `num_dofs` や `dof_names` などの関節の情報は、物理エンジンが Articulation を初期化した後でないと取得できません。サンプルでは `app_utils.play()` と `simulation_app.update()` を 1 回呼んでから表示しています。

### 指令がないときの Jetbot {#idle-jetbot}

`01_load_jetbot.py` の最後では、何も指令を与えずに 1 秒進めて、Jetbot の位置と車輪の速度を表示しています。

```text
位置 (x, y, z) [m]: [-0.     0.     0.033]
姿勢 (w, x, y, z): [ 1.    -0.    -0.003 -0.   ]
車輪の角速度 [rad/s]: [0. 0.]
```

高さ 0.05 m に置いた Jetbot が 0.033 m まで下がって地面に着き、その場に止まっています。2 章で `Target Velocity` を 0 のまま再生したときと同じです。

## 差動二輪の制御 {#differential-drive}

Jetbot のように、左右の車輪の速さを変えて進んだり曲がったりする仕組みを **差動二輪** (differential drive) と呼びます。

- 左右を **同じ速さ** で回すと、まっすぐ進む
- 左右を **逆向き** に回すと、その場で回る
- 左右の **速さを変える** と、遅いほうに曲がる

2 章で、左のホイールの `Target Velocity` を 0 にすると左に曲がったのはこのためです。

### 直進速度と旋回速度から車輪の速さを求める {#wheel-velocity}

ロボットを動かすときは、「秒速何 m で進み、秒速何ラジアンで回るか」で考えるほうがわかりやすいです。この 2 つ (直進速度 v [m/s] と旋回速度 ω [rad/s]) から、左右の車輪の角速度は次の式で求められます。

- 左の車輪 = (v − ω × b / 2) / r
- 右の車輪 = (v + ω × b / 2) / r

ここで r は車輪の半径、b は左右の車輪の間隔です。Jetbot では r = 0.03 m、b = 0.1125 m です (公式サンプルの値)。旋回速度 ω は、上から見て左回り (反時計回り) をプラスとします。

この計算をしてくれるのが `DifferentialController` です。

```python title="examples/05_robot_control/02_drive_jetbot.py (抜粋)"
from isaacsim.robot.experimental.wheeled_robots.controllers import DifferentialController
from isaacsim.robot.experimental.wheeled_robots.robots import WheeledRobot

# WheeledRobot は Articulation に「車輪の関節」を扱う機能を足したクラス
jetbot = WheeledRobot(
    "/World/Jetbot",
    wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
    usd_path=assets_root_path + "/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda",
    positions=[0.0, 0.0, 0.05],
)

# 差動二輪のコントローラ: (直進速度, 旋回速度) → (左車輪, 右車輪) の角速度
controller = DifferentialController(wheel_radius=WHEEL_RADIUS, wheel_base=WHEEL_BASE)
```

`WheeledRobot` は、`usd_path` を渡すと Reference の追加までまとめて行います。`wheel_dof_names` で、どの関節が車輪かを指定します。

### 走らせる {#drive}

`02_drive_jetbot.py` では、次の予定で走らせます。

```python title="examples/05_robot_control/02_drive_jetbot.py (抜粋)"
# 走行の予定: (説明, 直進速度 [m/s], 旋回速度 [rad/s], 時間 [秒])
PLAN = [
    ("直進", 0.2, 0.0, 3.0),
    ("左に 90 度旋回", 0.0, math.pi / 4, 2.0),  # pi/4 rad/s x 2 秒 = pi/2 rad = 90 度
    ("直進", 0.2, 0.0, 3.0),
    ("停止", 0.0, 0.0, 1.0),
]

for label, linear_speed, angular_speed, duration in PLAN:
    wheel_velocities = controller.forward([linear_speed, angular_speed])
    for _ in range(round(duration / PHYSICS_DT)):
        jetbot.apply_wheel_actions(wheel_velocities)
        simulation_app.update()
```

`controller.forward([直進速度, 旋回速度])` で左右の車輪の角速度を求め、`jetbot.apply_wheel_actions()` で車輪に指令します。2 章で `Target Velocity` を入力していた操作を、Python から毎ステップ行っているわけです。

実行結果は次のとおりです。

```text
スタート           x = -0.000 m  y = -0.000 m  向き =    -0.0 度
--- 直進: 左右の車輪の角速度 = [6.67 6.67] rad/s
直進 の後          x =  0.646 m  y = -0.005 m  向き =    -1.0 度
--- 左に 90 度旋回: 左右の車輪の角速度 = [-1.47  1.47] rad/s
左に 90 度旋回 の後   x =  0.648 m  y = -0.004 m  向き =    74.0 度
--- 直進: 左右の車輪の角速度 = [6.67 6.67] rad/s
直進 の後          x =  0.822 m  y =  0.617 m  向き =    73.8 度
--- 停止: 左右の車輪の角速度 = [0. 0.] rad/s
停止 の後          x =  0.823 m  y =  0.618 m  向き =    73.8 度
```

- **直進**: 左右とも 0.2 / 0.03 = 6.67 rad/s。3 秒で 0.6 m 進む計算で、実際には 0.646 m 進みました
- **旋回**: 左右が逆向きの 1.47 rad/s。90 度回る計算ですが、実際には **74 度** しか回りませんでした

!!! note "指令どおりには動かない"
    旋回が 16 度ほど足りないのは、車輪が地面の上で滑るなど、車輪と地面の接触が理想どおりではないためと考えられます。直進の距離が計算より長いのも同じです。

    車輪の回転から計算した動きと、実際の動きはずれます。実機のロボットでも同じことが起きます。決まった時間だけ指令を出す方法 (**オープンループ** 制御) では、このずれを直せません。次の節の `03_go_to_goal.py` のように、今の位置と向きを見ながら指令を変える方法 (**フィードバック** 制御) を使います。

位置と向きは `get_world_poses()` で取得しています。向きは四元数で返ってくるので、z 軸まわりの回転角 (**ヨー角**) に変換して表示しています。

```python title="examples/05_robot_control/02_drive_jetbot.py (抜粋)"
def yaw_from_quaternion(w: float, x: float, y: float, z: float) -> float:
    """四元数 (w, x, y, z) から z 軸まわりの回転角 (ヨー角) [rad] を求める。"""
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
```

## キーボードやスクリプトで走らせる {#keyboard-and-script}

### 目標地点まで自動で走らせる {#go-to-goal}

`03_go_to_goal.py` は、Jetbot を目標地点 (既定では x = 1.5 m、y = 1.0 m) まで自動で走らせます。毎ステップ、今の位置・向きと目標地点から、直進速度と旋回速度を計算し直します。

```python title="examples/05_robot_control/03_go_to_goal.py (抜粋)"
def compute_command(x: float, y: float, yaw: float, goal: list[float]) -> tuple[float, float]:
    """現在の位置・向きと目標地点から (直進速度, 旋回速度) を求める。"""
    dx, dy = goal[0] - x, goal[1] - y
    distance = math.hypot(dx, dy)
    heading_error = wrap_angle(math.atan2(dy, dx) - yaw)  # 目標の方向と今の向きの差

    angular_speed = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, K_ANGULAR * heading_error))
    # 目標が横や後ろにあるうちは、前に進まずにその場で向きを変える
    linear_speed = min(MAX_LINEAR_SPEED, K_LINEAR * distance) * max(0.0, math.cos(heading_error))
    return linear_speed, angular_speed
```

考え方は次のとおりです。

- **旋回速度**: 目標の方向と今の向きの差 (`heading_error`) に比例させる。ずれが大きいほど速く回り、目標のほうを向くと 0 になる
- **直進速度**: 目標までの距離に比例させる。近づくほど遅くなる。さらに `cos(heading_error)` を掛けて、目標が横や後ろにあるうちは前に進まないようにする
- どちらも上限 (`MAX_LINEAR_SPEED`・`MAX_ANGULAR_SPEED`) で頭打ちにする

このように、ずれの大きさに比例した指令を出す方法を **比例制御** (P 制御) と呼びます。実行結果は次のとおりです。

```text
[go_to_goal] 目標地点: (1.50, 1.00)
t =  0.0 秒  位置 = (-0.00, -0.00)  向き =   -0.0 度  残り = 1.80 m
t =  1.0 秒  位置 = ( 0.23,  0.08)  向き =   30.3 度  残り = 1.56 m
t =  2.0 秒  位置 = ( 0.46,  0.24)  向き =   35.3 度  残り = 1.29 m
...
t =  9.0 秒  位置 = ( 1.45,  0.96)  向き =   36.8 度  残り = 0.06 m
[go_to_goal] 到着しました (9.4 秒)
```

目標の方向は約 34 度です。最初の 1〜2 秒でそちらを向き、その後はまっすぐ進んで、近づくにつれて遅くなっています。`02_drive_jetbot.py` では旋回が足りませんでしたが、こちらは向きのずれを毎ステップ見て直すので、目標にたどり着けます。

`--goal` で目標地点を変えられます。たとえば `--goal -1.0 1.5` (左斜め後ろ) にすると、最初の 2 秒ほどはほとんど前に進まずに向きを変え (1 秒後に 80.9 度、2 秒後に 121.3 度)、その後まっすぐ進んで 10.3 秒で到着しました。

`--livestream` を付けると Web ビューアで動きを見られます。このときは、Web ビューアで再生 (▶) を押すまで動き出しません (接続する前に走り終わらないようにするため)。

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/05_robot_control/03_go_to_goal.py --goal -1.0 1.5 --livestream
```

7 章では、このスクリプトに LiDAR による障害物回避を加えます。

### キーボードで操作する {#keyboard}

`04_keyboard_drive.py` では、Web ビューアから矢印キーで Jetbot を操作します。キーボードの入力は Web ビューアから送るので、このスクリプトは `--livestream` を付けなくても常に画面を配信します。手順は 4 章の [Web ビューアで画面を見ながら実行する](04-python-standalone.md#run-with-livestream) と同じです。

```bash
docker compose -f docker/compose.yml stop isaac-sim
docker compose -f docker/compose.yml up -d --no-deps web-viewer

docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/05_robot_control/04_keyboard_drive.py
```

ログに `ビューポートをクリックしてから矢印キーを押してください` と表示されたら、`http://localhost:8210` を開きます。

1. ビューポートの何もないところを 1 回クリックする
2. 矢印キーを押す

| キー | 動き |
| --- | --- |
| ++up++ / ++down++ | 前進 / 後退 (0.2 m/s) |
| ++left++ / ++right++ | 左 / 右に旋回 (1 rad/s) |

キーを押している間だけ走り、離すと止まります。++up++ と ++left++ を同時に押すと、左に曲がりながら進みます。終わるときは、実行したターミナルで ++ctrl+c++ を押します。

!!! warning "先にビューポートをクリックする"
    検証環境では、Web ビューアを開いただけでは、キーを押しても Jetbot は動きませんでした。ビューポートを 1 回クリックすると、キーの入力が Isaac Sim に届くようになりました。

スクリプトでは、`carb.input` でキーボードのイベントを受け取る関数を登録し、押されているキーを覚えておきます。

```python title="examples/05_robot_control/04_keyboard_drive.py (抜粋)"
import carb.input
import omni.appwindow

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


# キーボードのイベントを受け取る関数を登録する
input_interface = carb.input.acquire_input_interface()
keyboard = omni.appwindow.get_default_app_window().get_keyboard()
keyboard_subscription = input_interface.subscribe_to_keyboard_events(keyboard, on_keyboard_event)
```

メインループでは、押されているキーの指令を足し合わせて、`DifferentialController` に渡します。指令の作り方が「キーボード」に変わっただけで、車輪を動かす部分は `02_drive_jetbot.py` と同じです。

```python title="examples/05_robot_control/04_keyboard_drive.py (抜粋)"
while simulation_app.is_running():
    if app_utils.is_playing():
        # 押されているキーの指令を足し合わせる (↑ と ← を同時に押すと、左に曲がりながら進む)
        linear_speed = sum(KEY_COMMANDS[key][0] for key in pressed_keys)
        angular_speed = sum(KEY_COMMANDS[key][1] for key in pressed_keys)
        jetbot.apply_wheel_actions(controller.forward([linear_speed, angular_speed]))
    simulation_app.update()
```

!!! tip "キーボードの操作は公式サンプルにはない"
    Isaac Sim 6.1.0 の standalone_examples には、車輪型のロボットをキーボードで操作するスタンドアロンのサンプルはありません。`04_keyboard_drive.py` はこのチュートリアルで用意したものです。

## まとめ {#summary}

- Jetbot の USD は `get_assets_root_path()` で得たアセットルートから読み込む
- ロボットはリンク (剛体) を関節でつないだ **Articulation** として扱う。Jetbot はリンク 3 個、回転関節 2 個 (2 DOF)
- 差動二輪では、直進速度 v と旋回速度 ω から、左右の車輪の角速度を求める。`DifferentialController` がこの計算を行い、`WheeledRobot.apply_wheel_actions()` で車輪に指令する
- 時間を決めて指令を出すだけ (オープンループ) では、滑りなどで指令どおりに動かない。90 度の旋回指令で 74 度しか回らなかった
- 今の位置と向きを見ながら指令を計算し直す (フィードバック、比例制御) と、目標地点にたどり着ける
- `carb.input` でキーボードのイベントを受け取れば、Web ビューアから操作できる

## 演習 {#exercises}

1. `02_drive_jetbot.py` の旋回の時間を延ばして、ちょうど 90 度回るように調整してください。何秒にすればよいでしょうか。
2. `02_drive_jetbot.py` の `PLAN` を書き換えて、Jetbot に 1 辺 0.5 m の正方形を描かせてみましょう。スタート地点にどれくらい正確に戻ってくるでしょうか。
3. `03_go_to_goal.py` の `K_ANGULAR` を `0.5` や `8.0` に変えて、到着までの時間と動き方がどう変わるかを確かめてください (`--livestream` で見るとわかりやすいです)。
4. `04_keyboard_drive.py` に、++space++ を押すと止まる機能を追加してください (ヒント: `carb.input.KeyboardInput.SPACE`。Isaac Sim の再生・一時停止のショートカットと重なる点にも注意しましょう)。

## 参考リンク {#references}

- [Mobile Robot Controllers (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/robot_simulation/mobile_robot_controllers.html)
- [Wheeled Robots (Experimental) API (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/py/source/extensions/isaacsim.robot.experimental.wheeled_robots/docs/index.html)
- [Core Experimental API: Prims (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/py/source/extensions/isaacsim.core.experimental.prims/docs/index.html)
- [Physics Simulation Fundamentals (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/physics/simulation_fundamentals.html)
- [jetbot_differential_move.py (standalone_examples v6.1.0、GitHub)](https://github.com/isaac-sim/IsaacSim/blob/v6.1.0/source/standalone_examples/api/isaacsim.robot.wheeled_robots.examples/jetbot_differential_move.py)
