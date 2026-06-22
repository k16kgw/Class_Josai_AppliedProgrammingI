# 第10回　データ分析実践I：行政統計

## 前回の復習

第9回は，天気予報データに緯度・経度を結合し，地図上で地域差を確認した．

| 処理 | 第9回に行ったこと |
| --- | --- |
| データ取得 | 気象庁APIから複数都道府県のJSONを取得した |
| 前処理 | JSONを表に変換し，予報地域ごとに集計した |
| 結合 | 地域名をキーにして緯度・経度・標高を結合した |
| 可視化 | `plotly`で値の大小と位置関係を同時に表した |
| 保存 | `write_html()`でインタラクティブな地図を保存した |

今回も，**問いを立てる → データを取得する → 前処理する → 可視化する → 読み取る**という流れで分析する．

## 今回のテーマ

行政統計は，人口，世帯，産業，教育，福祉など，社会の状態を把握するために国や自治体が作成しているデータである．

今回は総務省統計局の**住民基本台帳人口移動報告**を使い，都道府県間の人口移動を分析する．

> **人は，どの都道府県からどの都道府県へ移動しているのか．**

都道府県を点，人口移動を矢印として考えると，人口移動は**ネットワーク**として表現できる．

```text
埼玉県 ── 66,159人 ──▶ 東京都
東京都 ── 71,169人 ──▶ 埼玉県
```

同じ2都県間でも，方向によって移動者数は異なる．
したがって，今回は**向き**と**重み**を持つネットワークを扱う．

## 到達目標

- 行政統計の出典，調査年，単位，表の行と列の意味を確認できる
- クロス集計表を，分析しやすい長形式のデータに変換できる
- 人口移動を重み付き有向ネットワークとして説明できる
- `NetworkX`を使ってネットワークを作成できる
- 流入者数，流出者数，純移動，PageRankを計算できる
- 表示するエッジを絞り，読み取れるネットワーク図を作成できる
- 可視化から分かることと，このデータだけでは分からないことを区別できる

## 今回の分析の流れ

| 段階 | 実施すること | 作成されるもの |
| --- | --- | --- |
| テーマ設定 | 都道府県間の人口移動を問いにする | 分析の目的 |
| データ取得 | e-Statから2025年のExcelを取得する | `prefecture_migration_2025.xlsx` |
| 前処理 | クロス集計表を長形式へ変換する | `prefecture_migration_edges_2025.csv` |
| ネットワーク化 | 都道府県と人口移動から有向グラフを作る | `DiGraph` |
| 指標計算 | 流入者数，流出者数，純移動，PageRankを求める | ノード集計表 |
| 可視化 | 全国の主要な移動と特定県の移動を描く | PNGファイル |
| 考察 | 集中する地域，強い結び付き，限界を整理する | README.md |

---

## 準備

````{note} 演習0：作業フォルダを作成する

1. ターミナルで次のコマンドを順に実行する．

```bash
cd /Users/<ユーザ名>/applied_programming_i
mkdir 10
cd 10
mkdir -p notebooks data/raw data/processed src reports/figures
git init
```

2. `README.md`を作成し，次の内容を記入する．

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
- 観察用ノートブック：notebooks/administrative_statistics.ipynb
- 作成するスクリプト：
  - src/plot_my_prefecture_migration_network.py
  - src/plot_migration_pagerank.py
- 出力する図：
  - reports/figures/my_prefecture_migration_network.png
  - reports/figures/migration_pagerank.png
```

3. `.gitignore`を作成する．

```gitignore
.DS_Store
*.swp
*~
.vscode/
.ipynb_checkpoints/
*.ipynb
data/raw/
```

4. 作成したファイルをコミットする．

```bash
git add .
git commit -m "first commit"
```

5. `notebooks/administrative_statistics.ipynb`を新規作成する．
````

---

## 使用する行政統計

### 住民基本台帳人口移動報告

住民基本台帳人口移動報告は，住民基本台帳法に基づく転入届などから，国内の人口移動を集計した統計である．

今回は，2026年2月3日に公開された**2025年結果**を使う．

| 項目 | 内容 |
| --- | --- |
| 提供者 | 総務省統計局 |
| 統計名 | 住民基本台帳人口移動報告 |
| 対象年 | 2025年 |
| 使用表 | 表2 男女、移動前の住所地別都道府県間移動者数 |
| 単位 | 人 |
| 行 | 移動前の住所地 |
| 列 | 移動後の住所地 |
| 結果概要 | https://www.stat.go.jp/data/idou/2025np/jissu/youyaku/index.html |
| 統計表 | https://www.e-stat.go.jp/stat-search/files?layout=datalist&lid=000001476215 |

```{important} 行と列の意味
元のExcelでは，行が**移動前の住所地**，列が**移動後の住所地**である．

