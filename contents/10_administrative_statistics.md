# 第10回　データ分析実践I：行政統計

### 前回の復習

- 地図上への可視化は，場所ごとの違い・地域的な偏りを確認するための切り口である
- 度分形式の緯度・経度は，度 + 分/60 で度単位の小数に変換する
- 地図に載せる前に，欠損の有無と値の分布を確認する
- `plotly`はデータ観察用，`folium`はHTML保存用の地図に向いている
- 欠損は誤りとは限らない（気温を観測していない観測所など）

### 今回の位置づけ

第10回から第12回では，気象以外のデータを使って，データ分析の実践例を学ぶ．
各回では，**テーマ設定 → データ取得 → 前処理 → 可視化 → 考察**を一つの流れとして扱う．
これは最終レポートで各自が行う作業と同じ流れである．

第10回では**行政統計**を扱う．
行政統計は，人口，世帯，産業，教育，福祉など，社会の状態を把握するために国や自治体が作成しているデータである．

### 到達目標

国の統計ポータルe-Statの**統計ダッシュボードAPI**を使い，都道府県別の人口と高齢化率を取得・可視化する．

- 行政統計データを使った分析テーマを，図にできる問いとして設定できる
- APIキー不要の統計ダッシュボードAPIから，指標コードを指定してデータを取得できる
- データの出典，調査年，地域の単位，数値の単位を確認できる
- 地域コードをキーにして複数の表を結合できる（第7回の復習）
- 棒グラフ・ヒストグラム・散布図を使い分けて行政統計を可視化できる
- 図から読み取れることと，読み取れないことを分けて説明できる

### 準備

````{note} 演習0：作業フォルダを作成する

1. ターミナルで次のコマンドを順に実行する．

```bash
cd /User/<ユーザ名>/applied_programming_i
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

統計ダッシュボードAPIから都道府県別の人口データを取得し，人口と高齢化率の関係を可視化する．

## 第10回 分析記録

- テーマ：都道府県の人口規模と高齢化に関係はあるか
- 元データ：
  - data/raw/dashboard_population.json（都道府県別の総人口）
  - data/raw/dashboard_aging.json（都道府県別の65歳以上人口割合）
  - data/raw/dashboard_regions.json（都道府県コード表）
- 出典：e-Stat 統計ダッシュボード（総務省統計局）
- URL：https://dashboard.e-stat.go.jp/
- 調査年：2020年（国勢調査）
- 観察用ノートブック：notebooks/administrative_statistics.ipynb（Gitでは管理しない）
- 作成するスクリプト：
  - src/plot_pref_population_aging.py
  - src/plot_pref_aging_top10.py
- 作成するデータ：
  - data/processed/pref_population_aging.csv
- 出力する図：
  - reports/figures/pref_population_aging_scatter.png
  - reports/figures/pref_aging_top10.png
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

5. JupyterLabまたはVS Codeで`notebooks/administrative_statistics.ipynb`を新規作成する．
````

---

## テーマ設定

行政統計では，次のような問いを立てることができる．

| 分野 | 問いの例 |
| --- | --- |
| 人口 | 人口が多い地域と少ない地域にはどのような違いがあるか |
| 世帯 | 単身世帯の割合は地域によってどのように異なるか |
| 産業 | 地域ごとに産業構成はどのように異なるか |
| 福祉 | 高齢化率と福祉関連指標にはどのような関係があるか |

問いを立てるときは，最初から大きすぎるテーマにしない．
「地域別に比較する」「時点別に比較する」「2つの指標の関係を見る」のように，**図にできる問い**へ落とし込む．

今回は次の問いを扱う．

> **都道府県の人口規模と高齢化率に関係はあるか．**

この問いは「2つの指標の関係を見る」型であり，散布図で確認できる．
人口の比較には棒グラフ，高齢化率の分布にはヒストグラムも使う．

---

## 使用するデータ：e-Stat統計ダッシュボード

**e-Stat**：日本の政府統計をまとめて公開しているポータルサイト．
国勢調査をはじめ，ほとんどの政府統計はここから取得できる．

e-Statの通常のAPIは利用登録（APIキー）が必要だが，主要な指標をまとめた**統計ダッシュボード**のAPIは**登録不要**で利用できる．

| 項目 | 内容 |
| --- | --- |
| サービス名 | e-Stat 統計ダッシュボード |
| 提供 | 総務省統計局 |
| URL | https://dashboard.e-stat.go.jp/ |
| API仕様 | https://dashboard.e-stat.go.jp/static/api |
| 利用条件 | 出典を記載して利用できる（利用規約を確認すること） |

### エンドポイントとパラメタ

第5回で学んだ通り，APIは**エンドポイント**と**パラメタ**で問い合わせ条件を指定する．
今回は2つのエンドポイントを使う．

| エンドポイント | 役割 |
| --- | --- |
| `https://dashboard.e-stat.go.jp/api/1.0/Json/getData` | 指標の値を取得する |
| `https://dashboard.e-stat.go.jp/api/1.0/Json/getRegionInfo` | 地域コードと地域名の対応を取得する |

