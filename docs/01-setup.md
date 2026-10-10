# 1. 環境構築

!!! info "この章で学ぶこと"
    Docker で Isaac Sim 6.1.0 を起動し、ブラウザから画面を表示する

    - **所要時間**: 60 分 (ダウンロード時間を除く)
    - **前提**: 0 章
    - **対象バージョン**: Isaac Sim 6.1.0

!!! warning "執筆中"
    この章はまだ執筆中です。

## ホストの要件

Isaac Sim 6.1.0 の公式の要件 ([Isaac Sim Requirements](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html)) のうち、最小構成と、このチュートリアルの検証環境を並べると次のようになります。

| 項目 | 公式の最小要件 | 検証環境 |
| --- | --- | --- |
| OS | Ubuntu 22.04 / 24.04 | Ubuntu 24.04.3 LTS |
| CPU | Intel Core i7 (第 7 世代) / AMD Ryzen 5 以上、4 コア | Intel Core i7-9800X (8 コア / 16 スレッド) |
| メモリ | 32GB | 32GB |
| ストレージ | 50GB (SSD) | 50GB 以上の空き |
| GPU | GeForce RTX 4080 | GeForce RTX 2080 Ti |
| VRAM | 16GB | 11GB |

Isaac Sim のコンテナは Linux でのみサポートされています。このチュートリアルでも Linux (Ubuntu) を前提にします。

!!! warning "検証環境の GPU は公式の最小要件を下回っています"
    検証環境の RTX 2080 Ti (VRAM 11GB) は、公式の最小要件 (RTX 4080 / VRAM 16GB) を満たしていません。このチュートリアルの範囲 (Jetbot 1 台程度のシーン) では動作を確認していますが、より重いシーンでは動かない可能性があります。

あとで実行する互換性チェック (`isaac-sim.compatibility_check.sh`) は、公式の要件とは別の基準で判定します。検証環境では次のように表示され、全体の判定は `PASSED` でした。

| 項目 | 判定 | 互換性チェックの最低要件 |
| --- | --- | --- |
| NVIDIA ドライバ | `supported` | 535.161 |
| GPU 0: VRAM | `enough (more is recommended)` | 10GB |
| CPU のコア数 | `excellent` | 4 |
| RAM | `enough (more is recommended)` | 32GB |
| ストレージ | `excellent` | 50GB |

`enough (more is recommended)` は「最低要件は満たすが、推奨には届かない」という意味です。

## NVIDIA ドライバ

ホストに NVIDIA ドライバが入っているかを `nvidia-smi` で確認します。

```bash
nvidia-smi
```

GPU の名前と `Driver Version` が表示されれば、ドライバは入っています。バージョンの目安は次のとおりです。

| 基準 | Linux のドライバのバージョン |
| --- | --- |
| 公式の検証済みバージョン ([Isaac Sim Requirements](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html)) | 595.58.03 |
| 互換性チェックの最低要件 | 535.161 |
| このチュートリアルの検証環境 | 595.99.02 |

ドライバが入っていない場合や、バージョンが古い場合は、Ubuntu のパッケージや NVIDIA の公式サイトのインストーラで更新してください。

!!! warning "ドライバを更新したら PC を再起動する"
    ドライバを更新したあと再起動しないと、ドライバのライブラリと動いているカーネルモジュールのバージョンが食い違います。この状態では `nvidia-smi` が `Driver/library version mismatch` で失敗し、Isaac Sim のコンテナも起動しません。詳しくは [付録 B の「`driver/library version mismatch` でコンテナが起動しない」](appendix/troubleshooting.md#driver-mismatch) を参照してください。

## Docker と NVIDIA Container Toolkit

TODO

## リポジトリの取得とキャッシュ用ディレクトリ

TODO

## Isaac Sim の起動

TODO

## Web ビューアで接続する

TODO

## 停止と再起動

TODO

## まとめ

TODO

## 演習

TODO

## 参考リンク

- TODO
