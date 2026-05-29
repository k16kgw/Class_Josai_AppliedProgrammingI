# 第8回　データの可視化

### 前回の復習

- 前処理：取得したデータを**分析しやすい形に整える**作業
- 1つのJSONの中にも，複数の表に相当するデータが入っていることがある
- 横方向の結合は，共通のキーを使って別の列を追加する処理である
- 結合できるかどうかは，列名だけでなく，地域や時刻の意味が一致しているかで判断する
- 結合によって発生する空欄は，必ずしもデータの誤りではない
- データ観察はNotebookで行い，再実行する本処理はPythonファイルとして保存する

前回までは，第5回で取得した気象庁の天気予報JSONを使い，データ取得，前処理，結合，集計用データセットの作成を行った．
今回は，前処理済みデータを使って図を作成し，データ分析を一気通貫で実施する流れの中で，可視化がどのような役割を持つかを学ぶ．

**可視化**：データの傾向，違い，外れた値，時間変化などを図として表現し，人間が理解しやすい形にする作業

可視化は分析結果の飾りではなく，次の問いを確認するための工程である．

- データにどのような傾向があるか
- 地域やカテゴリによって違いがあるか
- 前処理や集計が意図した通りにできているか
- 読み手に誤解なく伝わる図になっているか

### 到達目標

データ分析の一連の流れの中で，可視化を適切に使う方法を学ぶ．

- データ分析の流れの中で，可視化の役割を説明できる
- 図を作る前に，行数，列名，値の範囲を確認できる
- 目的に応じて棒グラフなどの図を選択できる
- Pythonの `matplotlib` を使って図を作成できる
- 図のタイトル，軸ラベル，凡例，単位を適切に設定できる
- 作成した図を画像ファイルとして保存できる
- 図から読み取れることと，読み取れないことを文章で説明できる

### 準備

<span style="color:red">今回は第5回で作成したフォルダ `5` 内で作業を続ける．</span>

第7回までに作成した次のファイルを使う．

```text
5/data/processed/jma_tokyo_weather_pop_clean.csv
5/data/processed/weather_summary_by_area.csv
```

````{note} 演習0：作業フォルダとデータを確認する

1. 第5回で作成した `/User/<ユーザ名>/applied_programming_i/5` を開く．
2. 次のディレクトリ構成になっているか確認する．

```text
5/
├── notebooks/
│   ├── preprocessing1.ipynb
│   ├── preprocessing2.ipynb
│   └── visualization.ipynb
├── data/
│   ├── raw/
│   └── processed/
│       ├── jma_tokyo_weather_pop_clean.csv
│       └── weather_summary_by_area.csv
├── reports/
│   └── figures/
├── src/
└── README.md
```

3. `notebooks/`，`reports/figures/`，`src/` がない場合は作成する．
4. JupyterLabまたはVS Codeで `notebooks/visualization.ipynb` を新規作成する．
5. 第7回で `data/processed/jma_tokyo_weather_pop_clean.csv` と `data/processed/weather_summary_by_area.csv` を作成していない場合は，第7回のスクリプトを実行する．
6. `README.md` に次の内容を追記する．

```markdown
## 第8回 可視化記録

- 元データ：
  - data/processed/jma_tokyo_weather_pop_clean.csv
  - data/processed/weather_summary_by_area.csv
- 観察用ノートブック：notebooks/visualization.ipynb（Gitでは管理しない）
- 可視化スクリプト：
  - src/plot_weather_summary.py
  - src/plot_pop_by_time.py
- 出力した図：
  - reports/figures/weather_summary_by_area.png
  - reports/figures/pop_by_time.png
- 可視化の目的：
  - 地域別・天気カテゴリ別の件数を比較する
  - 降水確率が付いている予報時刻と値を確認する
```

7. `.gitignore` に次の記述があることを確認する．

```gitignore
# Jupyter Notebook
.ipynb_checkpoints
*.ipynb
```
````
---

## データ分析の流れと可視化

データ分析の流れは次のように考えられる．

```text
データ取得 → 前処理 → 集計 → 可視化 → 分析 → 報告
```