`getData`の主なパラメタ

| パラメタ | 意味 | 今回の指定 |
| --- | --- | --- |
| `IndicatorCode` | 指標コード（どの統計値か） | 下の表を参照 |
| `Time` | 時点 | `2020CY00`（2020年） |
| `RegionalRank` | 地域の単位 | `3`（都道府県） |

今回使う指標コード

| 指標コード | 指標名 | 出典統計 |
| --- | --- | --- |
| `0201010000000010000` | 総人口（総数） | 国勢調査（2020年） |
| `0201010010000020030` | 総人口に占める割合（65歳以上） | 国勢調査（2020年） |

「総人口に占める割合（65歳以上）」は**高齢化率**と呼ばれる指標である．

````{note} 演習1：APIからデータを取得する
`notebooks/administrative_statistics.ipynb`に「データの取得」という見出しを作り，次のセルを順番に実行せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

**セル2：必要なライブラリをインストールする**

```bash
!python -m pip install requests pandas seaborn matplotlib
```

**セル3：総人口と高齢化率を取得して保存する**

`params`にパラメタをまとめて`requests.get()`に渡す（第5回の復習）．

```python
import json
from pathlib import Path

import requests

get_data_url = "https://dashboard.e-stat.go.jp/api/1.0/Json/getData"

Path("../data/raw").mkdir(parents=True, exist_ok=True)

targets = {
    "dashboard_population.json": "0201010000000010000",
    "dashboard_aging.json": "0201010010000020030",
}

for file_name, indicator_code in targets.items():
    params = {
        "Lang": "JP",
        "IndicatorCode": indicator_code,
        "Time": "2020CY00",
        "RegionalRank": "3",
    }

    response = requests.get(get_data_url, params=params)
    response.raise_for_status()
    data = response.json()

    with open(f"../data/raw/{file_name}", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("saved:", file_name)
```

**セル4：都道府県コード表を取得して保存する**

`ParentRegionCode=00000`（全国）を指定すると，その下位地域である47都道府県の一覧が返される．

```python
get_region_url = "https://dashboard.e-stat.go.jp/api/1.0/Json/getRegionInfo"

params = {
    "Lang": "JP",
    "ParentRegionCode": "00000",
}

response = requests.get(get_region_url, params=params)
response.raise_for_status()
region_data = response.json()

with open("../data/raw/dashboard_regions.json", "w", encoding="utf-8") as f:
    json.dump(region_data, f, ensure_ascii=False, indent=2)

print("saved: dashboard_regions.json")
```

実行後，次を確認せよ．

1. `data/raw`に3つのJSONファイルが作成されたか
2. README.mdの分析記録に取得日をメモしたか
````

データが取得できない場合は，次のリンクからダウンロード・解凍して`data/raw`に配置すること．

- [dashboard_population_json.zip](./analysis/10/data/raw/dashboard_population_json.zip)
- [dashboard_aging_json.zip](./analysis/10/data/raw/dashboard_aging_json.zip)
- [dashboard_regions_json.zip](./analysis/10/data/raw/dashboard_regions_json.zip)

````{note} 演習2：JSONの構造を確認する
「JSONの構造確認」という見出しを作り，次のセルを順番に実行せよ．

**セル1：値のJSONの構造を確認する**

