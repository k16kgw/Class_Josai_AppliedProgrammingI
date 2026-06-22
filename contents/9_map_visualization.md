# 第9回　地図上への可視化

### 前回の復習

可視化：データの傾向を知るために様々な切り口からデータを眺める手法

週間予報データを使い折れ線グラフや棒グラフでデータを眺めた．

| 何を見るか | 確認できること | 図の例 |
| --- | --- | --- |
| 値の分布を見る | 値がどの範囲に多いか，外れた値があるか | ヒストグラム |
| 2つの値の関係を見る | 一方が大きいとき，もう一方も大きいか | 散布図 |
| 連続的な変化を見る | 日付に沿って値がどう変わるか | 折れ線グラフ |
| グループを比較する | 地域や地点によって違いがあるか | 棒グラフ，色分けした図 |

### 到達目標

次の視点を追加する．

| 何を見るか | 確認できること | 図の例 |
| --- | --- | --- |
| **場所ごとの違いを見る** | どの場所で値が大きいか，地域的な偏りがあるか | **地図上への可視化** |

- 気象庁の天気予報JSONから，地図上に表示するための表を作成する
- 位置情報を持たない表に，緯度・経度・標高を持つCSVを結合する
- `plotly`を使い，Notebook上でインタラクティブな地図を作成する
- `plotly`の`write_html`を使い，HTMLファイルとして保存できる地図を作成する
- 位置情報に関連する情報を付加して可視化する

```{tip} 地図上に可視化する意味
空間的な位置情報は多くの情報を包含している．
現実世界の現象の多くは3次元空間に紐づけられており，その空間の情報を引きずっていることが多々ある．
地図上にデータを可視化することで空間的な傾向を眺めやすくなる．

例えば，地図上に可視化することで，近い場所で似ているのか，海沿い・内陸・山地・島しょ部で違いがあるかといった空間的な傾向を眺めやすくなる．
```

**今回の流れ**

| 段階 | 内容 | 目的 |
| --- | --- | --- |
| 1 | 第5回で取得した東京都の天気予報JSONを読み込む | これまで扱ったデータを再利用する |
| 2 | 週間予報から降水確率を取り出す | 地図に載せる値を作る |
| 3 | 地域名に緯度・経度・標高を結合する | 地図に載せられる表にする |
| 4 | 東京都の予報データを地図上に表示する | 地図可視化の基本を確認する |
| 5 | 東京都・埼玉県・長野県・新潟県のJSONをAPIで取得する | 複数都道府県のデータ取得を練習する |
| 6 | 降水確率と標高を地図上に重ねて表示する | 複数の情報を同時に眺める |
| 7 | 各自で好きな都道府県を追加する | 最終レポートに向けた応用練習をする |

### 準備

今回は新しくフォルダ`9`を作成して作業する．
第5回で取得した`jma_tokyo_forecast.json`を使うので，手元にない場合は下のリンクからダウンロードしてよい．

````{note} 演習0：作業フォルダを作成する

1. ターミナルを起動し，次のコマンドを順に実行する．

```bash
cd /Users/<ユーザ名>/applied_programming_i
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
│   │   └── jma_tokyo_forecast.json
│   └── processed/
├── reports/
│   └── figures/
├── src/
└── README.md
```

3. 第5回で作成した`5/data/raw/jma_tokyo_forecast.json`を`9/data/raw`にコピーする．

ファイルが手元にない場合は，次のリンクからダウンロード・解凍して`data/raw`に配置すること．

- [jma_tokyo_forecast_json.zip](./analysis/5/data/raw/jma_tokyo_forecast_json.zip)

4. JupyterLabまたはVS Codeで`notebooks/map_visualization.ipynb`を新規作成する．

5. `README.md`を作成し，次の内容を記入する．

```markdown
# 応用プログラミングI 第9回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

気象庁の天気予報JSONから地図用データを作成し，降水確率と標高を地図上に可視化する．

## 第9回 分析記録

- 元データ：
  - data/raw/jma_tokyo_forecast.json
  - 気象庁の天気予報JSON API
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json など
- 観察用ノートブック：notebooks/map_visualization.ipynb（Gitでは管理しない）
- 予報地域・アメダス対応データ：data/processed/forecast_area_points.csv（気象庁JSONから作成）
- 作成するデータ：
  - data/processed/tokyo_weekly_weather_from_json.csv
  - data/processed/tokyo_forecast_map_data.csv
  - data/processed/multi_pref_weekly_weather.csv
  - data/processed/multi_pref_forecast_map_data.csv
- 作成するスクリプト：
  - src/build_my_forecast_map.py
- 出力する図：
  - reports/figures/tokyo_pop_map_check.html
  - reports/figures/multi_pref_pop_map.html
  - reports/figures/multi_pref_elevation_map.html
  - reports/figures/multi_pref_pop_elevation_map.html
  - reports/figures/my_forecast_pop_elevation_map.html
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

## 地図上への可視化

地図上への可視化は，**位置情報**と**表示したい値**を組み合わせて行う．
地図に点を置くには，少なくとも次の情報が必要である．

| 必要な情報 | 例 | 今回の扱い |
| --- | --- | --- |
| 位置 | 緯度，経度 | アメダス地点情報から取得する |
| 値 | 平均降水確率，最大降水確率，標高 | 色や点の大きさで表す |
| 名前 | 東京地方，北部，中部など | クリック時やマウスオーバー時に表示する |

````{tip} 注意
気象庁の天気予報JSONには`地域名`や`地域コード`は含まれているが，緯度・経度・標高は含まれていないため，別に情報を取得してCSVを結合する必要がある．

気象庁の天気予報では予報地域に対応する代表的なアメダス地点が別のJSONで公開されている．
今回はそのアメダス地点を地図に載せるための代表点として使う．

```text
天気予報JSONから作った表
  発表区域名，地域名，平均降水確率，最大降水確率など
        +
予報地域・アメダス対応CSV
  発表区域名，地域名，アメダス地点名，緯度，経度，標高
        ↓
地図用データ
  発表区域名，地域名，アメダス地点名，緯度，経度，標高，平均降水確率，最大降水確率など
