# 第9回　地図上への可視化

### 今後の進め方

第8回までは，気象庁の予報データを使って，データ取得，前処理，集計，可視化の基本を学んだ．
第9回では，位置情報を含むデータを地図上に可視化する方法を学ぶ．

第10回以降は，気象データだけでなく，行政統計，経済，スポーツのデータを使った分析実践例を扱う．
それぞれの回では，単に図を作るだけでなく，**テーマ設定，データ取得，前処理，可視化，考察**までの流れを確認する．

第9回以降のシラバスは次のように変更する．

| 回 | 旧シラバス | 新シラバス | 変更の意図 |
| --- | --- | --- | --- |
| 第9回 | 統計的理解 | 可視化II：地図上への可視化 | 位置情報を含むデータを地図上で確認し，地域的な傾向を探る |
| 第10回 | データ分析I：回帰 | データ分析実践I：行政統計 | 行政統計を使って，テーマ設定から可視化までの流れを学ぶ |
| 第11回 | データ分析II：分類 | データ分析実践II：経済データ | 経済データを使って，時系列や比較の可視化を学ぶ |
| 第12回 | データ分析演習 | データ分析実践III：スポーツデータ | スポーツデータを使って，目的に応じた集計と可視化を学ぶ |
| 第13回 | 演習レビュー | 休講：レポート作成 | 各自で最終レポートを作成する時間に充てる |

### 到達目標

- 地図上への可視化が有効な場面を説明できる
- 緯度・経度を持つデータを読み込み，地図上に点として表示できる
- 色，大きさ，ポップアップを使って，地図上に追加情報を表現できる
- 地図上の分布から読み取れることと，読み取れないことを区別できる
- `pandas`，`janome`，`seaborn`，`plotly`，`folium`を使い分けて可視化できる

---

## 地図上への可視化で考えること

地図上への可視化は，地域差や空間的な偏りを確認したいときに有効である．
ただし，地図に点を置くだけでは分析にならない．

図を作る前に，次を確認する．

| 観点 | 確認すること |
| --- | --- |
| 場所 | 緯度・経度，住所，市区町村コードなど，位置を表す情報があるか |
| 値 | 地図上で色や大きさに対応させたい数値やカテゴリがあるか |
| 単位 | 点が地点を表すのか，市区町村などの地域を表すのか |
| 比較 | 何と何を比較したいのか |
| 注意点 | 人口規模，面積，観測点の偏りなどを考慮する必要があるか |

第9回では，次のようにライブラリを使い分ける．

| ライブラリ | 主な役割 |
| --- | --- |
| `pandas` | 位置情報を含むCSVを読み込み，欠損値や列を確認する |
| `janome` | 地名や施設名など，日本語の名前に含まれる単語を確認する |
| `seaborn` | 地図に載せる前に，値の分布やカテゴリ別の違いを確認する |
| `plotly` | Notebook上でインタラクティブな地図をすばやく作る |
| `folium` | 地図をHTMLとして保存し，ブラウザで確認できる形にする |

---

## 演習の流れ

この回では，位置情報を含むサンプルデータを使って，次の流れで作業する．

```text
テーマ設定
  ↓
データ取得
  ↓
pandasで読み込み
  ↓
前処理
  ↓
janomeで日本語名を確認
  ↓
seabornで分布を確認
  ↓
plotlyで地図上に可視化
  ↓
foliumでHTML地図を作成
  ↓
読み取れることを文章で整理
```

### 演習1：位置情報を含むデータを読み込む

`pandas`を使ってCSVを読み込み，行数，列名，欠損値，緯度・経度の範囲を確認する．

```python
import pandas as pd

df = pd.read_csv("../data/raw/sample_location_data.csv")

print(df.shape)
print(df.columns)
df.head()
```

### 演習2：日本語名を単語に分けて確認する

地名や施設名などの日本語テキストは，必要に応じて単語に分けて確認する．
ここでは`name`列に入っている名称を`janome`で分かち書きする．

```python
from collections import Counter
from janome.tokenizer import Tokenizer

tokenizer = Tokenizer()
words = []

for name in df["name"].dropna().astype(str):
    for token in tokenizer.tokenize(name):
        part = token.part_of_speech.split(",")[0]

        if part in {"名詞", "動詞", "形容詞"}:
            words.append(token.surface)

word_count_df = pd.DataFrame(
    Counter(words).most_common(10),
    columns=["単語", "出現回数"]
)

word_count_df
```

### 演習3：地図に載せる前に分布を確認する

地図上に載せる前に，値の分布を確認する．
値の偏りが大きい場合，地図上の色や大きさが読みにくくなることがある．

```python
import seaborn as sns

sns.histplot(data=df, x="value")
```

### 演習4：plotlyで地図上にプロットする

`plotly.express`を使って，緯度・経度を地図上に表示する．

```python
import plotly.express as px

fig = px.scatter_map(
    df,
    lat="latitude",
    lon="longitude",
    color="category",
    size="value",
    hover_name="name",
    zoom=9,
    height=600,
)

fig.show()
```

### 演習5：foliumでHTML地図を作成する

`folium`を使うと，地図をHTMLファイルとして保存できる．
Notebook上で確認するだけでなく，ブラウザで開ける地図として残したいときに便利である．

```python
import folium

center_lat = df["latitude"].mean()
center_lon = df["longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

for _, row in df.iterrows():
    popup_text = f"{row['name']}<br>値：{row['value']}<br>カテゴリ：{row['category']}"

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        popup=popup_text,
        color="blue",
        fill=True,
        fill_opacity=0.6,
    ).add_to(m)

m
```

HTMLファイルとして保存する場合は，次を実行する．

```python
from pathlib import Path

Path("../reports/figures").mkdir(parents=True, exist_ok=True)
m.save("../reports/figures/sample_location_map.html")
```

### 演習6：地図から読み取れることを書く

作成した地図を見て，次の観点で短い文章を書く．

1. 値が大きい地点はどこに多いか
2. 地域による偏りはあるか
3. 地図だけでは判断できないことは何か

---

## まとめ

- 地図上への可視化は，地域差や空間的な偏りを確認するために有効である
- 地図に載せる前に，データの行数，列名，欠損値，値の分布を確認する
- `folium`を使うと，地図をHTMLとして保存し，ブラウザで確認できる
- 点の色や大きさは，読み手が何を比較するかを意識して設定する
- 地図から読み取れることと，地図だけでは判断できないことを分けて説明する