```python
with open("../data/raw/dashboard_population.json", encoding="utf-8") as f:
    population_data = json.load(f)

data_obj = population_data["GET_STATS"]["STATISTICAL_DATA"]["DATA_INF"]["DATA_OBJ"]

print("データ件数:", len(data_obj))
data_obj[0]
```

**セル2：1件の中身を確認する**

```python
data_obj[0]["VALUE"]
```

実行後，次を確認せよ．

1. データは何件入っているか（47都道府県なら47件のはずである）
2. 地域コードはどのキーに入っているか（`@regionCode`）
3. 統計値はどのキーに入っているか（`$`）
4. 統計値は数値と文字列のどちらで入っているか
````

```{tip} JSONの階層をたどる
統計ダッシュボードAPIのレスポンスは
`GET_STATS → STATISTICAL_DATA → DATA_INF → DATA_OBJ`
という階層になっており，`DATA_OBJ`が1件ずつの値のリストである．
第5回で学んだ通り，いきなり全部を理解しようとせず，`keys()`で階層を1段ずつ確認しながらたどるとよい．
```

---

## 前処理：3つの表を結合する

取得した3つのJSONを，分析しやすい**1つの表**にまとめる．

```text
dashboard_population.json（地域コード，総人口）
dashboard_aging.json（地域コード，高齢化率）
dashboard_regions.json（地域コード，都道府県名）
  ↓ 地域コードをキーに結合（第7回の復習）
pref_population_aging.csv（都道府県名，総人口，高齢化率）
```

````{note} 演習3：JSONを表に変換して結合する
「前処理：表の作成と結合」という見出しを作り，次のセルを順番に実行せよ．

**セル1：値のJSONを表に変換する関数を作る**

総人口と高齢化率で同じ処理を行うため，関数にまとめる．
統計値`$`は文字列で入っているため，`float()`で数値に変換する．

```python
import pandas as pd


def dashboard_to_df(path, value_name):
    """統計ダッシュボードAPIのJSONを地域コードと値の表に変換する．"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    data_obj = data["GET_STATS"]["STATISTICAL_DATA"]["DATA_INF"]["DATA_OBJ"]

    rows = []

    for obj in data_obj:
        value = obj["VALUE"]
        rows.append({
            "地域コード": value["@regionCode"],
            value_name: float(value["$"]),
        })

    return pd.DataFrame(rows)


population_df = dashboard_to_df("../data/raw/dashboard_population.json", "総人口")
aging_df = dashboard_to_df("../data/raw/dashboard_aging.json", "高齢化率")

print("総人口の表:", population_df.shape)
print("高齢化率の表:", aging_df.shape)
population_df.head()
```

**セル2：都道府県コード表を作る**

```python
with open("../data/raw/dashboard_regions.json", encoding="utf-8") as f:
    region_data = json.load(f)

class_obj = region_data["GET_META_REGION_INF"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]
pref_list = class_obj[0]["CLASS"]

region_df = pd.DataFrame([
    {"地域コード": pref["@regionCode"], "都道府県名": pref["@name"]}
    for pref in pref_list
])

print("都道府県コード表:", region_df.shape)
region_df.head()
```

**セル3：地域コードをキーに3つの表を結合する**

```python
pref_df = (
    region_df
    .merge(population_df, on="地域コード")
    .merge(aging_df, on="地域コード")
)

print("結合後の表:", pref_df.shape)
pref_df.head()
```

**セル4：結合結果と単位を確認する**

```python
print("行数（47になっているか）:", len(pref_df))
print("欠損の数:")
print(pref_df.isna().sum())

pref_df[["総人口", "高齢化率"]].describe()
```

**セル5：CSVに保存する**

```python
output_path = "../data/processed/pref_population_aging.csv"

pref_df.to_csv(output_path, index=False)

print("saved:", output_path)
```

実行後，次を確認せよ．

1. 結合後の表は47行になっているか（増えたり減ったりしていたら結合キーを疑う）
2. 総人口の単位は何か（人），高齢化率の単位は何か（%）
3. 埼玉県の総人口と高齢化率はいくつか
4. 高齢化率の最小値・最大値はどの程度か
````

