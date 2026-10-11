# Isaac Sim 入門チュートリアル

Docker 上で [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac/sim) を動かし、Python からロボットのシミュレーションができるようになるまでを解説する、初学者向けのチュートリアルです。

!!! warning "執筆中"
    このチュートリアルは現在執筆中です。下の [目次](#contents) で「執筆中」となっている章は、内容が未完成か、検証環境での動作確認が済んでいません。

## 対象読者 {#audience}

- Python でプログラムを書ける
- Linux の基本的なコマンド操作と Docker の基礎を知っている
- ロボティクスやロボットシミュレータは初めて

## ゴール {#goal}

Python のスタンドアロンスクリプトでシーンを構築し、移動ロボット (Jetbot) を動かして、カメラや LiDAR のデータを取得できるようになることです。最後のミニプロジェクトでは、LiDAR で障害物を避けながらゴールへ向かうロボットを作ります。

ROS 2 との連携や Isaac Lab による強化学習は扱いません。これらは [付録 C](appendix/next-steps.md) で入り口を紹介します。

## 対象環境 {#environment}

- Isaac Sim 6.1.0 (`nvcr.io/nvidia/isaac-sim:6.1.0`)
- Ubuntu + NVIDIA RTX GPU + Docker
- 画面はブラウザ (Web ビューア) で表示します
- GPU がない場合は [付録 A. クラウドで動かす](appendix/cloud.md) を参照してください

!!! note "検証環境について"
    本チュートリアルは Ubuntu 24.04 + RTX 2080 Ti で動作を確認しています。これは Isaac Sim 6.1.0 の推奨要件 (RTX 4080 / VRAM 16GB) を下回る構成です。推奨要件を満たす環境であれば、より快適に動作するはずです。

## 目次 {#contents}

| 章 | 内容 | 状態 |
| --- | --- | --- |
| [0. はじめに](00-introduction.md) | 対象読者・ゴール・全体の流れと Isaac Sim の概要 | 完成 |
| [1. 環境構築](01-setup.md) | Docker で Isaac Sim を起動し、ブラウザで画面を表示する | 完成 |
| [2. GUI の基本](02-gui-basics.md) | 画面構成を理解し、物体を置いて物理シミュレーションを動かす | 完成 |
| [3. USD の基礎](03-usd-basics.md) | シーンを表すデータ形式 USD の基本概念 | 完成 |
| [4. Python スタンドアロン入門](04-python-standalone.md) | Python スクリプトからシーンを作り、シミュレーションを動かす | 完成 |
| [5. ロボットを動かす](05-robot-control.md) | Jetbot を読み込み、差動二輪の制御で走らせる | 完成 |
| [6. センサ](06-sensors.md) | Jetbot にカメラと LiDAR を取り付け、データを取得・保存する | 完成 |
| [7. ミニプロジェクト](07-mini-project.md) | LiDAR で障害物を避けながらゴールへ向かう | 完成 |

付録

| 付録 | 状態 |
| --- | --- |
| [A. クラウドで動かす](appendix/cloud.md) | 完成 |
| [B. トラブルシューティング](appendix/troubleshooting.md) | 完成 |
| [C. 次の一歩](appendix/next-steps.md) | 完成 |

## 進め方 {#how-to-proceed}

0 章から順に読み進めることを想定しています。サンプルコードは [GitHub リポジトリ](https://github.com/atinfinity/isaac-sim-tutorial) の `examples/` にあり、1 章でリポジトリを取得したあと、各章でコンテナ内から実行します。

うまく動かないときは、まず [付録 B. トラブルシューティング](appendix/troubleshooting.md) を確認してください。

## フィードバック {#feedback}

誤りの報告や改善の提案は [GitHub の Issue](https://github.com/atinfinity/isaac-sim-tutorial/issues) へお願いします。Pull Request も歓迎します。詳しくは [CONTRIBUTING.md](https://github.com/atinfinity/isaac-sim-tutorial/blob/main/CONTRIBUTING.md) を参照してください。

## ライセンス {#license}

本文は [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)、サンプルコードは [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) で公開しています。
