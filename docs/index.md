# Isaac Sim 入門チュートリアル

Docker 上で [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac/sim) を動かし、Python からロボットのシミュレーションができるようになるまでを解説する、初学者向けのチュートリアルです。

!!! warning "執筆中"
    このチュートリアルは現在執筆中です。

## 対象読者

- Python でプログラムを書ける
- Linux の基本的なコマンド操作と Docker の基礎を知っている
- ロボティクスやロボットシミュレータは初めて

## ゴール

Python のスタンドアロンスクリプトでシーンを構築し、移動ロボット (Jetbot) を動かして、カメラや LiDAR のデータを取得できるようになることです。

## 対象環境

- Isaac Sim 6.1.0 (`nvcr.io/nvidia/isaac-sim:6.1.0`)
- Ubuntu + NVIDIA RTX GPU + Docker
- GPU がない場合は [クラウドで動かす](appendix/cloud.md) を参照

## 目次

0. [はじめに](00-introduction.md)
1. [環境構築](01-setup.md)
2. [GUI の基本](02-gui-basics.md)
3. [USD の基礎](03-usd-basics.md)
4. [Python スタンドアロン入門](04-python-standalone.md)
5. [ロボットを動かす](05-robot-control.md)
6. [センサ](06-sensors.md)
7. [ミニプロジェクト: 障害物を避けてゴールへ](07-mini-project.md)

## ライセンス

本文は [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)、サンプルコードは [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) で公開しています。
