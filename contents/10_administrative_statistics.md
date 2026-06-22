# 第10回　データ分析実践I：行政統計

### 前回の復習

第9回は天気予報データに緯度・経度・標高を結合し，複数の都道府県を地図上に可視化した．

| 処理 | 第9回に行ったこと |
| --- | --- |
| データ取得 | 気象庁APIから複数都道府県のJSONを取得した |
| 前処理 | JSONを表に変換し，地域ごとに集計した |
| 結合 | 地域名をキーにして緯度・経度・標高を結合した |
| 可視化 | 色と点の大きさで複数の値を表した |
| 保存 | `plotly`の地図をHTMLファイルとして保存した |

これまでは行や列に並んだ値の分布・値同士の関係・時間変化・場所ごとの違いを可視化してきた．

今回は次の視点を追加する．

| 何を見るか | 確認できること | 図の例 |
| --- | --- | --- |
| **対象同士の関係を見る** | どの対象が強く結び付いているか，中心はどこか | **ネットワーク図** |

### 到達目標

総務省統計局の住民基本台帳人口移動報告を使い，都道府県間の人口移動を分析する．

- 行政統計の出典，調査年，単位，行と列の意味を確認できる
- クロス集計表（ワイド形式）を，エッジリスト形式（長形式）へ変換する意味を説明できる
- 人口移動を重み付き有向ネットワークとして説明できる
- `NetworkX`を使ってネットワークを作成できる
- 流入者数，流出者数，純移動，PageRankを計算できる
- コミュニティ検出を使って，強く結び付いた都道府県のクラスターを探すことができる
- 表示する関係を適切に絞り，読み取れるネットワーク図を作成できる
- 可視化から読み取れることと，このデータだけでは分からないことを区別できる

**今回の流れ**

| 段階 | 内容 | 目的 |
| --- | --- | --- |
| 1 | 公式Excelを取得する | 行政統計の出典と表の構造を確認する |
| 2 | 配布スクリプトでエッジリスト形式のCSVを作る | ネットワークを作れる表に変換する |
| 3 | CSVの行数・列・値を確認する | 可視化前にデータの意味を理解する |
| 4 | 重み付き有向グラフを作る | 人口移動をネットワークとして表現する |
| 5 | 流入者数・流出者数・純移動を求める | 都道府県ごとの特徴を比較する |
| 6 | 全国の主要な人口移動を可視化する | ネットワーク全体の構造を眺める |
| 7 | 特定県の人口移動を可視化する | 局所的な関係を詳しく見る |
| 8 | PageRankを計算する | 移動先としての中心性を確認する |
| 9 | コミュニティを検出する | 強く結び付いた都道府県のクラスターを探す |

### 準備

今回は新しくフォルダ`10`を作成して作業する．

````{note} 演習0：作業フォルダを作成する
1. ターミナルを起動し，次のコマンドを順に実行する．

```bash
cd /Users/<ユーザ名>/applied_programming_i
mkdir 10
cd 10
mkdir -p notebooks data/raw data/processed src reports/figures
git init
```

2. 次のディレクトリ構成になっているか確認する．

```text
10/
├── notebooks/
│   └── statistics.ipynb（←今回作成するファイル）
├── data/
│   ├── raw/
│   │   └── prefecture_migration_2025.xlsx
│   └── processed/
│       └── prefecture_migration_edges_2025.csv
├── reports/
│   └── figures/
├── src/
│   └── build_prefecture_migration_edges.py
└── README.md
```

3. JupyterLabまたはVS Codeで`notebooks/statistics.ipynb`を新規作成する．

4. `README.md`を作成し，次の内容を記入する．

```markdown
# 応用プログラミングI 第10回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

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
  - reports/figures/migration_communities.png
  - reports/figures/my_prefecture_migration_network.png
  - reports/figures/migration_pagerank.png
```

5. `.gitignore`を作成し，次の内容を記入する．

```gitignore
.DS_Store
*.swp
*~
.vscode/
.ipynb_checkpoints/
*.ipynb
data/raw/
```

6. 作成したファイルをコミットする．

```bash
git add .
git commit -m "first commit"
```
````

---

## 使用する行政統計

### 住民基本台帳人口移動報告

- 行政統計：人口・世帯・産業・教育・福祉など社会の状態を把握するために国や自治体が作成しているデータ
- 総務省統計局の**住民基本台帳人口移動報告**：住民基本台帳法に基づく転入届などから国内の人口移動を集計したものである．

| 項目 | 内容 |
| --- | --- |
| 提供者 | 総務省統計局 |
| 統計名 | 住民基本台帳人口移動報告 |
| 対象年 | 2025年 |
| 公開日 | 2026年2月3日 |
| 使用表 | 表2 男女、移動前の住所地別都道府県間移動者数 |
| 単位 | 人 |
| 行 | 移動前の住所地 |
| 列 | 移動後の住所地 |
| 結果概要 | https://www.stat.go.jp/data/idou/2025np/jissu/youyaku/index.html |
| 統計表 | https://www.e-stat.go.jp/stat-search/files?layout=datalist&lid=000001476215 |

```{note} 行と列の意味
元のExcelでは，行が**移動前の住所地**，列が**移動後の住所地**である．

行が埼玉県，列が東京都の値は「埼玉県から東京都へ移動した人数」を表す．
向きを逆に解釈しないように注意すること．
```

### 人口移動をネットワークとして考える

都道府県を点，人口移動を矢印として考えると，都道府県間の人口移動をネットワークとして表現できる．

```text
埼玉県 ── 66,159人 ──▶ 東京都
東京都 ── 71,169人 ──▶ 埼玉県
```

同じ2都県間でも，方向によって移動者数は異なる．

| 人口移動データ | ネットワーク |
| --- | --- |
| 都道府県 | ノード |
| 転出元から転入先への移動 | 有向エッジ |
| 移動者数 | エッジの重み |

今回扱うネットワークには次の特徴がある．

- **有向グラフ**：移動には転出元から転入先への向きがある
- **重み付きグラフ**：移動者数をエッジの重みとして持つ
- **自己ループなし**：同じ都道府県内の移動は扱わない

---

## データを取得して前処理する

元のExcelは，行に移動前の住所地，列に移動後の住所地を並べた**クロス集計表（ワイド形式）**である．
男女別の列や大都市圏の列も含まれているため，配布スクリプトを使って必要な部分を取り出す．

### クロス集計表とエッジリスト形式

