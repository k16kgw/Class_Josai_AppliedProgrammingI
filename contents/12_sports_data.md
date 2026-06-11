# 第12回　データ分析実践III：スポーツデータ

### 前回の復習

- 経済データでは，単位に加えて基準年を確認する
- 時系列データは，日付型に変換し，時間順に並べてから可視化する
- 同じ時点の行が重複していないかを確認する
- 水準（指数）と変化率（前年同月比）は同じデータの別の見方である

### 今回の位置づけ

第12回では**スポーツデータ**を扱う．
スポーツデータは，試合結果，チーム成績，選手成績など，**集計や比較に向いた**データが多い．

データ分析実践の最終回として，テーマ設定からデータ取得・前処理・集計・可視化・考察までを扱い，最終レポートで必要になる「図表と文章で説明する」力を確認する．

### 到達目標

GitHub上で公開されている国際サッカー試合結果のデータを使い，日本代表の成績の変化とホームアドバンテージを分析する．

- スポーツデータを使った分析テーマを設定できる
- GitHub上で公開されているオープンデータを取得し，ライセンスを確認できる
- 条件を組み合わせた行の抽出（日本代表の試合の抽出）ができる
- 行ごとの条件から新しい列（勝ち・負け・引き分け）を作成できる
- グループ別集計を使って，年代別・条件別の成績を比較できる
- 分析結果を，図表と文章を組み合わせて説明できる

### 準備

````{note} 演習0：作業フォルダを作成する

1. ターミナルで次のコマンドを順に実行する．

```bash
cd /User/<ユーザ名>/applied_programming_i
mkdir 12
cd 12
mkdir -p notebooks data/raw data/processed src reports/figures
git init
```

2. `README.md`を作成し，次の内容を記入する．

```markdown
# 応用プログラミングI 第12回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

国際サッカー試合結果のデータを使い，日本代表の成績の変化とホームアドバンテージを可視化する．

## 第12回 分析記録

- テーマ：日本代表は強くなったのか／ホームで戦うと有利なのか
- 元データ：data/raw/international_results.csv（国際サッカー試合結果，1872年〜）
- 出典：GitHub リポジトリ martj42/international_results
- URL：https://github.com/martj42/international_results
- ライセンス：CC0 1.0（パブリックドメイン）
- 観察用ノートブック：notebooks/sports_data.ipynb（Gitでは管理しない）
- 作成するスクリプト：
  - src/plot_japan_decade_winrate.py
  - src/plot_home_advantage.py
- 作成するデータ：
  - data/processed/japan_results.csv
- 出力する図：
  - reports/figures/japan_decade_winrate.png
  - reports/figures/home_advantage.png
```

3. `.gitignore`を作成し，次の内容を記入する（第9回と同じ）．

```gitignore
.DS_Store
*.swp
*~
.vscode/
.ipynb_checkpoints
*.ipynb
data/raw/
```

4. 作成したファイルをコミットする．

```bash
git add .
git commit -m "first commit"
```

5. JupyterLabまたはVS Codeで`notebooks/sports_data.ipynb`を新規作成する．
````

---

## テーマ設定

スポーツデータでは，次のような問いを立てることができる．

| 観点 | 問いの例 |
| --- | --- |
| チーム比較 | 得点が多いチームと少ないチームにはどのような違いがあるか |
| 時間変化 | チームの成績は年代とともにどのように変化したか |
| 条件比較 | ホームとアウェイで成績に違いはあるか |
| 分布 | 得点はどのような分布をしているか |

ランキングを作るだけでなく，**分布や関係を見る**ことが重要である．
上位だけに注目すると，全体の傾向を見落とすことがある．

今回は次の2つの問いを扱う．

> **問い1：日本代表の成績は年代とともに良くなっているか．**  
> **問い2：ホームで戦うチームは本当に有利なのか．**

問い1は「時間変化」型，問い2は「条件比較」型の問いである．

---

## 使用するデータ：国際サッカー試合結果

今回は，GitHub上で公開されているオープンデータを使う．

| 項目 | 内容 |
| --- | --- |
| データ名 | International football results from 1872 to 2026 |
| 公開場所 | GitHub リポジトリ `martj42/international_results` |
| 内容 | 1872年以降の男子サッカー国際Aマッチ約49,000試合の結果 |
| ライセンス | CC0 1.0（出典表記なしでも利用できるが，記載するのが望ましい） |
| 形式 | CSV |