```{tip} 結合後の行数を必ず確認する
第7回で学んだ通り，結合後は**行数が想定通りか**を必ず確認する．
47都道府県の表同士を結合したのに行数が47でない場合は，キーの不一致や重複が起きている．
```

---

## 可視化の実施

### 人口の比較：棒グラフ

````{note} 演習4：人口上位の都道府県を棒グラフにする
「可視化」という見出しを作り，次のセルを順番に実行せよ．

**セル1：ライブラリを読み込む**

```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
```

**セル2：人口上位10都道府県の棒グラフを作る**

```python
top10_df = pref_df.sort_values("総人口", ascending=False).head(10)

fig, ax = plt.subplots(figsize=(7, 5))

sns.barplot(data=top10_df, x="総人口", y="都道府県名", ax=ax)

ax.set_title("総人口の上位10都道府県（2020年国勢調査）")
ax.set_xlabel("総人口（人）")
ax.set_ylabel("都道府県")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 上位10都道府県はどこか，埼玉県は何位か
2. 1位と10位ではどの程度の差があるか
````

### 高齢化率の分布と関係：ヒストグラムと散布図

````{note} 演習5：高齢化率の分布と人口との関係を見る
次のセルを順番に実行せよ．

**セル1：高齢化率の分布をヒストグラムで見る**

```python
fig, ax = plt.subplots(figsize=(7, 4))

sns.histplot(data=pref_df, x="高齢化率", bins=10, ax=ax)

ax.set_title("都道府県別高齢化率の分布（2020年）")
ax.set_xlabel("高齢化率（%）")
ax.set_ylabel("都道府県数")

plt.tight_layout()
plt.show()
```

**セル2：人口と高齢化率の散布図を作る**

人口は東京都の約1,400万人から鳥取県の約55万人まで**桁が大きく異なる**ため，横軸を対数にして眺める．

```python
fig, ax = plt.subplots(figsize=(7, 5))

sns.scatterplot(data=pref_df, x="総人口", y="高齢化率", s=60, ax=ax)

ax.set_xscale("log")
ax.set_title("総人口と高齢化率の関係（2020年）")
ax.set_xlabel("総人口（人，対数軸）")
ax.set_ylabel("高齢化率（%）")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 高齢化率はどの範囲に集中しているか
2. 人口が少ない県ほど高齢化率が高い傾向は見られるか
3. 傾向から外れている都道府県はどこか（マウスでは確認できないため，`pref_df.sort_values("高齢化率")`などで表からも確認せよ）
4. 対数軸にしない場合，図はどう見えるか（`ax.set_xscale("log")`を外して試せ）
````

````{note} 演習6：考察を書く
README.mdの分析記録に，図から読み取れることを次の形で整理して記入せよ．

1. 人口規模と高齢化率にはどのような傾向があるか
2. 傾向から外れる都道府県はどこか
3. この分析だけでは判断できないことは何か
   （例：なぜそうなるのかという**原因**は，この2つの指標だけからは分からない）
````

````{warning} 課題1：人口と高齢化率の散布図をPythonファイルで作成する
演習5で確認した内容を応用する．
以下のコードの`<HOGEHOGE1>`，`<HOGEHOGE2>`，`<PIYOPIYO>`を適切に書き換えてpythonスクリプト`src/plot_pref_population_aging.py`を作成し，コードを実行して画像ファイル`reports/figures/pref_population_aging_scatter.png`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_pref_population_aging.py`と画像ファイル`reports/figures/pref_population_aging_scatter.png`を<span style="color:red">WebClass「第10回課題」問1・問2</span>から提出せよ．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

input_path = "data/processed/pref_population_aging.csv"
output_path = "reports/figures/pref_population_aging_scatter.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

pref_df = pd.read_csv(input_path)

fig, ax = plt.subplots(figsize=(7, 5))

sns.scatterplot(
    data=pref_df,
    x=<HOGEHOGE1>,
    y=<HOGEHOGE2>,
    s=60,
    ax=ax,
)

ax.set_xscale(<PIYOPIYO>)
ax.set_title("総人口と高齢化率の関係（2020年）")
ax.set_xlabel("総人口（人，対数軸）")
ax.set_ylabel("高齢化率（%）")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```

