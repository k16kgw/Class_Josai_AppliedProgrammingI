# 第11回　データ分析実践II：経済データ

### 前回の復習

- テーマ設定では，「比較する」「関係を見る」のように**図にできる問い**へ落とし込む
- e-Statの統計ダッシュボードAPIは，APIキー不要で指標コードを指定してデータを取得できる
- 地域コードのような**コード**は，名前の表と結合して使う
- 結合後は行数が想定通りかを必ず確認する
- 桁が大きく異なる値の散布図では対数軸を検討する

### 今回の位置づけ

第11回では**経済データ**を扱う．
経済データには，物価，賃金，為替，株価，消費など，**時間に沿って変化する**データが多い．
今回は時系列データを中心に，テーマ設定からデータ取得・前処理・可視化・考察までを扱う．

題材は**消費者物価指数**（CPI: Consumer Price Index）である．
ニュースで「物価が3%上がった」と言うときの「物価」は，多くの場合この指数の変化率を指している．

### 到達目標

統計ダッシュボードAPIから消費者物価指数の月次データを取得し，物価の長期変化と直近の変化を可視化する．

- 経済データを使った分析テーマを設定できる
- 指数データの**基準年**の意味を説明できる（2020年基準＝2020年の平均を100とする）
- 年月を表す文字列を日付型に変換し，時間順に並べられる
- 同じ年月の行が重複していないかを確認し，必要な系列だけを取り出せる
- 折れ線グラフで長期の変化と直近の変化を可視化できる
- **前年同月比**を計算し，変化率として解釈できる

### 準備

````{note} 演習0：作業フォルダを作成する

1. ターミナルで次のコマンドを順に実行する．

```bash
cd /User/<ユーザ名>/applied_programming_i
mkdir 11
cd 11
mkdir -p notebooks data/raw data/processed src reports/figures
git init
```

2. `README.md`を作成し，次の内容を記入する．

```markdown
# 応用プログラミングI 第11回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

消費者物価指数の月次データを取得し，物価の長期変化と前年同月比を可視化する．

## 第11回 分析記録

- テーマ：日本の物価はどのように変化してきたか
- 元データ：data/raw/dashboard_cpi.json（消費者物価指数，全国，月次）
- 出典：e-Stat 統計ダッシュボード（原典：総務省統計局「消費者物価指数」）
- URL：https://dashboard.e-stat.go.jp/
- 基準年：2020年（2020年平均=100）
- 観察用ノートブック：notebooks/economic_data.ipynb（Gitでは管理しない）
- 作成するスクリプト：
  - src/plot_cpi_recent.py
  - src/plot_cpi_yoy.py
- 作成するデータ：
  - data/processed/cpi_monthly.csv
- 出力する図：
  - reports/figures/cpi_recent.png
  - reports/figures/cpi_yoy.png
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

5. JupyterLabまたはVS Codeで`notebooks/economic_data.ipynb`を新規作成する．
````

---

## テーマ設定

経済データでは，次のような問いを立てることができる．

| 観点 | 問いの例 |
| --- | --- |
| 時間変化 | 物価や消費は時間とともにどのように変化しているか |
| 比較 | 複数の地域や品目で変化の仕方は異なるか |
| 関係 | 2つの指標には似た動きがあるか |
| 変化点 | ある時期を境に傾向が変わっているか |

今回は次の問いを扱う．

> **日本の物価は長期的・短期的にどのように変化してきたか．**

「時間変化を見る」型の問いであり，折れ線グラフで確認できる．

### 指数と基準年

**消費者物価指数**：家計が購入するモノやサービスの価格を総合した指数．
**2020年基準**では，2020年の平均価格水準を100として各月の水準を表す．

- 指数が110 → 2020年平均より物価が10%高い
- 指数が80 → 2020年平均より物価が20%低い

```{tip} 基準年に注意
指数は基準年が変わると数値が変わる．
異なる基準年の指数をそのまま比較してはいけない．
経済データを使うときは，**単位**だけでなく**基準年**も必ず確認すること．
```

今回は次の2系列を使う．

| 指標コード | 指標名 |
| --- | --- |
| `0703010501010090000` | 消費者物価指数（総合）2020年基準 |
| `0703010501010090010` | 消費者物価指数（生鮮食品を除く総合）2020年基準 |

「生鮮食品を除く総合」は，天候で大きく変動する生鮮食品を除いた系列で，物価の基調を見るためにニュースでもよく使われる（「コアCPI」と呼ばれる）．

---

## データの取得

`getData`エンドポイントに，今回は次のパラメタを指定する．

| パラメタ | 意味 | 今回の指定 |
| --- | --- | --- |
| `IndicatorCode` | 指標コード（カンマ区切りで複数指定できる） | 上の2系列 |
| `RegionCode` | 地域コード | `00000`（全国） |
| `Cycle` | データの周期 | `1`（月次） |

````{note} 演習1：消費者物価指数を取得する
`notebooks/economic_data.ipynb`に「データの取得」という見出しを作り，次のセルを順番に実行せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

**セル2：必要なライブラリをインストールする**

```bash
!python -m pip install requests pandas seaborn matplotlib
```

**セル3：APIからデータを取得して保存する**

```python
import json
from pathlib import Path

