# 付録 C. 次の一歩

!!! info "この章で学ぶこと"
    ROS 2 連携や Isaac Lab など、このチュートリアルの先に進むための情報

    - **所要時間**: 15 分
    - **前提**: 7 章
    - **対象バージョン**: Isaac Sim 6.1.0

7 章までで、Python のスタンドアロンスクリプトからシーンを作り、Jetbot を動かし、カメラと LiDAR のデータを取得して障害物回避を行いました。この付録では、そこから先に進むための代表的な方向を紹介します。どれも本チュートリアルの範囲外なので、概要と公式ドキュメントへの入り口だけを示します。

!!! note "この付録の内容はほとんど未検証です"
    本チュートリアルの検証環境 (Ubuntu 24.04 + RTX 2080 Ti) で確認したのは、[同梱の ROS 2 ライブラリが読み込まれること](#ros2-internal-libs) だけです。トピックの配信・購読や Isaac Lab などは試していません。バージョンの対応関係などは、執筆時点の公式ドキュメントに基づいています。

## ROS 2 との連携 {#ros2}

実際のロボット開発では、ロボットのソフトウェアを ROS 2 で書くことが多くあります。Isaac Sim には ROS 2 Bridge があり、シミュレータ上のセンサデータを ROS 2 のトピックとして配信したり、ROS 2 から受け取った速度指令でロボットを動かしたりできます。7 章の障害物回避を ROS 2 のノードとして書き直し、同じノードを実機でも使う、といった使い方ができます。

!!! note "Isaac ROS とは別物"
    ROS 2 Bridge は Isaac Sim の機能です。名前の似た Isaac ROS は、実機のロボットで動かす GPU 高速化された ROS 2 のパッケージ群で、Isaac Sim とは別のソフトウェアです。違いは [0 章の「Isaac Sim と関連するソフトウェア」](../00-introduction.md#ecosystem) を参照してください。

Isaac Sim 6.1.0 が対応している ROS 2 のディストリビューションは次の 2 つです。

| ディストリビューション | 対象の OS | 備考 |
| --- | --- | --- |
| Jazzy | Ubuntu 24.04 | 本チュートリアルの検証環境ではこちらを推奨 |
| Humble | Ubuntu 22.04 | |

Isaac Sim には ROS 2 のライブラリが同梱されています (internal ROS libraries)。そのため、Isaac Sim 側に ROS 2 をインストールしなくても ROS 2 Bridge は動作します。ただし、`ros2 topic echo` などのコマンドや自作のノードを動かすには、ホストや別のコンテナに ROS 2 を用意する必要があります。

### 同梱の ROS 2 ライブラリを確かめる {#ros2-internal-libs}

本チュートリアルの Docker 構成 (`docker compose -f docker/compose.yml up -d`) でも、起動時に同梱の ROS 2 ライブラリが読み込まれます。`docker compose` で起動して `(healthy)` になったあと、Isaac Sim のログ (ホストの `~/docker/isaac-sim/logs/Kit/` の下にある `kit_*.log`) を検索すると確認できます。

```bash
log=$(ls -t ~/docker/isaac-sim/logs/Kit/*/*/kit_*.log | head -1)   # いちばん新しいログ
grep -a -E "rclpy|\[ext: isaacsim\.ros2\.bridge-.*\] startup" "$log" | grep -v walked
```

検証環境では、次の出力がありました (行頭の時刻などは省略しています)。

```text
Attempting to load system rclpy
Could not import system rclpy: No module named 'rclpy'
Attempting to load internal rclpy for ROS Distro: jazzy
rclpy loaded
[ext: isaacsim.ros2.bridge-5.1.4] startup
```

コンテナに ROS 2 は入っていないので、まずシステムの `rclpy` を探して見つからず、次に同梱の Jazzy 用の `rclpy` を読み込んでいます。そのあとで ROS 2 Bridge の拡張機能 (`isaacsim.ros2.bridge`) が起動しています。

!!! tip "Docker で使う場合"
    公式ドキュメントには、ROS 2 を Docker コンテナで動かす手順 (Running ROS in Docker Containers) も載っています。ROS 2 の環境を Isaac Sim のコンテナと分けておくと、ホストを汚さずに試せます。

!!! warning "Python のバージョンに注意"
    Isaac Sim 6.1.0 の Python は 3.12 です。`rclpy` で独自のメッセージ型 (Custom ROS Interfaces) を使う場合は、ワークスペースも Python 3.12 でビルドする必要があります。Ubuntu 22.04 + Humble の組み合わせでは標準の Python が 3.10 なので、特に注意してください。

まずは公式の ROS 2 チュートリアルの最初の数本を順に進めるのがおすすめです。インストール手順と、チュートリアルで使う ROS 2 ワークスペース ([IsaacSim-ros_workspaces](https://github.com/isaac-sim/IsaacSim-ros_workspaces)) の準備から始まります。

## Isaac Lab で強化学習 {#isaac-lab}

Isaac Lab は、Isaac Sim の上に作られたロボット学習用のフレームワークです。多数の環境を GPU 上で並列にシミュレーションし、強化学習や模倣学習でロボットの制御方策を学習させます。本チュートリアルでは制御則を手で書きましたが、Isaac Lab では「何を達成すればよいか」を報酬として与え、動かし方そのものを学習させます。

Isaac Lab は Isaac Sim のバージョンと対応が決まっています。執筆時点での対応は次のとおりです。

| Isaac Lab | 対応する Isaac Sim |
| --- | --- |
| `v3.0.0-EA` タグ / `release/3.0.0` ブランチ / `develop` ブランチ | 6.1 |
| `main` ブランチ / v2.3.X | 4.5 / 5.0 / 5.1 |

`main` ブランチは Isaac Sim 6.1 に対応していない点に注意してください。本チュートリアルと同じ Isaac Sim 6.1.0 で試す場合は、`v3.0.0-EA` (Early Access 版) か `release/3.0.0` を使います。対応関係は今後変わる可能性があるので、必ず Isaac Lab のインストールガイドで最新の情報を確認してください。

!!! warning "動作要件"
    Isaac Lab の推奨環境は RAM 32GB・VRAM 16GB です。本チュートリアルの検証環境の RTX 2080 Ti (VRAM 11GB) はこれを満たしていません。並列環境の数を減らせば動く場合もありますが、本格的に学習させるなら要件を満たす GPU か、[付録 A](cloud.md) で紹介するクラウド環境を検討してください。

インストール方法は pip・バイナリ・ソース・Docker から選べます。本チュートリアルと同じく Docker で環境を揃えたい場合は、Docker を使う方法が扱いやすいでしょう。

## その他の方向 {#other-directions}

ROS 2 と Isaac Lab 以外にも、Isaac Sim には次のような機能があります。興味に合わせて公式ドキュメントを読み進めてください。

- **公式サンプル (Examples)**: 本チュートリアルが参考にした standalone_examples を含め、マニピュレータ・移動ロボット・人型ロボットなど多くのサンプルがあります。次に何をするか迷ったら、まずここから気になるものを動かしてみるのがおすすめです
- **合成データ生成 (Replicator)**: 物体の位置・照明・テクスチャなどをランダムに変えながら画像とアノテーションを大量に生成し、物体検出などの学習データを作れます。6 章で使ったアノテータの仕組みの延長にあります
- **自作ロボットの取り込み (Robot Setup / URDF Importer)**: URDF などで記述されたロボットを取り込み、関節やコリジョンを設定する方法です。Jetbot 以外のロボットを使いたくなったら読んでください
- **センサ (Sensors)**: 6 章で扱ったカメラと LiDAR のほかに、IMU・接触センサ・レーダなどがあります。各センサの設定方法もここで説明されています

## まとめ {#summary}

- ROS 2 Bridge を使うと、Isaac Sim を ROS 2 のシステムにつないで、実機と同じノードをシミュレーション上で動かせます。Isaac Sim 6.1.0 は Jazzy と Humble に対応しています
- Isaac Lab を使うと、ロボットの制御方策を強化学習などで学習させられます。Isaac Sim 6.1 に対応するのは `v3.0.0-EA` / `release/3.0.0` で、VRAM 16GB が推奨です
- このほか、合成データ生成・自作ロボットの取り込み・各種センサなど、目的に応じて公式ドキュメントを読み進めてください

## 演習 {#exercises}

1. 公式の ROS 2 チュートリアルを参考に、Jetbot のカメラ画像を ROS 2 のトピックとして配信し、`ros2 topic list` でトピックが見えることを確認してみましょう
2. 7 章の障害物回避を、LiDAR のトピック (`sensor_msgs/msg/LaserScan` など) を購読して速度指令 (`geometry_msgs/msg/Twist`) を配信する ROS 2 ノードとして書き直すには、どの部分をどう分ければよいか考えてみましょう
3. Isaac Lab のインストールガイドで、自分の環境 (OS・GPU・Isaac Sim のバージョン) に合う Isaac Lab のバージョンとインストール方法を調べてみましょう

## 参考リンク {#references}

- [ROS 2 (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/ros2_tutorials/index.html)
- [ROS 2 Installation (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_ros.html)
- [IsaacSim-ros_workspaces (GitHub)](https://github.com/isaac-sim/IsaacSim-ros_workspaces)
- [Isaac Lab ドキュメント](https://isaac-sim.github.io/IsaacLab/main/index.html)
- [Isaac Lab インストールガイド](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html)
- [Examples (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/introduction/examples.html)
- [Replicator (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/replicator_tutorials/index.html)
- [Robot Setup (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/robot_setup/index.html)
- [URDF Importer Extension (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/importer_exporter/ext_isaacsim_asset_importer_urdf.html)
- [Sensors (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/sensors/index.html)