```
````

今回は次のライブラリを使う．

| ライブラリ | 主な役割 | この回での使い方 |
| --- | --- | --- |
| `json` | JSONファイルの読み込み | 第5回で取得したJSONを読み込む |
| `requests` | Web上のデータ取得 | 複数都道府県の天気予報JSONを取得する |
| `pandas` | 表形式データの作成・確認・前処理 | JSONから表を作り，アメダス地点情報を結合する |
| `plotly` | インタラクティブな地図の作成・保存 | Notebook上で地図を眺め，HTMLとして保存する |

---

## 使用するデータ

### 気象庁の天気予報JSON

前半では第5回で取得した東京都の天気予報JSONを使う．

```text
data/raw/jma_tokyo_forecast.json
```

後半では次のURLから複数都道府県の天気予報JSONを取得する．

```text
https://www.jma.go.jp/bosai/forecast/data/forecast/<発表区域コード>.json
```

| 発表区域名 | 発表区域コード | 今回の扱い |
| --- | --- | --- |
| 東京都 | `130000` | 第5回のJSONとAPI取得の両方で使う |
| 埼玉県 | `110000` | APIで取得する |
| 長野県 | `200000` | APIで取得する |
| 新潟県 | `150000` | APIで取得する |

各区域のコードは次のJSONから確認することができる．

https://www.jma.go.jp/bosai/common/const/area.json

### 区域の地図上の表示

地図上に表示するには各地点の緯度・経度情報が必要である．
そこで，予報区域とアメダス地点の対応，アメダス地点とその緯度・経度情報の対応から予報区域の緯度・経度を定める．

- 予報区域コードとアメダス地点の対応は次のJSONから確認することができる．

    https://www.jma.go.jp/bosai/forecast/const/forecast_area.json

    後のプログラムではこのJSONファイルを `data/raw/forecast_area.json` に保存する．

- アメダス地点とその緯度・経度の対応は次のJSONから確認することができる．

    https://www.jma.go.jp/bosai/amedas/const/amedastable.json

    後のプログラムではこのJSONファイルを `data/raw/amedastable.json` に保存する．

ここから予報区域にアメダス地点の緯度・経度・標高を対応させたCSVを作成する．

```text
data/processed/forecast_area_points.csv
```

主な列：

- `発表区域名`
- `発表区域コード`
- `地域名`
- `地域コード`
- `細分地域名`
- `細分地域コード`
- `アメダス番号`
- `アメダス地点名`
- `緯度`
- `経度`
- `標高`
- `予報区域対応取得元`
- `座標標高取得元`

<!-- 
このデータは，次の2段階で作成する．

| 手順 | 使うJSON | 取得するもの |
| --- | --- | --- |
| 1 | 気象庁`forecast_area.json` | 予報地域コードとアメダス番号の対応 |
| 2 | 気象庁`amedastable.json` | アメダス地点の緯度・経度・標高 |
 -->
<!-- 
```{tip} 予報地域と細分地域
週間予報で使われる地域の細かさは，都道府県によって異なる．
例えば東京都は「東京地方」「伊豆諸島」「小笠原諸島」に分かれるが，埼玉県・長野県・新潟県の週間予報は県全体で出る．
一方，アメダス地点との対応は「南部」「北部」「中部」などの細分地域を持つことがある．
このため，今回作るCSVでは，予報データと結合するための`地域名`・`地域コード`と，アメダス対応を確認するための`細分地域名`・`細分地域コード`を分けて保存する．
```
 -->
<!-- 
```{tip} 地域名だけで結合しない
「北部」「中部」「南部」のような地域名は，複数の都道府県で使われることがある．
そのため，`地域名`だけで結合すると別の都道府県の座標が混ざる可能性がある．
今回は`発表区域名`と`地域名`の2つをキーにして結合する．
```
 -->
<!--  
```{tip} アメダス地点は予報区域そのものではない
ここで使う緯度・経度・標高は，予報地域に対応するアメダス地点の値である．
例えば「長野県中部」という予報地域全体の標高ではなく，対応するアメダス地点である「松本」「諏訪」「軽井沢」などの標高である．
地図上に表示するときは，予報地域の厳密な範囲ではなく，予報地域を点で眺めるための代表地点として扱う．
```
 -->

---

## 東京都のJSONを地図用データにする

まず，第5回で取得した東京都のJSONを使う．
ここでは，週間予報に含まれる`降水確率`を取り出し，地域ごとの平均降水確率を地図上に表示する．

### 生データのJSONファイルから週間予報のCSVファイルを作成する

第5回で取得した`data/raw/jma_tokyo_forecast.json`から，週間予報の降水確率を取り出し，`data/processed/tokyo_weekly_weather_from_json.csv`を作成する．
この処理はNotebookではなく，Pythonファイルにまとめてターミナルから実行する．

1. ターミナルで`9`フォルダに移動する

    ```bash
    cd /Users/<ユーザ名>/applied_programming_i/9
    ```

2. ターミナルで後で必要になるライブラリをインストールする

    ```bash
    python -m pip install pandas plotly requests
    ```

    `python`コマンドが動かない場合は，次の`python3`で実行する．

    ```bash
    python3 -m pip install pandas plotly requests
    ```

3. Pythonファイルをダウンロードする

    次のリンクを右クリックし，リンクアドレスをコピーする．

    [build_tokyo_weekly_weather_from_json_py.zip](./analysis/9/src/build_tokyo_weekly_weather_from_json_py.zip)

    コピーしたURLを使って，ターミナルで次のコマンドを実行する．
    `<コピーしたURL>`の部分は，コピーしたリンクアドレスに置き換えること．

    ```bash
    curl -L "<コピーしたURL>" -o src/build_tokyo_weekly_weather_from_json_py.zip
    ```

4. zipを解凍する

    ```bash
    unzip -o src/build_tokyo_weekly_weather_from_json_py.zip -d src
    ```

    解凍後，ファイル `src/build_tokyo_weekly_weather_from_json.py` があることを確認する．

5. ターミナルでPythonファイルを実行する

    ```bash
    python src/build_tokyo_weekly_weather_from_json.py
    ```

    `python`コマンドが動かない場合は，次のように`python3`で実行する．

    ```bash
    python3 src/build_tokyo_weekly_weather_from_json.py
    ```

実行後，次を確認する．

- `data/processed/tokyo_weekly_weather_from_json.csv`が作成されたか
- ターミナルに行数・列数，地域名，降水確率が空欄の行数が表示されたか
- エラーが出た場合，`data/raw/jma_tokyo_forecast.json`が`9`フォルダ内にあるか

作成されたCSVファイルの中身を確認する．

````{note} 演習1：作成したCSVをNotebookで確認する
`notebooks/map_visualization.ipynb`に「東京都の週間予報CSVを確認する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：Notebookで必要なライブラリをインストールする**

このNotebookで実行しているPythonに必要なライブラリをインストールする．

```bash
%pip install pandas plotly requests
```

**セル2：ライブラリを読み込む**

```python
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
```

**セル3：作成したCSVを読み込む**

Notebookから実行するので，データのパスは`../data/processed/...`とする．

```python
tokyo_weather_path = "../data/processed/tokyo_weekly_weather_from_json.csv"

tokyo_weather_df = pd.read_csv(tokyo_weather_path)

tokyo_weather_df.head()
```

**セル4：表の形と空欄を確認する**

```python
print("行数・列数:", tokyo_weather_df.shape)
print("地域名:", tokyo_weather_df["地域名"].unique())
print("降水確率が空欄の行数:", tokyo_weather_df["降水確率"].isna().sum())

