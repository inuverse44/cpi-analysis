# 消費者物価指数の集計・可視化サンプル

公開データを使ったデータ解析の見本です。公開データ（総務省統計局「消費者物価指数」）を使い、**計画 → データの検証 → 集計 → 図とレポート**までを、誰でも再現できる形で公開しています。

- 結果：[REPORT.md](REPORT.md)
- 分析計画書（問い・データ・手法・検証・トレーサビリティ）：[docs/analysis-plan.md](docs/analysis-plan.md)
- ホームページ：https://www.inuverse.dev

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="figures/o03-rice-index-dark.png">
  <img src="figures/o03-rice-index-light.png" alt="お米の値段（2020年平均＝100）" width="100%">
</picture>

## 構成

| 場所 | 内容 |
| --- | --- |
| `data/raw/` | 統計局から取得したままの元データと、その取得日・SHA-256 |
| `data/processed/` | 加工済みのデータ（UTF-8 の CSV） |
| `figures/` | 図（ライト用・ダーク用） |
| `src/cpi_analysis/` | 読み込み・検証・集計・図・レポートのコード |
| `tests/` | 検証（分析計画書 §6 の V-01〜V-06） |

## 再現の手順

[uv](https://docs.astral.sh/uv/) を使います。

```sh
uv sync
uv run cpi-analysis          # 検証 → 集計 → 図と表 → REPORT.md
uv run pytest                # 検証
uv run cpi-analysis fetch    # 統計局から最新のデータを取り込み直す（SOURCES.md も更新）
```

図には日本語フォント（ヒラギノ角ゴシック、Noto Sans CJK JP など）が必要です。

## 出典とライセンス

- データ：出典：「消費者物価指数」（総務省統計局）（https://www.stat.go.jp/data/cpi/1.html ）を加工して作成。統計局ホームページの利用規約（公共データ利用規約 第 1.0 版、CC BY 4.0 と互換）に従います。
- コード：MIT License