したがって，行が埼玉県，列が東京都の値は「埼玉県から東京都へ移動した人数」を表す．
向きを逆に解釈しないように注意すること．
```

### ネットワークとしての対応

| 人口移動データ | ネットワーク |
| --- | --- |
| 都道府県 | ノード |
| 転出元から転入先への移動 | 有向エッジ |
| 移動者数 | エッジの重み |
| 転入者数の合計 | 入次数の重み付き合計 |
| 転出者数の合計 | 出次数の重み付き合計 |

今回のグラフは次の性質を持つ．

- **有向グラフ**：移動には転出元から転入先への向きがある
- **重み付きグラフ**：移動者数をエッジの重みとして持つ
- **自己ループなし**：同じ都道府県内の移動は扱わない

---

## ネットワーク科学的な解析手法

ネットワーク科学では，個々の値だけでなく，対象同士の**関係の構造**を分析する．

通常の都道府県別統計では，「東京都の転入者数はいくつか」のように各地域を1行ずつ見る．
ネットワーク分析では，さらに次のような問いを考える．

- どの都道府県間の結び付きが強いか
- 移動が集中する中心的な都道府県はどこか
- 双方向に強い移動がある組合せはどこか
- 首都圏や近畿圏のようなまとまりは見られるか
- 特定の都道府県は，どの地域と直接結び付いているか

### 重み付き隣接行列

都道府県間の人口移動は，重み付き隣接行列$W$として表すことができる．

$$
W=
\begin{pmatrix}
w_{11} & w_{12} & \cdots & w_{1N}\\
w_{21} & w_{22} & \cdots & w_{2N}\\
\vdots & \vdots & \ddots & \vdots\\
w_{N1} & w_{N2} & \cdots & w_{NN}
\end{pmatrix}
$$

$w_{ij}$は，都道府県$i$から都道府県$j$へ移動した人数である．
今回のデータでは$N=47$であり，同じ都道府県内の移動を扱わないため，対角成分$w_{ii}$は使用しない．

行方向に合計すると都道府県$i$からの流出者数，列方向に合計すると都道府県$j$への流入者数になる．

```text
                     転入先
              埼玉県  東京都  神奈川県
転出元 埼玉県      -    66159     16859
       東京都  71169        -     87758
       神奈川県 15791   88983          -