可視化は，集計後に図を作るだけの作業ではない．
分析の途中でデータを眺め，前処理や集計が正しくできているかを確認するためにも使う．

### 可視化で確認すること

- 値の大きさの違い
- 地域やカテゴリごとの差
- 時間に沿った変化
- 欠損値や空欄の影響
- 分析結果を説明するために必要な図かどうか

### 図を作る前に考えること

図を作る前に，次を決める．

- 何を比較したいのか
- 横軸に何を置くのか
- 縦軸に何を置くのか
- 色や凡例で何を表すのか
- 図を見た人に何を読み取ってほしいのか

```{tip} 注意
図はきれいに作ることが目的ではない．
問いに対して，データから分かることを誤解なく伝えることが目的である．
```

---

## 使用するデータ

今回は，第7回で作成した前処理済みデータと集計データを使う．

### 前処理済みデータ

```text
data/processed/jma_tokyo_weather_pop_clean.csv
```

主な列：

- `地域名`
- `地域コード`
- `予報時刻`
- `予報日`
- `予報時`
- `天気`
- `天気カテゴリ`
- `降水確率`

### 集計データ

```text
data/processed/weather_summary_by_area.csv
```

主な列：

- `地域名`
- `天気カテゴリ`
- `件数`
- `降水確率あり件数`
- `平均降水確率`

```{tip} 注意
今回のデータは，短期予報JSONから作成した小さなデータである．
したがって，図から大きな一般法則を読み取るのではなく，前処理済みデータを可視化する手順を学ぶことを目的とする．
```

---

## 可視化の準備

Pythonで図を作成するために，`matplotlib` を使う．

````{note} 演習1：matplotlibを確認する
`notebooks/visualization.ipynb` に「可視化の準備」という見出しを作り，次のセルを順番に実行せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

**セル2：matplotlibを読み込む**

```python
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Hiragino Sans"
```

**セル3：簡単な図を作る**

```python
fig, ax = plt.subplots()

ax.bar(["A", "B", "C"], [3, 1, 2])
ax.set_title("棒グラフの確認")
ax.set_xlabel("カテゴリ")
ax.set_ylabel("件数")

plt.show()
```

実行後，次を確認せよ．

1. 図が表示されたか
2. 日本語のタイトルや軸ラベルが表示されたか
3. 日本語が文字化けした場合，どのように見えるか
````

```{tip} 注意
日本語が正しく表示されない場合は，授業環境のフォント設定によって文字化けしている可能性がある．
Macでは `Hiragino Sans` を指定すると表示できることが多い．
```

---

## 図を作る前にデータを確認する

図を作る前に，行数，列名，値の例を確認する．
データの形を確認しないまま図を作ると，意図しない列を使ったり，空欄を含んだまま計算したりする可能性がある．

````{note} 演習2：可視化に使うデータを確認する
`notebooks/visualization.ipynb` に「可視化に使うデータを確認する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：CSVを読み込む**（`<HOGE>`には適切なディレクトリを指定すること）

```python
import csv

summary_path = "<HOGE>/weather_summary_by_area.csv"
weather_path = "<HOGE>/jma_tokyo_weather_pop_clean.csv"

with open(summary_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    summary_rows = list(reader)
    summary_fieldnames = reader.fieldnames

with open(weather_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    weather_rows = list(reader)
    weather_fieldnames = reader.fieldnames
```

**セル2：行数と列名を確認する**

```python
print("集計データの行数:", len(summary_rows))
print("集計データの列名:", summary_fieldnames)
print("前処理済みデータの行数:", len(weather_rows))
print("前処理済みデータの列名:", weather_fieldnames)
```

**セル3：値の例を確認する**

```python
print("集計データの先頭3行:")
for row in summary_rows[:3]:
    print(row)

print("前処理済みデータの先頭3行:")
for row in weather_rows[:3]:
    print(row)
```

実行後，次を確認せよ．

1. 集計データにはどのような列があるか
2. 前処理済みデータにはどのような列があるか
3. `件数` や `降水確率` は文字列として読み込まれているか
````

---