import requests

get_data_url = "https://dashboard.e-stat.go.jp/api/1.0/Json/getData"

params = {
    "Lang": "JP",
    "IndicatorCode": "0703010501010090000,0703010501010090010",
    "RegionCode": "00000",
    "Cycle": "1",
}

response = requests.get(get_data_url, params=params)
response.raise_for_status()
cpi_data = response.json()

Path("../data/raw").mkdir(parents=True, exist_ok=True)

with open("../data/raw/dashboard_cpi.json", "w", encoding="utf-8") as f:
    json.dump(cpi_data, f, ensure_ascii=False, indent=2)

total_number = cpi_data["GET_STATS"]["STATISTICAL_DATA"]["RESULT_INF"]["TOTAL_NUMBER"]
print("データ件数:", total_number)
```

実行後，次を確認せよ．

1. `data/raw/dashboard_cpi.json`が作成されたか
2. データは何件入っているか
3. README.mdの分析記録に取得日をメモしたか
````

データが取得できない場合は，次のリンクからダウンロード・解凍して`data/raw`に配置すること．

- [dashboard_cpi_json.zip](./analysis/11/data/raw/dashboard_cpi_json.zip)

````{note} 演習2：データの中身と「2重の系列」を確認する
「JSONの構造確認」という見出しを作り，次のセルを順番に実行せよ．

**セル1：1件の中身を確認する**

```python
data_obj = cpi_data["GET_STATS"]["STATISTICAL_DATA"]["DATA_INF"]["DATA_OBJ"]

data_obj[0]["VALUE"]
```

`@time`が`19700100`のような形式（**西暦4桁 + 月2桁 + 00**）で入っていることを確認せよ．

**セル2：`@isSeasonal`の値を数える**

```python
from collections import Counter

seasonal_counts = Counter(
    obj["VALUE"]["@isSeasonal"] for obj in data_obj
)

print(seasonal_counts)
```

実行後，次を確認せよ．

1. `@isSeasonal`には`"1"`と`"2"`の2種類があるか
2. それぞれ何件ずつあるか
````

```{tip} 原数値と季節調整値
`@isSeasonal`は，`"1"`が**原数値**（観測されたままの値），`"2"`が**季節調整値**（季節による規則的な変動を取り除いた値）を表す．
このAPIは両方をまとめて返すため，**そのまま表にすると同じ年月の行が2重に存在する**ことになる．
気づかずに平均や図を作ると誤った結果になる．
今回は原数値（`"1"`）だけを使う．
```

---

## 前処理：時系列の表を作る

JSONを次の形の表に変換する．

| 指標名 | 年月 | 指数 |
| --- | --- | --- |
| 総合 | 1970-01-01 | 30.3 |
| 総合 | 1970-02-01 | ... | 

````{note} 演習3：時系列の表に変換して保存する
「前処理：時系列の表の作成」という見出しを作り，次のセルを順番に実行せよ．

**セル1：JSONから必要な値を取り出して表にする**

- 指標コードを日本語の指標名に対応づける
- `@isSeasonal == "1"`（原数値）の行だけを使う
- `@time`の先頭4桁が年，次の2桁が月である

```python
import pandas as pd

