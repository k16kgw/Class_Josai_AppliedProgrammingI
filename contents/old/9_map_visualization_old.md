# 第9回　可視化II：地図上への可視化

### 前回の復習

第8回では，週間予報データを使い，折れ線グラフや棒グラフでデータを眺めた．
可視化は，データの傾向を知るために，色々な切り口からデータを眺める手法である．

| 第8回で見た切り口 | 確認できること | 図の例 |
| --- | --- | --- |
| 値の分布を見る | 値がどの範囲に多いか，外れた値があるか | ヒストグラム |
| 2つの値の関係を見る | 一方が大きいとき，もう一方も大きいか | 散布図 |
| 時間変化を見る | 日付に沿って値がどう変わるか | 折れ線グラフ |
| グループを比較する | 地域や地点によって違いがあるか | 棒グラフ，色分けした図 |

今回は，ここに新しい切り口を追加する．

| 今回追加する切り口 | 確認できること | 図の例 |
| --- | --- | --- |
| **場所ごとの違いを見る** | どの場所で値が大きいか，地域的な偏りがあるか | **地図上への可視化** |

```{tip} 地図にする意味
地図は「場所」を読むための図である．
同じ値でも，棒グラフで見る場合と地図上で見る場合では，気づきやすいことが異なる．
地図では，近い場所どうしが似ているか，海沿い・内陸・島しょ部で違いがあるか，といった空間的な傾向を眺めやすい．
```

### 今回の位置づけ

最終レポートでは，各自でデータを選び，**データ取得 → 前処理 → 可視化 → 考察**を一気通貫で行う．
第9回では，その練習として，気象庁の天気予報データを地図上に表示する．

今日の流れは次の通りである．

| 段階 | 内容 | 目的 |
| --- | --- | --- |
| 1 | 東京都の週間予報CSVを読み込む | 第8回までのデータを確認する |
| 2 | 地点名・地域名に緯度経度を対応させる | 予報データを地図に載せられる形にする |
| 3 | 東京都の気温データを地図上に表示する | 地図可視化の基本を試す |
| 4 | 東京都の降水確率データを地図上に表示する | 気温以外の予報値に応用する |
| 5 | 自分で選んだ複数地域の予報データを取得して地図化する | 最終レポートに向けた一気通貫の練習をする |

### 到達目標

- 位置情報を持たない表に，緯度・経度の表を結合して地図用データを作成できる
- `plotly`を使ってNotebook上でインタラクティブな地図を作成できる
- `folium`を使ってHTMLファイルとして保存できる地図を作成できる
- 気温と降水確率を，地図上で別々の見方として可視化できる
- 自分で選んだ複数地域の予報データを取得し，1つのCSVにまとめ，地図上に表示できる

---

## 準備

今回は新しくフォルダ`9`を作成して作業する．
第8回で作成した週間予報CSVを使うが，手元にない場合は下のリンクからダウンロードしてよい．

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

3. 第8回で作成した次の2つのCSVを`9/data/processed`にコピーする．

```text
data/processed/jma_tokyo_weekly_temperature.csv
data/processed/jma_tokyo_weekly_weather.csv
```

ファイルが手元にない場合は，次のリンクからダウンロード・解凍して`data/processed`に配置すること．

- [jma_tokyo_weekly_temperature_csv.zip](./analysis/5/data/processed/jma_tokyo_weekly_temperature_csv.zip)
- [jma_tokyo_weekly_weather_csv.zip](./analysis/5/data/processed/jma_tokyo_weekly_weather_csv.zip)

4. JupyterLabまたはVS Codeで`notebooks/map_visualization.ipynb`を新規作成する．

5. `README.md`を作成し，次の内容を記入する．