```{tip} GitHubで公開されるオープンデータ
オープンデータは政府のポータルだけでなく，GitHub上でも数多く公開されている．
GitHubで管理されているデータは，**変更履歴が残る**・**誰がいつ更新したか分かる**という利点がある．
これはまさに本講義で学んできたGitの仕組みである．
利用するときは，リポジトリの`README`と`LICENSE`を必ず確認すること．
```

`results.csv`の列は次の通りである．

| 列名 | 内容 |
| --- | --- |
| `date` | 試合日 |
| `home_team` | ホームチーム名 |
| `away_team` | アウェイチーム名 |
| `home_score` | ホームチームの得点（90分＋延長．PK戦は含まない） |
| `away_score` | アウェイチームの得点 |
| `tournament` | 大会名（`Friendly`は親善試合） |
| `city` | 開催都市 |
| `country` | 開催国 |
| `neutral` | 中立地開催かどうか（`True`/`False`） |

````{note} 演習1：データを取得する
`notebooks/sports_data.ipynb`に「データの取得」という見出しを作り，次のセルを順番に実行せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

**セル2：必要なライブラリをインストールする**

```bash
!python -m pip install requests pandas seaborn matplotlib
```

**セル3：GitHubからCSVを取得して保存する**

GitHub上のファイルは，`raw.githubusercontent.com`から始まるURLで**ファイルそのもの**を取得できる．

```python
from pathlib import Path

import requests

csv_url = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

response = requests.get(csv_url)
response.raise_for_status()

Path("../data/raw").mkdir(parents=True, exist_ok=True)

with open("../data/raw/international_results.csv", "w", encoding="utf-8") as f:
    f.write(response.text)

print("saved: ../data/raw/international_results.csv")
```

実行後，次を確認せよ．

1. `data/raw/international_results.csv`が作成されたか
2. README.mdの分析記録に取得日をメモしたか
````

データが取得できない場合は，次のリンクからダウンロード・解凍して`data/raw`に配置すること．

- [international_results_csv.zip](./analysis/12/data/raw/international_results_csv.zip)

````{note} 演習2：データの形を確認する
「データの確認」という見出しを作り，次のセルを順番に実行せよ．

**セル1：CSVを読み込んで先頭行を確認する**

```python
import pandas as pd

results_df = pd.read_csv("../data/raw/international_results.csv")

print("行数・列数:", results_df.shape)
results_df.head()
```

**セル2：列の型と欠損を確認する**

```python
results_df.info()
```

```python
results_df.isna().sum()
```

**セル3：大会名の内訳を確認する**

```python
results_df["tournament"].value_counts().head(10)
```

実行後，次を確認せよ．

1. 何試合分のデータが入っているか
2. 得点（`home_score`，`away_score`）に欠損はあるか
3. 欠損があるのはどのような試合か（`results_df[results_df["home_score"].isna()]`で確認せよ．
   このデータには**開催予定でまだ結果が出ていない試合**も含まれている）
4. 最も多い大会の種類は何か
````

---

## 前処理

````{note} 演習3：分析に使う表を作る
「前処理」という見出しを作り，次のセルを順番に実行せよ．

**セル1：日付の変換と列の追加を行う**

- 試合日を日付型に変換し，`年`列を作る
- 得点が欠損している行（結果が出ていない試合）を除外する
- 1試合の合計得点`総得点`列を作る

```python
results_df["date"] = pd.to_datetime(results_df["date"])
results_df["年"] = results_df["date"].dt.year

results_df = results_df.dropna(subset=["home_score", "away_score"]).copy()
results_df["総得点"] = results_df["home_score"] + results_df["away_score"]

print("前処理後の行数:", len(results_df))
print("期間:", results_df["年"].min(), "〜", results_df["年"].max())
```

**セル2：日本代表の試合を取り出す**

ホームまたはアウェイのどちらかが`Japan`の試合を取り出す．
`|`は「または」を表す（第6回の復習）．

```python
japan_df = results_df[
    (results_df["home_team"] == "Japan") | (results_df["away_team"] == "Japan")
].copy()

print("日本代表の試合数:", len(japan_df))
japan_df.head()
```

