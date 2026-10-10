# docker/

チュートリアルで使う Isaac Sim 6.1.0 の Docker 構成です。詳しい手順はチュートリアル本文の「1. 環境構築」を参照してください。

| ファイル | 内容 |
| --- | --- |
| `compose.yml` | Isaac Sim (ヘッドレス + WebRTC) と Web ビューアを起動する |
| `.env.example` | `compose.yml` の設定値の例。`.env` にコピーして使う |

## スモークテスト (執筆者向け)

検証環境で Isaac Sim 6.1.0 が動くかを確かめる手順です。リポジトリのルートで実行します。

### 0. 事前準備

```bash
mkdir -p ~/docker/isaac-sim/{cache/main,cache/computecache,cache/kit,config,data,logs,pkg}
mkdir -p ~/.cache/ov/hub
sudo chown -R 1234:1234 ~/docker/isaac-sim ~/.cache/ov/hub
docker pull nvcr.io/nvidia/isaac-sim:6.1.0
```

### 1. 互換性チェック

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint bash isaac-sim \
  -c "./isaac-sim.compatibility_check.sh --/app/quitAfter=10 --no-window"
```

### 2. ヘッドレスで Python スクリプトを実行

```bash
docker compose -f docker/compose.yml run --rm --no-deps --entrypoint /isaac-sim/python.sh isaac-sim \
  /workspace/examples/00_smoke_test/smoke_test.py
```

`[smoke_test] OK` が表示され、Jetbot の x 座標が増えていれば成功です。初回はシェーダーのコンパイルとアセットのダウンロードに時間がかかります。

### 3. Web ビューアで GUI を表示

```bash
docker compose -f docker/compose.yml up -d
docker compose -f docker/compose.yml ps   # 両方 healthy になるまで待つ
```

Chromium 系のブラウザで `http://localhost:8210` を開き、Isaac Sim の画面が表示されることを確認します。上端のメニューバーが見えない場合は、ブラウザを全画面表示にします。

続けて、Jetbot を配置して再生できるかを確認します。Jetbot は `Create > Robots` の一覧にはないため、Asset Browser から配置します。

1. `Create > Robots > Asset Browser` を開く (Content タブで `/Isaac/Robots` が開く)
2. 左のツリーで `Isaac Sim` の下の `Robots_Multiphysics` を展開し、`NVIDIA > Jetbot` の `jetbot.usda` をビューポートにドラッグ&ドロップする
3. 再生 (▶) する

停止するには次を実行します。

```bash
docker compose -f docker/compose.yml down
```

### Web ビューアの操作の注意

Isaac Sim 6.1.0 の Web ビューアで確認した挙動です。

- **画面の上端が切れる**: ブラウザのウィンドウが小さいと、上端のメニューバーが切れることがあります。ブラウザを全画面表示にしてください
- **キー入力の宛先**: キー入力はフォーカスの有無にかかわらず Isaac Sim に送られます。テキスト欄にフォーカスが当たっていないまま文字を打つと、ショートカットとして解釈されます。たとえば `E` で Rotate ツールに切り替わります
- **テキスト欄への入力**: 速く入力したキーや、連続して押した `BackSpace` は取りこぼされることがあります。`Ctrl+A` での全選択も効きませんでした。ファイルダイアログでパスを入力するより、左のツリーをたどるほうが確実です
- **ファイルダイアログのツリー**: マウスホイールではスクロールしませんでした。項目が隠れているときは、ダイアログの右下の角をドラッグして広げてください

> [!NOTE]
> **ブラウザの自動操作 (Claude in Chrome など) で操作する場合**: クリックの押下と解放の間隔が短いと、メニューバーは開いても、メニュー項目・ツリー・ボタンのクリックが Isaac Sim に届きません。押下と解放を分けて送る (同じ座標へのドラッグとして送る) と届きます。

### 記録してほしいこと

- 各ステップの成否と、失敗した場合のエラーログ
- `nvidia-smi` の出力 (ドライバのバージョン)
- 起動にかかった時間 (初回と 2 回目)
- ステップ 3 の実行中の VRAM 使用量 (`nvidia-smi`)