**クロス集計表**は，2つ以上のカテゴリを行と列に配置し，その組合せごとの件数や集計値をセルに記録した表である．
列方向へ項目が広がるため，データ形式としては**ワイド形式**とも呼ばれる．

今回のExcelでは，行が転出元，列が転入先，セルが移動者数である．
ネットワーク科学では，この形は**隣接行列形式**に対応する．

| 転出元＼転入先 | 埼玉県 | 東京都 | 神奈川県 |
| --- | ---: | ---: | ---: |
| 埼玉県 | - | 66159 | 16859 |
| 東京都 | 71169 | - | 87758 |
| 神奈川県 | 15791 | 88983 | - |

**長形式**は，1回の観測や1つの組合せを1行に記録する形式である．
ネットワークデータでは，1本のエッジを1行にした長形式を**エッジリスト形式**と呼ぶ．

| 転出元 | 転入先 | 移動者数 |
| --- | --- | ---: |
| 埼玉県 | 東京都 | 66159 |
| 東京都 | 埼玉県 | 71169 |
| 東京都 | 神奈川県 | 87758 |

以降は，用途に対応させて次の用語を使う．

| 表の形 | 本講義で使用する用語 | 主な用途 |
| --- | --- | --- |
| 行と列の組合せをセルに記録する | クロス集計表（ワイド形式・隣接行列形式） | 表全体を眺める，行列として扱う |
| 1本の関係を1行に記録する | エッジリスト形式（長形式） | 絞り込み，集計，ネットワーク作成 |

````{note} 演習1：公式Excelと前処理スクリプトを取得する

**1．ターミナルで必要なライブラリをインストールする**

```bash
python3 -m pip install pandas openpyxl networkx matplotlib seaborn
```

**2．e-Statから公式Excelを取得する**

`10`フォルダ内で次のコマンドを実行する．

```bash
curl -L "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040407039&fileKind=0" -o data/raw/prefecture_migration_2025.xlsx
```

取得できなかった場合は，次のファイルをダウンロードして`data/raw`に配置すること．

[prefecture_migration_2025.xlsx](./analysis/10/data/raw/prefecture_migration_2025.xlsx)

**3．前処理スクリプトを取得する**

次のリンクを右クリックし，リンクアドレスをコピーする．

[build_prefecture_migration_edges_py.zip](./analysis/10/src/build_prefecture_migration_edges_py.zip)

コピーしたURLを使って，ターミナルで次のコマンドを実行する．

```bash
curl -L "<コピーしたURL>" -o src/build_prefecture_migration_edges_py.zip
unzip -o src/build_prefecture_migration_edges_py.zip -d src
```

**4．前処理スクリプトを実行する**

```bash
python3 src/build_prefecture_migration_edges.py
```

実行後，次のように表示されることを確認する．

```text
行数: 2162
都道府県数: 47
移動者数合計: 2515731
saved: data/processed/prefecture_migration_edges_2025.csv
```

うまく作成できなかった場合は，次のファイルをダウンロード・解凍し，`data/processed`に配置して以降の演習を進めること．

[prefecture_migration_edges_2025_csv.zip](./analysis/10/data/processed/prefecture_migration_edges_2025_csv.zip)
````

### 配布スクリプトの動作

配布スクリプトは次の処理を行う．

| 処理 | 内容 |
| --- | --- |
| Excelの読み込み | 見出しを付けずに表全体を読み込む |
| 列の選択 | 47都道府県の「総数」列だけを選ぶ |
| 行の選択 | 国籍区分が「移動者」である47都道府県だけを選ぶ |
| エッジリスト形式への変換 | 1本の人口移動を，転出元，転入先，移動者数の1行にする |
| 不要行の除外 | 同じ都道府県の組合せと値のないセルを除く |
| 検査 | 転出元と転入先に47都道府県があるか確認する |
| 保存 | CSVファイルとして保存する |

変換後のCSVは，1本の人口移動を1行に記録した**エッジリスト形式（長形式）**になる．

| 年 | 転出元 | 転入先 | 移動者数 |
| --- | --- | --- | ---: |
| 2025 | 神奈川県 | 東京都 | 88983 |
| 2025 | 東京都 | 神奈川県 | 87758 |
| 2025 | 東京都 | 埼玉県 | 71169 |

```{tip} 表の形式を目的に応じて使い分ける
クロス集計表（ワイド形式）は，人が行列全体を眺める場合に便利である．

一方，エッジリスト形式（長形式）では1行が1本のエッジに対応するため，絞り込み，並べ替え，集計，ネットワーク作成を行いやすい．
```

---

## Notebookでデータを確認する

可視化を始める前に，作成されたCSVの内容を確認する．

````{note} 演習2：Notebookの準備をする
`notebooks/statistics.ipynb`に「ライブラリの準備」という見出しを作り，次のセルを順番に実行せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

`10/notebooks`が表示されることを確認する．

**セル2：Notebookで必要なライブラリをインストールする**

```bash
%pip install pandas networkx matplotlib seaborn
```

**セル3：ライブラリを読み込む**

```python
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
```
````

````{note} 演習3：人口移動データを確認する
「人口移動データを確認する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：CSVを読み込む**

```python
edge_path = "../data/processed/prefecture_migration_edges_2025.csv"

edge_df = pd.read_csv(edge_path)

edge_df.head(10)
```

**セル2：表の形と列名を確認する**

```python
print("行数・列数:", edge_df.shape)
print("列名:", edge_df.columns.tolist())
```

**セル3：欠損とデータ型を確認する**

```python
print("欠損数:")
print(edge_df.isna().sum())

print("データ型:")
print(edge_df.dtypes)
```

**セル4：都道府県数と移動者数の合計を確認する**

```python
print("転出元の都道府県数:", edge_df["転出元"].nunique())
print("転入先の都道府県数:", edge_df["転入先"].nunique())
print("移動者数合計:", edge_df["移動者数"].sum())
```

**セル5：移動者数が多い組合せを確認する**

```python
edge_df.nlargest(10, "移動者数")
```

実行後，次を確認せよ．

1. 行数が`47 × 46 = 2162`になっているか
2. `転出元`と`転入先`にそれぞれ47都道府県が含まれているか
3. `移動者数`は数値になっているか
4. 同じ2都県でも方向によって移動者数が異なるか
5. 移動者数が大きい組合せは大都市圏に集中しているか
````

---

## ネットワーク科学的な解析手法

**ネットワーク科学**は，対象そのものの特徴だけでなく，対象同士の**関係の構造**を分析する分野である．

