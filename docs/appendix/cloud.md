# 付録 A. クラウドで動かす

!!! info "この章で学ぶこと"
    手元に NVIDIA GPU がない場合にクラウド (Brev など) で Isaac Sim を使う

    - **所要時間**: 60 分
    - **前提**: 0 章
    - **対象バージョン**: Isaac Sim 6.1.0

!!! warning "この付録の手順は未検証です"
    このチュートリアルの検証環境は、手元の PC (RTX 2080 Ti) です。この付録の内容は、公式ドキュメント (Isaac Sim 6.1.0) と公式リポジトリの説明をもとにまとめたもので、クラウドでの手順は実際には試していません。画面の表示や手順は変わることがあるので、操作するときは必ずリンク先の公式ドキュメントを確認してください。

Isaac Sim を動かすには、RTX 対応の NVIDIA GPU が必要です (0 章)。手元にない場合は、クラウドの GPU インスタンスを借りて動かし、画面をブラウザに配信 (ストリーミング) する方法があります。公式ドキュメントの [Cloud Deployment](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_cloud.html) には、次のような選択肢が載っています。

| 方法 | 概要 |
| --- | --- |
| Isaac Launchable | NVIDIA Brev 上に、Isaac Sim・Isaac Lab・VS Code がそろった環境を作る。ブラウザだけで使える |
| NVIDIA Brev | Brev で GPU インスタンス (VM) を借り、自分で Isaac Sim のコンテナを動かす |
| AWS・Azure・GCP など | 各クラウドの GPU インスタンスで動かす。クラウドごとの手順がある |

この付録では、手軽な順に Isaac Launchable と Brev の GPU インスタンスを紹介します。どちらも **NVIDIA Brev** という NVIDIA の GPU クラウドのサービスを使います。

!!! warning "料金に注意"
    クラウドの GPU インスタンスは、時間に応じて料金がかかります。使い終わったら、インスタンスを必ず停止または削除してください。停止したインスタンスにも、ストレージの料金がかかることがあります。料金は Brev のページで確認してください。

## Isaac Launchable {#isaac-launchable}