INDICATOR_NAMES = {
    "0703010501010090000": "総合",
    "0703010501010090010": "生鮮食品を除く総合",
}

rows = []

for obj in data_obj:
    value = obj["VALUE"]

    if value["@isSeasonal"] != "1":
        continue

    time_code = value["@time"]
    year = time_code[:4]
    month = time_code[4:6]

    rows.append({
        "指標名": INDICATOR_NAMES[value["@indicator"]],
        "年月": f"{year}-{month}",
        "指数": float(value["$"]),
    })

cpi_df = pd.DataFrame(rows)

print("行数:", len(cpi_df))
cpi_df.head()
```

**セル2：年月を日付型に変換して並べ替える**

```python
cpi_df["年月"] = pd.to_datetime(cpi_df["年月"])
cpi_df = cpi_df.sort_values(["指標名", "年月"]).reset_index(drop=True)

print("期間:", cpi_df["年月"].min(), "〜", cpi_df["年月"].max())
cpi_df.head()
```

**セル3：重複がないか確認する**

同じ指標名・同じ年月の行が2行以上あれば，前処理に誤りがある．

```python
duplicated_count = cpi_df.duplicated(subset=["指標名", "年月"]).sum()

print("重複している行数:", duplicated_count)
```

**セル4：CSVに保存する**

```python
output_path = "../data/processed/cpi_monthly.csv"

cpi_df.to_csv(output_path, index=False)

print("saved:", output_path)
```

実行後，次を確認せよ．

1. データはいつからいつまでの期間か
2. 重複している行数は0か（0でない場合は`@isSeasonal`の絞り込みを確認せよ）
3. 指標名ごとの行数はほぼ同じか（`cpi_df["指標名"].value_counts()`で確認せよ）
````

---

## 可視化の実施

### 長期の変化を見る

````{note} 演習4：50年間の物価の変化を折れ線グラフにする
「可視化」という見出しを作り，次のセルを順番に実行せよ．

**セル1：ライブラリを読み込む**

```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
```

**セル2：総合指数の長期推移を描く**

```python
total_df = cpi_df[cpi_df["指標名"] == "総合"]

fig, ax = plt.subplots(figsize=(9, 5))

sns.lineplot(data=total_df, x="年月", y="指数", ax=ax)

ax.set_title("消費者物価指数（総合，全国，2020年=100）")
ax.set_xlabel("年")
ax.set_ylabel("指数")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 物価が急激に上がっている時期はいつか（1970年代に何が起きたか調べてみよ）
2. ほとんど変化していない時期はいつからいつまでか
3. 直近で再び上がり始めたのはいつ頃か
````

### 直近の変化を見る

````{note} 演習5：2015年以降の2系列を比較する
次のセルを順番に実行せよ．

**セル1：2015年以降を取り出して2系列を比較する**