## 地域別・天気カテゴリ別の件数を可視化する

まず，地域ごとに天気カテゴリの件数を比較する．
この目的には，**棒グラフ**が向いている．

### 棒グラフが向いている場合

- 地域ごとの件数を比較する
- カテゴリごとの数を比較する
- 大きい・小さいの違いを見たい

ここでは，地域ごとに棒を立て，天気カテゴリを色で分けた積み上げ棒グラフを作成する．

````{note} 演習3：地域別・天気カテゴリ別の棒グラフを作成する
`notebooks/visualization.ipynb` に「地域別・天気カテゴリ別の棒グラフ」という見出しを作り，次のセルを順番に実行せよ．

**セル1：集計データを図に使いやすい形へ変換する**

```python
summary = {}
areas = []
categories = []

for row in summary_rows:
    area = row["地域名"]
    category = row["天気カテゴリ"]
    count = int(row["件数"])

    summary[(area, category)] = count

    if area not in areas:
        areas.append(area)
    if category not in categories:
        categories.append(category)

print("地域:", areas)
print("カテゴリ:", categories)
```

**セル2：積み上げ棒グラフを作成する**

```python
fig, ax = plt.subplots(figsize=(8, 5))

bottoms = [0] * len(areas)

for category in categories:
    values = [summary.get((area, category), 0) for area in areas]
    ax.bar(areas, values, bottom=bottoms, label=category)
    bottoms = [bottom + value for bottom, value in zip(bottoms, values)]

ax.set_title("地域別・天気カテゴリ別の件数")
ax.set_xlabel("地域")
ax.set_ylabel("件数")
ax.legend(title="天気カテゴリ")

plt.xticks(rotation=20)
plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 地域ごとに棒が表示されているか
2. 天気カテゴリごとに色が分かれているか
3. タイトル，軸ラベル，凡例は読みやすいか
4. 図からどの地域にどの天気カテゴリが多いと読み取れるか
````

````{warning} 課題1：地域別・天気カテゴリ別の図をPythonファイルで作成する
演習3で確認した内容をもとに，`src/plot_weather_summary.py` を作成せよ．
次のコードの `<FUGAFUGA>` と `<HOGEHOGE>` を適切に置き換え，`reports/figures/weather_summary_by_area.png` を作成すること．

```python
import csv
from pathlib import Path

import matplotlib.pyplot as plt

input_path = "data/processed/weather_summary_by_area.csv"
output_path = "reports/figures/weather_summary_by_area.png"

plt.rcParams["font.family"] = "Hiragino Sans"
Path("reports/figures").mkdir(parents=True, exist_ok=True)

summary = {}
areas = []
categories = []

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        area = row["地域名"]
        category = row["天気カテゴリ"]
        count = int(row["件数"])

        <FUGAFUGA>

fig, ax = plt.subplots(figsize=(8, 5))

bottoms = [0] * len(areas)

for category in categories:
    values = [summary.get((area, category), 0) for area in areas]
    ax.bar(areas, values, bottom=bottoms, label=category)
    bottoms = [bottom + value for bottom, value in zip(bottoms, values)]

ax.set_title("地域別・天気カテゴリ別の件数")
ax.set_xlabel("地域")
ax.set_ylabel("件数")
ax.legend(title="天気カテゴリ")

plt.xticks(rotation=20)
plt.tight_layout()
<HOGEHOGE>

print("saved:", output_path)
```

作成したPythonファイルをターミナルで実行せよ．

```bash
python src/plot_weather_summary.py
```

次のファイルをWebClass「第8回課題」問1・問2から提出せよ．

1. `src/plot_weather_summary.py`
2. `reports/figures/weather_summary_by_area.png`
````

<!--
summary[(area, category)] = count

if area not in areas:
    areas.append(area)
if category not in categories:
    categories.append(category)

plt.savefig(output_path, dpi=150)
-->

---

## 降水確率を可視化する

次に，降水確率が入っている行だけを取り出し，予報時刻ごとの降水確率を確認する．
降水確率は0から100までの値であり，値の大小を比較したいので棒グラフで表す．

```{tip} 注意
第7回で確認したように，天気表と降水確率表は予報時刻が完全には一致しない．
そのため，結合後のデータには `降水確率` が空欄の行がある．
可視化するときは，空欄の行をどう扱ったかを説明できるようにする．
```

````{note} 演習4：降水確率がある行だけを取り出す
`notebooks/visualization.ipynb` に「降水確率を可視化する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：降水確率がある行だけを取り出す**

```python
pop_rows = []

