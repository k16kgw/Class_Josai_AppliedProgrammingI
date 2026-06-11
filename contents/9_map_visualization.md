# 第9回　可視化II：地図上への可視化

### 前回の復習

- 可視化：データの傾向を知るために，色々な切り口からデータを眺める手法
- 図を作る前に，行数，列名，値の例，空欄の有無を確認する
- 図には，タイトル，軸ラベル，単位，凡例を適切に設定する
- データ観察はNotebookで行い，再実行する本処理はPythonファイルとして保存する

データを眺める切り口と図の対応

| 切り口 | 確認できること | 図の例 |
| --- | --- | --- |
| 値の分布を見る | 値がどの範囲に多いか，外れた値があるか | ヒストグラム |
| 2つの値の関係を見る | 一方が大きいとき，もう一方も大きいか | 散布図 |
| 時間変化を見る | 日付や時刻に沿って値がどう変わるか | 折れ線グラフ |
| グループを比較する | 地域や地点によって違いがあるか | 棒グラフ，色分けした図 |

今回はこの表に新しい切り口を1つ追加する．

| 切り口 | 確認できること | 図の例 |
| --- | --- | --- |
| **場所ごとの違いを見る** | どの場所で値が大きいか，地域的な偏りがあるか | **地図上への可視化** |

### 今後の進め方

第9回以降は，毎回新しい分析フォルダを作成し，**データ取得 → 前処理 → 可視化**の一連の流れを一気通貫で行う．
これは，最終レポートで各自が同じ流れを最初から最後まで実行するための練習である．

| 回 | テーマ | 扱うデータ |
| --- | --- | --- |
| 第9回 | 可視化II：地図上への可視化 | 気象庁アメダスの観測データ |
| 第10回 | データ分析実践I：行政統計 | e-Statの人口統計 |
| 第11回 | データ分析実践II：経済データ | 消費者物価指数 |
| 第12回 | データ分析実践III：スポーツデータ | 国際サッカー試合結果 |
| 第13回 | 休講：レポート作成 | 各自で選択 |

### 到達目標

気象庁の**アメダス**（地域気象観測システム）のデータを使い，関東の最新気温を地図上に可視化する．

**地図上への可視化**：位置情報（緯度・経度）を持つデータを地図上に表示し，場所による値の違いを眺める手法

- 地図上への可視化が有効な場面を説明できる
- 緯度・経度を含むJSONを前処理し，地図に載せられる表を作成できる
- 度分形式の緯度・経度を度単位に変換できる
- `plotly`を使ってNotebook上にインタラクティブな地図を表示できる
- `folium`を使って地図をHTMLファイルとして保存できる
- 地図から読み取れることと，読み取れないことを区別できる

### 準備

今回から，回ごとに新しい分析フォルダを作成する．
第5回の演習0と同じ手順で，フォルダ`9`を作成してGitの初期化を行う．

````{note} 演習0：作業フォルダを作成する

1. ターミナルを起動し，次のコマンドを順に実行する．

```bash
cd /User/<ユーザ名>/applied_programming_i
mkdir 9
cd 9
mkdir -p notebooks data/raw data/processed src reports/figures
git init
```

2. 次のディレクトリ構成になっているか確認する．

```text
9/
├── notebooks/
│   └── map_visualization.ipynb（←今回作成するファイル）
├── data/
│   ├── raw/
│   └── processed/
├── reports/
│   └── figures/
├── src/
└── README.md
```

3. `README.md`を作成し，次の内容を記入する．

```markdown
# 応用プログラミングI 第9回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

アメダスの観測データを取得し，関東の最新気温を地図上に可視化する．

## 第9回 分析記録

- 元データ：
  - data/raw/amedastable.json（アメダス観測所一覧）
  - data/raw/amedas_latest_map.json（最新の観測値）
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/amedas/const/amedastable.json ほか
- 観察用ノートブック：notebooks/map_visualization.ipynb（Gitでは管理しない）
- 作成するスクリプト：
  - src/plot_amedas_temperature_map.py
  - src/plot_amedas_lat_temperature.py
- 作成するデータ：
  - data/processed/amedas_kanto_temperature.csv
- 出力する図：
  - reports/figures/amedas_kanto_temperature_map.html
  - reports/figures/amedas_lat_temperature.png
- 可視化の目的：
  - 関東のどの場所で気温が高いか・低いかを確認する
  - 緯度と気温の関係を確認する
```