```python
recent_df = cpi_df[cpi_df["年月"] >= "2015-01-01"]

fig, ax = plt.subplots(figsize=(9, 5))

sns.lineplot(data=recent_df, x="年月", y="指数", hue="指標名", ax=ax)

ax.set_title("消費者物価指数の推移（2015年以降，全国，2020年=100）")
ax.set_xlabel("年")
ax.set_ylabel("指数")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 「総合」と「生鮮食品を除く総合」の動きはどこが似ていて，どこが違うか
2. どちらの系列の方が変動が滑らかか（生鮮食品を除くとなぜ滑らかになるのか）
3. 長期の図では見えなかったことが見えるようになったか
````

### 変化率に直して見る：前年同月比

指数の水準だけでなく，**前の年の同じ月と比べて何%変化したか**（前年同月比）で見ると，ニュースで報道される「物価上昇率」と同じ見方になる．

$$
\text{前年同月比（\%）} = \left( \frac{\text{今月の指数}}{\text{12か月前の指数}} - 1 \right) \times 100
$$

`pandas`では，12行前との変化率を計算する`pct_change(12)`が使える．

````{note} 演習6：前年同月比を計算して可視化する
次のセルを順番に実行せよ．

**セル1：前年同月比を計算する**

`pct_change(12)`は12行前（=12か月前）に対する変化率を返すため，100倍して%にする．

```python
total_df = cpi_df[cpi_df["指標名"] == "総合"].copy()
total_df["前年同月比"] = total_df["指数"].pct_change(12) * 100

total_df.tail()
```

**セル2：2000年以降の前年同月比を描く**

```python
yoy_df = total_df[total_df["年月"] >= "2000-01-01"]

fig, ax = plt.subplots(figsize=(9, 5))

sns.lineplot(data=yoy_df, x="年月", y="前年同月比", ax=ax)

ax.axhline(0, color="gray", linewidth=1)
ax.set_title("消費者物価指数（総合）の前年同月比（2000年以降）")
ax.set_xlabel("年")
ax.set_ylabel("前年同月比（%）")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 前年同月比がマイナス（物価が前年より下がっている）の時期はあるか
2. 前年同月比が大きく上がった時期はいつか
3. 指数の図と前年同月比の図では，同じデータでも印象がどう変わるか
````

```{tip} 最初の12か月は欠損になる
`pct_change(12)`は12か月前のデータが必要なため，先頭の12行は欠損（`NaN`）になる．
これはデータの誤りではなく，計算上どうしても生じる欠損である．
図にするときは期間を絞るか，欠損を除外すればよい．
```

````{warning} 課題1：2015年以降の物価をPythonファイルで可視化する
演習5で確認した内容を応用する．
以下のコードの`<HOGEHOGE1>`〜`<HOGEHOGE3>`を適切に書き換えてpythonスクリプト`src/plot_cpi_recent.py`を作成し，コードを実行して画像ファイル`reports/figures/cpi_recent.png`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_cpi_recent.py`と画像ファイル`reports/figures/cpi_recent.png`を<span style="color:red">WebClass「第11回課題」問1・問2</span>から提出せよ．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

input_path = "data/processed/cpi_monthly.csv"
output_path = "reports/figures/cpi_recent.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

cpi_df = pd.read_csv(input_path)
cpi_df["年月"] = pd.to_datetime(cpi_df["年月"])

recent_df = cpi_df[cpi_df["年月"] >= <HOGEHOGE1>]

fig, ax = plt.subplots(figsize=(9, 5))

sns.lineplot(
    data=recent_df,
    x=<HOGEHOGE2>,
    y=<HOGEHOGE3>,
    hue="指標名",
    ax=ax,
)

ax.set_title("消費者物価指数の推移（2015年以降，全国，2020年=100）")
ax.set_xlabel("年")
ax.set_ylabel("指数")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```

作成したPythonファイルを`11`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_cpi_recent.py
```

実行後，`reports/figures/cpi_recent.png`が作成されていることを確認せよ．
````

<!--
````{dropdown} 解答例
- `<HOGEHOGE1>`：`"2015-01-01"`
- `<HOGEHOGE2>`：`"年月"`
- `<HOGEHOGE3>`：`"指数"`
````
-->

````{warning} 課題2：前年同月比をPythonファイルで可視化する
演習6で確認した内容を応用する．
以下のコードの`<FUGAFUGA>`，`<HOGEHOGE1>`，`<HOGEHOGE2>`を適切に書き換えてpythonスクリプト`src/plot_cpi_yoy.py`を作成し，コードを実行して画像ファイル`reports/figures/cpi_yoy.png`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_cpi_yoy.py`と画像ファイル`reports/figures/cpi_yoy.png`を<span style="color:red">WebClass「第11回課題」問3・問4</span>から提出せよ．

