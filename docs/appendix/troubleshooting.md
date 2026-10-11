# 付録 B. トラブルシューティング

!!! info "この章で学ぶこと"
    よくあるエラーと対処法

    - **所要時間**: -
    - **前提**: 1 章
    - **対象バージョン**: Isaac Sim 6.1.0

この付録のエラーメッセージは、検証環境 (Ubuntu 24.04 + RTX 2080 Ti) でわざと問題を起こして確認したものです。再現できなかった問題は、考えられる原因だけを挙げています。

うまく動かないときは、まず次の 3 つを確認してください。

```bash
nvidia-smi                                  # ホストで GPU とドライバが認識されているか
docker compose -f docker/compose.yml ps     # コンテナが起動し、healthy になっているか
docker compose -f docker/compose.yml logs isaac-sim | tail -50   # Isaac Sim のログ
```

ここにない問題に出会ったら、[Issue](https://github.com/atinfinity/isaac-sim-tutorial/issues/new/choose) で報告してもらえると助かります。

## 環境構築 {#setup}

### `driver/library version mismatch` でコンテナが起動しない {#driver-mismatch}

`docker compose run` や `docker compose up` で、次のようなエラーが出てコンテナが起動しないことがあります。

```text
nvidia-container-cli: initialization error: nvml error: driver/library version mismatch: unknown
```

このとき、ホストの `nvidia-smi` も `Failed to initialize NVML: Driver/library version mismatch` で失敗します。

NVIDIA ドライバを更新したあと、PC を再起動していないのが原因です。ドライバのライブラリは新しいバージョンに置き換わっていますが、動いているカーネルモジュールは古いままなので、両者のバージョンが合いません。PC を再起動してください。

```bash
cat /proc/driver/nvidia/version   # 動いているカーネルモジュールのバージョン
```

再起動後に `nvidia-smi` が正常に表示されれば解決です。

### その他の理由でコンテナが起動しない {#container-not-starting}

エラーメッセージから原因を切り分けます。

**`unknown or invalid runtime name`**: Docker に `nvidia` ランタイムが登録されていません。

```text
docker: Error response from daemon: unknown or invalid runtime name: nvidia
```

NVIDIA Container Toolkit が入っていないか、インストール後の Docker の設定 (`nvidia-ctk runtime configure --runtime=docker` と Docker の再起動) をしていないのが原因です。1 章の [Docker と NVIDIA Container Toolkit](../01-setup.md#docker) の手順をやり直し、`docker info | grep -i runtimes` に `nvidia` が出ることを確認してください。

!!! note
    検証環境には Container Toolkit が入っているため、存在しないランタイム名 (`nvidiax`) を指定して同じ種類のエラーが出ることを確認しました。

**`manifest unknown`**: 指定したイメージのタグが存在しません。

```text
Error response from daemon: manifest for nvcr.io/nvidia/isaac-sim:6.1.99 not found: manifest unknown: manifest unknown
```

`docker/.env` の `ISAAC_SIM_IMAGE` を設定している場合は、タグ (`6.1.0`) の綴りを確認してください。ネットワークの問題でイメージを取得できない場合も `docker pull` の段階で失敗するので、`docker pull nvcr.io/nvidia/isaac-sim:6.1.0` を単独で実行して確認します。

**上のどちらでもない場合**: NVIDIA ドライバが古い可能性があります (検証環境では再現していません)。ホストの `nvidia-smi` の右上に出るドライバのバージョンが、[Isaac Sim Requirements](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html) の要件を満たしているかを確認してください。

!!! tip
    `nvcr.io/nvidia/isaac-sim:6.1.0` の取得に NGC へのログイン (`docker login nvcr.io`) は必要ありません。

### キャッシュ用ディレクトリの権限エラー {#permission-denied}

キャッシュ用ディレクトリをホストのユーザーの所有のままにしておくと、コンテナは起動しますが、ログに次のようなエラーがたくさん出て、Isaac Sim が正しく動きません。

```text
[Error] [omni.datastore] Failed to create local file data store at '/isaac-sim/kit/cache/DerivedDataCache'
[Error] [omni.rtx] Failed to initialize rtx::shaderdb::ContextManager
PermissionError: [Errno 13] Permission denied: '/isaac-sim/.cache/warp'
pxr.Tf.ErrorException: ... OmniUsdResolver: Unable to open asset '.../default_environment.usd'. Could not download local file
```

!!! warning
    このときも、スクリプトの終了コードは 0 (成功) になることがあります。終了コードだけで判断せず、ログに `Permission denied` がないかを確認してください。

コンテナ内の Isaac Sim は uid 1234 のユーザーで動きます。ホスト側のキャッシュ用ディレクトリが uid 1234 の所有になっていないと、書き込みに失敗します。1 章の手順どおりに作成し直してください。

```bash
sudo chown -R 1234:1234 ~/docker/isaac-sim ~/.cache/ov/hub
```

### サンプルの出力ファイルを保存できない {#output-permission}

6 章・7 章のサンプルは、ホストのディレクトリをマウントして画像を保存します。保存先のディレクトリを uid 1234 が書き込めないと、次のようなエラーが出ます。

```text
[Error] [omni.kit.app._impl] [py stderr]: PermissionError: [Errno 13] Permission denied: '/tmp/output/06_camera'
```

!!! warning
    このエラーが出ても、スクリプトの終了コードは 0 (成功) になります。画像ができていないときは、ログに `PermissionError` がないかを確認してください。

コンテナ内の Isaac Sim は uid 1234 のユーザーで動きます。マウントするディレクトリの所有者を uid 1234 に変えてください。

```bash
sudo chown 1234:1234 output
```

`sudo` を使えない場合は、1 章で作った `~/docker/isaac-sim/data` (すでに uid 1234 の所有) に保存する方法もあります。このディレクトリはコンテナの `/isaac-sim/.local/share/ov/data` にマウントされているので、`--output` で保存先を指定します。

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/06_sensors/01_camera.py --output /isaac-sim/.local/share/ov/data/output/06_camera
```

画像はホストの `~/docker/isaac-sim/data/output/06_camera/` にできます (所有者は uid 1234 なので、ホストのユーザーは読めますが書き換えられません)。

### 互換性チェックの結果の読み方 {#compatibility-check}

1 章の互換性チェック (`isaac-sim.compatibility_check.sh`) は、最後に `System checking result: PASSED` と表示されれば問題ありません。検証環境 (RTX 2080 Ti / VRAM 11GB / RAM 32GB) では次のように表示されました。

| 項目 | 表示 | 意味 |
| --- | --- | --- |
| GPU 0: VRAM | `enough (more is recommended)` | 最低要件 (10GB) は満たすが、推奨には届かない |
| RAM | `enough (more is recommended)` | 最低要件 (32GB) は満たすが、推奨には届かない |
| Display | `no display was detected` | ヘッドレスで動かしているため。Web ビューアで表示するので問題ない |

途中で次のような警告が出ますが、ヘッドレスで動かすときに出るもので、動作には影響しませんでした。

- `OmniHub: ... Hub encountered error. Trying to reconnect to Hub.` (数十回繰り返す)
- `GLFW initialization failed.` / `Failed to startup plugin carb.windowing-glfw.plugin`
- `failed to open the default display.`
- `IOMMU is enabled.`

## Web ビューア {#web-viewer}

### Web ビューアに何も映らない {#blank-viewer}

表示によって原因が分かれます。

**`Reconnection attempt (5 of 5) failed` と表示される**: Web ビューアが Isaac Sim に接続できていません。Isaac Sim が動いていないときは、次のように表示されます。

```text
ERROR

Reconnection attempt (5 of 5) failed. Session start failed with error: "Error occurred during sign-in request to signaling server."
```

`docker compose -f docker/compose.yml ps` で `isaac-sim` が `(healthy)` になっているかを確認してください。起動中 (`health: starting`) の場合は、healthy になるまで待ってからページを再読み込みします。スクリプトを `--livestream` 付きで実行している場合は、スクリプトの起動が終わるまで待ってから再読み込みします。

**画面が真っ黒のまま**: 接続した直後は、映像が黒いままのことがあります。ビューポートの上でマウスを動かすと表示されます。

**それでも映らない場合**: 次の原因が考えられます (検証環境では再現していません)。

- Chromium 系以外のブラウザを使っている。Chrome や Edge で開いてください
- 別の PC から接続しているのに `ISAACSIM_HOST` を設定していない ([別の PC のブラウザから接続できない](#remote-access) を参照)

### メニューが見えない (画面の上端が切れる) {#menu-hidden}

Isaac Sim の画面は表示されるのに、上端のメニューバー (`File`・`Edit`・`Create` など) が見えないことがあります。ブラウザのウィンドウが小さく、画面の上端が切れているのが原因です。

ブラウザを全画面表示にすると、メニューが見えるようになります。

### キー操作が効かない {#key-input}

Web ビューアでは、キー操作はブラウザに表示された映像にフォーカスがあるときだけ Isaac Sim に届きます。++f++ や ++space++ などが効かないときは、一度ビューポートをクリックしてから押してください (2 章の [ビューポートの操作](../02-gui-basics.md#viewport-navigation) も参照)。

### 別の PC のブラウザから接続できない {#remote-access}

既定の設定では、Web ビューアは `127.0.0.1` (ブラウザを開いた PC 自身) の Isaac Sim に接続しようとします。別の PC から開くには、Isaac Sim を動かしているホストの LAN 側 IP アドレスを設定します。

1. ホストの IP アドレスを調べます

    ```bash
    hostname -I
    ```

2. `docker/.env.example` を `docker/.env` にコピーし、`ISAACSIM_HOST` の行のコメントを外して、調べた IP アドレスに書き換えます

    ```bash
    ISAACSIM_HOST=192.168.1.50
    ```

3. Web ビューアはビルド時に `ISAACSIM_HOST` の値を埋め込むので、`--build` を付けて起動し直します

    ```bash
    docker compose -f docker/compose.yml up -d --build
    ```

4. 両方のサービスが `(healthy)` になったら、ブラウザで `http://<ホストの IP アドレス>:8210` を開きます

検証環境では、この手順で `http://192.168.1.50:8210` を開き、Isaac Sim の画面が表示されることを確認しました。

それでも接続できない場合は、ホストのファイアウォールで次のポートが塞がれていないかを確認してください。

| ポート | 用途 |
| --- | --- |
| 8210 | Web ビューアのページ |
| 49100 | シグナリング (接続の確立) |
| 47998 | 映像のストリーミング |

!!! tip "元に戻すとき"
    `docker/.env` から `ISAACSIM_HOST` の行を消し (またはコメントに戻し)、もう一度 `--build` を付けて起動します。

### 画面がカクつく・遅延が大きい {#laggy-viewer}

検証環境では、同じ LAN 内の別の PC から接続して、ビューポートの操作やシミュレーションの再生でカクつきや遅延は感じませんでした。カクつく場合は、次の原因が考えられます (検証環境では再現していません)。

- Wi-Fi など、ネットワークの帯域が足りない。有線 LAN で接続するか、同じ PC のブラウザ (`http://localhost:8210`) で開いて比べてみてください
- GPU の負荷が高い。`nvidia-smi` で GPU の使用率を確認し、シーンを軽くする (ロボットやセンサの数を減らす) と改善するかを試してください

## 実行時 {#runtime}

### 画面の下端に黄色い警告が出る {#status-bar-warnings}

GUI を操作していると、画面の下端 (ステータスバー) に黄色い警告が表示されることがあります。検証環境では次の警告が出ましたが、どれも操作やシミュレーションには影響しませんでした。

| 警告 | 出たとき |
| --- | --- |
| `Failed to startup plugin carb.windowing-glfw.plugin ...` | 再生を止めたとき。ヘッドレスで動かしているために出る |
| `Encountered USD Warnings but USD Diagnostics are muted. ...` | Jetbot をドラッグ&ドロップで配置したとき |
| `Warning: attribute isaac:actuator not found for path /World/jetbot/chassis/left_wheel_joint` | Stage でホイールの関節を選んだとき |
| `Unexpected reference count of 2 for UsdStage ...` | `File > Save As...` で保存したとき |

警告が出たあとに期待どおりに動かないときは、下段の **Console** タブにエラーが出ていないかを確認してください。

### Create メニューに Jetbot がない {#jetbot-not-in-menu}

`Create > Robots` に直接並んでいるのは、Ant・Spot・Franka・Humanoid・Nova Carter・Quadcopter だけです。Jetbot は `Create > Robots > Asset Browser` で Content タブを開き、左のツリーで `Isaac Sim` の下の `Robots_Multiphysics > NVIDIA > Jetbot` にある `jetbot.usda` を、ビューポートにドラッグ&ドロップして配置します。

### 起動が遅い {#slow-startup}

初回の起動では、シェーダーのコンパイルとアセットのダウンロードが行われるため時間がかかります。キャッシュ用ディレクトリをマウントしていれば、2 回目以降は速くなります。

検証環境 (RTX 2080 Ti / Core i7-9800X) での所要時間は次のとおりでした。

| 処理 | 初回 | 2 回目 |
| --- | --- | --- |
| イメージの取得 (`docker pull`、21.1GB) | 約 17 分 | - |
| スモークテスト (ヘッドレスで Python スクリプトを実行) | 約 4.5 分 | 約 1 分 |
| `docker compose up` で healthy になるまで | 約 4.5 分 (Web ビューアのビルドを含む) | 約 1.5 分 |

起動直後は CPU 使用率が高い状態 (16 論理コアのうち 13 コア分ほど) がしばらく続きます。

### アセットを読み込めない {#asset-loading}

5 章以降のサンプルは、Jetbot などのアセットをインターネット上のサーバー (Amazon S3) から読み込みます。ネットワークにつながらない状態で実行すると、次のエラーで止まります。

```text
RuntimeError: Could not find assets root folder: https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.1
```

アセットのルートを調べる `get_assets_root_path()` が、サーバーに接続できずに失敗しています。ホストからインターネットに接続できるか (プロキシの設定が必要な環境ではないか) を確認してください。

!!! warning
    このエラーでも、スクリプトの終了コードは 0 (成功) になりました。

検証環境では、ネットワークを切ったコンテナ (`docker run --network none`) で 5 章のサンプルを実行して、このエラーを確認しました。エラーになるまでに約 80 秒かかります。

### GPU のメモリが足りない {#out-of-memory}

検証環境 (RTX 2080 Ti / VRAM 11GB) で Web ビューアから GUI を使ったときの使用量は次のとおりでした。Jetbot 1 台程度のシーンであれば、VRAM 11GB でも十分に余裕があります。

| 状態 | VRAM | RAM (isaac-sim コンテナ) |
| --- | --- | --- |
| 起動直後 (空のシーン) | 約 0.8GB | 約 9.6GB |
| Jetbot を配置 | 約 1.9GB | 約 12.6GB |
| Jetbot を配置して再生中 | 約 2.1GB | 約 12.7GB |

このチュートリアルの範囲では、メモリ不足は再現しませんでした。大きなシーンでメモリが足りなくなった場合は、次を試してください。

- `nvidia-smi` で、ほかのプロセス (別の Isaac Sim のコンテナなど) が VRAM を使っていないかを確認する
- `docker stats` で、isaac-sim コンテナの RAM の使用量を確認する
- シーンのロボットやセンサの数、カメラの解像度を減らす

### サンプルコードでエラーが出る {#example-errors}

まず、ログの中のエラー (`Error` や `Traceback`) を確認してください。Isaac Sim のログは長いので、`grep` で絞り込むと見つけやすくなります。

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/05_robot_control/01_load_jetbot.py 2>&1 | grep -a -E "Error|Traceback"
```

!!! warning "終了コードは当てにならない"
    スクリプトの中で例外が起きても、終了コードが 0 (成功) になることがあります。期待した出力 (画像やメッセージ) が出ているかで判断してください。

よく出るエラーと参照先は次のとおりです。

| エラー | 原因 | 参照先 |
| --- | --- | --- |
| `No module named 'isaacsim'` | `python.sh` 以外の Python で実行している | [下記](#no-module-isaacsim) |
| `No module named 'pxr'` | USD のパスを設定せずに 3 章のスクリプトを実行している | [下記](#no-module-pxr) |
| `RuntimeError: Could not find assets root folder` | アセットのサーバーに接続できない | [アセットを読み込めない](#asset-loading) |
| `PermissionError: [Errno 13] Permission denied` | 出力先に書き込めない | [サンプルの出力ファイルを保存できない](#output-permission) |

上のどれでもなく、`AttributeError` や `ImportError` が出る場合は、Isaac Sim のバージョンが違う可能性があります (検証環境では再現していません)。このチュートリアルのサンプルは Isaac Sim 6.1.0 の API (`isaacsim.core.experimental`) を使っているので、ほかのバージョンでは動かないことがあります。`docker/.env` の `ISAAC_SIM_IMAGE` を確認してください。

#### `No module named 'isaacsim'` {#no-module-isaacsim}

サンプルをホストの Python (`python3` や `uv run python`) で実行すると、次のエラーになります。

```text
ModuleNotFoundError: No module named 'isaacsim'
```

`isaacsim` パッケージはコンテナの中にしかないためです。4 章の [スクリプトをコンテナで実行する](../04-python-standalone.md#run-in-container) のとおり、コンテナの `/isaac-sim/python.sh` で実行してください。なお、コンテナの中にも `python3` コマンドはありません (`--entrypoint python3` を指定すると `executable file not found in $PATH` になります)。

#### `No module named 'pxr'` {#no-module-pxr}

3 章のサンプルのように `SimulationApp` を起動せずに USD を扱うスクリプトを、コンテナの `python.sh` でそのまま実行すると、次のエラーになります。

```text
ModuleNotFoundError: No module named 'pxr'
```

Isaac Sim の USD ライブラリ (`pxr`) は拡張機能 `omni.usd.libs` に含まれていて、そのままでは `python.sh` から import できないためです。3 章の [USD の基礎](../03-usd-basics.md) の手順のとおり、実行前に `PYTHONPATH` と `LD_LIBRARY_PATH` を設定してください。

```bash
export PYTHONPATH=$(ls -d /isaac-sim/extscache/omni.usd.libs-*)
export LD_LIBRARY_PATH=$PYTHONPATH/bin
```

4 章以降のように `SimulationApp` を起動するスクリプトでは、この設定は要りません。

## 参考リンク {#references}

- [Troubleshooting (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/overview/troubleshooting.html)
- [Known Issues (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/overview/known_issues.html)
- [Setup Tips (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_faq.html)
- [Container Installation (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_container.html)
- [Isaac Sim Requirements (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html)
- [NVIDIA Developer Forums - Isaac Sim](https://forums.developer.nvidia.com/c/omniverse/simulation/69)