```

Excelのクロス集計表は隣接行列に近い形である．
一方，`NetworkX`では「転出元，転入先，移動者数」を1行にしたエッジリストが扱いやすい．

### 分析するスケール

ネットワークは，分析する範囲によって見えるものが異なる．

| スケール | 主な対象 | 今回調べること | 使用する方法 |
| --- | --- | --- | --- |
| ネットワーク全体 | 47都道府県全体 | どの程度つながっているか | ノード数，エッジ数，密度 |
| ノード | 1つの都道府県 | 移動がどの程度集まるか | 流入者数，流出者数，純移動，PageRank |
| エッジ | 2都道府県間 | どの移動が強いか | 移動者数，方向，双方向の比較 |
| 局所構造 | 特定県と周辺 | どの地域と直接結び付くか | ego network |
| 中間構造 | 複数の地域群 | まとまりがあるか | コミュニティ検出 |

今回の講義では，全体，ノード，エッジ，局所構造を扱う．
コミュニティ検出は自主学習用の発展問題とする．

### ノード数・エッジ数・密度

ノード数を$N$，エッジ数を$M$とする．
自己ループを持たない有向グラフでは，最大で$N(N-1)$本のエッジを持つことができる．

ネットワーク密度$d$は次で定義される．

$$
d=\frac{M}{N(N-1)}
$$

密度が1に近いほど，多くのノード間にエッジが存在する．

今回の人口移動データでは，すべての異なる都道府県の組合せに移動者がいるため，密度は1である．
したがって，「つながっているか」だけでは都道府県間の違いを説明しにくい．
**エッジの重みである移動者数**を見る必要がある．

### 次数とstrength

有向グラフでは，ノードに入るエッジと，ノードから出るエッジを区別する．

| 指標 | 意味 | 人口移動での解釈 |
| --- | --- | --- |
| 入次数$k_i^{in}$ | ノード$i$へ入るエッジの本数 | 何都道府県から転入があるか |
| 出次数$k_i^{out}$ | ノード$i$から出るエッジの本数 | 何都道府県へ転出があるか |
| 入strength$s_i^{in}$ | 入るエッジの重みの合計 | 他県からの流入者数 |
| 出strength$s_i^{out}$ | 出るエッジの重みの合計 | 他県への流出者数 |

$$
k_i^{in}=\sum_j a_{ji},
\qquad
k_i^{out}=\sum_j a_{ij}
$$

ここで$a_{ij}$は，エッジがあれば1，なければ0となる隣接行列の要素である．

重みを考慮したstrengthは次で求める．

$$
s_i^{in}=\sum_j w_{ji},
\qquad
s_i^{out}=\sum_j w_{ij}
$$

今回のネットワークでは，多くの都道府県の入次数・出次数がほぼ同じになる．
そのため，次数よりもstrengthの方が分析に適している．

### 中心性

中心性は，ネットワークの中でノードがどのような意味で中心的かを数値化する方法である．
中心性には複数の定義があり，分析目的に応じて使い分ける．

| 中心性 | 着目すること | 人口移動で考えられる解釈 |
| --- | --- | --- |
| 次数中心性 | 接続先の多さ | 多くの都道府県と移動がある |
| strength | エッジの重みの合計 | 流入・流出する人数が多い |
| PageRank | 中心的なノードからの流入 | 移動先としてネットワーク上の中心にある |
| 媒介中心性 | 最短経路上に現れる頻度 | 地域間をつなぐ位置にある |

中心性が高いことは，その都道府県の価値，住みやすさ，政策の良し悪しを直接表すものではない．
あくまで，定義したネットワーク上での位置を表す．

```{warning} 重みと距離は同じではない
人口移動ネットワークでは，移動者数が大きいほど結び付きが強い．
一方，最短経路を使う媒介中心性では，重みを「距離」として扱うと，小さい値ほど近いと解釈される．

移動者数を使って最短経路を計算する場合は，例えば

$$
\text{距離}_{ij}=\frac{1}{w_{ij}}
$$

のように，強い結び付きを短い距離へ変換する必要がある．
今回の講義では，この変換を必要としないstrengthとPageRankを中心に扱う．
```

### PageRank

PageRankは，単に流入するエッジの本数や重みだけでなく，**どのノードから流入しているか**も考慮する中心性である．

概念的には，ノード$i$のPageRank$PR(i)$を次のように繰り返し計算する．

$$
PR(i)
=
\frac{1-\alpha}{N}
+
\alpha
\sum_{j\rightarrow i}
PR(j)
\frac{w_{ji}}{\sum_k w_{jk}}
$$

$\alpha$は，リンクをたどる影響の強さを表すパラメタであり，通常は$0.85$程度を使う．

人口移動ネットワークでは，移動者数の大きい都道府県から多くの人が流入する地域ほど，PageRankが高くなりやすい．
ただし，人口規模そのものの影響も受けるため，値の解釈には注意が必要である．

### ego network

ego networkは，注目する1つのノードと，その周辺のノード・エッジを取り出した部分ネットワークである．

今回の講義では，埼玉県を中心として次を表示する．

- 埼玉県からの流出者数が多い上位の都道府県
- 埼玉県への流入者数が多い上位の都道府県

全国ネットワークでは全体的な集中やまとまりを確認しやすい．
ego networkでは，特定の都道府県について方向や移動者数を詳しく確認しやすい．

### エッジの抽出としきい値

エッジ数が多いネットワークをそのまま描くと，線が重なって読み取れない．
可視化では，次のような方法で表示するエッジを絞ることがある．

- 移動者数の上位$n$本だけを表示する
- 移動者数が一定値以上のエッジだけを表示する
- 特定の都道府県に接続するエッジだけを表示する

```{important} 指標の計算と図の表示を区別する
エッジを絞ると，見やすい図を作ることができる．
一方，エッジを絞ったグラフで中心性を計算すると，元のネットワークとは異なる結果になる．

今回の講義では，原則として次のように使い分ける．