例えば，都道府県ごとの人口だけを並べた表では，各都道府県の大きさを比較できる．
一方，都道府県間の人口移動ネットワークを作ると，どの地域同士が強く結び付いているかを調べることができる．

人口移動データでは，次のような問いを考えることができる．

- どの都道府県間の**結び付き**が強いか
- 移動が集中する**中心的な都道府県**はどこか
- 双方向に強い移動がある組合せはどこか
- 首都圏や近畿圏のような**まとまり**は見られるか
- 特定の都道府県はどの地域と強く結び付いているか

### ネットワークの構成要素

ネットワークは，ノードの集合$V$とエッジの集合$E$を使って次のように表す．

$$
G=(V,E)
$$

| 用語 | 意味 | 今回の人口移動ネットワーク |
| --- | --- | --- |
| ノード | 分析対象となる点 | 都道府県 |
| エッジ | ノード間の関係 | 都道府県間の人口移動 |
| 向き | 関係が進む方向 | 転出元から転入先 |
| 重み | 関係の強さを表す値 | 移動者数 |
| 自己ループ | 同じノードに戻るエッジ | 今回は扱わない |

### ネットワークの種類

ネットワークは，エッジの向きと重みの有無によって分類できる．

| 種類 | 説明 | 例 |
| --- | --- | --- |
| 無向ネットワーク | エッジに向きがない | 友人関係，共著関係 |
| 有向ネットワーク | エッジに向きがある | 人口移動，Webページのリンク |
| 重みなしネットワーク | 関係の有無だけを表す | 道路が接続しているか |
| 重み付きネットワーク | 関係の強さも表す | 移動者数，取引金額 |

今回扱うのは，**重み付き有向ネットワーク**である．

### ネットワークの表現方法

ネットワークをデータとして保存する代表的な方法には，隣接行列形式とエッジリスト形式がある．

| 表現方法 | 1行・1セルが表すもの | 今回のデータ |
| --- | --- | --- |
| 隣接行列形式 | 2つのノードの組合せ | 元Excelのクロス集計表（ワイド形式） |
| エッジリスト形式 | 1本のエッジ | 前処理後のCSV（長形式） |

重み付き隣接行列$W$の要素$w_{ij}$は，ノード$i$からノード$j$へのエッジの重みを表す．
今回のデータでは，都道府県$i$から都道府県$j$へ移動した人数である．

NetworkXでは，前処理後のエッジリスト形式を使ってグラフを作成する．

### ネットワークを分析する単位

ネットワーク分析では，全体，ノード，エッジ，部分構造という異なる単位を調べる．

| 分析単位 | 主な問い | 代表的な方法 |
| --- | --- | --- |
| ネットワーク全体 | 全体はどの程度つながっているか | ノード数，エッジ数，密度 |
| ノード | どのノードが中心的か | 次数，重み付き次数，PageRank |
| エッジ | どの関係が強いか | 重み，方向，双方向の差 |
| 局所ネットワーク | 特定ノードの周囲はどうなっているか | ego network |
| グループ構造 | 強く結び付いたまとまりはあるか | コミュニティ検出 |

### クラスターとコミュニティ

ネットワークの中で，内部では強く結び付き，外部との結び付きが相対的に弱いノードの集まりを**コミュニティ**と呼ぶ．
一般的なデータ分析の言葉では，このようなまとまりを**クラスター**と呼ぶこともある．

本講義では，ネットワーク上で検出されるクラスターを**コミュニティ（クラスター）**と表記する．

```{tip} クラスタリング係数とは異なる
ネットワーク科学には，あるノードの隣接ノード同士がどの程度つながっているかを表す**クラスタリング係数**という別の指標もある．

今回探すコミュニティ（クラスター）は，複数のノードをグループに分けるものであり，クラスタリング係数とは異なる．
```

### 今回使用する解析手法

| 分析する範囲 | 解析手法 | 確認すること |
| --- | --- | --- |
| ネットワーク全体 | ノード数，エッジ数，密度 | 全体がどの程度つながっているか |
| 都道府県 | 重み付き入次数・出次数 | 流入者数と流出者数 |
| 都道府県 | 純移動 | 流入と流出の差 |
| 都道府県 | PageRank | 移動先としての中心性 |
| 都道府県間 | エッジの重み | どの人口移動が強いか |
| 特定県の周辺 | ego network | どの地域と直接強く結び付くか |
| 都道府県のまとまり | コミュニティ検出 | 強く結び付いたクラスター |

概念は，この後の演習で実際に値を計算しながら確認する．

---

## 重み付き有向グラフを作成する

### ノード・エッジ・重み

- $V$：ノードの集合
- $E$：エッジの集合
- $G=(V,E)$：ネットワーク

今回のデータでは
- ノード：都道府県
- エッジ：人口移動
  - 転出元から転入先への向き
  - 移動者数の重み

### ネットワーク密度

自己ループを持たない有向グラフでは，最大で$N(N-1)$本のエッジを持つことができる．

```{tip} 定義：ネットワーク密度
ネットワーク密度$d$は次で定義される．

$$
d=\frac{M}{N(N-1)}
$$

ここに，$N$はノード数，$M$はエッジ数である．
```

今回のデータでは，すべての異なる都道府県間に人口移動があるため，密度は1となる．

### 実装

`NetworkX`では，有向グラフを`DiGraph`で表す．

````{note} 演習4：NetworkXの有向グラフを作成する
「重み付き有向グラフを作る」という見出しを作り，次のセルを順番に実行せよ．

**セル1：CSVからグラフを作る**

```python
G = nx.from_pandas_edgelist(
    edge_df,
    source="転出元",
    target="転入先",
    edge_attr="移動者数",
    create_using=nx.DiGraph,
)
```

**セル2：ノード数とエッジ数を確認する**

```python
print("ノード数:", G.number_of_nodes())
print("エッジ数:", G.number_of_edges())
```

**セル3：埼玉県から東京都へのエッジを確認する**

```python
G["埼玉県"]["東京都"]
```

**セル4：ネットワーク密度を確認する**

```python
print("密度:", nx.density(G))
```

実行後，次を確認せよ．

1. ノード数は47か
2. エッジ数は2162か
3. 埼玉県から東京都への移動者数は66159人か
4. 密度は1になっているか
````

---

## 流入者数・流出者数・純移動

有向グラフでは，ノードに入るエッジと，ノードから出るエッジを区別する．