for row in weather_rows:
    if row["降水確率"] != "":
        pop_rows.append(row)

pop_rows.sort(key=lambda row: (row["予報時刻"], row["地域名"]))

print("降水確率がある行数:", len(pop_rows))
pop_rows
```

**セル2：図に使うラベルと値を作る**

```python
labels = []
values = []

for row in pop_rows:
    label = row["地域名"] + "\n" + row["予報日"] + " " + row["予報時"]
    labels.append(label)
    values.append(int(row["降水確率"]))

print(labels)
print(values)
```

**セル3：降水確率の棒グラフを作成する**

```python
fig, ax = plt.subplots(figsize=(9, 5))

ax.bar(labels, values)
ax.set_title("予報時刻別の降水確率")
ax.set_xlabel("地域・予報時刻")
ax.set_ylabel("降水確率（%）")
ax.set_ylim(0, 100)

plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. `降水確率` が空欄の行を除外できているか
2. 縦軸は0から100になっているか
3. 横軸のラベルは読みやすいか
4. 図からどの地域・時刻の降水確率が高いと読み取れるか
````

````{warning} 課題2：降水確率の図をPythonファイルで作成する
演習4で確認した内容をもとに，`src/plot_pop_by_time.py` を作成せよ．
次のコードの `<FUGAFUGA>` と `<HOGEHOGE>` を適切に置き換え，`reports/figures/pop_by_time.png` を作成すること．

```python
import csv
from pathlib import Path

import matplotlib.pyplot as plt

input_path = "data/processed/jma_tokyo_weather_pop_clean.csv"
output_path = "reports/figures/pop_by_time.png"

plt.rcParams["font.family"] = "Hiragino Sans"
Path("reports/figures").mkdir(parents=True, exist_ok=True)

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

pop_rows = []

<FUGAFUGA>

labels = []
values = []

for row in pop_rows:
    label = row["地域名"] + "\n" + row["予報日"] + " " + row["予報時"]
    labels.append(label)
    values.append(int(row["降水確率"]))

fig, ax = plt.subplots(figsize=(9, 5))

ax.bar(labels, values)
ax.set_title("予報時刻別の降水確率")
ax.set_xlabel("地域・予報時刻")
ax.set_ylabel("降水確率（%）")
ax.set_ylim(0, 100)

plt.xticks(rotation=30, ha="right")
plt.tight_layout()
<HOGEHOGE>

print("saved:", output_path)
```

作成したPythonファイルをターミナルで実行せよ．

```bash
python src/plot_pop_by_time.py
```

次のファイルをWebClass「第8回課題」問3・問4から提出せよ．

1. `src/plot_pop_by_time.py`
2. `reports/figures/pop_by_time.png`
````

<!--
for row in rows:
    if row["降水確率"] != "":
        pop_rows.append(row)

pop_rows.sort(key=lambda row: (row["予報時刻"], row["地域名"]))

plt.savefig(output_path, dpi=150)
-->

---

## 図から読み取れることを書く

図を作成したら，図から読み取れることを文章で説明する．
このとき，図から読み取れることと，読み取れないことを分けて書くことが重要である．

### 読み取れることの例

- どの地域でどの天気カテゴリが多いか
- 降水確率が高い地域・時刻はどこか
- 空欄を除外した図であること

### 読み取れないことの例

- 長期的な天気の傾向
- 東京都全体の気候の特徴
- 他の日にも同じ傾向があるかどうか

今回のデータは，取得時点の短期予報から作成した小さなデータである．
そのため，図から読み取れることは，このデータの範囲に限定して説明する．

````{warning} 課題3：可視化結果を文章で説明する
README.mdに次の見出しを追加し，作成した2つの図から読み取れることを記述せよ．