- **指標の計算**：2162本のエッジを持つ全体ネットワークを使う
- **全国図の表示**：移動者数上位60本を使う
- **地域の詳細表示**：対象県への流入・流出上位を使う
```

### コミュニティ

コミュニティとは，ネットワーク内部で互いに強く結び付いたノードの集まりである．

人口移動ネットワークでは，首都圏，近畿圏，中京圏などがまとまりとして検出される可能性がある．
ただし，アルゴリズムやエッジの絞り方によって結果は変わる．

検出されたコミュニティは，既存の地方区分が自動的に再現されたものとは限らない．
どのエッジと重みを使った結果なのかを確認して解釈する必要がある．

### 今回使用する解析手法

| 解析手法 | 使用するデータ | 確認すること |
| --- | --- | --- |
| 密度 | 全エッジ | 接続の有無だけでは差が出にくいこと |
| strength | 全エッジ | 各都道府県への流入量・流出量 |
| 純移動 | 全エッジ | 流入と流出の差 |
| PageRank | 全エッジ | 移動先としてのネットワーク上の中心性 |
| 上位エッジの可視化 | 上位60エッジ | 全国的な強い人口移動 |
| ego network | 特定県の上位流入・流出 | 特定県と周辺地域の関係 |

---

## データを取得して前処理する

元のExcelは，見出しが複数行に分かれ，男女別の列や大都市圏の列も含まれている．
今回の目的はネットワーク分析であるため，Excelを長形式へ変換する処理は配布スクリプトで行う．

````{note} 演習1：公式Excelと前処理スクリプトを取得する

**1．必要なライブラリをインストールする**

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
````

うまく作成できなかった場合は，次のファイルをダウンロード・解凍し，`data/processed`に配置して以降の演習を進めること．

[prefecture_migration_edges_2025_csv.zip](./analysis/10/data/processed/prefecture_migration_edges_2025_csv.zip)

### 前処理スクリプトの動作

配布スクリプトは次の処理を行っている．

| 処理 | 内容 |
| --- | --- |
| Excelの読み込み | 見出しを付けずに表全体を読み込む |
| 列の選択 | 47都道府県の「総数」列だけを選ぶ |
| 行の選択 | 国籍区分が「移動者」である47都道府県だけを選ぶ |
| 長形式への変換 | 転出元，転入先，移動者数を1行にする |
| 不要行の除外 | 同一県内の組合せと値のないセルを除く |
| 検査 | 転出元と転入先に47都道府県があるか確認する |
| 保存 | CSVファイルとして保存する |

元のクロス集計表は，人間が全体を見るには便利である．
一方，ネットワークを作るには次のような長形式が扱いやすい．

| 年 | 転出元 | 転入先 | 移動者数 |
| --- | --- | --- | ---: |
| 2025 | 神奈川県 | 東京都 | 88983 |
| 2025 | 東京都 | 神奈川県 | 87758 |
| 2025 | 東京都 | 埼玉県 | 71169 |

````{note} 演習2：前処理済みデータを確認する
Notebookに「人口移動データを確認する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：ライブラリを読み込む**

```python
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
```

**セル2：CSVを読み込む**

```python
edge_path = "../data/processed/prefecture_migration_edges_2025.csv"

edge_df = pd.read_csv(edge_path)

edge_df.head(10)
```

**セル3：行数，欠損，データ型を確認する**

```python
print("行数:", len(edge_df))
print("転出元の数:", edge_df["転出元"].nunique())
print("転入先の数:", edge_df["転入先"].nunique())
print("欠損数:")
print(edge_df.isna().sum())
print("データ型:")
print(edge_df.dtypes)
```

**セル4：移動者数の大きい組合せを確認する**

```python
edge_df.nlargest(10, "移動者数")
```

実行後，次を確認せよ．

1. 行数が`47 × 46 = 2162`になっているか
2. `移動者数`は数値になっているか
3. 同じ2都県でも，方向によって移動者数が異なるか
4. 移動者数が大きい組合せは大都市圏に集中しているか
````

---

## ネットワークを作成する

### 有向グラフと重み

`NetworkX`では，有向グラフを`DiGraph`で表す．

```text
G = (V, E)

V：ノードの集合
E：向きを持つエッジの集合
```

今回のエッジは，さらに移動者数という重み$w_{ij}$を持つ．

$$
w_{ij}
=
\text{都道府県 }i\text{ から都道府県 }j\text{ への移動者数}
$$

````{note} 演習3：NetworkXの有向グラフを作成する

```python
G = nx.from_pandas_edgelist(
    edge_df,
    source="転出元",
    target="転入先",
    edge_attr="移動者数",
    create_using=nx.DiGraph,
)