```markdown
# 応用プログラミングI 第9回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

気象庁の週間予報データを地図上に可視化する．

## 第9回 分析記録

- 元データ：
  - data/processed/jma_tokyo_weekly_temperature.csv
  - data/processed/jma_tokyo_weekly_weather.csv
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 観察用ノートブック：notebooks/map_visualization.ipynb（Gitでは管理しない）
- 作成するデータ：
  - data/processed/tokyo_temperature_points.csv
  - data/processed/tokyo_weather_area_points.csv
  - data/processed/tokyo_temperature_map_data.csv
  - data/processed/tokyo_pop_map_data.csv
- 作成するスクリプト：
  - src/plot_tokyo_pop_map.py
  - src/build_selected_forecast_map.py
- 出力する図：
  - reports/figures/tokyo_temperature_map_check.html
  - reports/figures/tokyo_pop_map.html
  - reports/figures/selected_forecast_map.html
- 可視化の目的：
  - 東京都の週間予報を地図上で確認する
  - 自分で選んだ複数地域の予報データを地図上に表示する
```

6. `.gitignore`を作成し，次の内容を記入する．

```gitignore
.DS_Store
*.swp
*~
.vscode/
.ipynb_checkpoints
*.ipynb
data/raw/
```

7. 作成したファイルをコミットする．

```bash
git add .
git commit -m "first commit"
```
````

---

## 地図上への可視化で考えること

地図上への可視化は，**位置情報**と**表示したい値**を組み合わせて行う．
地図に点を置くには，少なくとも次の情報が必要である．

| 必要な情報 | 例 | 今回の扱い |
| --- | --- | --- |
| 位置 | 緯度，経度 | 地点名・地域名に代表点の緯度経度を対応させる |
| 値 | 平均最高気温，平均降水確率 | 色や点の大きさで表す |
| 名前 | 東京，八丈島，父島，東京地方など | クリック時やマウスオーバー時に表示する |

今回使う気象庁の週間予報CSVには，`地点名`や`地域名`は含まれているが，緯度・経度は含まれていない．
そこで，次のように小さな対応表を自分で作成し，予報データに結合する．

```text
週間予報CSV
  地点名，最高気温，最低気温，降水確率など
        +
座標の対応表
  地点名，緯度，経度
        ↓
地図用データ
  地点名，緯度，経度，地図に表示したい値
```

```{tip} 代表点
「東京地方」「伊豆諸島」のような地域は，本来は面積を持つ範囲である．
今回はポイントマップの練習なので，地域全体を1つの点で代表させる．
このような点を**代表点**と呼ぶことにする．
代表点は便利だが，地域全体を正確に表しているわけではない点に注意する．
```

第9回では，次のライブラリを使う．

| ライブラリ | 主な役割 | この回での使い方 |
| --- | --- | --- |
| `pandas` | 表形式データの読み込み・確認・前処理 | CSVを読み込み，座標表と結合する |
| `plotly` | Notebook上のインタラクティブな地図 | 試験的に気温データを地図で眺める |
| `folium` | HTMLとして保存できる地図 | 課題として提出できる地図を作る |
| `requests` | Web上のデータ取得 | 複数地域の天気予報JSONを取得する |

---

## 使用するデータ

### 週間気温データ

```text
data/processed/jma_tokyo_weekly_temperature.csv
```

主な列：

- `地点名`
- `地点コード`
- `予報日`
- `最低気温`
- `最高気温`

このデータは，「東京」「八丈島」「父島」など，気温を予報する地点ごとの週間予報である．

### 週間天気データ

```text
data/processed/jma_tokyo_weekly_weather.csv
```

主な列：

- `地域名`
- `地域コード`
- `予報日`
- `天気コード`
- `降水確率`
- `信頼度`

このデータは，「東京地方」「伊豆諸島」「小笠原諸島」など，天気や降水確率を予報する地域ごとの週間予報である．

```{warning} 地点名と地域名は同じではない
気温データは`地点名`，天気データは`地域名`を使う．
「東京」と「東京地方」のように似ている名前もあるが，データ上は別の単位である．
そのため，気温用の座標表と降水確率用の座標表を分けて作成する．
```

---

## データを確認する

````{note} 演習1：CSVを読み込んで中身を確認する
`notebooks/map_visualization.ipynb`に「データの確認」という見出しを作り，次のセルを順番に実行せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

**セル2：必要なライブラリをインストールする**