tokyo_weather_df[["降水確率"]].describe()
```

実行後，次を確認せよ．

1. `降水確率`は数値として扱われているか
2. 空欄になっている降水確率はあるか
3. `tokyo_weather_df`として表を読み込めているか
````

### 予報地域とアメダスのデータを対応させるCSVファイルを作成する

1. 取得する発表区域を定義する

    今回は，東京都・埼玉県・長野県・新潟県を扱う．
    発表区域コードは文字列として扱う．
    先頭が`0`のコードもあるため，数値ではなく文字列にしておく．

    ```python
    FORECAST_OFFICES = {
        "東京都": "130000",
        "埼玉県": "110000",
        "長野県": "200000",
        "新潟県": "150000",
    }
    ```

2. 予報地域・アメダス地点に関するJSONを取得する

   - `area.json`：発表区域や予報地域の名前を確認するためのJSON
   - `forecast_area.json`：予報地域コードとアメダス番号の対応を持つJSON
   - `amedastable.json`：アメダス地点の緯度・経度・標高を持つJSON

   ```python
   area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
   forecast_area_url = "https://www.jma.go.jp/bosai/forecast/const/forecast_area.json"
   amedas_url = "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"

   area_response = requests.get(area_url)
   area_response.raise_for_status()
   area_data = area_response.json()

   forecast_area_response = requests.get(forecast_area_url)
   forecast_area_response.raise_for_status()
   forecast_area_data = forecast_area_response.json()

   amedas_response = requests.get(amedas_url)
   amedas_response.raise_for_status()
   amedas_data = amedas_response.json()

   print("area.jsonに含まれる発表区域数:", len(area_data["offices"]))
   print("forecast_area.jsonに含まれる発表区域数:", len(forecast_area_data))
   print("amedastable.jsonに含まれるアメダス地点数:", len(amedas_data))
   ```

3. データを眺める（特に`class10`）

    `forecast_area.json`の中には，`class10`，`class20`，`amedas`という値が入っている．
    このうち今回使用するのは`class10`と`amedas`である．

    | 項目 | 意味 | 今回の使い方 |
    | --- | --- | --- |
    | `class10` | 予報で使われる細分地域のコード | `area.json`の`class10s`と照合して，細分地域名を取り出す |
    | `amedas` | 対応するアメダス地点番号 | `amedastable.json`と照合して，緯度・経度・標高を取り出す |
    | `class20` | 市区町村など，さらに細かい地域のコード | 今回の地図作成では使わない |

    `area.json`の中身をそのまま眺める．

    ```python
    area_data.keys()
    ```
    ```{dropdown} 出力
    dict_keys(['centers', 'offices', 'class10s', 'class15s', 'class20s'])
    ```

    東京都の`forecast_area.json`の中身をそのまま眺める．

    ```python
    forecast_area_data["130000"]
    ```
    ```{dropdown} 出力
    [{'class10': '130010', 'amedas': ['44132'], 'class20': '1310100'},  
    {'class10': '130020', 'amedas': ['44172'], 'class20': '1336100'},  
    {'class10': '130030', 'amedas': ['44263'], 'class20': '1340100'},  
    {'class10': '130040', 'amedas': ['44301'], 'class20': '1342100'}]  
    ```

    次に，`class10`のコードを地域名に変換して表示する．

    ```python
    for item in forecast_area_data["130000"]:
        class10_code = item["class10"]
        class10_name = area_data["class10s"][class10_code]["name"]

        print(
            class10_code,
            class10_name,
            "amedas:",
            item["amedas"],
            "class20:",
            item["class20"],
        )
    ```
    ```{dropdown} 出力
    130010 東京地方 amedas: ['44132'] class20: 1310100
    130020 伊豆諸島北部 amedas: ['44172'] class20: 1336100
    130030 伊豆諸島南部 amedas: ['44263'] class20: 1340100
    130040 小笠原諸島 amedas: ['44301'] class20: 1342100
    ```

    ````{tip} 注意
    `class10`は予報地域を表す便利なコードであるが，週間予報の地域区分と完全に一致しない場合がある．
    例えば東京都では，`forecast_area.json`では「伊豆諸島北部」「伊豆諸島南部」に分かれているが，週間予報では「伊豆諸島」としてまとめて表示される．
    このような違いを次のセルで前処理する．

    ```python
    def to_weekly_forecast_area(office_name, office_code, class10_code, class10_name):
        if office_code == "130000" and class10_code in {"130020", "130030"}:
            return "130100", "伊豆諸島"

        if office_code == "130000":
            return class10_code, class10_name

        return office_code, office_name
    ```
    ````

4. 前処理（度分形式を小数の緯度・経度に変換する関数を作る）

    `amedastable.json`の緯度(latitude)・経度(longitude)は`[度, 分]`の形で入っている．
    地図では小数の緯度・経度を使うため，`度 + 分/60`に変換する．

    ```python
    def degree_minute_to_decimal(value):
        return value[0] + value[1] / 60
    ```

````{note} 演習3：予報地域・アメダス対応CSVを作成する

「予報地域・アメダス対応データを作る」という見出しを作り，次のセルを順番に実行せよ．

**セル1（データの結合）：予報地域とアメダス地点を対応させた表を作る**

1つの予報地域に複数のアメダス地点が対応している場合がある．
その場合，地図上には同じ予報値を持つ点が複数表示される．

```python
point_rows = []

for office_name, office_code in FORECAST_OFFICES.items():
    for item in forecast_area_data[office_code]:
        class10_code = item["class10"]
        class10_name = area_data["class10s"][class10_code]["name"]
        forecast_area_code, forecast_area_name = to_weekly_forecast_area(
            office_name,
            office_code,
            class10_code,
            class10_name,
        )

        for amedas_id in item["amedas"]:
            amedas_info = amedas_data[amedas_id]

            lat = degree_minute_to_decimal(amedas_info["lat"]) # latitude
            lon = degree_minute_to_decimal(amedas_info["lon"]) # longitude

            point_rows.append({
                "発表区域名": office_name,
                "発表区域コード": office_code,
                "地域名": forecast_area_name,
                "地域コード": forecast_area_code,
                "細分地域名": class10_name,
                "細分地域コード": class10_code,
                "アメダス番号": amedas_id,
                "アメダス地点名": amedas_info["kjName"],
                "緯度": round(lat, 6),
                "経度": round(lon, 6),
                "標高": amedas_info["alt"],
                "予報区域対応取得元": "気象庁 forecast_area.json",
                "座標標高取得元": "気象庁 amedastable.json",
            })

point_df = pd.DataFrame(point_rows)

point_df
```

**セル2：CSVとして保存する**

```python
point_df.to_csv(
    "../data/processed/forecast_area_points.csv",
    index=False
)