4. `.gitignore`を作成し，次の内容を記入する．

```gitignore
.DS_Store
*.swp
*~
.vscode/
.ipynb_checkpoints
*.ipynb
data/raw/
```

5. 作成したファイルをコミットする．

```bash
git add .
git commit -m "first commit"
```

6. JupyterLabまたはVS Codeで`notebooks/map_visualization.ipynb`を新規作成する．
````

---

## 地図上への可視化で考えること

地図上への可視化は，**地域差や空間的な偏り**を確認したいときに有効である．
ただし，地図に点を置くだけでは分析にならない．

図を作る前に，次を確認する．

| 観点 | 確認すること |
| --- | --- |
| 場所 | 緯度・経度，住所，市区町村コードなど，位置を表す情報があるか |
| 値 | 地図上で色や大きさに対応させたい数値やカテゴリがあるか |
| 単位 | 点が観測地点を表すのか，市区町村などの地域を表すのか |
| 比較 | 何と何を比較したいのか |
| 注意点 | 観測点の偏り，人口規模，面積などを考慮する必要があるか |

地図上への可視化には大きく2種類がある．

| 種類 | 描き方 | 例 |
| --- | --- | --- |
| ポイントマップ | 地点ごとに点を打ち，色や大きさで値を表す | 観測所ごとの気温 |
| コロプレス図 | 地域（都道府県など）を値に応じて塗り分ける | 都道府県別の人口密度 |

今回は，アメダスの観測所という「地点」のデータを扱うため，**ポイントマップ**を作成する．

第9回では，次のようにライブラリを使い分ける．

| ライブラリ | 主な役割 | この回での使い方 |
| --- | --- | --- |
| `requests` | Web上のデータの取得 | アメダスのJSONを取得する |
| `pandas` | 表形式データの作成・確認・前処理 | JSONから地図に載せる表を作る |
| `seaborn` | 地図に載せる前の分布・関係の確認 | 気温の分布や緯度との関係を確認する |
| `plotly` | Notebook上のインタラクティブな地図 | 観測所の気温を地図上で眺める |
| `folium` | HTMLとして保存できる地図 | 提出用の地図ファイルを作る |

---

## 使用するデータ：アメダス

**アメダス**（AMeDAS: Automated Meteorological Data Acquisition System）：気象庁の地域気象観測システム．
全国約1,300地点で気温・降水量・風などを自動観測している．

今回は次の3つのURLを使う．

| URL | 内容 |
| --- | --- |
| `https://www.jma.go.jp/bosai/amedas/const/amedastable.json` | 観測所一覧（名前，緯度・経度，標高） |
| `https://www.jma.go.jp/bosai/amedas/data/latest_time.txt` | 最新の観測時刻 |
| `https://www.jma.go.jp/bosai/amedas/data/map/<時刻>.json` | 指定時刻の全観測所の観測値 |

観測所一覧`amedastable.json`は，**観測所番号をキーとするJSON**になっている．

```json
"44132": {
    "type": "A",
    "elems": "11111111",
    "lat": [35, 41.5],
    "lon": [139, 45.0],
    "alt": 25,
    "kjName": "東京",
    "knName": "トウキョウ",
    "enName": "Tokyo"
}
```

- `lat`，`lon`：緯度・経度．`[度, 分]`の**度分形式**で入っている（後で前処理が必要）
- `alt`：標高（m）
- `kjName`：観測所名（漢字）

観測値のJSONも観測所番号をキーとしており，気温は`temp`に`[値, 品質フラグ]`の形で入っている．

```json
"44132": {
    "temp": [21.6, 0],
    "humidity": [77, 0],
    ...
}
```

````{note} 演習1：アメダスのデータを取得する
`notebooks/map_visualization.ipynb`に「データの取得」という見出しを作り，次のセルを順番に実行せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

**セル2：必要なライブラリをインストールする**

初回のみ実行する．すでにインストール済みの場合はすぐに終了する．

```bash
!python -m pip install requests pandas seaborn matplotlib plotly folium
```