| 指標 | 一般的な意味 | 人口移動での意味 |
| --- | --- | --- |
| 入次数 | 入るエッジの本数 | 何都道府県から転入があるか |
| 出次数 | 出るエッジの本数 | 何都道府県へ転出があるか |
| 重み付き入次数 | 入るエッジの重みの合計 | 流入者数 |
| 重み付き出次数 | 出るエッジの重みの合計 | 流出者数 |

ノード$i$の流入者数$s_i^{in}$と流出者数$s_i^{out}$は次で求める．

$$
s_i^{in}=\sum_j w_{ji},
\qquad
s_i^{out}=\sum_j w_{ij}
$$

都道府県間の純移動は次で求める．

$$
\text{都道府県間純移動}_i=s_i^{in}-s_i^{out}
$$

````{note} 演習5：都道府県ごとの流入・流出を集計する
「流入者数・流出者数・純移動」という見出しを作り，次のセルを順番に実行せよ．

**セル1：流入者数と流出者数を求める**

```python
inflow_totals = dict(G.in_degree(weight="移動者数"))
outflow_totals = dict(G.out_degree(weight="移動者数"))

node_df = pd.DataFrame({
    "都道府県": list(G.nodes())
})

node_df["流入者数"] = node_df["都道府県"].map(inflow_totals)
node_df["流出者数"] = node_df["都道府県"].map(outflow_totals)
node_df["都道府県間純移動"] = node_df["流入者数"] - node_df["流出者数"]

node_df.head()
```

**セル2：純移動の上位と下位を確認する**

```python
print("純移動が多い都道府県")
display(node_df.nlargest(10, "都道府県間純移動"))

print("純移動が少ない都道府県")
display(node_df.nsmallest(10, "都道府県間純移動"))
```

**セル3：流入者数と流出者数を散布図で比較する**

```python
fig, ax = plt.subplots(figsize=(7, 6))

sns.scatterplot(
    data=node_df,
    x="流出者数",
    y="流入者数",
    size="流入者数",
    sizes=(30, 300),
    ax=ax,
)

limit = max(node_df["流入者数"].max(), node_df["流出者数"].max())
ax.plot([0, limit], [0, limit], linestyle="--", color="gray")

for _, row in node_df.nlargest(8, "流入者数").iterrows():
    ax.text(
        row["流出者数"],
        row["流入者数"],
        row["都道府県"],
        fontsize=8,
    )

ax.set_title("都道府県間人口移動の流入者数と流出者数（2025年）")
ax.set_xlabel("流出者数（人）")
ax.set_ylabel("流入者数（人）")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 破線より上にある都道府県は何を意味するか
2. 純移動が多い都道府県はどこか
3. 流入者数と流出者数の両方が大きい都道府県はどこか
````

```{tip} 注意：純移動の解釈
ここで求めた値は，国内の**都道府県間移動のみ**から計算した純移動である．
国外との移動，同じ都道府県内の移動，出生，死亡は含まれず，都道府県の人口増減そのものと同じではないことに注意する．
```

---

## 全国の主要な人口移動を可視化する

### ネットワーク図で表す情報

ネットワーク図では，データを次の視覚要素に対応させる．

| データ | 視覚要素 |
| --- | --- |
| 都道府県 | ノード |
| 人口移動の方向 | 矢印 |
| 移動者数 | エッジの太さ |
| 流入者数 | ノードの色 |
| 都道府県間の関係 | ノードの配置 |

```{tip} 注意：目的に応じたデータの選択
2162本のエッジをすべてプロットすると線が重なって読めないため，移動者数が多い上位60本のみに絞って表示することで見やすい図にすることができる．
一方，上位60本のエッジに絞ったグラフで各種指標を計算すると，元のネットワークとは異なる結果になる．
従って，目的に応じて次のようにデータを使い分ける．

- 指標の計算：2162本の全エッジを持つネットワーク`G`を使う
- 全国図の表示：移動者数上位60本から作ったネットワーク`top_G`を使う
```

````{note} 演習6：移動者数上位60組のネットワークを描く
「全国の主要な人口移動」という見出しを作り，次のセルを順番に実行せよ．

**セル1：移動者数上位60組を取り出す**

```python
top_edges_df = edge_df.nlargest(60, "移動者数")

top_edges_df.head()
```

**セル2：表示用のグラフを作る**

```python
top_G = nx.from_pandas_edgelist(
    top_edges_df,
    source="転出元",
    target="転入先",
    edge_attr="移動者数",
    create_using=nx.DiGraph,
)

print("表示するノード数:", top_G.number_of_nodes())
print("表示するエッジ数:", top_G.number_of_edges())
```

**セル3：ノードの位置と表示サイズを準備する**

```python
pos = nx.spring_layout(
    top_G,
    weight="移動者数",
    seed=42,
    k=1.2,
)

edge_weights = [
    top_G[source][target]["移動者数"]
    for source, target in top_G.edges()
]

max_weight = max(edge_weights)

edge_widths = [
    0.5 + 4 * weight / max_weight
    for weight in edge_weights
]

node_values = [
    inflow_totals[node]
    for node in top_G.nodes()
]
```

**セル4：ネットワーク図を作成して保存する**

```python
Path("../reports/figures").mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(12, 10))

nodes = nx.draw_networkx_nodes(
    top_G,
    pos,
    node_color=node_values,
    node_size=700,
    cmap="viridis",
    ax=ax,
)

nx.draw_networkx_edges(
    top_G,
    pos,
    width=edge_widths,
    alpha=0.45,
    arrows=True,
    arrowsize=12,
    edge_color="gray",
    ax=ax,
)

nx.draw_networkx_labels(
    top_G,
    pos,
    font_family="Hiragino Sans",
    font_size=8,
    ax=ax,
)

fig.colorbar(nodes, ax=ax, label="流入者数（人）")
ax.set_title("都道府県間人口移動ネットワーク：移動者数上位60組（2025年）")
ax.axis("off")

plt.tight_layout()
plt.savefig(
    "../reports/figures/top60_migration_network.png",
    dpi=150,
)
plt.show()
```

実行後，次を確認せよ．

1. 多くの太いエッジが集まる都道府県はどこか
2. 首都圏，近畿圏，中京圏にはどのようなまとまりがあるか
3. 双方向に強い移動がある組合せはどこか
4. 表示されていない移動が「存在しない」とはいえないのはなぜか
````

```{tip} spring layout
`spring_layout`は，ノード間をばねで結んだように配置するアルゴリズムである．

