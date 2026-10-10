# 付録 B. トラブルシューティング

!!! info "この章で学ぶこと"
    よくあるエラーと対処法

    - **所要時間**: -
    - **前提**: 1 章
    - **対象バージョン**: Isaac Sim 6.1.0

!!! warning "執筆中"
    この章はまだ執筆中です。症状とエラーメッセージは、検証環境で実際に確認したものから順に追加していきます。

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

TODO: 症状・原因・対処

- NVIDIA Container Toolkit が入っていない、または Docker に設定されていない (`runtime: nvidia` が使えない)
- NVIDIA ドライバのバージョンが古い
- イメージの取得 (`docker pull`) に失敗している

!!! tip
    `nvcr.io/nvidia/isaac-sim:6.1.0` の取得に NGC へのログイン (`docker login nvcr.io`) は必要ありません。

### キャッシュ用ディレクトリの権限エラー {#permission-denied}

TODO: 実際のエラーメッセージ

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

TODO: 症状・原因・対処

- Isaac Sim の起動が終わっていない (`docker compose ps` で healthy になるまで待つ)
- Chromium 系以外のブラウザを使っている
- 別の PC から接続しているのに `ISAACSIM_HOST` を設定していない

### メニューが見えない (画面の上端が切れる) {#menu-hidden}

Isaac Sim の画面は表示されるのに、上端のメニューバー (`File`・`Edit`・`Create` など) が見えないことがあります。ブラウザのウィンドウが小さく、画面の上端が切れているのが原因です。

ブラウザを全画面表示にすると、メニューが見えるようになります。

### 別の PC のブラウザから接続できない {#remote-access}

TODO: 手順の確認

Web ビューアは、ビルド時に `ISAACSIM_HOST` の値を埋め込みます。`docker/.env` でホストの LAN 側 IP アドレスを設定したら、`--build` を付けて起動し直してください。

```bash
docker compose -f docker/compose.yml up -d --build
```

ファイアウォールでポート (8210、49100、47998) が塞がれていないかも確認してください。

### 画面がカクつく・遅延が大きい {#laggy-viewer}

TODO

検証環境では、同じ LAN 内の別の PC から接続して、ビューポートの操作やシミュレーションの再生でカクつきや遅延は感じませんでした。

## 実行時 {#runtime}

### Create メニューに Jetbot がない {#jetbot-not-in-menu}

`Create > Robots` に直接並んでいるのは、Ant・Spot・Franka・Humanoid・Nova Carter・Quadcopter だけです。Jetbot は `Create > Robots > Asset Browser` から開くフォルダの `NVIDIA > Jetbot` にある `jetbot.usd` を、ビューポートにドラッグ&ドロップして配置します。

### 起動が遅い {#slow-startup}

初回の起動では、シェーダーのコンパイルとアセットのダウンロードが行われるため時間がかかります。キャッシュ用ディレクトリをマウントしていれば、2 回目以降は速くなります。

検証環境 (RTX 2080 Ti / Core i7-9800X) での所要時間は次のとおりでした。

| 処理 | 初回 | 2 回目 |
| --- | --- | --- |
| イメージの取得 (`docker pull`、21.1GB) | 約 17 分 | - |
| スモークテスト (ヘッドレスで Python スクリプトを実行) | 約 4.5 分 | 約 1 分 |
| `docker compose up` で healthy になるまで | 約 4.5 分 (Web ビューアのビルドを含む) | 約 1.5 分 |

起動直後は CPU 使用率が高い状態 (16 論理コアのうち 13 コア分ほど) がしばらく続きます。

### アセットの読み込みが終わらない {#asset-loading}

TODO

### GPU のメモリが足りない {#out-of-memory}

TODO: メモリ不足時のエラーメッセージ

検証環境 (RTX 2080 Ti / VRAM 11GB) で Web ビューアから GUI を使ったときの使用量は次のとおりでした。Jetbot 1 台程度のシーンであれば、VRAM 11GB でも十分に余裕があります。

| 状態 | VRAM | RAM (isaac-sim コンテナ) |
| --- | --- | --- |
| 起動直後 (空のシーン) | 約 0.8GB | 約 9.6GB |
| Jetbot を配置 | 約 1.9GB | 約 12.6GB |
| Jetbot を配置して再生中 | 約 2.1GB | 約 12.7GB |

### サンプルコードでエラーが出る {#example-errors}

TODO: よくある原因 (Isaac Sim のバージョン違い、`python.sh` 以外の Python で実行している など)

## 参考リンク {#references}

- [Troubleshooting (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/overview/troubleshooting.html)
- [Known Issues (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/overview/known_issues.html)
- [Setup Tips (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_faq.html)
- [Container Installation (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_container.html)
- [Isaac Sim Requirements (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html)
- [NVIDIA Developer Forums - Isaac Sim](https://forums.developer.nvidia.com/c/omniverse/simulation/69)