**セル3：観測所一覧を取得して保存する**

第5回で学んだ`requests`を使う．

```python
import json
from pathlib import Path

import requests

station_url = "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"

response = requests.get(station_url)
response.raise_for_status()
stations = response.json()

Path("../data/raw").mkdir(parents=True, exist_ok=True)

with open("../data/raw/amedastable.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)

print("観測所数:", len(stations))
```

**セル4：最新の観測値を取得して保存する**

最新の観測時刻を取得し，その時刻の観測値JSONのURLを組み立てる．

```python
from datetime import datetime

latest_time_url = "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"

response = requests.get(latest_time_url)
response.raise_for_status()
latest_time_text = response.text.strip()

print("最新の観測時刻:", latest_time_text)

latest_time = datetime.fromisoformat(latest_time_text)
stamp = latest_time.strftime("%Y%m%d%H%M%S")
map_url = f"https://www.jma.go.jp/bosai/amedas/data/map/{stamp}.json"

print("観測値のURL:", map_url)

response = requests.get(map_url)
response.raise_for_status()
observations = response.json()

with open("../data/raw/amedas_latest_map.json", "w", encoding="utf-8") as f:
    json.dump(observations, f, ensure_ascii=False, indent=2)

print("観測値のある観測所数:", len(observations))
```

実行後，次を確認せよ．

1. `data/raw/amedastable.json`と`data/raw/amedas_latest_map.json`が作成されたか
2. 観測所一覧には何地点が含まれているか
3. 最新の観測時刻はいつか（観測値は10分ごとに更新されている）
4. README.mdの分析記録に取得日時をメモしたか
````

データが取得できない場合は，次のリンクからダウンロード・解凍して`data/raw`に配置すること．

- [amedastable_json.zip](./analysis/9/data/raw/amedastable_json.zip)
- [amedas_latest_map_json.zip](./analysis/9/data/raw/amedas_latest_map_json.zip)

````{note} 演習2：JSONの中身を確認する
「JSONの構造確認」という見出しを作り，次のセルを順番に実行せよ．

**セル1：観測所一覧の1件を確認する**

```python
stations["44132"]
```

**セル2：観測値の1件を確認する**

```python
observations["44132"]
```

**セル3：観測所番号の上2桁を確認する**

観測所番号の上2桁は地域（府県）を表す番号になっている．

```python
for station_id in ["43056", "44132", "45212"]:
    print(station_id, stations[station_id]["kjName"])
```

実行後，次を確認せよ．

1. `lat`と`lon`はどのような形式で入っているか
2. 東京（44132）の現在の気温は何度か
3. 観測所番号の上2桁と観測所の場所にはどのような対応があるか
````

---

## 前処理：地図に載せる表を作る

### 度分形式の変換

`amedastable.json`の緯度・経度は`[度, 分]`の度分形式である．
地図用ライブラリは**度単位の小数**（十進度）を使うため，次の式で変換する．

$$
\text{十進度} = \text{度} + \frac{\text{分}}{60}
$$

例）東京（44132）の緯度`[35, 41.5]`は $35 + 41.5/60 \approx 35.6917$ 度となる．

### 観測所番号と都県の対応

観測所番号の上2桁は府県を表す番号になっており，関東の7都県は次の通りである．

| 上2桁 | 都県 |
| --- | --- |
| 40 | 茨城県 |
| 41 | 栃木県 |
| 42 | 群馬県 |
| 43 | 埼玉県 |
| 44 | 東京都 |
| 45 | 千葉県 |
| 46 | 神奈川県 |

````{note} 演習3：関東の観測所表を作る
「前処理：観測所表の作成」という見出しを作り，次のセルを順番に実行せよ．

**セル1：観測所一覧から関東の観測所を取り出す**

```python
import pandas as pd

PREF_CODES = {
    "40": "茨城県",
    "41": "栃木県",
    "42": "群馬県",
    "43": "埼玉県",
    "44": "東京都",
    "45": "千葉県",
    "46": "神奈川県",
}

rows = []

for station_id, info in stations.items():
    pref_code = station_id[:2]

    if pref_code not in PREF_CODES:
        continue

    lat = info["lat"][0] + info["lat"][1] / 60
    lon = info["lon"][0] + info["lon"][1] / 60

    rows.append({
        "観測所番号": station_id,
        "観測所名": info["kjName"],
        "都県名": PREF_CODES[pref_code],
        "緯度": round(lat, 4),
        "経度": round(lon, 4),
        "標高": info["alt"],
    })

station_df = pd.DataFrame(rows)

print("関東の観測所数:", len(station_df))
station_df.head()
```