強く結び付いたノードは近くなりやすいが，図上の位置は実際の地理的位置ではない．
地図とネットワーク図は，表している位置の意味が異なる．
```

---

## 1つの都道府県を中心に詳しく見る

全国図ではネットワーク全体のまとまりを確認できるが，個別の矢印は読み取りにくい．

特定のノードと，その周辺のノード・エッジを取り出した部分ネットワークを**ego network**という．
ここでは，埼玉県への流入上位5件と，埼玉県からの流出上位5件を表示する．

````{note} 演習7：埼玉県の人口移動ネットワークを描く
「埼玉県の人口移動」という見出しを作り，次のセルを順番に実行せよ．

**セル1：埼玉県に関係する上位の移動を取り出す**

```python
target_prefecture = "埼玉県"
top_n = 5

outgoing_df = (
    edge_df[edge_df["転出元"] == target_prefecture]
    .nlargest(top_n, "移動者数")
)

incoming_df = (
    edge_df[edge_df["転入先"] == target_prefecture]
    .nlargest(top_n, "移動者数")
)

ego_edges_df = (
    pd.concat([outgoing_df, incoming_df])
    .drop_duplicates(["転出元", "転入先"])
)

ego_edges_df
```

**セル2：ego networkを作る**

```python
ego_G = nx.from_pandas_edgelist(
    ego_edges_df,
    source="転出元",
    target="転入先",
    edge_attr="移動者数",
    create_using=nx.DiGraph,
)

pos = nx.spring_layout(
    ego_G,
    weight="移動者数",
    seed=42,
    k=1.5,
)
```

**セル3：ノードとエッジの色・太さを準備する**

```python
edge_colors = [
    "darkorange" if source == target_prefecture else "steelblue"
    for source, target in ego_G.edges()
]

edge_widths = [
    1
    + 5
    * ego_G[source][target]["移動者数"]
    / ego_edges_df["移動者数"].max()
    for source, target in ego_G.edges()
]

node_colors = [
    "crimson" if node == target_prefecture else "lightgray"
    for node in ego_G.nodes()
]
```

**セル4：ネットワーク図を作成して保存する**

```python
Path("../reports/figures").mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(9, 7))

nx.draw_networkx_nodes(
    ego_G,
    pos,
    node_color=node_colors,
    node_size=1600,
    edgecolors="black",
    ax=ax,
)

nx.draw_networkx_edges(
    ego_G,
    pos,
    edge_color=edge_colors,
    width=edge_widths,
    arrows=True,
    arrowsize=20,
    connectionstyle="arc3,rad=0.08",
    ax=ax,
)

nx.draw_networkx_labels(
    ego_G,
    pos,
    font_family="Hiragino Sans",
    font_size=10,
    ax=ax,
)

edge_labels = {
    (source, target): f"{data['移動者数']:,}"
    for source, target, data in ego_G.edges(data=True)
}

nx.draw_networkx_edge_labels(
    ego_G,
    pos,
    edge_labels=edge_labels,
    font_size=8,
    rotate=False,
    ax=ax,
)

ax.set_title("埼玉県の人口移動ego network（2025年）")
ax.axis("off")

plt.tight_layout()
plt.savefig(
    "../reports/figures/saitama_migration_network.png",
    dpi=150,
)
plt.show()
```

実行後，次を確認せよ．

1. 埼玉県からの流出が多い都道府県はどこか
2. 埼玉県への流入が多い都道府県はどこか
3. 同じ相手でも，流入と流出のどちらが多いか
4. 全国図より読み取りやすくなったことは何か
````

````{warning} 課題1：選択した都道府県のego networkを作成する

演習7を参考に，埼玉県以外の都道府県を1つ選び，その都道府県への流入上位7件と，その都道府県からの流出上位7件を表示するネットワーク図を作成せよ．

演習7のコードをPythonスクリプトにまとめ，`src/plot_my_prefecture_migration_network.py`を作成すること．

次の部分を自分が選択した都道府県に変更する．

```python
target_prefecture = <HOGEHOGE>
top_n = <FUGAFUGA>
```

### 条件

1. `target_prefecture`を埼玉県以外にする
2. `top_n`を`7`にする
3. 中心にする都道府県とその他の都道府県を異なる色で表示する
4. 流入と流出を異なる色で表示する
5. エッジの太さを移動者数に対応させる
6. エッジに移動者数を表示する
7. `reports/figures/my_prefecture_migration_network.png`として保存する

作成したPythonファイルを`10`フォルダ内で実行すること．

```bash
python3 src/plot_my_prefecture_migration_network.py
```

作成したPythonスクリプト`src/plot_my_prefecture_migration_network.py`と画像ファイル`reports/figures/my_prefecture_migration_network.png`を<span style="color:red">WebClass「第10回課題」問1・問2</span>から提出せよ．
````

<!--
````{dropdown} 課題1 解答例

- `<HOGEHOGE>`：選択した都道府県名を文字列で指定する
- `<FUGAFUGA>`：`7`
````
-->

---

## PageRankで移動先としての中心性を見る

### 中心性

中心性は，ネットワークの中でノードがどのような意味で中心的かを数値化する方法である．

| 指標 | 着目すること | 人口移動での解釈 |
| --- | --- | --- |
| 重み付き入次数 | 入るエッジの重みの合計 | 流入者数が多い |
| 重み付き出次数 | 出るエッジの重みの合計 | 流出者数が多い |
| PageRank | 中心的なノードからの流入 | 移動先として中心的である |

PageRankは，単に流入量を合計するだけでなく，**どのノードから流入しているか**も考慮する．

```{tip} 注意：PageRankの解釈
PageRankが高いことは，その都道府県が優れていることや住みやすいことを意味しない．

今回作成した人口移動ネットワークにおいて，移動先として中心的な位置にあることを表す指標の1つである．
```

````{note} 演習8：重み付きPageRankを計算して可視化する
「人口移動ネットワークのPageRank」という見出しを作り，次のセルを順番に実行せよ．

**セル1：PageRankを計算する**

```python
pagerank = nx.pagerank(
    G,
    alpha=0.85,
    weight="移動者数",
)

node_df["PageRank"] = node_df["都道府県"].map(pagerank)

node_df.sort_values("PageRank", ascending=False).head(10)
```

**セル2：PageRank上位10都道府県を取り出す**

```python
pagerank_top10_df = (
    node_df
    .sort_values("PageRank", ascending=False)
    .head(10)
)

pagerank_top10_df[
    ["都道府県", "流入者数", "流出者数", "都道府県間純移動", "PageRank"]
]
```

**セル3：棒グラフで可視化する**

```python
fig, ax = plt.subplots(figsize=(7, 5))