初回のみ実行する．すでにインストール済みの場合はすぐに終了する．

```bash
!python -m pip install pandas plotly folium requests
```

**セル3：ライブラリを読み込む**

```python
from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import requests
```

**セル4：週間気温データを読み込む**

Notebookから実行するので，データのパスは`../data/processed/...`とする．

```python
temperature_path = "../data/processed/jma_tokyo_weekly_temperature.csv"

weekly_temperature_df = pd.read_csv(temperature_path)

print("行数・列数:", weekly_temperature_df.shape)
weekly_temperature_df.head()
```

**セル5：週間天気データを読み込む**

```python
weather_path = "../data/processed/jma_tokyo_weekly_weather.csv"

weekly_weather_df = pd.read_csv(weather_path)

print("行数・列数:", weekly_weather_df.shape)
weekly_weather_df.head()
```

**セル6：地点名と地域名を確認する**

```python
print("気温データの地点名")
print(weekly_temperature_df["地点名"].unique())

print()
print("天気データの地域名")
print(weekly_weather_df["地域名"].unique())
```

実行後，次を確認せよ．

1. 週間気温データにはどの地点が含まれているか
2. 週間天気データにはどの地域が含まれているか
3. 気温データと天気データで，場所を表す列名がどのように違うか
````

---

## 座標の対応表を作る

地図上に点を置くには，緯度と経度が必要である．
今回は練習として，次の代表点を使う．

| 用途 | 名前 | 緯度 | 経度 | 備考 |
| --- | --- | --- | --- | --- |
| 気温 | 東京 | 35.6895 | 139.6917 | 東京都庁付近 |
| 気温 | 八丈島 | 33.1030 | 139.7890 | 八丈島付近 |
| 気温 | 父島 | 27.0945 | 142.1918 | 父島付近 |
| 降水確率 | 東京地方 | 35.6895 | 139.6917 | 東京地方の代表点 |
| 降水確率 | 伊豆諸島 | 33.1030 | 139.7890 | 伊豆諸島の代表点 |
| 降水確率 | 小笠原諸島 | 27.0945 | 142.1918 | 小笠原諸島の代表点 |

````{note} 演習2：座標の対応表を作成する
「座標の対応表」という見出しを作り，次のセルを順番に実行せよ．

**セル1：気温地点の座標表を作る**

```python
temperature_point_df = pd.DataFrame({
    "地点名": ["東京", "八丈島", "父島"],
    "緯度": [35.6895, 33.1030, 27.0945],
    "経度": [139.6917, 139.7890, 142.1918],
})

temperature_point_df
```

**セル2：降水確率地域の座標表を作る**

```python
weather_area_point_df = pd.DataFrame({
    "地域名": ["東京地方", "伊豆諸島", "小笠原諸島"],
    "緯度": [35.6895, 33.1030, 27.0945],
    "経度": [139.6917, 139.7890, 142.1918],
})

weather_area_point_df
```

**セル3：座標表をCSVとして保存する**

```python
Path("../data/processed").mkdir(parents=True, exist_ok=True)

temperature_point_df.to_csv(
    "../data/processed/tokyo_temperature_points.csv",
    index=False
)
weather_area_point_df.to_csv(
    "../data/processed/tokyo_weather_area_points.csv",
    index=False
)

print("saved: ../data/processed/tokyo_temperature_points.csv")
print("saved: ../data/processed/tokyo_weather_area_points.csv")
```

実行後，次を確認せよ．

1. 気温データ用の座標表は`地点名`を持っているか
2. 降水確率データ用の座標表は`地域名`を持っているか
3. `data/processed`に2つのCSVが作成されたか
````

---

## 東京都の気温データを地図に表示する

まず，練習として東京都の週間気温データを地図上に表示する．
ここでは，地点ごとに週間の平均最高気温を計算し，地図上に表示する．

````{note} 演習3：気温データと座標表を結合する
「気温データの地図用データ作成」という見出しを作り，次のセルを順番に実行せよ．

**セル1：気温データの空欄を除く**