print("ノード数:", G.number_of_nodes())
print("エッジ数:", G.number_of_edges())
print("密度:", nx.density(G))
```

実行後，次を確認せよ．

1. ノード数は47か
2. エッジ数は2162か
3. 密度は1になっているか
````

```{important} エッジ数だけでは違いが分からない
今回のデータでは，すべての異なる都道府県間に人口移動がある．
そのため，「接続している都道府県の数」を数えるだけでは，どの都道府県もほぼ同じになる．

重要なのは，エッジが存在するかではなく，**何人移動したかという重み**である．
```

---

## 重み付きネットワークの指標

### 流入者数と流出者数

ノード$i$への流入者数を$s_i^{in}$，ノード$i$からの流出者数を$s_i^{out}$とする．

$$
s_i^{in}=\sum_j w_{ji}
$$

$$
s_i^{out}=\sum_j w_{ij}
$$

これらは，重み付き入次数，重み付き出次数に相当し，**strength**とも呼ばれる．

都道府県間の純移動は次で求める．

$$
\text{都道府県間純移動}_i=s_i^{in}-s_i^{out}
$$

````{note} 演習4：都道府県ごとのネットワーク指標を作る

**セル1：流入者数と流出者数を求める**

```python
in_strength = dict(G.in_degree(weight="移動者数"))
out_strength = dict(G.out_degree(weight="移動者数"))

node_df = pd.DataFrame({
    "都道府県": list(G.nodes())
})

node_df["流入者数"] = node_df["都道府県"].map(in_strength)
node_df["流出者数"] = node_df["都道府県"].map(out_strength)
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

**セル3：流入者数と流出者数の関係を見る**

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
    ax.text(row["流出者数"], row["流入者数"], row["都道府県"], fontsize=8)

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

```{warning} 純移動の解釈
ここで求めた値は，国内の**都道府県間移動だけ**から計算した純移動である．
国外との移動，同一都道府県内の移動，出生，死亡は含まれない．
都道府県の人口増減そのものと同じではない．
```

---

## 全国の主要な人口移動を可視化する

47都道府県間の2162本のエッジをすべて描くと，線が重なって読めない．
そこで，移動者数が多い上位60本だけを表示する．

これはデータを削除する前処理ではなく，**図で何を見せるかを決める表示上の選択**である．

````{note} 演習5：移動者数上位60組のネットワークを描く

```python
top_edges_df = edge_df.nlargest(60, "移動者数")

top_G = nx.from_pandas_edgelist(
    top_edges_df,
    source="転出元",
    target="転入先",
    edge_attr="移動者数",
    create_using=nx.DiGraph,
)

pos = nx.spring_layout(
    top_G,
    weight="移動者数",
    seed=42,
    k=1.2,
)

edge_weights = [
    top_G[u][v]["移動者数"]
    for u, v in top_G.edges()
]

max_weight = max(edge_weights)
edge_widths = [
    0.5 + 4 * weight / max_weight
    for weight in edge_weights
]

node_values = [
    in_strength[node]
    for node in top_G.nodes()
]

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
plt.show()
```

実行後，次を確認せよ．

1. 多くの太いエッジが集まる都道府県はどこか
2. 首都圏，近畿圏，中京圏にはどのようなまとまりがあるか
3. 双方向に強い移動がある組合せはどこか
4. この図に表示されていない移動が「存在しない」とはいえないのはなぜか
````

```{tip} spring layout
`spring_layout`は，ノード間をばねで結んだように配置するアルゴリズムである．
強く結び付いたノードは近くなりやすいが，図上の位置は実際の地理的位置ではない．
地図とネットワーク図は，表している位置の意味が異なる．
```

---

## 1つの都道府県を中心に詳しく見る

全国図では全体構造を確認できるが，個別の矢印は読み取りにくい．
次に，埼玉県への流入上位5件と，埼玉県からの流出上位5件だけを取り出す．

中心と直接つながる部分ネットワークは，**ego network**と呼ばれる．

````{note} 演習6：埼玉県の人口移動ネットワークを描く

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

**セル2：ego networkを作成する**

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

**セル3：方向と移動者数が分かる図を作る**

```python
edge_colors = [
    "darkorange" if source == target_prefecture else "steelblue"
    for source, target in ego_G.edges()
]

edge_widths = [
    1 + 5 * ego_G[source][target]["移動者数"]
    / ego_edges_df["移動者数"].max()
    for source, target in ego_G.edges()
]

node_colors = [
    "crimson" if node == target_prefecture else "lightgray"
    for node in ego_G.nodes()
]

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
plt.show()
```

