# 付録 E: 自作ロボットの取り込み (URDF)

> [!NOTE]
> 検証環境 (Ubuntu 24.04 + RTX 2080 Ti、Isaac Sim 6.1.0 の Docker イメージ) で、ヘッドレスで実行して動作を確認しました。GUI の `File > Import` による取り込みも、Web ビューアで確かめました。

| ファイル | 内容 |
| --- | --- |
| `my_diffbot.urdf` | 題材にする差動二輪ロボット (Jetbot とほぼ同じ大きさ、箱・円柱・球だけで作っている) |
| `01_import_urdf.py` | URDF を URDF Importer の Python API で USD に変換する |
| `02_inspect_robot.py` | 変換した USD のリンク・コリジョン・質量・関節を表示する |
| `03_drive_my_robot.py` | 変換したロボットを 5 章と同じ手順 (直進 → 左に 90 度旋回 → 直進) で走らせる |

## 実行方法

リポジトリのルートで、`01` → `02` → `03` の順に実行します。`01` で変換した USD は `/isaac-sim/.local/share/ov/data/output/appendix_e_urdf/my_diffbot/` (ホストでは `~/docker/isaac-sim/data/output/appendix_e_urdf/my_diffbot/`) に保存され、`02` と `03` はそれを読み込みます。

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/appendix_e_urdf/01_import_urdf.py
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/appendix_e_urdf/02_inspect_robot.py
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/appendix_e_urdf/03_drive_my_robot.py
```

- `01_import_urdf.py --default`: 設定を変えずに (既定のまま) 変換する。土台が床に固定され、車輪の駆動の強さが 0 になる
- `03_drive_my_robot.py --no-caster-material`: 補助輪に摩擦 0 の物理マテリアルを割り当てずに走らせる

`--default` で変換したあとは、もう一度 `--default` なしで `01` を実行してから `02`・`03` に戻ってください。

## 検証で確認したこと

- [x] 3 本とも、エラーなく最後まで実行できる
- [x] `01`: 2 回目以降は前回の出力を消してから、同じ場所に変換する。`my_diffbot.usda` と `payloads/` の下の 5 つの `.usda` ができる
- [x] `02`: variant `Physics` (`mujoco`・`none`・`physics`・`physx`) のうち `physx` を選んで読み込める。変換した直後の USD では、どれも選ばれていない
- [x] `02`: 質量 (0.5・0.05・0.05・0.01 kg)、コリジョンの形と大きさ、関節の種類と回転軸が URDF のとおりになる。車輪の関節の駆動は stiffness 0、damping 174.53、maxForce 1.0
- [x] `02` (`01 --default` のあと): `root_joint` (固定関節) ができ、damping が 0 になる
- [x] `03`: 旋回で向きが 73.8 度変わる (5 章の Jetbot は 74.0 度)。最後の位置は x = 0.771 m、y = 0.529 m
- [x] `03 --no-caster-material`: 旋回で向きが 47.1 度しか変わらない
- [x] `03` の補助輪のマテリアルで、摩擦の組み合わせ方を既定 (平均) のままにすると、旋回で向きが 60.1 度変わる
- [x] 0.2 m/s で 2 秒進む指令で比べると、既定のままでは動かない (車輪は指令と関係なく 77.03 と -6.09 rad/s で回る)、`fix_base=False` だけでも動かない (車輪がほぼ回らない)、駆動の設定も加えると 0.361 m 進む
- [x] `URDFImporterConfig` の `usd_path` の既定値は URDF と同じフォルダ。`examples/` は読み取り専用でマウントしているので、保存先を指定する
- [x] `WheeledRobot(..., usd_path=<変換した USD>)` で読み込むと、variant が選ばれず `Path.IsValidPathString(NoneType)` で止まる
- [x] GUI の `File > Import` (Base Type: Mobile) で取り込める。ダイアログに関節の駆動の設定はなく、車輪の関節の damping は入らない (警告「Stiffness and damping not available joint ...」が出る)。`Add Reference to Stage` では `/my_diffbot` に読み込まれ、variant `Physics` は `physx` が選ばれる