**セル3：日本から見た勝敗の列を作る**

日本がホームかアウェイかで得点差の向きが変わるため，行ごとに判定する関数を作って`apply()`で適用する．

```python
def japan_result(row):
    """日本から見た勝敗を返す．"""
    if row["home_team"] == "Japan":
        diff = row["home_score"] - row["away_score"]
    else:
        diff = row["away_score"] - row["home_score"]

    if diff > 0:
        return "勝ち"
    elif diff < 0:
        return "負け"
    else:
        return "引き分け"


japan_df["結果"] = japan_df.apply(japan_result, axis=1)

japan_df[["date", "home_team", "away_team", "home_score", "away_score", "結果"]].head()
```

**セル4：CSVに保存する**

```python
output_path = "../data/processed/japan_results.csv"

japan_df.to_csv(output_path, index=False)

print("saved:", output_path)
```

実行後，次を確認せよ．

1. 日本代表の試合は何試合あるか
2. `結果`列の判定は正しいか（先頭の数行を手で確かめよ）
3. `data/processed/japan_results.csv`が作成されたか
````

---

## 集計と可視化

### 問い1：日本代表は強くなったのか

````{note} 演習4：年代別の勝率を可視化する
「集計と可視化」という見出しを作り，次のセルを順番に実行せよ．

**セル1：ライブラリを読み込む**

```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
```

**セル2：全期間の結果を集計する**

```python
japan_df["結果"].value_counts()
```

**セル3：年代別に勝率を集計する**

10年区切りの`年代`列を作り（例：2014年 → 2010年代），年代ごとに試合数と勝利数を集計する．

```python
japan_df["年代"] = (japan_df["年"] // 10) * 10
japan_df["勝利"] = (japan_df["結果"] == "勝ち").astype(int)

decade_df = (
    japan_df.groupby("年代", as_index=False)
    .agg(
        試合数=("勝利", "count"),
        勝利数=("勝利", "sum"),
    )
)

decade_df["勝率"] = decade_df["勝利数"] / decade_df["試合数"]

decade_df
```

**セル4：年代別の勝率を折れ線グラフにする**

```python
fig, ax = plt.subplots(figsize=(8, 5))

sns.lineplot(data=decade_df, x="年代", y="勝率", marker="o", ax=ax)

ax.set_title("日本代表の年代別勝率")
ax.set_xlabel("年代")
ax.set_ylabel("勝率")
ax.set_ylim(0, 1)

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 勝率が最も低い年代・高い年代はいつか
2. 年代によって試合数に大きな差はあるか（試合数が少ない年代の勝率は信頼できるか）
3. 「勝率が上がった＝強くなった」と言い切ってよいか（対戦相手の強さはこの集計に含まれているか）
````

### 問い2：ホームは本当に有利なのか

````{note} 演習5：ホームアドバンテージを可視化する
次のセルを順番に実行せよ．

**セル1：中立地開催を除いて平均得点を集計する**

中立地（`neutral`が`True`）の試合では「ホーム」に意味がないため除外する．

```python
not_neutral_df = results_df[results_df["neutral"] == False]

home_mean = not_neutral_df["home_score"].mean()
away_mean = not_neutral_df["away_score"].mean()

print("対象試合数:", len(not_neutral_df))
print("ホームチームの平均得点:", round(home_mean, 2))
print("アウェイチームの平均得点:", round(away_mean, 2))
```

**セル2：棒グラフで比較する**

```python
home_away_df = pd.DataFrame({
    "種類": ["ホーム", "アウェイ"],
    "平均得点": [home_mean, away_mean],
})

fig, ax = plt.subplots(figsize=(5, 5))

sns.barplot(data=home_away_df, x="種類", y="平均得点", ax=ax)

ax.set_title("ホームとアウェイの平均得点（中立地を除く全試合）")
ax.set_xlabel("")
ax.set_ylabel("平均得点")

plt.tight_layout()
plt.show()
```

**セル3：総得点の分布をヒストグラムで見る**

```python
fig, ax = plt.subplots(figsize=(7, 4))

sns.histplot(data=results_df, x="総得点", bins=range(0, 15), ax=ax)