print("saved: ../data/processed/forecast_area_points.csv")
```

**セル3：1つの予報地域に複数のアメダス地点がある例を確認する**

```python
point_df[point_df["地域名"].duplicated(keep=False)].sort_values(
    ["発表区域名", "地域名", "細分地域名"]
)
```

実行後，次を確認せよ．

1. `data/processed/forecast_area_points.csv`が作成されたか
2. `アメダス地点名`，`緯度`，`経度`，`標高`が入っているか
3. 1つの予報地域に複数のアメダス地点が対応している例はあるか
4. 標高は地域全体ではなく，アメダス地点の値であることを説明できるか
````

````{warning} 課題1：東京都の地図用データを作成する
「東京都の地図用データを作る」という見出しを作り，次のセルを順番に実行せよ．
以下のコードのうちセル2の`<HOGEHOGE1>`，`<HOGEHOGE2>`，セル3の`<FUGAFUGA1>`，`<FUGAFUGA2>`を適切に書き換え，`data/processed/tokyo_forecast_map_data.csv`を作成せよ．

最後に，書き換えて実行した2つのセルのコードをコピーし，<span style="color:red">WebClass「第9回課題」問1</span>のtext解答欄にペーストして提出せよ．

**セル1：予報地域・アメダス対応CSVを読み込む**

```python
point_path = "../data/processed/forecast_area_points.csv"

point_df = pd.read_csv(point_path)

point_df.head()
```

**セル2：地域ごとに平均降水確率を計算する**

ここでは，まだ複雑な集計関数を使わず，地域名ごとにデータを取り出して平均を計算する．

```python
tokyo_source_df = tokyo_weather_df.dropna(subset=["降水確率"]).copy()
summary_rows = []

for area_name in tokyo_source_df["地域名"].unique():
    area_df = tokyo_source_df[tokyo_source_df["地域名"] == area_name]

    summary_rows.append({
        "発表区域名": "東京都",
        "地域名": area_name,
        "予報日数": len(area_df),
        "平均降水確率": <HOGEHOGE1>,
        "最大降水確率": <HOGEHOGE2>,
        "信頼度A件数": (area_df["信頼度"] == "A").sum(),
    })

tokyo_summary_df = pd.DataFrame(summary_rows)

tokyo_summary_df
```
<!-- 
```python
tokyo_source_df = tokyo_weather_df.dropna(subset=["降水確率"]).copy()
summary_rows = []

for area_name in tokyo_source_df["地域名"].unique():
    area_df = tokyo_source_df[tokyo_source_df["地域名"] == area_name]

    summary_rows.append({
        "発表区域名": "東京都",
        "地域名": area_name,
        "予報日数": len(area_df),
        "平均降水確率": round(area_df["降水確率"].mean(), 1),
        "最大降水確率": area_df["降水確率"].max(),
        "信頼度A件数": (area_df["信頼度"] == "A").sum(),
    })

tokyo_summary_df = pd.DataFrame(summary_rows)

tokyo_summary_df
```
 -->
**セル3：アメダス地点情報を結合する**

```python
tokyo_map_df = pd.merge(
    <FUGAFUGA1>,
    <FUGAFUGA2>,
    on=["発表区域名", "地域名"],
    how="left"
)

tokyo_map_df
```

<!-- 
```python
tokyo_map_df = pd.merge(
    tokyo_summary_df,
    point_df,
    on=["発表区域名", "地域名"],
    how="left"
)

tokyo_map_df
```
 -->
**セル4：結合できなかった行を確認する**

```python
tokyo_missing_point_df = tokyo_map_df[tokyo_map_df["緯度"].isna()]

tokyo_missing_point_df
```

**セル5：地図用データを保存する**

```python
tokyo_map_df.to_csv(
    "../data/processed/tokyo_forecast_map_data.csv",
    index=False
)

print("saved: ../data/processed/tokyo_forecast_map_data.csv")
```

実行後，次を確認せよ．（確認するだけでよい）

1. `平均降水確率`と`最大降水確率`が計算されているか
2. `緯度`，`経度`，`標高`が結合されているか
3. 結合できなかった行はないか
````

うまく作成できなかった場合は，次のファイルをダウンロード・解凍し，`data/processed`に配置して以降の演習を進めること．

[tokyo_forecast_map_data_csv.zip](./analysis/9/data/processed/tokyo_forecast_map_data_csv.zip)

### 東京都の降水確率を地図上に描画する

````{note} 演習4：東京都の降水確率を地図上に表示する
「東京都の降水確率を地図化する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：plotlyで地図を確認する**

```python
fig = px.scatter_map(
    tokyo_map_df,
    lat="緯度",
    lon="経度",
    color="平均降水確率",
    size="最大降水確率",
    hover_name="地域名",
    hover_data=["発表区域名", "細分地域名", "アメダス地点名", "平均降水確率", "最大降水確率", "標高"],
    color_continuous_scale="viridis",
    zoom=4,
    height=600,
)

fig.update_layout(
    title="東京都の週間予報：平均降水確率",
    map_style="open-street-map",
)

fig.show()
```

**セル2：HTMLとして保存する**

セル1で作成した`fig`をそのままHTMLファイルとして保存する．
このようにすると，Notebook上で確認した地図とほぼ同じ見た目のHTMLファイルを作成できる．

```python
Path("../reports/figures").mkdir(parents=True, exist_ok=True)

fig.write_html("../reports/figures/tokyo_pop_map_check.html")

print("saved: ../reports/figures/tokyo_pop_map_check.html")
```

実行後，次を確認せよ．

1. 東京地方，伊豆諸島，小笠原諸島が地図上に表示されているか
2. 平均降水確率が高い地域ほど色が変化して表示されているか
3. 最大降水確率が高い地域ほど点が大きく表示されているか
4. 点にマウスを重ねると，アメダス地点名，降水確率，標高が表示されるか
````

---

## 複数都道府県の予報JSONをAPIで取得する

次に，東京都だけでなく，埼玉県・長野県・新潟県の天気予報JSONをAPIから取得する．
今回は，関東平野，内陸の山地，日本海側を含めることで，地図上の違いを眺めやすくする．

````{note} 演習5：複数都道府県のJSONをAPIで取得する
「複数都道府県のJSON取得」という見出しを作り，次のセルを順番に実行せよ．

**セル1：取得する発表区域を定義する**

発表区域コードは文字列として扱う．
先頭が`0`のコードもあるため，数値ではなく文字列にしておく．

```python
FORECAST_OFFICES = {
    "東京都": "130000",
    "埼玉県": "110000",
    "長野県": "200000",
    "新潟県": "150000",
}
```

**セル2：APIからJSONを取得して保存する**

```python
forecast_jsons = {}

for office_name, office_code in FORECAST_OFFICES.items():
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{office_code}.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    forecast_jsons[office_name] = data

    output_path = f"../data/raw/forecast_{office_code}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("saved:", output_path)
```

**セル3：取得したJSONに含まれる地域名を確認する**

```python
for office_name, data in forecast_jsons.items():
    weekly_forecast = data[1]
    weather_series = weekly_forecast["timeSeries"][0]

    print("----", office_name, "----")
    for area in weather_series["areas"]:
        print(area["area"]["name"], area["area"]["code"])
