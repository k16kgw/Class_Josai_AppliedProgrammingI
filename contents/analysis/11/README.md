# 応用プログラミングI 第11回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

消費者物価指数と完全失業率を使い，時系列データの基本的な解析方法を学ぶ．

## 第11回 分析記録

- テーマ：日本の物価の変化と雇用状況にはどのような関係があるか
- 出典：e-Stat 統計ダッシュボード
- 原典：総務省統計局「消費者物価指数」
- 比較データ：総務省統計局「労働力調査」完全失業率
- 周期：月次
- 基準年：2020年（2020年平均=100）
- 元データ：data/raw/dashboard_cpi.json
- 比較用元データ：data/raw/dashboard_unemployment.json
- 前処理済みデータ：data/processed/cpi_monthly.csv
- 比較用データ：data/processed/cpi_unemployment_monthly.csv
- 観察用ノートブック：notebooks/time_series.ipynb（Gitでは管理しない）
- 作成するスクリプト：
  - src/plot_cpi_recent.py
  - src/plot_cpi_yoy.py
- 出力する図：
  - reports/figures/cpi_recent.png
  - reports/figures/cpi_yoy.png