ax.set_title("1試合の総得点の分布（全試合）")
ax.set_xlabel("総得点")
ax.set_ylabel("試合数")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. ホームとアウェイの平均得点にどの程度の差があるか
2. 1試合の総得点として最も多いのは何点か
3. 平均得点の差だけから「ホームが有利」と結論してよいか（他にどのような確認があり得るか）
````

````{note} 演習6：考察を書く
README.mdの分析記録に，図から読み取れることを次の形で整理して記入せよ．

1. 問い1について：年代別勝率から何が読み取れるか．試合数や対戦相手を考えると，何がまだ言えないか
2. 問い2について：ホームとアウェイの平均得点の差から何が読み取れるか
3. このデータだけでは判断できないことは何か
````

````{warning} 課題1：年代別勝率をPythonファイルで可視化する
演習4で確認した内容を応用する．
以下のコードの`<FUGAFUGA>`，`<HOGEHOGE1>`，`<HOGEHOGE2>`を適切に書き換えてpythonスクリプト`src/plot_japan_decade_winrate.py`を作成し，コードを実行して画像ファイル`reports/figures/japan_decade_winrate.png`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_japan_decade_winrate.py`と画像ファイル`reports/figures/japan_decade_winrate.png`を<span style="color:red">WebClass「第12回課題」問1・問2</span>から提出せよ．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

input_path = "data/processed/japan_results.csv"
output_path = "reports/figures/japan_decade_winrate.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

japan_df = pd.read_csv(input_path)

japan_df["年代"] = (japan_df["年"] // 10) * 10
japan_df["勝利"] = (japan_df["結果"] == <FUGAFUGA>).astype(int)

decade_df = (
    japan_df.groupby("年代", as_index=False)
    .agg(
        試合数=("勝利", "count"),
        勝利数=("勝利", "sum"),
    )
)

decade_df["勝率"] = decade_df[<HOGEHOGE1>] / decade_df[<HOGEHOGE2>]

print(decade_df)

fig, ax = plt.subplots(figsize=(8, 5))

sns.lineplot(data=decade_df, x="年代", y="勝率", marker="o", ax=ax)

ax.set_title("日本代表の年代別勝率")
ax.set_xlabel("年代")
ax.set_ylabel("勝率")
ax.set_ylim(0, 1)

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```

作成したPythonファイルを`12`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_japan_decade_winrate.py
```

実行後，`reports/figures/japan_decade_winrate.png`が作成されていることを確認せよ．
````

<!--
````{dropdown} 解答例
- `<FUGAFUGA>`：`"勝ち"`
- `<HOGEHOGE1>`：`"勝利数"`
- `<HOGEHOGE2>`：`"試合数"`
````
-->

````{warning} 課題2：ホームアドバンテージをPythonファイルで可視化する
演習5で確認した内容を応用する．
以下のコードの`<HOGEHOGE1>`〜`<HOGEHOGE3>`を適切に書き換えてpythonスクリプト`src/plot_home_advantage.py`を作成し，コードを実行して画像ファイル`reports/figures/home_advantage.png`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_home_advantage.py`と画像ファイル`reports/figures/home_advantage.png`を<span style="color:red">WebClass「第12回課題」問3・問4</span>から提出せよ．

本課題は，元データ`data/raw/international_results.csv`の全試合（中立地を除く）を対象とする．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

input_path = "data/raw/international_results.csv"
output_path = "reports/figures/home_advantage.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

results_df = pd.read_csv(input_path)
results_df = results_df.dropna(subset=["home_score", "away_score"])

not_neutral_df = results_df[results_df["neutral"] == <HOGEHOGE1>]

home_mean = not_neutral_df[<HOGEHOGE2>].mean()
away_mean = not_neutral_df[<HOGEHOGE3>].mean()

print("対象試合数:", len(not_neutral_df))
print("ホーム平均得点:", round(home_mean, 2))
print("アウェイ平均得点:", round(away_mean, 2))

home_away_df = pd.DataFrame({
    "種類": ["ホーム", "アウェイ"],
    "平均得点": [home_mean, away_mean],
})

fig, ax = plt.subplots(figsize=(5, 5))

sns.barplot(data=home_away_df, x="種類", y="平均得点", ax=ax)

ax.set_title("ホームとアウェイの平均得点（中立地を除く全試合）")
ax.set_xlabel("")
ax.set_ylabel("平均得点")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```

作成したPythonファイルを`12`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_home_advantage.py
```