sns.barplot(
    data=pagerank_top10_df,
    x="PageRank",
    y="都道府県",
    color="steelblue",
    ax=ax,
)

ax.set_title("人口移動ネットワークのPageRank上位10都道府県（2025年）")
ax.set_xlabel("PageRank")
ax.set_ylabel("都道府県")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. PageRank上位にはどの都道府県が入っているか
2. 流入者数の上位とPageRankの上位は同じか
3. 人口規模が結果に影響している可能性はあるか
````

````{warning} 課題2：PageRank上位10都道府県をPythonファイルで可視化する

以下のコードの`<HOGEHOGE1>`から`<HOGEHOGE5>`を適切に書き換え，Pythonスクリプト`src/plot_migration_pagerank.py`を作成せよ．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns


input_path = "data/processed/prefecture_migration_edges_2025.csv"
output_path = "reports/figures/migration_pagerank.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

edge_df = pd.read_csv(input_path)

G = nx.from_pandas_edgelist(
    edge_df,
    source=<HOGEHOGE1>,
    target=<HOGEHOGE2>,
    edge_attr=<HOGEHOGE3>,
    create_using=<HOGEHOGE4>,
)

pagerank = nx.pagerank(
    G,
    weight=<HOGEHOGE5>,
)

pagerank_df = pd.DataFrame({
    "都道府県": list(pagerank.keys()),
    "PageRank": list(pagerank.values()),
})

top10_df = pagerank_df.nlargest(10, "PageRank")

fig, ax = plt.subplots(figsize=(7, 5))

sns.barplot(
    data=top10_df,
    x="PageRank",
    y="都道府県",
    color="steelblue",
    ax=ax,
)

ax.set_title("人口移動ネットワークのPageRank上位10都道府県（2025年）")
ax.set_xlabel("PageRank")
ax.set_ylabel("都道府県")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```

作成したPythonファイルを`10`フォルダ内で実行すること．

```bash
python3 src/plot_migration_pagerank.py
```

作成したPythonスクリプト`src/plot_migration_pagerank.py`と画像ファイル`reports/figures/migration_pagerank.png`を<span style="color:red">WebClass「第10回課題」問3・問4</span>から提出せよ．
````

<!--
````{dropdown} 課題2 解答例

- `<HOGEHOGE1>`：`"転出元"`
- `<HOGEHOGE2>`：`"転入先"`
- `<HOGEHOGE3>`：`"移動者数"`
- `<HOGEHOGE4>`：`nx.DiGraph`
- `<HOGEHOGE5>`：`"移動者数"`
````
-->

---

## 人口移動ネットワークのクラスターを探す

### コミュニティ検出

ネットワーク内部で，互いの結び付きが相対的に強いノードのまとまりを**コミュニティ（クラスター）**と呼ぶ．

今回は`greedy_modularity_communities()`を使う．
この方法は，同じコミュニティ内のエッジの重みが，偶然に接続した場合よりどの程度大きいかを表す**モジュラリティ**が高くなるようにノードをまとめる．

人口移動には方向があるが，この演習では地域間の結び付きの総量を調べるため，2都道府県間の往復移動者数を合計して無向グラフを作る．

$$
w_{ij}^{\mathrm{undirected}}
=
w_{ij}+w_{ji}
$$

```{important} 有向グラフから無向グラフへの変換
方向を取り除くと，「どちらからどちらへの移動が多いか」という情報は失われる．

今回は地域間の結び付きの強さからクラスターを探すために無向化する．
分析目的が異なれば，有向ネットワークに対応した別のコミュニティ検出法を選ぶ必要がある．
```

````{note} 演習9：人口移動ネットワークのコミュニティを検出する
「人口移動ネットワークのコミュニティ」という見出しを作り，次のセルを順番に実行せよ．

**セル1：往復の移動者数を合計する**

```python
pair_df = edge_df.copy()

pair_names = pair_df.apply(
    lambda row: sorted([row["転出元"], row["転入先"]]),
    axis=1,
    result_type="expand",
)

pair_df[["都道府県1", "都道府県2"]] = pair_names

undirected_edge_df = (
    pair_df
    .groupby(["都道府県1", "都道府県2"], as_index=False)["移動者数"]
    .sum()
    .rename(columns={"移動者数": "双方向移動者数"})
)

print("都道府県ペア数:", len(undirected_edge_df))
undirected_edge_df.nlargest(10, "双方向移動者数")
```

**セル2：重み付き無向グラフを作る**

```python
undirected_G = nx.from_pandas_edgelist(
    undirected_edge_df,
    source="都道府県1",
    target="都道府県2",
    edge_attr="双方向移動者数",
    create_using=nx.Graph,
)

print("ノード数:", undirected_G.number_of_nodes())
print("エッジ数:", undirected_G.number_of_edges())
```

**セル3：コミュニティを検出する**

```python
communities = list(
    nx.community.greedy_modularity_communities(
        undirected_G,
        weight="双方向移動者数",
    )
)

print("コミュニティ数:", len(communities))

for community_id, members in enumerate(communities, start=1):
    print(
        "コミュニティ",
        community_id,
        ":",
        "，".join(sorted(members)),
    )
```

**セル4：都道府県とコミュニティ番号の表を作る**

```python
community_rows = []

for community_id, members in enumerate(communities, start=1):
    for prefecture in members:
        community_rows.append({
            "都道府県": prefecture,
            "コミュニティ": community_id,
        })

community_df = (
    pd.DataFrame(community_rows)
    .sort_values(["コミュニティ", "都道府県"])
    .reset_index(drop=True)
)

community_df
```

**セル5：コミュニティごとに色分けして表示する**

```python
community_map = dict(
    zip(
        community_df["都道府県"],
        community_df["コミュニティ"],
    )
)

display_edges_df = undirected_edge_df.nlargest(
    80,
    "双方向移動者数",
)

community_plot_G = nx.from_pandas_edgelist(
    display_edges_df,
    source="都道府県1",
    target="都道府県2",
    edge_attr="双方向移動者数",
    create_using=nx.Graph,
)

community_plot_G.add_nodes_from(undirected_G.nodes())

pos = nx.spring_layout(
    undirected_G,
    weight="双方向移動者数",
    seed=42,
    k=1.0,
)

community_count = len(communities)
cmap = plt.get_cmap("tab10")

node_colors = [
    cmap(
        (community_map[node] - 1)
        / max(1, community_count - 1)
    )
    for node in community_plot_G.nodes()
]

edge_widths = [
    0.5
    + 4
    * community_plot_G[source][target]["双方向移動者数"]
    / display_edges_df["双方向移動者数"].max()
    for source, target in community_plot_G.edges()
]