実行後，次を確認せよ．

1. 埼玉県からの流出が多い都道府県はどこか
2. 埼玉県への流入が多い都道府県はどこか
3. 同じ相手でも，流入と流出のどちらが多いか
4. 全国図より読み取りやすくなったことは何か
````

---

## PageRankで流入先としての中心性を見る

PageRankは，単に流入量を合計するだけでなく，どのノードから流入しているかも考慮する中心性である．
今回は人口移動の重みを使って計算する．

```{warning} PageRankの意味
PageRankが高いことは，その都道府県が「優れている」ことを意味しない．
このネットワークにおいて，移動先として中心的な位置にあることを表す指標の1つである．
```

````{note} 演習7：重み付きPageRankを計算する

```python
pagerank = nx.pagerank(
    G,
    alpha=0.85,
    weight="移動者数",
)

node_df["PageRank"] = node_df["都道府県"].map(pagerank)

node_df.sort_values("PageRank", ascending=False).head(10)
```

流入者数の順位とPageRankの順位を比較せよ．

```python
comparison_df = node_df[
    ["都道府県", "流入者数", "流出者数", "都道府県間純移動", "PageRank"]
].sort_values("PageRank", ascending=False)

comparison_df.head(10)
```

実行後，次を確認せよ．

1. PageRank上位にはどの都道府県が入っているか
2. 流入者数の上位とPageRankの上位は同じか
3. 人口規模の大きさが結果に影響している可能性はあるか
````

---

## 考察

````{note} 演習8：README.mdに分析結果を整理する

README.mdの「第10回 分析記録」に次の内容を記入せよ．

1. 全国の主要な人口移動は，どの地域に集中していたか
2. 埼玉県と結び付きの強い都道府県はどこか
3. 流入者数，流出者数，純移動，PageRankは，それぞれ何を表すか
4. 全国図とego networkでは，読み取りやすいことがどのように違ったか
5. 今回のデータだけでは説明できないことは何か

考察では，図から観察した事実と，その理由についての推測を分けて書くこと．
````

```{important} この分析だけでは原因は分からない
人口移動には，就職，進学，住宅事情，家族，交通，災害など多くの要因が関係する．
人口移動ネットワークだけから，移動が生じた原因を断定することはできない．
```

---

## 課題

````{warning} 課題1：選択した都道府県のego networkを作成する

埼玉県以外の都道府県を1つ選び，その都道府県への流入上位7件と，その都道府県からの流出上位7件を表示するネットワーク図を作成せよ．

演習6のコードをPythonスクリプトにまとめ，`src/plot_my_prefecture_migration_network.py`を作成すること．

### 条件

1. `target_prefecture`を埼玉県以外に変更する
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

````{warning} 課題2：PageRank上位10都道府県を可視化する

次のコードの`<HOGEHOGE1>`から`<HOGEHOGE5>`を適切に書き換え，Pythonスクリプト`src/plot_migration_pagerank.py`を作成せよ．

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

## まとめ

- 都道府県間人口移動は，重み付き有向ネットワークとして表現できる
- クロス集計表は，転出元，転入先，移動者数を持つ長形式にすると扱いやすい
- すべての異なる都道府県間に移動があるため，エッジの有無より重みが重要である
- 流入者数と流出者数は，重み付き入次数・出次数として計算できる
- 全国図では全体構造，ego networkでは特定地域の関係を詳しく確認できる
- エッジを絞った図では，表示していない関係があることを明記する必要がある
- PageRankはネットワーク上の中心性の1つであり，価値や住みやすさを直接表すものではない
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
都道府県人口のデータを追加し，次のような移動率を計算して可視化せよ．

$$
\text{転出率}
=
\frac{\text{流出者数}}{\text{都道府県人口}}
\times 100
$$

人数で見た順位と，率で見た順位がどのように変わるか比較すること．
````

````{note} 発展問題2：人口移動ネットワークのコミュニティを求める

移動者数の多いエッジだけを残し，有向グラフを無向グラフに変換してコミュニティを求めよ．

`networkx.algorithms.community.greedy_modularity_communities()`などを調べて使用してよい．

得られたコミュニティが，首都圏，近畿圏，中京圏などの地域区分と対応しているか考察すること．
````
