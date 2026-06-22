# 応用プログラミングI 第10回

- 氏名：香川渓一郎
- 学籍番号：2025014

## 今日の目標

都道府県間の人口移動を重み付き有向ネットワークとして可視化する．

## 第10回 分析記録

- テーマ：人はどの都道府県からどの都道府県へ移動しているのか
- 出典：総務省統計局「住民基本台帳人口移動報告 2025年結果」
- 統計表：表2 男女、移動前の住所地別都道府県間移動者数
- 元データ：data/raw/prefecture_migration_2025.xlsx
- 前処理済みデータ：data/processed/prefecture_migration_edges_2025.csv
- 観察用ノートブック：notebooks/statistics.ipynb（Gitでは管理しない）
- 作成するスクリプト：
  - src/plot_my_prefecture_migration_network.py
  - src/plot_migration_pagerank.py
- 出力する図：
  - reports/figures/top60_migration_network.png
  - reports/figures/saitama_migration_network.png
  - reports/figures/my_prefecture_migration_network.png
  - reports/figures/migration_pagerank.png