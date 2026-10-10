"""SimulationApp を起動し、数フレーム更新してから終了する最小のスクリプト。

実行方法 (コンテナ内):
    /isaac-sim/python.sh /workspace/examples/04_python_standalone/01_hello_simulation_app.py

公式サンプル standalone_examples/api/isaacsim.simulation_app/hello_world.py (v6.1.0)
をもとにしている。
"""

import time

# 1. SimulationApp を起動する (Isaac Sim 本体が立ち上がる)
#    Isaac Sim のモジュールは、これより後でないと import できない
from isaacsim import SimulationApp

start = time.perf_counter()
simulation_app = SimulationApp({"headless": True})
print(f"[hello] SimulationApp の起動にかかった時間: {time.perf_counter() - start:.1f} 秒")

# 2. Isaac Sim のモジュールを import する
import omni.kit.app

app = omni.kit.app.get_app()
print(f"[hello] Kit のバージョン: {app.get_build_version()}")

# 3. アプリを数フレーム更新する
for _ in range(10):
    simulation_app.update()
print("[hello] 10 フレーム更新しました")

# 4. 終了する
simulation_app.close()