本課題では，「総合」の**前年同月比**を2000年以降について折れ線グラフで表示する．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

input_path = "data/processed/cpi_monthly.csv"
output_path = "reports/figures/cpi_yoy.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

cpi_df = pd.read_csv(input_path)
cpi_df["年月"] = pd.to_datetime(cpi_df["年月"])

total_df = cpi_df[cpi_df["指標名"] == "総合"].copy()
total_df = total_df.sort_values("年月")
total_df["前年同月比"] = total_df["指数"].pct_change(<FUGAFUGA>) * 100

yoy_df = total_df[total_df["年月"] >= "2000-01-01"]

fig, ax = plt.subplots(figsize=(9, 5))

sns.lineplot(
    data=yoy_df,
    x=<HOGEHOGE1>,
    y=<HOGEHOGE2>,
    ax=ax,
)

ax.axhline(0, color="gray", linewidth=1)
ax.set_title("消費者物価指数（総合）の前年同月比（2000年以降）")
ax.set_xlabel("年")
ax.set_ylabel("前年同月比（%）")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```

作成したPythonファイルを`11`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_cpi_yoy.py
```

実行後，次の点を確認せよ．

1. 前年同月比がマイナスの時期と大きくプラスの時期を図から特定できるか
2. `pct_change()`に渡す数を変えると何が変わるか
````

<!--
````{dropdown} 解答例
- `<FUGAFUGA>`：`12`
- `<HOGEHOGE1>`：`"年月"`
- `<HOGEHOGE2>`：`"前年同月比"`
````
-->

---

## まとめ

- 経済データでは，単位に加えて**基準年**（指数の場合）を必ず確認する
- 時系列データでは，年月を日付型に変換し，時間順に並べてから可視化する
- 同じ年月の行が**重複していないか**を確認する（原数値と季節調整値の混在など）
- 長期の図と期間を絞った図では見えることが違う．目的に応じて期間を選ぶ
- 指数の**水準**と**前年同月比（変化率）**は同じデータの別の見方であり，伝わる印象が大きく異なる
- `pct_change(12)`の先頭12か月の欠損のように，計算上必ず生じる欠損もある

次回はデータ分析実践IIIとしてスポーツデータを扱う．

- GitHub上で公開されているオープンデータ（国際サッカー試合結果）を使う
- グループ別の集計・ランキング・分布の可視化を行い，最終レポートにつなげる

### 課題の提出期限

<span style="color: red; ">6月30日(火)23:59まで</span>

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所から提出したものについて加点対象とします．

````{note} 課題3：3系列を比較する

指標コード`0703010501010090020`（消費者物価指数（食料（酒類を除く）及びエネルギーを除く総合）2020年基準）を追加で取得し，2015年以降について3系列の折れ線グラフを作成せよ．
この系列は食料とエネルギーの影響を除いたもので，「コアコアCPI」と呼ばれる．

`src/plot_cpi_three_series.py`を作成し，WebClass「第11回課題」問5から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 3系列の動きはどの時期に大きくずれているか
2. 「総合」だけが大きく動くとき，何の価格が動いていると考えられるか
3. ニュースで複数のCPIが使い分けられる理由を自分の言葉で説明できるか
````

````{note} 課題4：1970年代と2020年代の物価上昇を比較する

「総合」の前年同月比について，1970〜1979年と2020年以降の2つの期間を，それぞれ図にして比較せよ．
1つの図に重ねても，2つの図を並べてもよい．

`src/plot_cpi_compare_periods.py`を作成し，WebClass「第11回課題」問6から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 1970年代の物価上昇率は最大で何%程度か（オイルショックについて調べてみよ）
2. 2020年代の物価上昇率と比べてどの程度違うか
3. 2つの期間を比較するとき，縦軸の範囲をどう設定したか
````