**セル2：都県別の観測所数を確認する**

```python
station_df["都県名"].value_counts()
```

実行後，次を確認せよ．

1. 関東には何地点の観測所があるか
2. 緯度・経度は度単位の小数に変換されているか
3. 都県によって観測所数に違いはあるか
````

````{note} 演習4：最新気温を結合してCSVに保存する
「前処理：気温の結合」という見出しを作り，次のセルを順番に実行せよ．

**セル1：観測値JSONから気温を取り出して結合する**

観測所番号をキーにして，観測値JSONから気温を取り出す．
気温を観測していない観測所もあるため，`temp`がない場合は欠損（`None`）とする．

```python
temperatures = []

for station_id in station_df["観測所番号"]:
    record = observations.get(station_id, {})
    temp = record.get("temp")

    if temp is None:
        temperatures.append(None)
    else:
        temperatures.append(temp[0])

station_df["気温"] = temperatures

station_df.head()
```

**セル2：気温の欠損を確認する**

```python
missing_count = station_df["気温"].isna().sum()

print("気温が欠損している観測所数:", missing_count)
print("気温があるデータ数:", station_df["気温"].notna().sum())
```

**セル3：気温の分布を確認する**

地図に載せる前に，値の範囲をヒストグラムで確認する．

```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")

fig, ax = plt.subplots(figsize=(7, 4))

sns.histplot(data=station_df, x="気温", bins=10, ax=ax)

ax.set_title("関東の最新気温の分布")
ax.set_xlabel("気温（℃）")
ax.set_ylabel("観測所数")

plt.tight_layout()
plt.show()
```

**セル4：CSVに保存する**

```python
output_path = "../data/processed/amedas_kanto_temperature.csv"

station_df.to_csv(output_path, index=False)

print("saved:", output_path)
```

実行後，次を確認せよ．

1. 気温が欠損している観測所は何地点あるか（雨量だけを観測する観測所もある）
2. 気温はどの範囲に分布しているか
3. `data/processed/amedas_kanto_temperature.csv`が作成されたか
````

```{tip} 欠損は誤りとは限らない
アメダスには，気温・風・降水量などをすべて観測する観測所と，降水量だけを観測する観測所がある．
気温が欠損している行は，データの誤りではなく**そもそも気温を観測していない地点**である．
第6回で学んだ通り，欠損の理由を考えてから扱いを決めること．
```

---

## 地図上への可視化

### plotlyでインタラクティブな地図を作る

`plotly.express`の`scatter_map()`を使うと，緯度・経度を持つ表から地図上の散布図を作成できる．
Notebook上で拡大・縮小やマウスオーバーができるため，**データ観察**に向いている．

````{note} 演習5：plotlyで気温の地図を作る
「地図上への可視化」という見出しを作り，次のセルを順番に実行せよ．

**セル1：気温のある行だけを取り出す**

```python
plot_df = station_df.dropna(subset=["気温"]).copy()

print("地図に表示する観測所数:", len(plot_df))
```

**セル2：plotlyで地図上に表示する**

- `lat`，`lon`：点の位置に使う列
- `color="気温"`：気温に応じて点の色を変える
- `hover_name`：マウスオーバーで表示する名前

```python
import plotly.express as px

fig = px.scatter_map(
    plot_df,
    lat="緯度",
    lon="経度",
    color="気温",
    hover_name="観測所名",
    hover_data=["都県名", "標高", "気温"],
    color_continuous_scale="RdYlBu_r",
    zoom=7,
    height=600,
)

fig.show()
```

実行後，次を確認せよ．

1. 関東のどのあたりの気温が高いか・低いか
2. 標高の高い山間部（群馬県や栃木県の北部）と平野部で気温に違いはあるか
3. 海沿いと内陸で違いはあるか
4. マウスオーバーで観測所名と気温が表示されるか
````

