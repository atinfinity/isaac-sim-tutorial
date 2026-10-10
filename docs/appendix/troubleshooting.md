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

### コンテナが起動しない {#container-not-starting}

TODO: 症状・原因・対処

- NVIDIA Container Toolkit が入っていない、または Docker に設定されていない (`runtime: nvidia` が使えない)
- NVIDIA ドライバのバージョンが古い
- イメージの取得 (`docker pull`) に失敗している

### キャッシュ用ディレクトリの権限エラー {#permission-denied}

TODO: 実際のエラーメッセージ

コンテナ内の Isaac Sim は uid 1234 のユーザーで動きます。ホスト側のキャッシュ用ディレクトリが uid 1234 の所有になっていないと、書き込みに失敗します。1 章の手順どおりに作成し直してください。

```bash
sudo chown -R 1234:1234 ~/docker/isaac-sim ~/.cache/ov/hub
```

### サンプルの出力ファイルを保存できない {#output-permission}

TODO: 実際のエラーメッセージ

6 章・7 章のサンプルは、ホストのディレクトリをマウントして画像を保存します。保存先も uid 1234 が書き込める必要があります。

### 互換性チェックで警告が出る {#compatibility-check}

TODO: 検証環境 (RTX 2080 Ti) での出力と、無視してよい警告の説明

## Web ビューア {#web-viewer}

### Web ビューアに何も映らない {#blank-viewer}

TODO: 症状・原因・対処

- Isaac Sim の起動が終わっていない (`docker compose ps` で healthy になるまで待つ)
- Chromium 系以外のブラウザを使っている
- 別の PC から接続しているのに `ISAACSIM_HOST` を設定していない

### 別の PC のブラウザから接続できない {#remote-access}

TODO: 手順の確認

Web ビューアは、ビルド時に `ISAACSIM_HOST` の値を埋め込みます。`docker/.env` でホストの LAN 側 IP アドレスを設定したら、`--build` を付けて起動し直してください。

```bash
docker compose -f docker/compose.yml up -d --build
```

ファイアウォールでポート (8210、49100、47998) が塞がれていないかも確認してください。

### 画面がカクつく・遅延が大きい {#laggy-viewer}

TODO

## 実行時 {#runtime}

### 起動が遅い {#slow-startup}

TODO: 検証環境での初回と 2 回目の起動時間

初回の起動では、シェーダーのコンパイルとアセットのダウンロードが行われるため時間がかかります。キャッシュ用ディレクトリをマウントしていれば、2 回目以降は速くなります。

### アセットの読み込みが終わらない {#asset-loading}

TODO

### GPU のメモリが足りない {#out-of-memory}

TODO: 検証環境での VRAM 使用量と、メモリ不足時のエラーメッセージ

### サンプルコードでエラーが出る {#example-errors}

TODO: よくある原因 (Isaac Sim のバージョン違い、`python.sh` 以外の Python で実行している など)

## 参考リンク {#references}

- [Troubleshooting (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/overview/troubleshooting.html)
- [Known Issues (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/overview/known_issues.html)
- [Setup Tips (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_faq.html)
- [Container Installation (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_container.html)
- [Isaac Sim Requirements (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html)
- [NVIDIA Developer Forums - Isaac Sim](https://forums.developer.nvidia.com/c/omniverse/simulation/69)