```markdown
## 第8回 可視化結果の考察

### 地域別・天気カテゴリ別の件数

- 図から読み取れること：
- 注意点：

### 予報時刻別の降水確率

- 図から読み取れること：
- 注意点：
```

次の内容をWebClass「第8回課題」問5から提出せよ．

1. README.mdに追記した「第8回 可視化結果の考察」
````

---

## 誤解の少ない図にする

図を作るときは，見た目だけでなく，読み手が誤解しないかを確認する．

### 確認すること

- タイトルは図の内容を表しているか
- 横軸と縦軸にラベルがあるか
- 単位が必要な場合，単位が書かれているか
- 凡例は必要か
- 不要な装飾で値が読みにくくなっていないか
- 空欄や欠損値をどう扱ったか説明できるか
- 図から読み取れる範囲を超えて説明していないか

### 避けたい図

- 軸ラベルがない図
- 単位が分からない図
- 色の意味が分からない図
- 必要以上に立体的な図
- 0から始めるべき棒グラフの縦軸を途中から始めた図
- 小さなデータから大きな結論を述べてしまう図

---

## Git管理と可視化

可視化では，図そのものだけでなく，図を作る手順も残すことが重要である．

Gitで管理するとよいものは次の通りである．

- 可視化スクリプト（`src/*.py`）
- README
- 小さな集計データ
- 最終的に提出する図

一方，作業用NotebookはGitで管理しない．
Notebookで試行錯誤し，最終的に再実行できる処理をPythonファイルとして残す．

今回の処理の流れは，次のように表せる．

```text
data/processed/weather_summary_by_area.csv
  ↓
  ↓ notebooks/visualization.ipynbで図を確認
  ↓ src/plot_weather_summary.py
  ↓
reports/figures/weather_summary_by_area.png

data/processed/jma_tokyo_weather_pop_clean.csv
  ↓
  ↓ notebooks/visualization.ipynbで図を確認
  ↓ src/plot_pop_by_time.py
  ↓
reports/figures/pop_by_time.png
```

---

## まとめ

- 可視化は，データ分析の流れの中で，データの傾向や違いを確認し，結果を伝えるための工程である
- 図を作る前には，行数，列名，値の例，空欄の有無を確認する
- 件数やカテゴリの比較には棒グラフが使いやすい
- 図には，タイトル，軸ラベル，単位，凡例を適切に設定する
- 空欄を除外した場合は，その処理を説明できるようにする
- 図から読み取れることと，読み取れないことを分けて文章にする
- データ観察はNotebookで行い，再実行する本処理はPythonファイルとして保存する

次回は統計的な要約を扱う．

- 可視化で確認した傾向を，平均，分散，相関などの数値で要約する方法を学ぶ
- 図と数値を組み合わせて，データの特徴を説明する

### 課題の提出期限

<span style="color: red; ">6月9日(火)23:59まで</span>

---

## 自主学習用の発展問題

````{note} 発展課題1：横棒グラフに変更する

`weather_summary_by_area.png` を縦棒グラフではなく横棒グラフとして作成せよ．

次の問いに答えよ．

1. 横棒グラフにすると，地域名は読みやすくなるか
2. 縦棒グラフと横棒グラフのどちらが今回のデータに合っているか
3. その理由は何か
````

````{note} 発展課題2：色の順番を固定する

天気カテゴリの色が実行のたびに変わらないように，カテゴリの順番を自分で指定せよ．

例：

```python
categories = ["晴", "くもり", "雨", "雪", "その他"]
```

次の問いに答えよ．

1. 色の順番が固定されると，複数の図を比較しやすくなるか
2. 存在しないカテゴリを指定した場合，図はどうなるか
3. 凡例の順番は読みやすいか
````

````{note} 発展課題3：図の説明文を改善する

README.mdに書いた可視化結果の考察を読み直し，次の点を改善せよ．

1. 図から読み取れる事実と，自分の解釈が分かれているか
2. データの範囲を超えた説明になっていないか
3. 空欄を除外した処理について説明しているか
````