### foliumでHTMLとして保存できる地図を作る

`folium`を使うと，地図をHTMLファイルとして保存できる．
Notebookを開かなくてもブラウザで確認できるため，**報告・共有**に向いている．

````{note} 演習6：foliumで気温の地図を作る
次のセルを順番に実行せよ．

**セル1：気温に応じた色を返す関数を作る**

```python
def temperature_color(temperature):
    if temperature < 15:
        return "blue"
    elif temperature < 20:
        return "green"
    elif temperature < 25:
        return "orange"
    else:
        return "red"
```

**セル2：foliumで地図を作る**

```python
import folium

center_lat = plot_df["緯度"].mean()
center_lon = plot_df["経度"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=8)

for _, row in plot_df.iterrows():
    popup_text = f"{row['観測所名']}（{row['都県名']}）<br>気温：{row['気温']}℃"

    folium.CircleMarker(
        location=[row["緯度"], row["経度"]],
        radius=6,
        popup=popup_text,
        color=temperature_color(row["気温"]),
        fill=True,
        fill_opacity=0.7,
    ).add_to(m)

m
```

**セル3：HTMLファイルとして保存する**

```python
m.save("../reports/figures/amedas_kanto_temperature_check.html")

print("saved: ../reports/figures/amedas_kanto_temperature_check.html")
```

実行後，次を確認せよ．

1. 保存したHTMLファイルをブラウザで開けるか
2. 点をクリックすると観測所名と気温が表示されるか
3. 色の区切り（15℃，20℃，25℃）は今日の気温分布に合っているか
````

````{warning} 課題1：気温の地図をPythonファイルで作成する
演習6で確認した内容を応用する．
以下のコードの`<HOGEHOGE1>`，`<HOGEHOGE2>`，`<PIYOPIYO1>`，`<PIYOPIYO2>`を適切に書き換えてpythonスクリプト`src/plot_amedas_temperature_map.py`を作成し，コードを実行してHTMLファイル`reports/figures/amedas_kanto_temperature_map.html`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_amedas_temperature_map.py`とHTMLファイル`reports/figures/amedas_kanto_temperature_map.html`を<span style="color:red">WebClass「第9回課題」問1・問2</span>から提出せよ．

```{tip} ポイント
いきなりpythonファイルを作成するのではなく，notebookで試験的にコードを実行し，うまくコードが走るようになってからpythonコードにコピーして実施すると書きやすい．
```

```python
from pathlib import Path

import folium
import pandas as pd

input_path = "data/processed/amedas_kanto_temperature.csv"
output_path = "reports/figures/amedas_kanto_temperature_map.html"

Path("reports/figures").mkdir(parents=True, exist_ok=True)

station_df = pd.read_csv(input_path)
plot_df = station_df.dropna(subset=[<HOGEHOGE1>]).copy()


def temperature_color(temperature):
    if temperature < 15:
        return "blue"
    elif temperature < 20:
        return "green"
    elif temperature < 25:
        return "orange"
    else:
        return "red"


center_lat = plot_df["緯度"].mean()
center_lon = plot_df[<HOGEHOGE2>].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=8)

for _, row in plot_df.iterrows():
    popup_text = f"{row['観測所名']}（{row['都県名']}）<br>気温：{row['気温']}℃"

    folium.CircleMarker(
        location=[row[<PIYOPIYO1>], row[<PIYOPIYO2>]],
        radius=6,
        popup=popup_text,
        color=temperature_color(row["気温"]),
        fill=True,
        fill_opacity=0.7,
    ).add_to(m)

m.save(output_path)

print("saved:", output_path)
```

作成したPythonファイルを`9`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_amedas_temperature_map.py
```

実行後，`reports/figures/amedas_kanto_temperature_map.html`が作成されていることを確認せよ．
````

<!--
````{dropdown} 解答例
- `<HOGEHOGE1>`：`"気温"`
- `<HOGEHOGE2>`：`"経度"`
- `<PIYOPIYO1>`：`"緯度"`
- `<PIYOPIYO2>`：`"経度"`
````
-->