Path("../reports/figures").mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(12, 10))

nx.draw_networkx_nodes(
    community_plot_G,
    pos,
    node_color=node_colors,
    node_size=750,
    edgecolors="black",
    ax=ax,
)

nx.draw_networkx_edges(
    community_plot_G,
    pos,
    width=edge_widths,
    alpha=0.4,
    edge_color="gray",
    ax=ax,
)

nx.draw_networkx_labels(
    community_plot_G,
    pos,
    font_family="Hiragino Sans",
    font_size=8,
    ax=ax,
)

ax.set_title("都道府県間人口移動ネットワークのコミュニティ（2025年）")
ax.axis("off")

plt.tight_layout()
plt.savefig(
    "../reports/figures/migration_communities.png",
    dpi=150,
)
plt.show()
```

実行後，次を確認せよ．

1. コミュニティはいくつ検出されたか
2. 首都圏，近畿圏，中京圏はどのようなコミュニティに分かれたか
3. 一般的な地方区分と異なる都道府県はあるか
4. 地理的に近い都道府県が同じコミュニティになりやすいのはなぜか
5. エッジの表示を80本に絞っても，コミュニティの計算には全エッジを使用していることを説明できるか
````

```{tip} コミュニティは唯一の正解ではない
検出結果は，使用するデータ，重み，方向の扱い，アルゴリズムによって変わる．

検出されたクラスターをそのまま正解と考えるのではなく，どのような結び付きによってそのグループになったのかを元データと照らして考えることが重要である．
```

---

## 考察

````{note} 演習10：README.mdに分析結果を整理する

README.mdの「第10回 分析記録」に次の内容を記入せよ．

1. 全国の主要な人口移動はどの地域に集中していたか
2. 埼玉県と結び付きの強い都道府県はどこか
3. 流入者数，流出者数，純移動，PageRankはそれぞれ何を表すか
4. 全国図とego networkでは，読み取りやすいことがどのように違ったか
5. 検出されたコミュニティにはどのような地域的特徴があったか
6. 今回のデータだけでは説明できないことは何か

図から観察した事実と，理由についての推測を分けて書くこと．
````

```{note} この分析だけでは原因は分からない
人口移動には，就職，進学，住宅事情，家族，交通，災害など多くの要因が関係する．

人口移動ネットワークだけから，移動が生じた原因を断定することはできない．
```

---

## まとめ

- 行政統計では，出典，調査年，単位，行と列の意味を最初に確認する
- 都道府県間人口移動は，重み付き有向ネットワークとして表現できる
- クロス集計表（ワイド形式）は，エッジリスト形式（長形式）へ変換するとネットワークを作りやすい
- すべての異なる都道府県間に移動があるため，エッジの有無より重みが重要である
- 流入者数と流出者数は，重み付き入次数・出次数として計算できる
- 全国図では全体構造，ego networkでは特定地域の関係を詳しく確認できる
- 表示用にエッジを絞る場合は，表示していない関係があることに注意する
- PageRankはネットワーク上の中心性の1つであり，価値や住みやすさを直接表すものではない
- コミュニティ検出を使うと，人口移動によって強く結び付いた地域のクラスターを探すことができる
- 可視化から傾向は読み取れるが，人口移動の原因を断定することはできない

次回はデータ分析実践IIとして経済データを扱う．

### 課題の提出期限

<span style="color:red">6月23日(火)23:59まで</span>

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所から提出したものについて加点対象とします．

````{note} 発展問題1：人口規模で標準化した移動率を考える

移動者数が多い都道府県は，もともとの人口も多い可能性がある．
都道府県人口のデータを追加し，次の転出率を計算して上位10都道府県を可視化せよ．

$$
\text{転出率}
=
\frac{\text{流出者数}}{\text{都道府県人口}}
\times 100
$$

次のデータをダウンロード・解凍し，`data/raw`に配置して使用すること．

- [dashboard_population_json.zip](./analysis/10/data/raw/dashboard_population_json.zip)
- [dashboard_regions_json.zip](./analysis/10/data/raw/dashboard_regions_json.zip)

人口データは2020年国勢調査，人口移動データは2025年であり，厳密な同年比較ではない．
この違いを明記した上で，人数で見た順位と率で見た順位を比較すること．

`src/plot_prefecture_migration_rate.py`を作成し，WebClass「第10回発展問題」問1から提出せよ．

提出するのは作成したPythonファイルのみである．
````

<!--
````{dropdown} <span style="color:red">発展問題1 解答例</span>

```python
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


edge_path = "data/processed/prefecture_migration_edges_2025.csv"
population_path = "data/raw/dashboard_population.json"
region_path = "data/raw/dashboard_regions.json"
output_path = "reports/figures/prefecture_migration_rate.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

edge_df = pd.read_csv(edge_path)

outflow_df = (
    edge_df
    .groupby("転出元", as_index=False)["移動者数"]
    .sum()
    .rename(columns={
        "転出元": "都道府県",
        "移動者数": "流出者数",
    })
)

with open(population_path, encoding="utf-8") as f:
    population_data = json.load(f)

population_objects = (
    population_data["GET_STATS"]
    ["STATISTICAL_DATA"]["DATA_INF"]["DATA_OBJ"]
)

population_df = pd.DataFrame([
    {
        "地域コード": obj["VALUE"]["@regionCode"],
        "総人口": int(obj["VALUE"]["$"]),
    }
    for obj in population_objects
])

with open(region_path, encoding="utf-8") as f:
    region_data = json.load(f)

region_classes = (
    region_data["GET_META_REGION_INF"]["METADATA_INF"]
    ["CLASS_INF"]["CLASS_OBJ"][0]["CLASS"]
)

region_df = pd.DataFrame([
    {
        "地域コード": region["@regionCode"],
        "都道府県": region["@name"],
    }
    for region in region_classes
])

rate_df = (
    outflow_df
    .merge(region_df, on="都道府県")
    .merge(population_df, on="地域コード")
)

# 人口は2020年，人口移動は2025年であるため，厳密な同年比較ではない．
rate_df["転出率"] = (
    rate_df["流出者数"]
    / rate_df["総人口"]
    * 100
)

top10_df = rate_df.nlargest(10, "転出率")

fig, ax = plt.subplots(figsize=(8, 5))

sns.barplot(
    data=top10_df,
    x="転出率",
    y="都道府県",
    color="steelblue",
    ax=ax,
)