**Isaac Launchable** は、Isaac Sim と Isaac Lab をブラウザだけで試せるようにした環境です。Brev の **Launchable** (設定済みの GPU 環境のテンプレート) として提供されていて、公式リポジトリ [isaac-sim/isaac-launchable](https://github.com/isaac-sim/isaac-launchable) がそのテンプレートになっています。

ブラウザでは、次の 2 つのタブを使います。

- VS Code (コードの編集やコマンドの実行)
- Isaac Sim の画面 (ストリーミングで表示)

### 手順の概要 {#launchable-steps}

公式ドキュメント ([Isaac Launchable Deployment](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_advanced_cloud_setup_launchable.html)) の手順は、おおまかに次のとおりです。

1. NVIDIA Brev のアカウントを用意する
2. 公式ドキュメントのリンクから Isaac Launchable のページを開き、`Deploy Launchable` でインスタンスを作る
3. インスタンスの準備 (起動・ビルド・セットアップ) が終わるまで待つ。初回は時間がかかる
4. Brev のインスタンスのページの「Using Secure Links」にある URL を開き、Brev のアカウントでログインすると VS Code が開く
5. VS Code の中の README に従って Isaac Sim を起動し、URL の末尾を `/viewer` に変えたタブで画面を見る

!!! warning "Isaac Sim のバージョンが違う"
    執筆時点の Isaac Launchable の README には、含まれる Isaac Sim のバージョンが **6.0.1** と書かれています。このチュートリアルが対象とする 6.1.0 とは異なるため、4 章以降のサンプルコードがそのまま動くとは限りません。まずは Isaac Sim の GUI を触ってみる (2 章・3 章) 用途に向いています。

Isaac Launchable は学習用で、本番の用途には向かないとされています。

## Brev の GPU インスタンス {#brev}

Brev で GPU インスタンス (VM) を借りて、このチュートリアルと同じ Docker の構成 (1 章) を動かす方法です。Isaac Sim 6.1.0 を使えるので、本文のサンプルコードを動かすならこちらです。

### 手順の概要 {#brev-steps}

公式ドキュメント ([NVIDIA Brev Deployment](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_advanced_cloud_setup_brev.html)) の手順は、おおまかに次のとおりです。

1. [NVIDIA Brev](https://developer.nvidia.com/brev) にサインインする
2. `Create New Instance` で、GPU に `1x NVIDIA L40S` を選んでインスタンスを作る
3. VM の準備ができたら、ポート **49100・47998・8210** を、**自分の IP アドレスからだけ** 接続できるように公開する
4. インスタンスのページの `Open Notebook` から Jupyter Notebook を開き、その中のターミナルを使う

ターミナルが使えるようになったら、あとは 1 章とほぼ同じです。違いは、Web ビューアに **インスタンスの公開 IP アドレス** を設定するところです。

### このチュートリアルの構成で起動する {#brev-compose}

インスタンスのターミナルで、このリポジトリを clone し、1 章と同じようにキャッシュ用のディレクトリを作ります。

```bash
git clone https://github.com/atinfinity/isaac-sim-tutorial.git
cd isaac-sim-tutorial
mkdir -p ~/docker/isaac-sim/{cache/main,cache/computecache,cache/kit,config,data,logs,pkg}
mkdir -p ~/.cache/ov/hub
sudo chown -R 1234:1234 ~/docker/isaac-sim ~/.cache/ov/hub
```

Web ビューアは、ビルドするときに接続先 (`ISAACSIM_HOST`) を埋め込みます。手元の PC では `127.0.0.1` のままで動きますが、クラウドではブラウザとインスタンスが別のマシンなので、インスタンスの公開 IP アドレスを指定します。`docker/.env.example` を `docker/.env` にコピーし、`ISAACSIM_HOST` を設定します。

```bash
cp docker/.env.example docker/.env
echo "ISAACSIM_HOST=$(curl -s ifconfig.me)" >> docker/.env
docker compose -f docker/compose.yml up -d --build
```

公式ドキュメントでも、公開 IP アドレスを `curl -s ifconfig.me` で調べて `ISAACSIM_HOST` に渡しています。起動したら、手元の PC の Chromium 系ブラウザで `http://<公開 IP アドレス>:8210` を開きます。

!!! tip "うまく接続できないとき"
    [付録 B: 別の PC のブラウザから接続できない](troubleshooting.md#remote-access) も参照してください。`ISAACSIM_HOST` を変えたら、`--build` を付けて起動し直す必要があります。

## セキュリティ上の注意 {#security}

公式ドキュメントには、次の警告があります。

- Isaac Sim のライブストリーミングは、プライベートなネットワークや信頼できるネットワークで使うことを前提にしている
- ストリーミングの接続口 (ポート 49100・47998) と Web ビューア (8210) には、**認証も暗号化もない**

つまり、ポートをインターネット全体に公開すると、URL を知っている誰でも Isaac Sim の画面を見たり操作したりできてしまいます。クラウドで使うときは、次の点を守ってください。

- **ポートは自分の IP アドレスからだけ** 接続できるように制限する (Brev のポート公開の設定や、クラウドのファイアウォール / セキュリティグループで設定する)
- 広く公開する必要があるときは、HTTPS/TLS と認証を備えたリバースプロキシを前に置く (公式ドキュメントの推奨)
- 使い終わったらインスタンスを停止または削除する。動かしたままにしない
- 秘密の情報 (API キーやパスワードなど) をインスタンスに置きっぱなしにしない

Isaac Launchable は、Brev の Secure Links (Brev のアカウントでのログインが必要な URL) 経由で接続するため、ポートを自分で公開する必要はありません。

## まとめ {#summary}

- 手元に RTX 対応の GPU がなくても、クラウドの GPU インスタンスで Isaac Sim を動かし、画面をブラウザに配信して使える
- **Isaac Launchable** は、Brev 上に Isaac Sim・Isaac Lab・VS Code の環境をまとめて作る。手軽だが、Isaac Sim のバージョンが 6.0.1 で、このチュートリアルの 6.1.0 とは異なる
- **Brev の GPU インスタンス** では、1 章と同じ Docker の構成を動かせる。Web ビューアの `ISAACSIM_HOST` にインスタンスの公開 IP アドレスを設定する
- ストリーミングには認証も暗号化もない。ポートは自分の IP アドレスからだけ接続できるように制限し、使い終わったらインスタンスを止める

## 演習 {#exercises}

1. 公式ドキュメントの [Cloud Deployment](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_cloud.html) を開き、自分がふだん使っているクラウドの手順があるかを確かめてください。
2. 自分の PC の公開 IP アドレスを調べ、クラウドのファイアウォールで「その IP アドレスからだけ、ポート 8210・49100・47998 に接続できる」ようにするには、どのような設定が必要かを考えてください。
3. (クラウドを使う場合) Brev の GPU インスタンスで 4 章のサンプルを実行し、手元の環境と同じ結果になるかを確かめてください。使い終わったら、インスタンスの停止を忘れないでください。

## 参考リンク {#references}

- [Cloud Deployment (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_cloud.html)
- [Isaac Launchable Deployment (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_advanced_cloud_setup_launchable.html)
- [NVIDIA Brev Deployment (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_advanced_cloud_setup_brev.html)
- [Container Deployment (Isaac Sim ドキュメント)](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_container.html)
- [isaac-sim/isaac-launchable (GitHub)](https://github.com/isaac-sim/isaac-launchable)
- [NVIDIA Brev](https://developer.nvidia.com/brev) / [Brev のドキュメント](https://docs.nvidia.com/brev/latest/)
- [Isaac Automator (GitHub)](https://github.com/isaac-sim/IsaacAutomator): AWS・Azure・GCP・Alibaba Cloud への配置を自動化するツール
