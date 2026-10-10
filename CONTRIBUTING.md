# コントリビューションガイド

このチュートリアルへの協力を歓迎します。誤字の指摘から、動かなかった手順の報告、内容の改善提案まで、どんなものでも助かります。

## Issue で報告する

[Issue](https://github.com/atinfinity/isaac-sim-tutorial/issues/new/choose) から、目的に合ったテンプレートを選んでください。

- **誤り・動かない手順の報告**: 本文の誤り、サンプルコードのエラー、手順どおりに進めても動かない箇所など
- **改善の提案**: わかりにくい説明、追加してほしい内容など

動かない手順を報告するときは、GPU・NVIDIA ドライバのバージョン・実行したコマンド・エラーメッセージを書いてもらえると、原因を調べやすくなります。

> [!NOTE]
> Isaac Sim 自体の不具合や、このチュートリアルの範囲外の質問は、[NVIDIA Developer Forums の Isaac Sim カテゴリ](https://forums.developer.nvidia.com/c/omniverse/simulation/69) のほうが早く解決することがあります。

## Pull Request を送る

1. リポジトリをフォークし、ブランチを作成します
2. 変更を加え、後述のチェックを通します
3. Pull Request を作成します。サンプルコードや GUI の手順を変更した場合は、どの環境 (GPU・ドライバ・Isaac Sim のバージョン) で動作を確認したかを書いてください

小さな誤字の修正であれば、各ページ右上の編集ボタンから直接 Pull Request を作ることもできます。

### ローカルでの確認

Python の依存は [uv](https://docs.astral.sh/uv/) で管理しています。

```bash
uv sync
uv run zensical serve          # サイトのプレビュー (http://localhost:8000)
uv run ruff check .            # Lint
uv run ruff format --check .   # フォーマットの確認
```

CI ではサイトのビルドと ruff のみを実行します。GPU がないため、サンプルコードの動作は CI では確認できません。手元の環境で実行して確認してください。

## 執筆ルール

本文を書くときは次のルールに従ってください。

- **バージョン**: Isaac Sim 6.1.0 を対象とします。API は `isaacsim.core.experimental` 系を使い、公式の standalone_examples (タグ `v6.1.0`) を正とします
- **文体**: 日本語の です・ます調で書きます
- **章の構成**
    - 冒頭に `!!! info "この章で学ぶこと"` を置き、学ぶこと・所要時間・前提となる章・対象バージョンを書きます
    - 末尾に まとめ・演習・参考リンク (公式ドキュメント) を置きます
- **注意やヒント**: admonition (`!!! warning` / `!!! tip` など) で書きます
- **UI のメニュー名**: 英語のまま書き、必要に応じて和訳を添えます (例: `Create > Mesh > Cube`)
- **画像**: WebP で `docs/assets/<章のファイル名>/` に置きます。動きを見せたいときは数秒の MP4 か GIF を使い、1 ファイル 5MB 以下に収めます
- **サンプルコード**: `examples/<章番号>_<名前>/` に置きます
- **検証**: GUI の操作手順とスクリーンショットは、実機で確認したものだけを載せます

## ライセンス

コントリビューションは、本文 (`docs/`) は [CC BY 4.0](LICENSE-docs)、コード (`examples/`, `docker/` など) は [Apache License 2.0](LICENSE) のもとで公開されることに同意したものとみなします。