```python
temperature_plot_source_df = weekly_temperature_df.dropna(
    subset=["最低気温", "最高気温"]
).copy()

temperature_plot_source_df.head()
```

**セル2：地点ごとに平均最高気温を計算する**

ここでは，まだ複雑な集計関数を使わず，地点名ごとにデータを取り出して平均を計算する．

```python
temperature_summary_rows = []

for point_name in temperature_plot_source_df["地点名"].unique():
    point_df = temperature_plot_source_df[
        temperature_plot_source_df["地点名"] == point_name
    ]

    temperature_summary_rows.append({
        "地点名": point_name,
        "予報日数": len(point_df),
        "平均最低気温": round(point_df["最低気温"].mean(), 1),
        "平均最高気温": round(point_df["最高気温"].mean(), 1),
    })

temperature_summary_df = pd.DataFrame(temperature_summary_rows)

temperature_summary_df
```

**セル3：座標表を結合する**

```python
temperature_map_df = pd.merge(
    temperature_summary_df,
    temperature_point_df,
    on="地点名",
    how="left"
)

temperature_map_df
```

**セル4：地図用データを保存する**

```python
temperature_map_df.to_csv(
    "../data/processed/tokyo_temperature_map_data.csv",
    index=False
)

print("saved: ../data/processed/tokyo_temperature_map_data.csv")
```

実行後，次を確認せよ．

1. `平均最高気温`が計算されているか
2. `緯度`と`経度`が結合されているか
3. 緯度・経度が空欄になっている行はないか
````

````{note} 演習4：plotlyで気温データを地図上に表示する
「plotlyで地図表示」という見出しを作り，次のセルを実行せよ．

```python
fig = px.scatter_map(
    temperature_map_df,
    lat="緯度",
    lon="経度",
    color="平均最高気温",
    size="予報日数",
    hover_name="地点名",
    hover_data=["平均最低気温", "平均最高気温"],
    color_continuous_scale="RdYlBu_r",
    zoom=5,
    height=600,
)

fig.update_layout(
    title="東京都の週間予報：地点別の平均最高気温",
    map_style="open-street-map",
)

fig.show()
```

実行後，次を確認せよ．

1. 東京，八丈島，父島の3地点が表示されているか
2. 平均最高気温が高い地点はどこか
3. マウスオーバーで地点名と平均気温が表示されるか
````

````{note} 演習5：foliumで気温データをHTMLとして保存する
`folium`を使うと，地図をHTMLファイルとして保存できる．
Notebookを開かなくてもブラウザで確認できるため，提出用・共有用の地図に向いている．

**セル1：気温に応じた色を返す関数を作る**

```python
def temperature_color(value):
    if value < 24:
        return "blue"
    elif value < 26:
        return "orange"
    else:
        return "red"
```

**セル2：foliumで地図を作る**

```python
center_lat = temperature_map_df["緯度"].mean()
center_lon = temperature_map_df["経度"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=5)

for _, row in temperature_map_df.iterrows():
    popup_text = (
        f"{row['地点名']}<br>"
        f"平均最低気温：{row['平均最低気温']}℃<br>"
        f"平均最高気温：{row['平均最高気温']}℃"
    )

    folium.CircleMarker(
        location=[row["緯度"], row["経度"]],
        radius=8,
        popup=popup_text,
        color=temperature_color(row["平均最高気温"]),
        fill=True,
        fill_opacity=0.7,
    ).add_to(m)

m
```

**セル3：HTMLファイルとして保存する**

```python
m.save("../reports/figures/tokyo_temperature_map_check.html")

print("saved: ../reports/figures/tokyo_temperature_map_check.html")
```

実行後，次を確認せよ．

1. 保存したHTMLファイルをブラウザで開けるか
2. 点をクリックすると地点名と気温が表示されるか
3. 色の区切りは今回の気温分布に合っているか
````

---

## 課題

