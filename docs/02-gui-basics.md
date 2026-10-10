# 2. GUI の基本

!!! info "この章で学ぶこと"
    画面構成を理解し、物体を置いて物理シミュレーションを動かす

    - **所要時間**: 45 分
    - **前提**: 1 章
    - **対象バージョン**: Isaac Sim 6.1.0

この章では、Web ビューアから Isaac Sim の GUI を操作して、次のことを順番に試します。

1. 画面の各部の役割と、ビューポートの視点の動かし方を知る
2. 地面と立方体を置き、立方体に物理を設定して落下させる
3. Jetbot を置き、ホイールを回して走らせる
4. 作ったシーンをファイルに保存する

4 章以降は Python で同じことをしますが、GUI で一度触っておくと、コードが何をしているのかをイメージしやすくなります。

始める前に、1 章の手順で Isaac Sim を起動し、Chromium 系のブラウザで `http://localhost:8210` を開いておいてください。

!!! tip "メニューバーが見えないとき"
    Web ビューアは 1920x1080 の映像をブラウザの窓に合わせて表示します。窓の縦横比によっては上端のメニューバーが切れて見えなくなるので、その場合はブラウザを全画面表示にしてください (付録 B の [メニューバーが見えない](appendix/troubleshooting.md#menu-hidden) も参照)。

## 画面構成 {#layout}

起動直後の画面は、おおまかに次の部分からできています。

![Isaac Sim 6.1.0 の既定のレイアウト](assets/02-gui-basics/layout.webp)

| 場所 | 名前 | 役割 |
| --- | --- | --- |
| 上端 | メニューバー | `File` / `Edit` / `Create` / `Window` / `Tools` / `Utilities` / `Layouts` / `Help` のメニュー |
| 中央 | Viewport (ビューポート) | シーンを 3D で表示する。物体の選択や移動もここで行う |
| 左端 | ツールバー | 上から選択・移動・回転・拡大縮小・スナップの切り替えと、再生 (▶) のボタン |
| 右上 | Stage (ステージ) | シーンに含まれる物体を、親子関係のあるツリーで表示する。`Layer` / `Render Settings` / `Robot Inspector` のタブと切り替えられる |
| 右下 | Property (プロパティ) | Stage や Viewport で選んだ物体の位置・大きさ・物理などの設定 |
| 下段 | Console / Content | Content はアセット (USD ファイル) のブラウザ、Console はログ |

Stage のツリーに並んでいる 1 つ 1 つの項目は **Prim** と呼ばれます。Prim や Stage が何なのかは 3 章で詳しく扱うので、ここでは「シーンに置いた物体の一覧」と考えておけば十分です。

### ビューポートの操作 {#viewport-navigation}

ビューポートの視点は、マウスで次のように動かします。

| 操作 | 動き |
| --- | --- |
| ++alt++ + 左ドラッグ (macOS では ++option++ + 左ドラッグ) | 注視点のまわりを回転する |
| 中ボタンでドラッグ | 平行移動する |
| ホイール | ズームする |
| 右ドラッグ + ++w++ / ++a++ / ++s++ / ++d++ | 視点を歩くように動かす |
| 物体を選んで ++f++ | 選んだ物体が画面に収まるように視点を合わせる |

迷子になったら、Stage で物体を選んで ++f++ を押すと戻れます。

!!! tip "キー操作が効かないとき"
    Web ビューアでは、キー操作はブラウザに表示された映像にフォーカスがあるときだけ Isaac Sim に届きます。キーが効かないときは、一度ビューポートをクリックしてから押してください。

## 物体を配置する {#place-objects}

まず、新しいシーンを作り、地面と立方体を置きます。

1. `File > New` で新しいシーンを作る
2. `Create > Physics > Ground Plane` で地面を置く
3. `Create > Shape > Cube` で立方体を置く

`File > New` の時点でシーンに未保存の変更があると、`Would you like to save this stage?` (保存しますか?) と聞かれます。ここでは保存しなくてよいので `Don't Save` を選びます。

新しいシーンには、最初から `World` と、平行光源 (太陽光のような光) の `Environment/defaultLight` があります。そのため照明は自分で置かなくても大丈夫です。操作が終わると、Stage には次の Prim が並びます。

| Prim のパス | 内容 |
| --- | --- |
| `/World/GroundPlane` | 地面 |
| `/World/Cube` | 立方体 |
| `/Environment/defaultLight` | 平行光源 (最初からある) |

置いた立方体は 1 辺 1 m で、中心が原点 (0, 0, 0) にあります。そのため、地面に半分埋まった状態になります。

### 移動・回転・拡大縮小 {#gizmo}

ビューポートで立方体をクリックして選択すると、操作用の矢印 (ギズモ) が表示されます。左端のツールバーか、次のキーでギズモを切り替えます。

| キー | ギズモ | 使い方 |
| --- | --- | --- |
| ++w++ | 移動 (Move) | 矢印をドラッグすると 1 軸、色の付いた四角をドラッグすると 2 軸に沿って動く |
| ++e++ | 回転 (Rotate) | 輪をドラッグすると、その軸まわりに回る |
| ++r++ | 拡大縮小 (Scale) | 矢印をドラッグすると 1 方向に伸び縮みする |
| ++esc++ | - | 選択を解除する |

矢印の色は軸に対応していて、赤が X、緑が Y、青が Z です。Isaac Sim では **Z 軸が上** なので、青い矢印を上にドラッグすると立方体が持ち上がります (座標系については 3 章の [座標系と単位](03-usd-basics.md#coordinate-systems) で詳しく扱います)。

ギズモで立方体を地面から 1 m ほど持ち上げておきましょう。正確な値にしたいときは、Property パネルの `Transform` にある `Translate` に数値を入力します。ここでは Z を `1.0` にします。入力したら、欄の外をクリックすると確定します。

`Transform` には `Translate` (位置)・`Orient` (向き)・`Scale` (拡大率) が並んでいます。欄に単位は表示されませんが、位置の単位は m です。

## 物理を設定する (重力・コリジョン) {#physics}

この状態で左端の再生ボタン (▶) を押しても、立方体は空中に浮いたまま動きません。`Create > Shape` で作った物体は見た目だけの物体で、物理の設定を持っていないからです。再生中は ▶ ボタンが一時停止 (❚❚) と停止 (■) のボタンに変わるので、確認したら停止 (■) を押しておきます。

物体が物理シミュレーションに参加するには、主に次の 2 つの設定が必要です。

| 設定 | 役割 | ないとどうなるか |
| --- | --- | --- |
| **Rigid Body** (剛体) | 質量を持ち、重力や力を受けて動く | 動かない (空中に固定される) |
| **Collider** (コリジョン) | 形を持ち、ほかの物体とぶつかる | ほかの物体をすり抜ける |

この 2 つは別々に付けられますが、多くの場合はまとめて付けます。

1. Stage で `Cube` を選ぶ
2. Property パネルの `Add` ボタンを押し、`Physics > Rigid Body with Colliders Preset` を選ぶ
3. 再生 (▶) する

`Add` ボタンは Property パネルの左上、Prim の名前の左にあります。適用すると、Property パネルに `Physics` のセクションが増え、その中に `Rigid Body` と `Collider` などの設定が並びます。

立方体が落下し、地面で止まれば成功です。止めるときは停止 (■) を押します。停止すると、立方体は再生前の位置 (Z = 1.0) に戻ります。

!!! tip "地面に Collider は要らないのか"
    `Create > Physics > Ground Plane` で作った地面には、最初から Collider が付いています。そのため立方体は地面をすり抜けずに止まります。

### 重力の設定 {#gravity}

重力などシーン全体の物理の設定は、**Physics Scene** という Prim が持っています。Physics Scene がないシーンで最初に再生すると、`/PhysicsScene` が自動で作られます。Stage で `PhysicsScene` を選ぶと、Property パネルの `Physics > Scene` に重力の向き (`Gravity Direction`) と大きさ (`Gravity Magnitude`) が表示されます。既定では向きが (0, 0, -1)、つまり下向きで、大きさは 9.81 m/s² です。

再生する前に重力を変えたいときは、`Create > Physics > Physics Scene` で自分で作ることもできます。

## Jetbot を置く {#jetbot}

このチュートリアルで使う 2 輪の移動ロボット Jetbot を置きます。Jetbot は `Create > Robots` の一覧にはないので、アセットのブラウザから探します。

1. `File > New` で新しいシーンを作り、`Create > Physics > Ground Plane` で地面を置く
2. `Create > Robots > Asset Browser` を選ぶ。下段の **Content** タブが開き、NVIDIA が公開しているアセットの `Isaac/Robots` フォルダが表示される
3. Content タブの左のツリーで、`Isaac Sim` の下の `Robots_Multiphysics` を展開し、`NVIDIA > Jetbot` を選ぶ
4. `jetbot.usda` をビューポートにドラッグ&ドロップする

Jetbot はドロップした位置の地面の上に置かれ、Stage に `/World/jetbot` ができます。Property パネルの `Translate` には、ドロップした位置の X・Y が入ります (Z は 0)。

!!! tip "フォルダの中身が表示されないとき"
    ツリーでフォルダを選んでも、右側の一覧が前のフォルダのままになることがあります。その場合は、一覧の右下にあるボタンで表示をリスト形式に切り替えると、中身が表示されます。

アセットは初回だけインターネットからダウンロードするので、表示されるまで少し時間がかかります。

!!! note "`Robots` と `Robots_Multiphysics`"
    `Isaac/Robots/NVIDIA/Jetbot` にも `jetbot.usd` があり、同じように置けます。このチュートリアルでは、4 章以降の Python のサンプル (公式の standalone_examples に合わせたもの) と同じ `Robots_Multiphysics` の `jetbot.usda` を使います。どちらも中の構造 (車体・ホイール・関節・カメラ) は同じです。

    Content タブのパス欄に、次の URL を直接入力して開くこともできます。

    ```text
    https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.1/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/
    ```

置けたら、Stage で Jetbot のツリーを展開してみましょう。次のような Prim が並んでいます。

| Prim | 内容 |
| --- | --- |
| `chassis` | 車体 |
| `left_wheel` / `right_wheel` | 左右のホイール |
| `chassis/left_wheel_joint` / `chassis/right_wheel_joint` | 車体とホイールをつなぐ回転関節 (ジョイント) |
| `chassis/rgb_camera/jetbot_camera` | 前方を向いたカメラ (6 章で使う) |

このまま再生 (▶) すると、Jetbot は地面に着地しますが、走り出しはしません。ホイールを回す指令を何も与えていないからです。

### ホイールを回して走らせる {#drive-wheels}

ホイールの関節には、目標の回転速度に向かって回そうとする **ドライブ** が付いています。この目標速度を GUI から変えてみます。

1. Stage で `chassis/left_wheel_joint` を選ぶ
2. Property パネルを下にスクロールし、`Drive` セクションの `Angular` にある `Target Velocity` を `360` にする
3. `chassis/right_wheel_joint` も同じように `360` にする
4. 再生 (▶) する

`Target Velocity` の欄はダブルクリックすると入力できます。入力したら、欄の外をクリックすると確定します。

Jetbot が前に進めば成功です。`Target Velocity` の単位は **度/秒** (欄にマウスを重ねると `Units: degrees / seconds` と表示されます) なので、`360` はホイールが 1 秒に 1 回転する速さです。

`Target Velocity` は再生中に変えても、すぐに反映されます。再生したまま `left_wheel_joint` の値を `0` にすると、左のホイールが止まり、Jetbot は左に曲がっていきます。

5 章では、この「左右のホイールの目標速度を決める」処理を Python から行い、Jetbot を思いどおりに走らせます。

## 再生と停止 {#play-stop}

ここまで使ってきた再生と停止を整理しておきます。

| 操作 | ボタン | キー | 動き |
| --- | --- | --- | --- |
| 再生 | ▶ | ++space++ | 物理シミュレーションを進める |
| 一時停止 | ❚❚ (再生中に ▶ の位置に出る) | ++space++ | その時点で止める。もう一度押すと続きから再生する |
| 停止 | ■ (再生中・一時停止中に出る) | - | シミュレーションを止め、物体を再生前の位置に戻す |

ボタンはどれも左端のツールバーの一番下にあります。

!!! warning "停止で戻るもの・戻らないもの"
    停止 (■) すると、再生中に物体が動いた結果は破棄され、再生前の位置に戻ります。

    ただし、再生中に Property パネルで変えた値は、停止しても元に戻りません。たとえば前の節で、再生中に `Target Velocity` を `0` にした場合は、停止後も `0` のままです。元の動きに戻したいときは、値を自分で戻してください。

## シーンを保存する {#save-scene}

作ったシーンは USD ファイルとして保存できます。コンテナの中のファイルはコンテナを削除すると消えるので、ホストのディレクトリをマウントしている場所に保存します。

| コンテナ内のパス | ホストのパス |
| --- | --- |
| `/isaac-sim/.local/share/ov/data` | `~/docker/isaac-sim/data` |

1. `File > Save As...` を選ぶ。`Save File As...` のダイアログが開く
2. 左のツリーで `isaac-sim > .local > share > ov > data` を選ぶ (上のパス欄が `/isaac-sim/.local/share/ov/data/` になる)
3. 右下のファイル形式の一覧で `*.usda` を選ぶ
4. `File name` に `jetbot_scene` と入力し、`Save` を押す

ファイル形式は次の 3 つから選べます。

| 形式 | ダイアログの説明 | 内容 |
| --- | --- | --- |
| `*.usd` | Can be Binary or Ascii | バイナリとテキストのどちらにもなれる |
| `*.usda` | Human-readable text format | テキスト形式 (人が読める) |
| `*.usdc` | Binary format | バイナリ形式 |

保存したファイルは、`File > Open` で開き直せます。ホストからは `~/docker/isaac-sim/data/jetbot_scene.usda` として見えるので、テキストエディタで中身を開いてみてください。拡張子を `.usda` にするとテキスト形式で保存されるので、人が読めます。

ファイルの中では、Jetbot は本体を丸ごとコピーするのではなく、`jetbot.usda` の URL を読み込む形で書かれています。

```usda
def "jetbot" (
    prepend payload = @https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.1/Isaac/Robots_Multiphysics/NVIDIA/Jetbot/jetbot.usda@
)
```

`payload` は、3 章で扱う **Reference** の仲間で、別のファイルの内容を取り込む仕組みです (読み込みを後回しにできる点が Reference と違います)。そのあとに、ホイールの `Target Velocity` のように GUI で変えた値だけが、差分として書かれています。

!!! tip "保存したファイルの所有者"
    コンテナは UID 1234 のユーザーで動いているので、保存したファイルの所有者も UID 1234 になります。ホストで編集できないときは、付録 B の [出力ファイルを編集できない](appendix/troubleshooting.md#output-permission) を参照してください。

## まとめ {#summary}

- 画面は Viewport・Stage・Property・Content などのパネルでできている
- ビューポートは ++alt++ + 左ドラッグで回転、中ボタンドラッグで平行移動、ホイールでズームする。迷ったら ++f++
- 物体が物理シミュレーションに参加するには Rigid Body (剛体) と Collider (コリジョン) が必要
- Jetbot は Asset Browser (Content タブ) の `Robots_Multiphysics > NVIDIA > Jetbot` から置く
- ホイールの関節のドライブに目標速度を与えると Jetbot が走る
- 停止すると再生前の状態に戻る。シーンはマウントしたディレクトリに `.usda` で保存する

## 演習 {#exercises}

1. 立方体に `Rigid Body with Colliders Preset` ではなく、`Add > Physics > Rigid Body` で Rigid Body だけを付けて再生してみましょう。どうなるでしょうか。予想してから確かめてください。
2. Physics Scene の重力の大きさを `1.62` (月面の重力) にして、立方体の落ち方を比べてみましょう。
3. Jetbot の左右のホイールの `Target Velocity` を、`360` と `-360` にして再生してみましょう。Jetbot はどのように動くでしょうか。
4. Jetbot の前に立方体 (Rigid Body with Colliders Preset 付き) を置き、Jetbot で押してみましょう。

## 参考リンク {#references}

- [Isaac Sim Basic Usage Tutorial](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/introduction/quickstart_isaacsim.html) (GUI での物体の配置と物理の設定)
- [Basic Robot Tutorial](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/introduction/quickstart_isaacsim_robot.html) (ロボットの配置と関節の確認)
- [GUI](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/gui/index.html)
- [Physics](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/physics/index.html)
- [Robot Assets](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/assets/usd_assets_robots.html) (Jetbot を含むロボットのアセット一覧)