```

実行後，次を確認せよ．

1. `data/raw`に4つのJSONファイルが保存されたか
2. 東京都・埼玉県・長野県・新潟県では，どのような地域名が使われているか
3. 「北部」「中部」「南部」のような地域名が複数の県で使われていないか
````

````{note} 演習6：複数都道府県のJSONから1つのCSVを作る
「複数都道府県の週間予報を表にする」という見出しを作り，次のセルを順番に実行せよ．

**セル1：JSONから週間天気を取り出す関数を作る**

```python
def build_weekly_weather_rows(data, office_name, office_code):
    weekly_forecast = data[1]
    weather_series = weekly_forecast["timeSeries"][0]
    rows = []

    for area in weather_series["areas"]:
        area_name = area["area"]["name"]
        area_code = area["area"]["code"]

        for i, forecast_time in enumerate(weather_series["timeDefines"]):
            pop_text = area["pops"][i]

            if pop_text == "":
                pop = None
            else:
                pop = int(pop_text)

            rows.append({
                "発表区域名": office_name,
                "発表区域コード": office_code,
                "発表機関": weekly_forecast["publishingOffice"],
                "発表時刻": weekly_forecast["reportDatetime"],
                "地域名": area_name,
                "地域コード": area_code,
                "予報時刻": forecast_time,
                "予報日": forecast_time[:10],
                "天気コード": area["weatherCodes"][i],
                "降水確率": pop,
                "信頼度": area["reliabilities"][i],
            })

    return rows
```

**セル2：4都県の週間予報を1つの表にまとめる**

```python
all_rows = []

for office_name, office_code in FORECAST_OFFICES.items():
    rows = build_weekly_weather_rows(
        forecast_jsons[office_name],
        office_name,
        office_code
    )
    all_rows.extend(rows)

multi_weather_df = pd.DataFrame(all_rows)

print("行数・列数:", multi_weather_df.shape)
multi_weather_df.head()
```

**セル3：CSVとして保存する**

```python
multi_weather_df.to_csv(
    "../data/processed/multi_pref_weekly_weather.csv",
    index=False
)

print("saved: ../data/processed/multi_pref_weekly_weather.csv")
```

実行後，次を確認せよ．

1. `発表区域名`に4都県が含まれているか
2. `地域名`だけでは同じ名前が複数県で使われていないか
3. `data/processed/multi_pref_weekly_weather.csv`が作成されたか
````

````{note} 演習7：複数都道府県の予報データに標高CSVを結合する
「複数都道府県の地図用データを作る」という見出しを作り，次のセルを順番に実行せよ．

※ この内容は課題1と本質的に同じであるため詳細な解説は行わない．

**セル1：地域ごとに降水確率を集計する**

```python
multi_source_df = multi_weather_df.dropna(subset=["降水確率"]).copy()
summary_rows = []

keys_df = multi_source_df[["発表区域名", "地域名"]].drop_duplicates()

for _, key_row in keys_df.iterrows():
    office_name = key_row["発表区域名"]
    area_name = key_row["地域名"]

    area_df = multi_source_df[
        (multi_source_df["発表区域名"] == office_name)
        & (multi_source_df["地域名"] == area_name)
    ]

    summary_rows.append({
        "発表区域名": office_name,
        "地域名": area_name,
        "予報日数": len(area_df),
        "平均降水確率": round(area_df["降水確率"].mean(), 1),
        "最大降水確率": area_df["降水確率"].max(),
        "信頼度A件数": (area_df["信頼度"] == "A").sum(),
    })

multi_summary_df = pd.DataFrame(summary_rows)

multi_summary_df.head()
```

**セル2：予報地域・アメダス対応CSVを結合する**

```python
multi_map_df = pd.merge(
    multi_summary_df,
    point_df,
    on=["発表区域名", "地域名"],
    how="left"
)

multi_map_df
```

**セル3：結合できなかった地域を確認する**

```python
missing_point_df = multi_map_df[multi_map_df["緯度"].isna()]

missing_point_df
```

**セル4：地図用データを保存する**

```python
multi_map_df.to_csv(
    "../data/processed/multi_pref_forecast_map_data.csv",
    index=False
)

print("saved: ../data/processed/multi_pref_forecast_map_data.csv")
```

実行後，次を確認せよ．

1. `平均降水確率`，`最大降水確率`，`標高`が同じ表に含まれているか
2. 結合できなかった地域はないか
3. 結合できなかった地域がある場合，週間予報の地域名と`forecast_area_points.csv`の`地域名`が対応しているか確認できるか
````

---

## 標高データと予報データを地図上に可視化する

ここからは，作成した`multi_pref_forecast_map_data.csv`を使って，複数の地図を作成する．
同じデータでも，何を色にするか，何を点の大きさにするかによって，見え方が変わる．

````{note} 演習9：平均降水確率と最大降水確率を地図上に表示する
「平均降水確率と最大降水確率の地図」という見出しを作り，次のセルを実行せよ．

```python
fig = px.scatter_map(
    multi_map_df,
    lat="緯度",
    lon="経度",
    color="平均降水確率",
    size="最大降水確率",
    hover_name="地域名",
    hover_data=["発表区域名", "細分地域名", "アメダス地点名", "平均降水確率", "最大降水確率", "標高"],
    color_continuous_scale="viridis",
    zoom=5,
    height=650,
)

fig.update_layout(
    title="東京都・埼玉県・長野県・新潟県の週間予報：平均降水確率・最大降水確率",
    map_style="open-street-map",
)

fig.show()

fig.write_html("../reports/figures/multi_pref_pop_map.html")

print("saved: ../reports/figures/multi_pref_pop_map.html")
```

実行後，次を確認せよ．

1. どの地域の平均降水確率が高いか
2. 日本海側の地域と内陸の地域に違いはあるか
3. 地図で見ると，棒グラフより分かりやすい点は何か
````

````{warning} 課題2：標高だけを地図上に表示する
「標高の地図」という見出しを作り，次のセルを順番に実行せよ．
以下のコードのうちセル2の`<HOGEHOGE1>`，`<HOGEHOGE2>`，`<HOGEHOGE3>`，`<HOGEHOGE4>`，`<HOGEHOGE5>`を適切に書き換え，`fig.write_html("../reports/figures/multi_pref_elevation_map.html")`の形式でHTMLファイルを保存せよ．

最後に，書き換えて実行したセル2のコードをコピーし，<span style="color:red">WebClass「第9回課題」問2</span>のtext解答欄にペーストして提出せよ．

さらに，実行後に次の問いにも答えよ．

1. 標高が高いアメダス地点はどこか
2. 平野部と山地を地図上で区別できるか

**セル1：標高の範囲を確認する**

```python
multi_map_df[["標高"]].describe()
```

**セル2：標高を地図上に表示する**

```python
fig = px.scatter_map(
    <HOGEHOGE1>,
    lat=<HOGEHOGE2>,
    lon=<HOGEHOGE3>,
    color=<HOGEHOGE4>,
    size=<HOGEHOGE5>,
    hover_name="地域名",
    hover_data=["発表区域名", "細分地域名", "アメダス地点名", "標高", "平均降水確率"],
    color_continuous_scale="viridis",
    size_max=25,
    zoom=5,
    height=650,
)

