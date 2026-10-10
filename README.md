# Isaac Sim 入門チュートリアル

Docker で始める NVIDIA Isaac Sim 初学者向けチュートリアル (日本語) です。

- **サイト**: https://atinfinity.github.io/isaac-sim-tutorial/ (公開準備中)
- **対象**: Isaac Sim 6.1.0 / Ubuntu + NVIDIA RTX GPU + Docker

## リポジトリ構成

| パス | 内容 |
| --- | --- |
| `docs/` | チュートリアル本文 (Markdown) |
| `docs/assets/<章>/` | 画像・動画 |
| `examples/` | 章ごとのサンプルコード |
| `docker/` | Isaac Sim と Web ビューアの Docker Compose 構成 |
| `zensical.toml` | サイト (Zensical) の設定 |

## サイトをローカルでプレビューする

[uv](https://docs.astral.sh/uv/) を使います。

```bash
uv sync
uv run zensical serve
```

## ライセンス

- 本文 (`docs/`): [CC BY 4.0](LICENSE-docs)
- コード (`examples/`, `docker/` など): [Apache License 2.0](LICENSE)

誤りの報告や改善提案は Issue へお願いします。Pull Request も歓迎します。