作成したPythonファイルを`10`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_pref_population_aging.py
```

実行後，`reports/figures/pref_population_aging_scatter.png`が作成されていることを確認せよ．
````

<!--
````{dropdown} 解答例
- `<HOGEHOGE1>`：`"総人口"`
- `<HOGEHOGE2>`：`"高齢化率"`
- `<PIYOPIYO>`：`"log"`
````
-->

````{warning} 課題2：高齢化率上位10県をPythonファイルで可視化する
演習4の棒グラフを応用する．
以下のコードの`<FUGAFUGA>`，`<HOGEHOGE1>`，`<HOGEHOGE2>`を適切に書き換えてpythonスクリプト`src/plot_pref_aging_top10.py`を作成し，コードを実行して画像ファイル`reports/figures/pref_aging_top10.png`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_pref_aging_top10.py`と画像ファイル`reports/figures/pref_aging_top10.png`を<span style="color:red">WebClass「第10回課題」問3・問4</span>から提出せよ．

本課題では，**高齢化率の上位10都道府県**を棒グラフで表示する．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

input_path = "data/processed/pref_population_aging.csv"
output_path = "reports/figures/pref_aging_top10.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

pref_df = pd.read_csv(input_path)

top10_df = pref_df.sort_values(<FUGAFUGA>, ascending=False).head(10)

fig, ax = plt.subplots(figsize=(7, 5))

sns.barplot(
    data=top10_df,
    x=<HOGEHOGE1>,
    y=<HOGEHOGE2>,
    ax=ax,
)

ax.set_title("高齢化率の上位10都道府県（2020年）")
ax.set_xlabel("高齢化率（%）")
ax.set_ylabel("都道府県")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```

作成したPythonファイルを`10`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_pref_aging_top10.py
```

実行後，次の点を確認せよ．

1. 高齢化率の上位10県と人口の上位10都道府県は重なっているか
2. 散布図で見た傾向と整合しているか
````

<!--
````{dropdown} 解答例
- `<FUGAFUGA>`：`"高齢化率"`
- `<HOGEHOGE1>`：`"高齢化率"`
- `<HOGEHOGE2>`：`"都道府県名"`
````
-->

---

## まとめ

- 行政統計では，出典，調査年，地域の単位，数値の単位を最初に確認する
- e-Statの統計ダッシュボードAPIは，APIキー不要で指標コードを指定してデータを取得できる
- APIのレスポンスでは，地域が**コード**で入っていることが多く，名前の表と結合して使う
- 結合後は行数が想定通り（今回は47行）かを必ず確認する
- 桁が大きく異なる値を散布図にするときは，対数軸を検討する
- 散布図から関係の傾向は読み取れるが，**原因**までは分からないことを意識する
- テーマ設定 → データ取得 → 前処理 → 可視化 → 考察の流れを，自分のテーマでも再現できるようにする

次回はデータ分析実践IIとして経済データを扱う．

- 消費者物価指数（CPI）の時系列データを取得する
- 日付の前処理と，時系列・前年同月比の可視化を行う

### 課題の提出期限

<span style="color: red; ">6月23日(火)23:59まで</span>

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所から提出したものについて加点対象とします．

````{note} 課題3：年少人口割合と高齢化率の関係を可視化する

指標コード`0201010010000020010`（総人口に占める割合（0〜14歳），**年少人口割合**）を追加で取得し，横軸を年少人口割合，縦軸を高齢化率とした散布図を作成せよ．

`src/plot_pref_age_structure.py`を作成し，WebClass「第10回課題」問5から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 年少人口割合と高齢化率にはどのような関係があるか
2. 両方の割合が低い都道府県はどこか（残りはどの年齢層が多いことになるか）
3. データ取得の処理を関数にまとめられたか
````

````{note} 課題4：人口上位と下位を1つの図で比較する

総人口の上位5都道府県と下位5都道府県を1つの棒グラフにまとめ，色分けして表示せよ．

`src/plot_pref_population_top_bottom.py`を作成し，WebClass「第10回課題」問6から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 上位と下位では何倍程度の差があるか
2. 1つの図にまとめるとき，軸や色でどのような工夫をしたか
3. 対数軸は必要か
````