fig.update_layout(
    title="アメダス地点の標高",
    map_style="open-street-map",
)

fig.show()

fig.write_html("../reports/figures/multi_pref_elevation_map.html")

print("saved: ../reports/figures/multi_pref_elevation_map.html")
```

<!-- 
```python
fig = px.scatter_map(
    multi_map_df,
    lat="緯度",
    lon="経度",
    color="標高",
    size="標高",
    hover_name="地域名",
    hover_data=["発表区域名", "細分地域名", "アメダス地点名", "標高", "平均降水確率"],
    color_continuous_scale="viridis",
    size_max=25,
    zoom=5,
    height=650,
)

fig.update_layout(
    title="アメダス地点の標高",
    map_style="open-street-map",
)

fig.show()

fig.write_html("../reports/figures/multi_pref_elevation_map.html")

print("saved: ../reports/figures/multi_pref_elevation_map.html")
```
 -->
````

````{note} 演習10：降水確率と標高を重ねて表示する
「降水確率と標高を重ねる」という見出しを作り，次のセルを順番に実行せよ．

ここでは，点の**色**で平均降水確率を表し，点の**大きさ**で標高を表す．
ただし，標高をそのまま半径に使うと大きくなりすぎるため，表示用の値を作る．

**セル1：表示用の標高サイズを作る**

```python
multi_map_df["標高表示サイズ"] = multi_map_df["標高"].clip(upper=800)

multi_map_df[["発表区域名", "地域名", "標高", "標高表示サイズ"]].head()
```

**セル2：plotlyで重ね合わせ地図を作る**

```python
Path("../reports/figures").mkdir(parents=True, exist_ok=True)

multi_map_df["標高表示サイズ"] = multi_map_df["標高"].clip(upper=800)

fig = px.scatter_map(
    multi_map_df,
    lat="緯度",
    lon="経度",
    color="平均降水確率",
    size="標高表示サイズ",
    hover_name="地域名",
    hover_data=["発表区域名", "細分地域名", "アメダス地点名", "平均降水確率", "最大降水確率", "標高"],
    color_continuous_scale="viridis",
    size_max=25,
    zoom=5,
    height=650,
)

fig.update_layout(
    title="東京都・埼玉県・長野県・新潟県の週間予報：平均降水確率と標高",
    map_style="open-street-map",
)

fig.show()

fig.write_html("../reports/figures/multi_pref_pop_elevation_map.html")

print("saved: ../reports/figures/multi_pref_pop_elevation_map.html")
```

実行後，次を確認せよ．

1. 色は平均降水確率に対応しているか
2. 点の大きさは標高に対応しているか
3. 1つの地図に2つの情報を載せることで，見やすくなった点と見にくくなった点は何か
````

```{tip} 重ねすぎに注意
1つの地図に多くの情報を重ねると，情報量は増えるが，読みにくくなることもある．
色，大きさ，透明度，凡例，ポップアップを使い分け，何を伝えたい図なのかを意識する．
```

---

### 好きな都道府県を追加して地図上に可視化する

````{warning} 課題3：好きな都道府県を追加して地図上に可視化する
東京都・埼玉県・長野県・新潟県に加えて，各自で好きな都道府県を1つ以上追加し，天気予報JSONをAPIで取得して，地図上に可視化せよ．

ただし，ここまでの内容を一つのPythonスクリプトにまとめ，ターミナル上で実行すること．

課題に取り組むにあたり，コードの細かい実行確認をするために，まずはNotebookファイルで個別に実行することを勧める．

作成したpythonスクリプト`src/build_my_forecast_map.py`とHTMLファイル`reports/figures/my_forecast_pop_elevation_map.html`をWebClass「第9回課題」問3・問4から提出せよ．
CSVファイルは提出しなくてよいが，スクリプトを実行したときに`data/processed/my_forecast_map_data.csv`が作成されるようにすること．

**条件**

1. `FORECAST_OFFICES`に，好きな都道府県を1つ以上追加する．
2. 追加した都道府県の天気予報JSONを`requests`で取得する．
3. `forecast_area.json`と`amedastable.json`を使い，追加した都道府県の予報地域・アメダス対応データを作成する．
4. `発表区域名`と`地域名`をキーにして，予報データとアメダス地点情報を結合する．
5. 平均降水確率と標高を重ねた地図を作成する．
6. HTMLファイルとして保存する．

**進め方**

1. 追加したい都道府県を選ぶ．
2. `FORECAST_OFFICES`に追加する．
3. JSONを取得して，含まれる`地域名`を確認する．
4. `forecast_area.json`と`amedastable.json`から，追加した都道府県のアメダス地点情報を取得する．
5. Notebookで試験的に実行する．
6. うまく動いたら，同じ処理を`src/build_my_forecast_map.py`にまとめる．
7. `9`フォルダ内で次のコマンドを実行する．

```bash
python src/build_my_forecast_map.py
```

実行後，次の点を確認せよ．

1. `data/processed/my_forecast_map_data.csv`が作成されたか
2. `reports/figures/my_forecast_pop_elevation_map.html`が作成されたか
3. 追加した都道府県の地域が地図上に表示されているか
4. 結合できずに`緯度`や`標高`が空欄になっている行はないか
5. 地図から読み取れることを，README.mdに1〜2文で記録したか
````
<!-- 
````{dropdown} 解答例
神奈川県を追加し，平均降水確率と標高を重ねた地図を作成する例である．
`src/build_my_forecast_map.py`として保存し，`9`フォルダ内で実行する．

```python
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests


FORECAST_OFFICES = {
    "東京都": "130000",
    "埼玉県": "110000",
    "長野県": "200000",
    "新潟県": "150000",
    "神奈川県": "140000",
}

area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
forecast_area_url = "https://www.jma.go.jp/bosai/forecast/const/forecast_area.json"
amedas_url = "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"

output_point_path = "data/processed/forecast_area_points.csv"
output_weather_path = "data/processed/my_weekly_weather.csv"
output_data_path = "data/processed/my_forecast_map_data.csv"
output_map_path = "reports/figures/my_forecast_pop_elevation_map.html"

Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("reports/figures").mkdir(parents=True, exist_ok=True)


