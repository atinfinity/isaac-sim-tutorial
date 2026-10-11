# 付録 C: ROS 2 のトピックを配信・購読する

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) で、ヘッドレスで実行して動作を確認しました。ROS 2 側は公式の Docker イメージ `ros:jazzy-ros-base` を使いました。

| ファイル | 内容 |
| --- | --- |
| `ros2_pubsub.py` | `/clock` を配信し、`/move_cube` (`std_msgs/msg/Empty`) を購読する |
| `fastdds.xml` | Fast DDS の通信を UDP だけにする設定。公式の [IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces) の `jazzy_ws/fastdds.xml` をそのまま使っている (Apache-2.0) |

## 実行方法

リポジトリのルートで、端末を 2 つ使います。

1 つ目の端末で、Isaac Sim 側のスクリプトを起動します。既定では 60 秒で終了します (`--duration` で変えられます)。

```bash
docker compose -f docker/compose.yml run --rm --no-deps \
  -e FASTRTPS_DEFAULT_PROFILES_FILE=/workspace/examples/appendix_c_ros2/fastdds.xml \
  --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/appendix_c_ros2/ros2_pubsub.py
```

`[ros2_pubsub] 開始します` と表示されたら、2 つ目の端末で ROS 2 のコンテナを起動し、トピックを確かめます。

```bash
docker run --rm -it --network host ros:jazzy-ros-base bash
# 以下はコンテナ内で実行する
source /opt/ros/jazzy/setup.bash
ros2 topic list
ros2 topic echo --once /clock
ros2 topic pub --times 3 --rate 1 /move_cube std_msgs/msg/Empty "{}"
```

`FASTRTPS_DEFAULT_PROFILES_FILE` は、Isaac Sim 側と ROS 2 側のどちらか一方に設定すれば十分でした。設定しないと、トピックの一覧には出てもデータが届きません (付録 C の本文を参照)。

## 検証で確認したこと

- [x] Isaac Sim 側に `FASTRTPS_DEFAULT_PROFILES_FILE` を設定した場合: `ros2 topic list` に `/clock` と `/move_cube` が出る。`ros2 topic echo --once /clock` でシミュレーション時刻 (`sec: 10` `nanosec: 850000000`) が届く。`ros2 topic hz /clock` は約 79 Hz。`/move_cube` を 3 回配信すると、Isaac Sim 側で 3 回とも受信する
- [x] ROS 2 側だけに設定した場合: 同じく `/clock` が届き (約 72 Hz)、`/move_cube` を 3 回とも受信する
- [x] どちらにも設定しない場合: `ros2 topic list` には `/clock` と `/move_cube` が出るが、`ros2 topic echo --once /clock` は 10 秒待っても何も表示されず、`ros2 topic hz /clock` も何も表示されない。`/move_cube` の受信は 0 回
- [ ] `docker compose up` で起動した Isaac Sim (GUI) との接続、カメラや LiDAR のトピックは試していない