````{warning} 課題1：東京都の降水確率を地図上に表示する
演習3〜5で確認した内容を応用する．
以下のコードの`<HOGEHOGE1>`〜`<HOGEHOGE5>`，`<PIYOPIYO1>`，`<PIYOPIYO2>`を適切に書き換えてpythonスクリプト`src/plot_tokyo_pop_map.py`を作成し，コードを実行してHTMLファイル`reports/figures/tokyo_pop_map.html`を作成せよ．  
最後に，作成したpythonスクリプト`src/plot_tokyo_pop_map.py`とHTMLファイル`reports/figures/tokyo_pop_map.html`を<span style="color:red">WebClass「第9回課題」問1・問2</span>から提出せよ．

```{tip} ポイント
いきなりpythonファイルを作成するのではなく，notebookで試験的にコードを実行し，うまくコードが走るようになってからpythonコードにコピーして実施すると書きやすい．
```

```python
from pathlib import Path

import folium
import pandas as pd

weather_path = "data/processed/jma_tokyo_weekly_weather.csv"
point_path = "data/processed/tokyo_weather_area_points.csv"
output_data_path = "data/processed/tokyo_pop_map_data.csv"
output_map_path = "reports/figures/tokyo_pop_map.html"

Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("reports/figures").mkdir(parents=True, exist_ok=True)

weekly_weather_df = pd.read_csv(weather_path)
weather_area_point_df = pd.read_csv(point_path)

weather_plot_source_df = weekly_weather_df.dropna(subset=[<HOGEHOGE1>]).copy()

pop_summary_rows = []

for area_name in weather_plot_source_df[<HOGEHOGE2>].unique():
    area_df = weather_plot_source_df[
        weather_plot_source_df[<HOGEHOGE2>] == area_name
    ]

    pop_summary_rows.append({
        "地域名": area_name,
        "予報日数": len(area_df),
        "平均降水確率": round(area_df[<HOGEHOGE3>].mean(), 1),
        "最大降水確率": area_df[<HOGEHOGE3>].max(),
    })

pop_summary_df = pd.DataFrame(pop_summary_rows)

pop_map_df = pd.merge(
    pop_summary_df,
    weather_area_point_df,
    on=<HOGEHOGE4>,
    how="left"
)

pop_map_df.to_csv(output_data_path, index=False)


def pop_color(value):
    if value < 40:
        return "green"
    elif value < 60:
        return "orange"
    else:
        return "red"


center_lat = pop_map_df[<HOGEHOGE5>].mean()
center_lon = pop_map_df["経度"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=5)

for _, row in pop_map_df.iterrows():
    popup_text = (
        f"{row['地域名']}<br>"
        f"平均降水確率：{row['平均降水確率']}%<br>"
        f"最大降水確率：{row['最大降水確率']}%"
    )

    folium.CircleMarker(
        location=[row[<PIYOPIYO1>], row[<PIYOPIYO2>]],
        radius=8 + row["平均降水確率"] / 10,
        popup=popup_text,
        color=pop_color(row["平均降水確率"]),
        fill=True,
        fill_opacity=0.7,
    ).add_to(m)

m.save(output_map_path)

print("saved:", output_data_path)
print("saved:", output_map_path)
```

作成したPythonファイルを`9`フォルダ内でターミナルから実行せよ．

```bash
python src/plot_tokyo_pop_map.py
```

実行後，次の点を確認せよ．

1. `reports/figures/tokyo_pop_map.html`が作成されているか
2. 東京地方，伊豆諸島，小笠原諸島が表示されているか
3. 平均降水確率が高い地域ほど，点が大きく表示されているか
4. 作成した地図から，どの地域の降水確率が高いと言えそうか
````

<!--
````{dropdown} 解答例
- `<HOGEHOGE1>`：`"降水確率"`
- `<HOGEHOGE2>`：`"地域名"`
- `<HOGEHOGE3>`：`"降水確率"`
- `<HOGEHOGE4>`：`"地域名"`
- `<HOGEHOGE5>`：`"緯度"`
- `<PIYOPIYO1>`：`"緯度"`
- `<PIYOPIYO2>`：`"経度"`
````
-->