ax.set_title("都道府県人口に対する都道府県間転出者数の割合")
ax.set_xlabel("転出率（%，人口は2020年，移動は2025年）")
ax.set_ylabel("都道府県")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```
````
-->

````{note} 発展問題2：双方向移動の非対称性を調べる

同じ2都道府県間でも，方向によって移動者数は異なる．

各都道府県ペアについて，次の値を計算せよ．

$$
\text{移動差}_{ij}=w_{ij}-w_{ji}
$$

双方向の移動者数の差が大きい上位10組を取り出し，どちらの方向への移動が多いか分かる棒グラフを作成すること．

`src/plot_migration_asymmetry.py`を作成し，WebClass「第10回発展問題」問2から提出せよ．

提出するのは作成したPythonファイルのみである．
````

<!--
````{dropdown} <span style="color:red">発展問題2 解答例</span>

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


input_path = "data/processed/prefecture_migration_edges_2025.csv"
output_path = "reports/figures/migration_asymmetry.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

edge_df = pd.read_csv(input_path)

reverse_df = edge_df.rename(columns={
    "転出元": "転入先",
    "転入先": "転出元",
    "移動者数": "逆方向移動者数",
})

comparison_df = edge_df.merge(
    reverse_df[["転出元", "転入先", "逆方向移動者数"]],
    on=["転出元", "転入先"],
)

# 同じ都道府県ペアを1回だけ残す．
comparison_df = comparison_df[
    comparison_df["転出元"] < comparison_df["転入先"]
].copy()

comparison_df["移動差"] = (
    comparison_df["移動者数"]
    - comparison_df["逆方向移動者数"]
)
comparison_df["差の絶対値"] = comparison_df["移動差"].abs()


def make_direction_label(row):
    if row["移動差"] >= 0:
        return f"{row['転出元']}→{row['転入先']}"
    return f"{row['転入先']}→{row['転出元']}"


comparison_df["多い方向"] = comparison_df.apply(
    make_direction_label,
    axis=1,
)

top10_df = comparison_df.nlargest(10, "差の絶対値")

fig, ax = plt.subplots(figsize=(9, 6))

sns.barplot(
    data=top10_df,
    x="差の絶対値",
    y="多い方向",
    color="darkorange",
    ax=ax,
)

ax.set_title("都道府県間人口移動の方向差が大きい組合せ（2025年）")
ax.set_xlabel("双方向の移動者数の差（人）")
ax.set_ylabel("移動者数が多い方向")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```
````
-->

````{note} 発展問題3：日本地図上に人口移動ネットワークを表示する

通常のネットワーク図では，ノードの位置は結び付きの強さによって決まる．
第9回で学んだ地図可視化を応用し，都道府県を日本地図上の位置に配置して人口移動ネットワークを表示せよ．

次の座標データをダウンロード・解凍し，`data/processed`に配置すること．

[prefecture_capital_coordinates_csv.zip](./analysis/10/data/processed/prefecture_capital_coordinates_csv.zip)

`plotly`がインストールされていない場合は，ターミナルで次を実行すること．

```bash
python3 -m pip install plotly
```

### 条件

1. 都道府県庁所在地を各都道府県の代表地点として使う
2. 移動者数上位40組を線で表示する
3. 線の太さを移動者数に対応させる
4. ノードの色と大きさを流入者数に対応させる
5. マウスを重ねると都道府県名と値が表示されるようにする
6. `reports/figures/migration_network_map.html`として保存する

`src/plot_migration_network_map.py`を作成し，WebClass「第10回発展問題」問3から提出せよ．

提出するのは作成したPythonファイルのみである．

```{warning} 地図上の線の意味
地図上の直線は，実際の移動経路や交通経路を表しているわけではない．
転出元と転入先の代表地点を結び，2都道府県間に人口移動があることを模式的に示している．
```
````

<!--
````{dropdown} <span style="color:red">発展問題3 解答例</span>

```python
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


edge_path = "data/processed/prefecture_migration_edges_2025.csv"
coordinate_path = "data/processed/prefecture_capital_coordinates.csv"
output_path = "reports/figures/migration_network_map.html"

Path("reports/figures").mkdir(parents=True, exist_ok=True)

edge_df = pd.read_csv(edge_path)
coordinate_df = pd.read_csv(coordinate_path)

coordinate_lookup = coordinate_df.set_index("都道府県")
top_edges_df = edge_df.nlargest(40, "移動者数")
max_movers = top_edges_df["移動者数"].max()

fig = go.Figure()

for _, row in top_edges_df.iterrows():
    source = coordinate_lookup.loc[row["転出元"]]
    target = coordinate_lookup.loc[row["転入先"]]
    label = (
        f"{row['転出元']}→{row['転入先']}<br>"
        f"移動者数：{row['移動者数']:,}人"
    )

    fig.add_trace(
        go.Scattermap(
            lat=[source["緯度"], target["緯度"]],
            lon=[source["経度"], target["経度"]],
            mode="lines",
            line={
                "width": 0.5 + 5 * row["移動者数"] / max_movers,
                "color": "rgba(80, 80, 80, 0.45)",
            },
            text=[label, label],
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        )
    )

inflow_df = (
    edge_df
    .groupby("転入先", as_index=False)["移動者数"]
    .sum()
    .rename(columns={
        "転入先": "都道府県",
        "移動者数": "流入者数",
    })
    .merge(coordinate_df, on="都道府県")
)

inflow_df["表示サイズ"] = (
    8
    + 22
    * inflow_df["流入者数"]
    / inflow_df["流入者数"].max()
)

fig.add_trace(
    go.Scattermap(
        lat=inflow_df["緯度"],
        lon=inflow_df["経度"],
        mode="markers",
        marker={
            "size": inflow_df["表示サイズ"],
            "color": inflow_df["流入者数"],
            "colorscale": "viridis",
            "showscale": True,
            "colorbar": {"title": "流入者数"},
        },
        text=(
            inflow_df["都道府県"]
            + "<br>代表地点："
            + inflow_df["代表地点"]
            + "<br>流入者数："
            + inflow_df["流入者数"].map("{:,}".format)
            + "人"
        ),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    )
)

fig.update_layout(
    title="日本地図上の都道府県間人口移動ネットワーク（上位40組）",
    map={
        "style": "open-street-map",
        "center": {"lat": 36.2, "lon": 137.0},
        "zoom": 4,
    },
    height=750,
    margin={"l": 0, "r": 0, "t": 50, "b": 0},
)

fig.write_html(output_path)

print("saved:", output_path)
```
````
-->