実行後，次の点を確認せよ．

1. ホームとアウェイの平均得点の差はどの程度か
2. この差の理由として，どのような仮説が考えられるか（応援，移動の疲れ，気候など）
3. 仮説を確かめるには，さらにどのようなデータが必要か
````

<!--
````{dropdown} 解答例
- `<HOGEHOGE1>`：`False`
- `<HOGEHOGE2>`：`"home_score"`
- `<HOGEHOGE3>`：`"away_score"`
````
-->

---

## 最終レポートへの接続

第13回は休講とし，各自で最終レポートを作成する（詳細は第13回のページを参照）．
最終レポートでは，各自でデータを選び，**データ取得 → 前処理 → 集計 → 可視化 → 考察**を一気通貫で行う．

第9回から第12回で扱った流れが，そのままレポートの雛形になる．

| 項目 | レポートで書くこと | 講義での例 |
| --- | --- | --- |
| テーマ | 何を明らかにしたいか（図にできる問い） | ホームは本当に有利なのか |
| データ | 名称・出典・URL・取得日・ライセンス | GitHub `martj42/international_results`，CC0 |
| 前処理 | どの列を使い，どのように整形したか | 日付変換，欠損の除外，勝敗列の作成 |
| 可視化 | どの図を作り，何を比較したか | 年代別勝率の折れ線，平均得点の棒グラフ |
| 考察 | 図から何が読み取れるか | ホームの平均得点はアウェイより高い |
| 限界 | この分析だけでは何が言えないか | 差の**原因**までは分からない |
| 再現性 | スクリプト・図・README・フォルダ構成 | `src/`，`reports/figures/`，README.md |

データのテーマは自由である（行政統計，気象，交通，経済，感染症，スポーツなど）．
第13回のページに，これまで使ったデータソースの一覧と選び方の注意をまとめてある．

---

## まとめ

- スポーツデータでは，ランキングだけでなく，分布や時間変化を見ることが重要である
- GitHub上のオープンデータは，`raw.githubusercontent.com`のURLでファイルを直接取得できる．`README`と`LICENSE`を必ず確認する
- 結果が出ていない試合のように，**欠損には理由がある**．理由を確認してから除外する
- 行ごとの条件判定で新しい列を作るときは，関数を定義して`apply()`を使う
- グループ別集計（年代別・条件別）は`groupby()`と`agg()`で行う
- 「勝率が上がった＝強くなった」のように，集計結果を**過度に一般化しない**．言えることと言えないことを分けて書く

次回（第13回）は休講とし，各自で最終レポートを作成する．

### 課題の提出期限

<span style="color: red; ">7月7日(火)23:59まで</span>

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所から提出したものについて加点対象とします．

````{note} 課題3：日本代表の対戦相手トップ10を可視化する

`japan_results.csv`を使い，日本代表の対戦回数が多い相手チーム上位10を棒グラフで表示せよ．
日本がホームの試合では`away_team`が，アウェイの試合では`home_team`が対戦相手であることに注意すること．

`src/plot_japan_opponents.py`を作成し，WebClass「第12回課題」問5から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 対戦回数が多いのはどの国・地域か
2. 地理的にどのような傾向があるか
3. 2つの列から対戦相手の一覧をどのように作ったか
````

````{note} 課題4：ワールドカップ本大会の得点の変化を可視化する

`tournament`が`FIFA World Cup`の試合だけを取り出し，大会年ごとの1試合平均総得点を折れ線グラフで表示せよ．

`src/plot_worldcup_goals.py`を作成し，WebClass「第12回課題」問6から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 平均総得点が最も高かった大会はいつか
2. 長期的に得点は増えているか減っているか
3. その理由としてどのような仮説が考えられるか
````

````{note} 課題5：好きな国で同じ分析を行う

日本以外の好きな国を1つ選び，演習3・演習4と同じ流れで年代別勝率の図を作成せよ．
チーム名はデータ内の英語表記（例：`Brazil`，`Germany`，`South Korea`）を使うこと．

`src/plot_other_team_winrate.py`を作成し，WebClass「第12回課題」問7から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 選んだ国の勝率は日本とどう違うか
2. 国名を変えるだけで再分析できるように，コードをどのように書いたか
````