````{warning} 課題2：複数地域の天気予報データを取得して日本地図上に表示する
自分で選んだ複数の地域について，気象庁の天気予報JSONを取得し，それらを1つのCSVファイルにまとめ，日本地図上に何かしらの予報データを表示せよ．  
最後に，作成したpythonスクリプト`src/build_selected_forecast_map.py`とHTMLファイル`reports/figures/selected_forecast_map.html`を<span style="color:red">WebClass「第9回課題」問3・問4</span>から提出せよ．

提出するHTMLでは，次のいずれかを地図上に表示すること．

- 平均降水確率
- 最大降水確率
- 信頼度Aの件数
- 最高気温の平均
- 自分で説明できる別の予報値

作成されるCSVファイル`data/processed/selected_forecast_map_data.csv`は提出しなくてよいが，スクリプトを実行したときに作成されるようにすること．

### 条件

1. 3つ以上の地域を自分で選ぶ．
2. 気象庁の予報JSONを`requests`で取得する．
3. 取得したデータを1つのCSVファイルにまとめる．
4. 地図上に点を表示し，色または大きさで予報値の違いを表す．
5. HTMLファイルとして保存する．

### 気象庁の予報JSONのURL

都府県などの発表区域コードを使って，次のURLからJSONを取得できる．

```text
https://www.jma.go.jp/bosai/forecast/data/forecast/<発表区域コード>.json
```

例：

| 地域 | 発表区域コード | URL |
| --- | --- | --- |
| 東京都 | `130000` | `https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json` |
| 神奈川県 | `140000` | `https://www.jma.go.jp/bosai/forecast/data/forecast/140000.json` |
| 埼玉県 | `110000` | `https://www.jma.go.jp/bosai/forecast/data/forecast/110000.json` |
| 千葉県 | `120000` | `https://www.jma.go.jp/bosai/forecast/data/forecast/120000.json` |

### 作成するCSVの例

平均降水確率を地図に載せる場合，CSVは次のような列を持つとよい．

| 列名 | 内容 |
| --- | --- |
| `発表区域名` | 東京都，神奈川県など |
| `地域名` | 東京地方，東部，西部など |
| `地域コード` | 気象庁の地域コード |
| `予報日数` | 集計に使った日数 |
| `平均降水確率` | 降水確率の平均 |
| `最大降水確率` | 降水確率の最大値 |
| `緯度` | 地図表示に使う代表点の緯度 |
| `経度` | 地図表示に使う代表点の経度 |

### 進め方

1. まず，どの地域のデータを取得するか決める．
2. それぞれのURLからJSONを取得する．
3. `data[1]["timeSeries"][0]`から週間の天気・降水確率を取り出す．
4. 地域ごとに平均降水確率などを計算する．
5. 地域名に代表点の緯度・経度を対応させる．
6. 1つのCSVファイルとして保存する．
7. `folium`で地図を作り，HTMLとして保存する．

### コードの骨組み

次の骨組みを参考にしてよい．
ただし，`FORECAST_AREAS`と`AREA_POINTS`は，自分で選んだ地域に合わせて変更すること．

