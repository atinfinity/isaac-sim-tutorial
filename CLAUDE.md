# Isaac Sim 入門チュートリアル

## 方針

- **読者**: Python は書けるが、ロボティクスやシミュレータは初めての人。Linux の基本操作と Docker の基礎は前提とする
- **ゴール**: Python のスタンドアロンスクリプトでシーン構築・シミュレーション・センサ取得ができるようになること。ROS 2 と Isaac Lab は付録で紹介するだけにとどめる
- **対象バージョン**: Isaac Sim 6.1.0 に固定する。API は `isaacsim.core.experimental` 系を使い、公式の standalone_examples (タグ `v6.1.0`) を正とする
- **題材**: 全章を通して Jetbot を使う。6 章で LiDAR を後付けし、7 章では LiDAR による障害物回避を扱う
- **実行環境**: Docker (`docker/compose.yml`) を使い、画面は Web ビューア (`:8210`) で見る。WebRTC Streaming Client は代替手段として扱い、X11 は扱わない
- **検証環境**: Ubuntu 24.04 + RTX 2080 Ti (NVIDIA ドライバ 595.99.02)。公式要件 (RTX 4080 / 16GB) 未満なので、本文にその旨を明記する
- **公開**: 0〜4 章が揃ったら GitHub Pages を有効化し、リポジトリ変数 `DEPLOY_PAGES=true` を設定する

## 執筆ルール

- 日本語の です・ます調で書く
- 各章の構成
    - 冒頭: `!!! info "この章で学ぶこと"` に、学ぶこと・所要時間・前提となる章・対象バージョンを書く
    - 末尾: まとめ・演習・参考リンク (公式ドキュメント) を置く
- 注意やヒントは admonition (`!!! warning` / `!!! tip` など) で書く
- UI のメニュー名は英語のまま書く。必要に応じて和訳を添える (例: `Create > Mesh > Cube`)
- 画像は WebP で `docs/assets/<章のファイル名>/` に置く。動きを見せたいときは数秒の MP4 か GIF を使い、1 ファイル 5MB 以下に収める
- サンプルコードは `examples/<章番号>_<名前>/` に置く
- ページ内リンクの対象にする見出しには `{#英字の-id}` を付ける (日本語の見出しは自動の ID が `_1` のようになるため)
- GUI の操作手順とスクリーンショットは、実機で検証したものだけを載せる

## コマンド

- Python の依存は uv で管理する (`pyproject.toml` の dependency-groups: `docs` = zensical、`dev` = ruff, usd-core)。pip や venv は直接使わない
- 依存の同期: `uv sync`
- サイトのプレビュー: `uv run zensical serve`
- Lint: `uv run ruff check .` / `uv run ruff format --check .`
- CI はサイトのビルドと ruff のみ (GPU がないため、サンプルコードの実行確認は手動で行う)