def fetch_json(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def degree_minute_to_decimal(value):
    return value[0] + value[1] / 60


def build_weekly_area_lookup(forecast_json):
    weekly_forecast = forecast_json[1]
    weather_series = weekly_forecast["timeSeries"][0]
    lookup = {}

    for area in weather_series["areas"]:
        lookup[area["area"]["code"]] = area["area"]["name"]

    return lookup


def to_weekly_forecast_area(
    office_name,
    office_code,
    class10_code,
    class10_name,
    weekly_area_lookup,
):
    if class10_code in weekly_area_lookup:
        return class10_code, weekly_area_lookup[class10_code]

    if office_code == "130000" and class10_code in {"130020", "130030"}:
        return "130100", "伊豆諸島"

    if len(weekly_area_lookup) == 1:
        area_code = list(weekly_area_lookup.keys())[0]
        area_name = weekly_area_lookup[area_code]
        return area_code, area_name

    return class10_code, class10_name


def build_weekly_weather_rows(data, office_name, office_code):
    weekly_forecast = data[1]
    weather_series = weekly_forecast["timeSeries"][0]
    rows = []

    for area in weather_series["areas"]:
        area_name = area["area"]["name"]
        area_code = area["area"]["code"]

        for i, forecast_time in enumerate(weather_series["timeDefines"]):
            pop_text = area["pops"][i]

            if pop_text == "":
                pop = None
            else:
                pop = int(pop_text)

            rows.append({
                "発表区域名": office_name,
                "発表区域コード": office_code,
                "発表機関": weekly_forecast["publishingOffice"],
                "発表時刻": weekly_forecast["reportDatetime"],
                "地域名": area_name,
                "地域コード": area_code,
                "予報時刻": forecast_time,
                "予報日": forecast_time[:10],
                "天気コード": area["weatherCodes"][i],
                "降水確率": pop,
                "信頼度": area["reliabilities"][i],
            })

    return rows


area_data = fetch_json(area_url)
forecast_area_data = fetch_json(forecast_area_url)
amedas_data = fetch_json(amedas_url)

forecast_jsons = {}

for office_name, office_code in FORECAST_OFFICES.items():
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{office_code}.json"
    data = fetch_json(url)
    forecast_jsons[office_name] = data

    output_path = f"data/raw/forecast_{office_code}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("saved:", output_path)

point_rows = []

for office_name, office_code in FORECAST_OFFICES.items():
    weekly_area_lookup = build_weekly_area_lookup(forecast_jsons[office_name])

    for item in forecast_area_data[office_code]:
        class10_code = item["class10"]
        class10_name = area_data["class10s"][class10_code]["name"]
        forecast_area_code, forecast_area_name = to_weekly_forecast_area(
            office_name,
            office_code,
            class10_code,
            class10_name,
            weekly_area_lookup,
        )

        for amedas_id in item["amedas"]:
            amedas_info = amedas_data[amedas_id]
            lat = degree_minute_to_decimal(amedas_info["lat"])
            lon = degree_minute_to_decimal(amedas_info["lon"])

            point_rows.append({
                "発表区域名": office_name,
                "発表区域コード": office_code,
                "地域名": forecast_area_name,
                "地域コード": forecast_area_code,
                "細分地域名": class10_name,
                "細分地域コード": class10_code,
                "アメダス番号": amedas_id,
                "アメダス地点名": amedas_info["kjName"],
                "緯度": round(lat, 6),
                "経度": round(lon, 6),
                "標高": amedas_info["alt"],
                "予報区域対応取得元": "気象庁 forecast_area.json",
                "座標標高取得元": "気象庁 amedastable.json",
            })

point_df = pd.DataFrame(point_rows)
point_df.to_csv(output_point_path, index=False)
print("saved:", output_point_path)

weather_rows = []

for office_name, office_code in FORECAST_OFFICES.items():
    weather_rows.extend(
        build_weekly_weather_rows(
            forecast_jsons[office_name],
            office_name,
            office_code,
        )
    )

weather_df = pd.DataFrame(weather_rows)
weather_df.to_csv(output_weather_path, index=False)
print("saved:", output_weather_path)

source_df = weather_df.dropna(subset=["降水確率"]).copy()
summary_rows = []

keys_df = source_df[["発表区域名", "地域名"]].drop_duplicates()

for _, key_row in keys_df.iterrows():
    office_name = key_row["発表区域名"]
    area_name = key_row["地域名"]

    area_df = source_df[
        (source_df["発表区域名"] == office_name)
        & (source_df["地域名"] == area_name)
    ]

    summary_rows.append({
        "発表区域名": office_name,
        "地域名": area_name,
        "予報日数": len(area_df),
        "平均降水確率": round(area_df["降水確率"].mean(), 1),
        "最大降水確率": area_df["降水確率"].max(),
        "信頼度A件数": (area_df["信頼度"] == "A").sum(),
    })

summary_df = pd.DataFrame(summary_rows)

map_df = pd.merge(
    summary_df,
    point_df,
    on=["発表区域名", "地域名"],
    how="left",
)

missing_df = map_df[map_df["緯度"].isna()]

if len(missing_df) > 0:
    print("結合できなかった行があります")
    print(missing_df[["発表区域名", "地域名"]])

map_df["標高表示サイズ"] = map_df["標高"].clip(upper=800)
map_df.to_csv(output_data_path, index=False)
print("saved:", output_data_path)

fig = px.scatter_map(
    map_df.dropna(subset=["緯度", "経度"]),
    lat="緯度",
    lon="経度",
    color="平均降水確率",
    size="標高表示サイズ",
    hover_name="地域名",
    hover_data=[
        "発表区域名",
        "細分地域名",
        "アメダス地点名",
        "平均降水確率",
        "最大降水確率",
        "標高",
    ],
    color_continuous_scale="viridis",
    size_max=25,
    zoom=6,
    height=650,
)

fig.update_layout(
    title="選択した都道府県の週間予報：平均降水確率と標高",
    map_style="open-street-map",
)

fig.write_html(output_map_path)
print("saved:", output_map_path)
```
````
 -->
````{dropdown} 都道府県コード一覧

**47都道府県の発表区域コード一覧**

天気予報JSONのURLでは，気象庁の**府県予報区コード**を指定する．

```text
https://www.jma.go.jp/bosai/forecast/data/forecast/<発表区域コード>.json
```

多くの都府県は1つのコードに対応するが，北海道・鹿児島県・沖縄県は複数の府県予報区に分かれている．
これらの道県全体のデータを取得したい場合は，該当するコードをすべて`FORECAST_OFFICES`に追加する必要がある．

| 都道府県 | 発表区域コード |
| --- | --- |
| 北海道 | 宗谷地方：`011000`，上川・留萌地方：`012000`，網走・北見・紋別地方：`013000`，十勝地方：`014030`，釧路・根室地方：`014100`，胆振・日高地方：`015000`，石狩・空知・後志地方：`016000`，渡島・檜山地方：`017000` |
| 青森県 | `020000` |
| 岩手県 | `030000` |
| 宮城県 | `040000` |
| 秋田県 | `050000` |
| 山形県 | `060000` |
| 福島県 | `070000` |
| 茨城県 | `080000` |
| 栃木県 | `090000` |
| 群馬県 | `100000` |
| 埼玉県 | `110000` |
| 千葉県 | `120000` |
| 東京都 | `130000` |
| 神奈川県 | `140000` |
| 新潟県 | `150000` |
| 富山県 | `160000` |
| 石川県 | `170000` |
| 福井県 | `180000` |
| 山梨県 | `190000` |
| 長野県 | `200000` |
| 岐阜県 | `210000` |
| 静岡県 | `220000` |
| 愛知県 | `230000` |
| 三重県 | `240000` |
| 滋賀県 | `250000` |
| 京都府 | `260000` |
| 大阪府 | `270000` |
| 兵庫県 | `280000` |
| 奈良県 | `290000` |
| 和歌山県 | `300000` |
| 鳥取県 | `310000` |
| 島根県 | `320000` |
| 岡山県 | `330000` |
| 広島県 | `340000` |
| 山口県 | `350000` |
| 徳島県 | `360000` |
| 香川県 | `370000` |
| 愛媛県 | `380000` |
| 高知県 | `390000` |
| 福岡県 | `400000` |
| 佐賀県 | `410000` |
| 長崎県 | `420000` |
| 熊本県 | `430000` |
| 大分県 | `440000` |
| 宮崎県 | `450000` |
| 鹿児島県 | 奄美地方：`460040`，鹿児島県（奄美地方除く）：`460100` |
| 沖縄県 | 沖縄本島地方：`471000`，大東島地方：`472000`，宮古島地方：`473000`，八重山地方：`474000` |

例えば，北海道全体を取得する場合は，次のように8つの府県予報区を指定する．

```python
FORECAST_OFFICES = {
    "宗谷地方": "011000",
    "上川・留萌地方": "012000",
    "網走・北見・紋別地方": "013000",
    "十勝地方": "014030",
    "釧路・根室地方": "014100",
    "胆振・日高地方": "015000",
    "石狩・空知・後志地方": "016000",
    "渡島・檜山地方": "017000",
}
```

コード一覧は，気象庁が公開している[地域定義JSON](https://www.jma.go.jp/bosai/common/const/area.json)の`offices`から確認できる．
````
---

## まとめ

- 地図上への可視化では各地点の**緯度・経度**情報が必要になる
- 気象庁の天気予報JSONには緯度・経度・標高がないため，別のCSVを結合する必要がある
- 標高と降水確率といった複数のデータを同時に可視化することで新しいものが見えてくることがある
- `plotly`はNotebook上で試験的に眺める地図の出力に有効である
- `plotly`の`write_html`を使うと，作成した地図をHTMLファイルとして提出・共有できる

次回はデータ分析実践Iとして行政統計を扱う．
気象データ以外のオープンデータを使い，テーマ設定，データ取得，前処理，可視化までを一通り行う．

### 課題の提出期限

<span style="color:red">6月19日(金)23:59まで</span>

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所，メール，WebClassのメッセージ，Teamsのチャットなどから提出したものについて加点対象とします．

なお，提出ファイルは`<学籍番号>_<氏名>_第9回発展問題.zip`のようにzip形式にまとめて提出してください．

````{note} 発展問題1：別の予報値を地図上に表示する

課題3では平均降水確率を使った．
同じJSONから別の値を取り出し，地図上に表示せよ．

候補：

- 最大降水確率
- 信頼度Aの件数
- 天気コードの出現回数

`src/build_my_forecast_other_value_map.py`を作成して実行せよ．
作成したPythonスクリプトファイル`src/build_my_forecast_other_value_map.py`と実行して得られるHTMLファイルの2つを提出せよ．
````

````{dropdown} <span style="color:red">発展問題1 解答例</span>
課題3で作成した`data/processed/my_forecast_map_data.csv`を読み込み，最大降水確率を色，信頼度A件数を点の大きさで表示する例である．

`src/build_my_forecast_other_value_map.py`として保存し，`9`フォルダ内で実行する．

```python
from pathlib import Path

import pandas as pd
import plotly.express as px


input_path = "data/processed/my_forecast_map_data.csv"
output_path = "reports/figures/my_forecast_other_value_map.html"

Path("reports/figures").mkdir(parents=True, exist_ok=True)

map_df = pd.read_csv(input_path)
plot_df = map_df.dropna(
    subset=["緯度", "経度", "最大降水確率", "信頼度A件数"]
).copy()

# 0件の地点も地図上に表示できるように1を加える．
plot_df["信頼度A表示サイズ"] = plot_df["信頼度A件数"] + 1

fig = px.scatter_map(
    plot_df,
    lat="緯度",
    lon="経度",
    color="最大降水確率",
    size="信頼度A表示サイズ",
    hover_name="地域名",
    hover_data=[
        "発表区域名",
        "細分地域名",
        "アメダス地点名",
        "平均降水確率",
        "最大降水確率",
        "信頼度A件数",
        "標高",
    ],
    color_continuous_scale="viridis",
    size_max=25,
    zoom=5,
    height=650,
)

fig.update_layout(
    title="週間予報：最大降水確率と信頼度A件数",
    map_style="open-street-map",
)

fig.write_html(output_path)

print("saved:", output_path)
```

```bash
python src/build_my_forecast_other_value_map.py
```

実行すると，`reports/figures/my_forecast_other_value_map.html`が作成される．
````

````{note} 発展問題2：標高と降水確率の関係を散布図で確認する

地図だけでなく，横軸を標高，縦軸を平均降水確率とした散布図を作成せよ．

`src/plot_elevation_pop_scatter.py`を作成して実行せよ．
作成したPythonスクリプトファイル`src/plot_elevation_pop_scatter.py`と実行して得られる画像ファイルの2つを提出せよ．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 標高が高いほど平均降水確率が高いように見えるか
2. 都道府県ごとに傾向は違うか
3. 地図と散布図とで読み取りやすい事項は何が異なるか
````

````{dropdown} <span style="color:red">発展問題2 解答例</span>
課題3で作成した`data/processed/my_forecast_map_data.csv`を読み込み，都道府県を色，最大降水確率を点の大きさで表す例である．

`src/plot_elevation_pop_scatter.py`として保存し，`9`フォルダ内で実行する．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


input_path = "data/processed/my_forecast_map_data.csv"
output_path = "reports/figures/elevation_pop_scatter.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

map_df = pd.read_csv(input_path)
plot_df = map_df.dropna(
    subset=["標高", "平均降水確率", "最大降水確率", "発表区域名"]
).copy()

fig, ax = plt.subplots(figsize=(8, 6))

sns.scatterplot(
    data=plot_df,
    x="標高",
    y="平均降水確率",
    hue="発表区域名",
    size="最大降水確率",
    sizes=(50, 250),
    alpha=0.8,
    ax=ax,
)

ax.set_title("アメダス地点の標高と平均降水確率")
ax.set_xlabel("標高（m）")
ax.set_ylabel("平均降水確率（%）")
ax.legend(
    title="発表区域・最大降水確率",
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
)

plt.tight_layout()
plt.savefig(output_path, dpi=150, bbox_inches="tight")

print("saved:", output_path)
```

```bash
python src/plot_elevation_pop_scatter.py
```

実行すると，`reports/figures/elevation_pop_scatter.png`が作成される．
````