```python
from pathlib import Path

import folium
import pandas as pd
import requests

FORECAST_AREAS = {
    "東京都": "130000",
    "神奈川県": "140000",
    "埼玉県": "110000",
}

AREA_POINTS = {
    "東京地方": {"緯度": 35.6895, "経度": 139.6917},
    "東部": {"緯度": 35.4478, "経度": 139.6425},
    "西部": {"緯度": 35.4667, "経度": 139.6222},
    "秩父地方": {"緯度": 35.9917, "経度": 139.0856},
}

output_data_path = "data/processed/selected_forecast_map_data.csv"
output_map_path = "reports/figures/selected_forecast_map.html"

Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("reports/figures").mkdir(parents=True, exist_ok=True)

rows = []

for office_name, office_code in FORECAST_AREAS.items():
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{office_code}.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    weekly_forecast = data[1]
    weather_series = weekly_forecast["timeSeries"][0]
    time_defines = weather_series["timeDefines"]

    for area in weather_series["areas"]:
        area_name = area["area"]["name"]
        area_code = area["area"]["code"]
        pops = []

        for i, forecast_time in enumerate(time_defines):
            pop_text = area["pops"][i]
            if pop_text != "":
                pops.append(int(pop_text))

        if len(pops) == 0:
            continue

        if area_name not in AREA_POINTS:
            continue

        rows.append({
            "発表区域名": office_name,
            "地域名": area_name,
            "地域コード": area_code,
            "予報日数": len(pops),
            "平均降水確率": round(sum(pops) / len(pops), 1),
            "最大降水確率": max(pops),
            "緯度": AREA_POINTS[area_name]["緯度"],
            "経度": AREA_POINTS[area_name]["経度"],
        })

map_df = pd.DataFrame(rows)
map_df.to_csv(output_data_path, index=False)


def pop_color(value):
    if value < 40:
        return "green"
    elif value < 60:
        return "orange"
    else:
        return "red"


m = folium.Map(location=[36.0, 138.5], zoom_start=5)

for _, row in map_df.iterrows():
    popup_text = (
        f"{row['発表区域名']}：{row['地域名']}<br>"
        f"平均降水確率：{row['平均降水確率']}%<br>"
        f"最大降水確率：{row['最大降水確率']}%"
    )

    folium.CircleMarker(
        location=[row["緯度"], row["経度"]],
        radius=8 + row["平均降水確率"] / 10,
        popup=popup_text,
        color=pop_color(row["平均降水確率"]),
        fill=True,
        fill_opacity=0.7,
    ).add_to(m)

m.save(output_map_path)

print("saved:", output_data_path)
print("saved:", output_map_path)
```

```{tip} 座標表を増やす
選んだ地域の`地域名`が`AREA_POINTS`にない場合，地図に表示されない．
その場合は，自分で代表点の緯度・経度を調べて`AREA_POINTS`に追加する．
地図に載せるには，データの値だけでなく，場所を表す情報が必要である．
```

実行後，次の点を確認せよ．

1. `data/processed/selected_forecast_map_data.csv`が作成されたか
2. 選んだ地域が3つ以上，CSVに含まれているか
3. `reports/figures/selected_forecast_map.html`が作成されたか
4. 地図上の色や大きさが，選んだ予報値に対応しているか
5. その地図から読み取れる傾向を，1〜2文で説明できるか
````

---

## まとめ

- 地図上への可視化では，値だけでなく**緯度・経度**が必要である
- 予報データに緯度・経度がない場合は，地点名・地域名と座標の対応表を作成する
- 地域を1点で表す場合，その点は地域全体ではなく**代表点**である
- `plotly`はNotebook上で試験的に地図を眺めるのに向いている
- `folium`はHTMLとして保存し，提出・共有する地図を作るのに向いている
- 最終レポートでは，データ取得，前処理，可視化，考察までの流れを自分で組み立てる

次回はデータ分析実践Iとして行政統計を扱う．
気象データ以外のオープンデータを使い，テーマ設定，データ取得，前処理，可視化までを一通り行う．

### 課題の提出期限

<span style="color: red; ">6月16日(火)23:59まで</span>

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所から提出したものについて加点対象とします．

````{note} 課題3：気温を使って複数地域の地図を作成する

課題2では降水確率を例にした．
同じように，複数地域の週間気温データを取得し，平均最高気温を日本地図上に表示せよ．

`src/build_selected_temperature_map.py`を作成し，WebClass「第9回課題」問5から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるHTMLファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 選んだ地域の中で平均最高気温が高い地域はどこか
2. 気温を予報する`地点名`と，天気を予報する`地域名`はどのように違うか
3. 降水確率の地図と気温の地図では，見え方がどのように違うか
````

````{note} 課題4：点の色分けを工夫する

課題2で作成した地図について，色分けの区切りを自分で変更し，より見やすい地図にせよ．

`src/build_selected_forecast_map_color.py`を作成し，WebClass「第9回課題」問6から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるHTMLファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 変更前の色分けでは何が見にくかったか
2. 変更後の色分けでは何が見やすくなったか
3. 値の範囲を確認してから色分けを決めたか
````