````{warning} 課題2：緯度と気温の関係をPythonファイルで可視化する
地図で眺めた傾向を，通常の図でも確認する．
以下のコードの`<HOGEHOGE1>`，`<HOGEHOGE2>`，`<PIYOPIYO>`を適切に書き換えてpythonスクリプト`src/plot_amedas_lat_temperature.py`を作成し，コードを実行して画像ファイル`reports/figures/amedas_lat_temperature.png`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_amedas_lat_temperature.py`と画像ファイル`reports/figures/amedas_lat_temperature.png`を<span style="color:red">WebClass「第9回課題」問3・問4</span>から提出せよ．

本課題では，横軸を**緯度**，縦軸を**気温**とした散布図を作成し，都県名で色分けする．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

input_path = "data/processed/amedas_kanto_temperature.csv"
output_path = "reports/figures/amedas_lat_temperature.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

station_df = pd.read_csv(input_path)
plot_df = station_df.dropna(subset=["気温"]).copy()

fig, ax = plt.subplots(figsize=(7, 5))

sns.scatterplot(
    data=plot_df,
    x=<HOGEHOGE1>,
    y=<HOGEHOGE2>,
    hue=<PIYOPIYO>,
    s=60,
    ax=ax,
)

ax.set_title("関東の観測所の緯度と気温の関係")
ax.set_xlabel("緯度（度）")
ax.set_ylabel("気温（℃）")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```

作成したPythonファイルを`9`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_amedas_lat_temperature.py
```

実行後，次の点を確認せよ．

1. 緯度が高い（北にある）観測所ほど気温は低いか
2. 同じ緯度でも気温が大きく異なる観測所はあるか（標高の影響を考えよ）
3. 地図と散布図では，見えてくることがどのように違うか
````

<!--
````{dropdown} 解答例
- `<HOGEHOGE1>`：`"緯度"`
- `<HOGEHOGE2>`：`"気温"`
- `<PIYOPIYO>`：`"都県名"`
````
-->

---

## まとめ

- 地図上への可視化は，**場所ごとの違い・地域的な偏り**を確認するための切り口である
- アメダスのような観測データは，観測所一覧と観測値が別のJSONで提供されることがある
- 度分形式の緯度・経度は，**度 + 分/60**で度単位の小数に変換する
- 地図に載せる前に，欠損の有無と値の分布を確認する
- `plotly`はNotebook上でのデータ観察に，`folium`はHTMLとして保存する報告用の地図に向いている
- 気温の欠損は誤りではなく，気温を観測していない観測所であることを説明できるようにする
- 地図から読み取れること（地域差）と，読み取れないこと（原因）を分けて文章にする

次回はデータ分析実践Iとして行政統計を扱う．

- e-Statの統計ダッシュボードAPIから都道府県別の人口データを取得する
- テーマ設定からデータ取得・前処理・可視化・考察までを一気通貫で行う

### 課題の提出期限

<span style="color: red; ">6月16日(火)23:59まで</span>

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所から提出したものについて加点対象とします．

````{note} 課題3：湿度の地図を作成する

観測値JSONの`humidity`を使い，関東の最新湿度の地図を作成せよ．

`src/plot_amedas_humidity_map.py`を作成し，WebClass「第9回課題」問5から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるHTMLファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 湿度を観測している観測所は気温と同じか
2. 湿度の色分けの区切りはどのように決めたか
3. 気温の地図と湿度の地図に共通する傾向はあるか
````

````{note} 課題4：全国の気温地図を作成する

`PREF_CODES`による絞り込みをやめて，全国すべての観測所の気温を地図に表示せよ．

`src/plot_amedas_japan_map.py`を作成し，WebClass「第9回課題」問6から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるHTMLファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 南北で気温にどのような傾向があるか
2. 観測所数が増えると，地図の見やすさはどう変わるか
3. 色分けの区切りは関東だけのときと同じでよいか
````

````{note} 課題5：標高と気温の関係を可視化する

`amedas_kanto_temperature.csv`の`標高`列を使い，横軸を標高，縦軸を気温とした散布図を作成せよ．

`src/plot_amedas_alt_temperature.py`を作成し，WebClass「第9回課題」問7から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 標高が高いほど気温は低いか
2. 標高100mあたり何度くらい気温が下がっているように見えるか（気象学では約0.6℃とされる）
3. 緯度と標高のどちらが今日の気温の違いをよく説明しているか
````
