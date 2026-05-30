# 第8回　データの可視化

### 前回の復習

- 前処理：取得したデータを**分析しやすい形に整える**作業
- 1つのJSONの中にも，複数の表に相当するデータが入っていることがある
- 表を結合するときは，地域や時刻の意味が一致しているかを確認する
- 結合によって発生する空欄は，必ずしもデータの誤りではない
- 日時文字列から日付や時刻を取り出すと，後の集計や可視化に使いやすくなる
- データ観察はNotebookで行い，再実行する本処理はPythonファイルとして保存する

第7回では，第5回で取得した気象庁の天気予報JSONから，短期予報の天気表と降水確率表を結合し，日付列と天気カテゴリを持つ分析用データセットを作成した．

第8回では，同じJSONに含まれる**週間予報**を使って，可視化しやすいデータを作成し，図を作成する．
第6回・第7回で学んだ前処理をもう一度すべて手作業で行うのではなく，今回は前処理と集計をまとめて実行する配布スクリプトを使い，集計用データセット作成と可視化を学ぶ．

**可視化**：データの傾向，違い，外れた値，時間変化などを図として表現し，人間が理解しやすい形にする作業

可視化は分析結果の飾りではなく，次の問いを確認するための工程である．

- データにどのような傾向があるか
- 地域や地点によって違いがあるか
- 前処理や集計が意図した通りにできているか
- 読み手に誤解なく伝わる図になっているか

### 到達目標

データ分析の一連の流れの中で，可視化を適切に使う方法を学ぶ．

- データ分析の流れの中で，可視化の役割を説明できる
- 図を作る前に，行数，列名，値の範囲を確認できる
- 週間予報から集計用データセットを作成する考え方を説明できる
- 目的に応じて折れ線グラフなどの図を選択できる
- Pythonの `matplotlib` を使って図を作成できる
- 図のタイトル，軸ラベル，凡例，単位を適切に設定できる
- 作成した図を画像ファイルとして保存できる
- 図から読み取れることと，読み取れないことを文章で説明できる

### 準備

今回は第5回で作成したフォルダ `5` 内で作業を続ける．

第5回で取得した次のファイルを使う．

```text
5/data/raw/jma_tokyo_forecast.json
```

これがない場合は次のリンクからダウンロードして配置すること．

[jma_tokyo_forecast_json.zip](./analysis/5/data/raw/jma_tokyo_forecast_json.zip)

また，今回は週間予報の前処理と集計をまとめて実行する次のPythonファイルを使う．

[build_weekly_forecast_tables_py.zip](./analysis/5/src/build_weekly_forecast_tables_py.zip)

ZIPファイルを展開し，`build_weekly_forecast_tables.py` を `5/src/` に配置すること．

````{note} 演習0：作業フォルダと配布スクリプトを確認する

1. 第5回で作成した `/User/<ユーザ名>/applied_programming_i/5` を開く．
2. 次のディレクトリ構成になっているか確認する．

```text
5/
├── notebooks/
│   ├── preprocessing1.ipynb
│   ├── preprocessing2.ipynb
│   └── visualization.ipynb（←今回作成するファイル）
├── data/
│   ├── raw/
│   │   └── jma_tokyo_forecast.json
│   └── processed/
├── reports/
│   └── figures/
├── src/
│   └── build_weekly_forecast_tables.py
└── README.md
```

3. `notebooks/`，`reports/figures/`，`src/`，`data/processed/` がない場合は作成する．
4. JupyterLabまたはVS Codeで `notebooks/visualization.ipynb` を新規作成する．
5. `README.md` に次の内容を追記する．

```markdown
## 第8回 可視化記録

- 元データ：data/raw/jma_tokyo_forecast.json
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 観察用ノートブック：notebooks/visualization.ipynb（Gitでは管理しない）
- 週間予報の前処理・集計スクリプト：src/build_weekly_forecast_tables.py
- 可視化スクリプト：
  - src/plot_weekly_pop.py
  - src/plot_weekly_temperature.py
  - src/write_visualization_comment.py
- 週間予報データ・集計データ：
  - data/processed/jma_tokyo_weekly_weather.csv
  - data/processed/jma_tokyo_weekly_temperature.csv
  - data/processed/jma_tokyo_weekly_weather_summary.csv
  - data/processed/jma_tokyo_weekly_temperature_summary.csv
- 出力した図：
  - reports/figures/weekly_pop_by_area.png
  - reports/figures/weekly_temperature_tokyo.png
- 可視化の目的：
  - 地域別に週間の降水確率の変化を確認する
  - 東京の最低気温と最高気温の変化を確認する
```

6. `.gitignore` に次の記述があることを確認する．

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

第8回では，次の流れで作業する．

```text
data/raw/jma_tokyo_forecast.json
  ↓
  ↓ src/build_weekly_forecast_tables.py
  ↓
data/processed/jma_tokyo_weekly_weather.csv
data/processed/jma_tokyo_weekly_temperature.csv
data/processed/jma_tokyo_weekly_weather_summary.csv
data/processed/jma_tokyo_weekly_temperature_summary.csv
  ↓
  ↓ notebooks/visualization.ipynbで集計結果と図を確認
  ↓ src/plot_weekly_pop.py
  ↓ src/plot_weekly_temperature.py
  ↓
reports/figures/weekly_pop_by_area.png
reports/figures/weekly_temperature_tokyo.png
```

```{tip} 注意
今回は前処理を省略するのではなく，第6回・第7回で学んだ処理を配布スクリプトとしてまとめて実行する．
第8回では，作成されたデータをどう確認し，どう集計し，どう図にするかに集中する．
```

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

## 週間予報の表と集計データを作成する

`jma_tokyo_forecast.json` は，一番外側がリストになっている．
本講義で使うサンプルでは，次のような構造になっている．

```text
data
├── data[0]：短期予報
│   ├── timeSeries[0]：天気，風，波
│   ├── timeSeries[1]：降水確率
│   └── timeSeries[2]：気温
└── data[1]：週間予報
    ├── timeSeries[0]：週間の天気，降水確率，信頼度
    └── timeSeries[1]：週間の最低気温・最高気温
```

今回は，`data[1]` の週間予報を使う．

````{note} 演習1：週間予報のCSVを作成する
ターミナルで `5` フォルダに移動し，次のコマンドを実行せよ．

```bash
python src/build_weekly_forecast_tables.py
```

実行後，次のファイルが作成されたことを確認せよ．

```text
data/processed/jma_tokyo_weekly_weather.csv
data/processed/jma_tokyo_weekly_temperature.csv
data/processed/jma_tokyo_weekly_weather_summary.csv
data/processed/jma_tokyo_weekly_temperature_summary.csv
```

それぞれの役割は次の通りである．

| ファイル | 内容 |
| --- | --- |
| `jma_tokyo_weekly_weather.csv` | 地域別・日付別の天気コード，降水確率，信頼度 |
| `jma_tokyo_weekly_temperature.csv` | 地点別・日付別の最低気温，最高気温，予報幅 |
| `jma_tokyo_weekly_weather_summary.csv` | 地域別の降水確率と信頼度の集計 |
| `jma_tokyo_weekly_temperature_summary.csv` | 地点別の最低気温・最高気温の集計 |
````

```{tip} 注意
週間予報の初日は，降水確率や気温が空欄になっていることがある．
空欄を見つけたらすぐに削除するのではなく，どの列で，どの行に，なぜ空欄があるのかを確認する．
```

---

## 使用するデータ

### 週間天気データ

```text
data/processed/jma_tokyo_weekly_weather.csv
```

主な列：

- `地域名`
- `地域コード`
- `予報時刻`
- `予報日`
- `天気コード`
- `降水確率`
- `信頼度`

このデータでは，地域ごとの降水確率の時間変化を可視化する．

### 週間気温データ

```text
data/processed/jma_tokyo_weekly_temperature.csv
```

主な列：

- `地点名`
- `地点コード`
- `予報時刻`
- `予報日`
- `最低気温`
- `最高気温`
- `最低気温上限`
- `最低気温下限`
- `最高気温上限`
- `最高気温下限`

このデータでは，地点ごとの最低気温・最高気温の時間変化を可視化する．

```{tip} 注意
週間天気データの `地域名` は「東京地方」「伊豆諸島」「小笠原諸島」である．
週間気温データの `地点名` は「東京」「八丈島」「父島」である．
地域と地点は単位が異なるため，今回は別々の図として扱う．
```

---

## 可視化の準備

Pythonで図を作成するために，`matplotlib` を使う．

````{note} 演習2：matplotlibを確認する
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

ax.plot(["5/21", "5/22", "5/23"], [21, 23, 20], marker="o")
ax.set_title("折れ線グラフの確認")
ax.set_xlabel("日付")
ax.set_ylabel("値")

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

````{note} 演習3：可視化に使うデータを確認する
`notebooks/visualization.ipynb` に「可視化に使うデータを確認する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：CSVを読み込む**（`<HOGE>`には適切なディレクトリを指定すること）

```python
import csv

weekly_weather_path = "<HOGE>/jma_tokyo_weekly_weather.csv"
weekly_temperature_path = "<HOGE>/jma_tokyo_weekly_temperature.csv"

with open(weekly_weather_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    weekly_weather_rows = list(reader)
    weekly_weather_fieldnames = reader.fieldnames

with open(weekly_temperature_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    weekly_temperature_rows = list(reader)
    weekly_temperature_fieldnames = reader.fieldnames
```

**セル2：行数と列名を確認する**

```python
print("週間天気データの行数:", len(weekly_weather_rows))
print("週間天気データの列名:", weekly_weather_fieldnames)
print()
print("週間気温データの行数:", len(weekly_temperature_rows))
print("週間気温データの列名:", weekly_temperature_fieldnames)
```

**セル3：値の例を確認する**

```python
print("週間天気データの先頭3行:")
for row in weekly_weather_rows[:3]:
    print(row)

print("週間気温データの先頭3行:")
for row in weekly_temperature_rows[:3]:
    print(row)
```

**セル4：空欄の数を確認する**

```python
weather_missing_pop = 0

for row in weekly_weather_rows:
    if row["降水確率"] == "":
        weather_missing_pop += 1

temperature_missing = 0

for row in weekly_temperature_rows:
    if row["最低気温"] == "" or row["最高気温"] == "":
        temperature_missing += 1

print("降水確率が空欄の行数:", weather_missing_pop)
print("最低気温または最高気温が空欄の行数:", temperature_missing)
```

実行後，次を確認せよ．

1. 週間天気データにはどのような列があるか
2. 週間気温データにはどのような列があるか
3. `降水確率`，`最低気温`，`最高気温` は文字列として読み込まれているか
4. 空欄の行はあるか
````

---

## 集計用データセットを作成する

可視化では，細かい行をそのまま図にする場合と，目的に合わせて集計した表を図にする場合がある．
第8回で配布した `src/build_weekly_forecast_tables.py` は，週間予報から次の2種類のデータを作成している．

- 日付ごとの細かい表：`jma_tokyo_weekly_weather.csv`，`jma_tokyo_weekly_temperature.csv`
- 地域別・地点別に要約した集計用データセット：`jma_tokyo_weekly_weather_summary.csv`，`jma_tokyo_weekly_temperature_summary.csv`

ここでは，集計用データセットがどのような考え方で作られているかをNotebookで確認する．

````{note} 演習4：週間予報の集計用データセットを確認する
`notebooks/visualization.ipynb` に「集計用データセットを作成する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：平均を計算する関数を準備する**

```python
def average_or_blank(values):
    if len(values) == 0:
        return ""

    return round(sum(values) / len(values), 1)
```

**セル2：地域別に週間の降水確率と信頼度を集計する**

```python
weather_summary = {}

for row in weekly_weather_rows:
    key = (row["地域名"], row["地域コード"])

    if key not in weather_summary:
        weather_summary[key] = {
            "予報日数": 0,
            "降水確率": [],
            "信頼度A件数": 0,
            "信頼度B件数": 0,
            "信頼度C件数": 0
        }

    weather_summary[key]["予報日数"] += 1

    if row["降水確率"] != "":
        weather_summary[key]["降水確率"].append(int(row["降水確率"]))

    if row["信頼度"] in {"A", "B", "C"}:
        weather_summary[key][f"信頼度{row['信頼度']}件数"] += 1

weather_summary_rows = []

for (area_name, area_code), values in weather_summary.items():
    pops = values["降水確率"]

    weather_summary_rows.append({
        "地域名": area_name,
        "地域コード": area_code,
        "予報日数": values["予報日数"],
        "降水確率あり件数": len(pops),
        "平均降水確率": average_or_blank(pops),
        "最大降水確率": max(pops) if len(pops) > 0 else "",
        "最小降水確率": min(pops) if len(pops) > 0 else "",
        "信頼度A件数": values["信頼度A件数"],
        "信頼度B件数": values["信頼度B件数"],
        "信頼度C件数": values["信頼度C件数"]
    })

weather_summary_rows.sort(key=lambda row: row["地域コード"])
weather_summary_rows
```

**セル3：地点別に週間の最低気温と最高気温を集計する**

```python
temperature_summary = {}

for row in weekly_temperature_rows:
    key = (row["地点名"], row["地点コード"])

    if key not in temperature_summary:
        temperature_summary[key] = {
            "予報日数": 0,
            "最低気温": [],
            "最高気温": []
        }

    temperature_summary[key]["予報日数"] += 1

    if row["最低気温"] != "":
        temperature_summary[key]["最低気温"].append(int(row["最低気温"]))

    if row["最高気温"] != "":
        temperature_summary[key]["最高気温"].append(int(row["最高気温"]))

temperature_summary_rows = []

for (point_name, point_code), values in temperature_summary.items():
    min_temps = values["最低気温"]
    max_temps = values["最高気温"]

    temperature_summary_rows.append({
        "地点名": point_name,
        "地点コード": point_code,
        "予報日数": values["予報日数"],
        "最低気温あり日数": len(min_temps),
        "最高気温あり日数": len(max_temps),
        "平均最低気温": average_or_blank(min_temps),
        "平均最高気温": average_or_blank(max_temps),
        "最低気温の最小値": min(min_temps) if len(min_temps) > 0 else "",
        "最高気温の最大値": max(max_temps) if len(max_temps) > 0 else ""
    })

temperature_summary_rows.sort(key=lambda row: row["地点コード"])
temperature_summary_rows
```

実行後，次を確認せよ．

1. `降水確率` が空欄の行は，平均の計算から除外されているか
2. `最低気温` や `最高気温` が空欄の行は，平均の計算から除外されているか
3. 地域別・地点別に，どのような値が要約されているか
4. 集計用データセットは，細かい表と比べて何が見やすくなっているか
````

```{tip} 注意
上の処理と同じ考え方が，配布スクリプト `src/build_weekly_forecast_tables.py` の中に入っている．
Notebookでは処理の意味を確認し，Pythonファイルでは同じ処理を再実行できる形にしている．
```

---

## 週間の降水確率を可視化する

週間予報では，複数の日付に対して降水確率が入っている．
時間に沿った変化を見るため，ここでは**折れ線グラフ**を使う．

### 折れ線グラフが向いている場合

- 時間に沿った変化を見たい
- 日付ごとの増減を確認したい
- 複数の地域や地点の変化を比較したい

````{note} 演習5：地域別の降水確率を折れ線グラフにする
`notebooks/visualization.ipynb` に「週間の降水確率を可視化する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：図に使うデータを作る**

```python
area_names = []
dates_by_area = {}
pop_by_area = {}

for row in weekly_weather_rows:
    if row["降水確率"] == "":
        continue

    area = row["地域名"]

    if area not in area_names:
        area_names.append(area)
        dates_by_area[area] = []
        pop_by_area[area] = []

    dates_by_area[area].append(row["予報日"][5:])
    pop_by_area[area].append(int(row["降水確率"]))

print("地域:", area_names)
print("東京地方の日付:", dates_by_area["東京地方"])
print("東京地方の降水確率:", pop_by_area["東京地方"])
```

**セル2：折れ線グラフを作成する**

```python
fig, ax = plt.subplots(figsize=(8, 5))

for area in area_names:
    ax.plot(
        dates_by_area[area],
        pop_by_area[area],
        marker="o",
        label=area
    )

ax.set_title("週間予報の降水確率")
ax.set_xlabel("予報日")
ax.set_ylabel("降水確率（%）")
ax.set_ylim(0, 100)
ax.legend(title="地域")

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 地域ごとに線が表示されているか
2. 縦軸は0から100になっているか
3. どの日に降水確率が高いか
4. 地域ごとの違いはあるか
5. 空欄の降水確率をどのように扱ったか
````

````{warning} 課題1：週間の降水確率をPythonファイルで可視化する
1. 演習5で確認した内容をもとに，`src/plot_weekly_pop.py` を作成し，
WebClass「第8回課題」問1から提出せよ．

提出するのはPythonファイルのみである．作成されるCSVファイルやPNGファイルは提出しなくてよい．

次のコードの `<FUGAFUGA>` と `<HOGEHOGE>` を適切に置き換え，`reports/figures/weekly_pop_by_area.png` を作成すること．

```python
import csv
from pathlib import Path

import matplotlib.pyplot as plt

input_path = "data/processed/jma_tokyo_weekly_weather.csv"
output_path = "reports/figures/weekly_pop_by_area.png"

plt.rcParams["font.family"] = "Hiragino Sans"
Path("reports/figures").mkdir(parents=True, exist_ok=True)

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

area_names = []
dates_by_area = {}
pop_by_area = {}

<FUGAFUGA>

fig, ax = plt.subplots(figsize=(8, 5))

for area in area_names:
    ax.plot(
        dates_by_area[area],
        pop_by_area[area],
        marker="o",
        label=area
    )

ax.set_title("週間予報の降水確率")
ax.set_xlabel("予報日")
ax.set_ylabel("降水確率（%）")
ax.set_ylim(0, 100)
ax.legend(title="地域")

plt.tight_layout()
<HOGEHOGE>

print("saved:", output_path)
```

作成したPythonファイルを `5` フォルダ内でターミナルから実行せよ．

```bash
python src/plot_weekly_pop.py
```

実行後，`reports/figures/weekly_pop_by_area.png` が作成されていることを確認せよ．
````

<!--
for row in rows:
    if row["降水確率"] == "":
        continue

    area = row["地域名"]

    if area not in area_names:
        area_names.append(area)
        dates_by_area[area] = []
        pop_by_area[area] = []

    dates_by_area[area].append(row["予報日"][5:])
    pop_by_area[area].append(int(row["降水確率"]))

plt.savefig(output_path, dpi=150)
-->

---

## 週間の気温を可視化する

次に，週間気温データを使って，東京の最低気温と最高気温を可視化する．
気温は日付に沿って変化する値なので，ここでも折れ線グラフを使う．

````{note} 演習6：東京の最低気温と最高気温を折れ線グラフにする
`notebooks/visualization.ipynb` に「週間の気温を可視化する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：東京の気温データを取り出す**

```python
target_point = "東京"

dates = []
min_temps = []
max_temps = []

for row in weekly_temperature_rows:
    if row["地点名"] != target_point:
        continue

    if row["最低気温"] == "" or row["最高気温"] == "":
        continue

    dates.append(row["予報日"][5:])
    min_temps.append(int(row["最低気温"]))
    max_temps.append(int(row["最高気温"]))

print("日付:", dates)
print("最低気温:", min_temps)
print("最高気温:", max_temps)
```

**セル2：折れ線グラフを作成する**

```python
fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(dates, max_temps, marker="o", label="最高気温")
ax.plot(dates, min_temps, marker="o", label="最低気温")

ax.set_title("東京の週間気温予報")
ax.set_xlabel("予報日")
ax.set_ylabel("気温（℃）")
ax.legend()

plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. 最高気温と最低気温が別の線として表示されているか
2. 気温の単位が分かるか
3. どの日の最高気温が高いか
4. 最高気温と最低気温の差が大きい日はいつか
5. 空欄の気温をどのように扱ったか
````

````{warning} 課題2：週間の気温をPythonファイルで可視化する
1. 演習6で確認した内容をもとに，`src/plot_weekly_temperature.py` を作成し，
WebClass「第8回課題」問2から提出せよ．

提出するのはPythonファイルのみである．作成されるCSVファイルやPNGファイルは提出しなくてよい．

次のコードの `<FUGAFUGA>` と `<HOGEHOGE>` を適切に置き換え，`reports/figures/weekly_temperature_tokyo.png` を作成すること．

```python
import csv
from pathlib import Path

import matplotlib.pyplot as plt

input_path = "data/processed/jma_tokyo_weekly_temperature.csv"
output_path = "reports/figures/weekly_temperature_tokyo.png"

plt.rcParams["font.family"] = "Hiragino Sans"
Path("reports/figures").mkdir(parents=True, exist_ok=True)

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

target_point = "東京"

dates = []
min_temps = []
max_temps = []

<FUGAFUGA>

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(dates, max_temps, marker="o", label="最高気温")
ax.plot(dates, min_temps, marker="o", label="最低気温")

ax.set_title("東京の週間気温予報")
ax.set_xlabel("予報日")
ax.set_ylabel("気温（℃）")
ax.legend()

plt.tight_layout()
<HOGEHOGE>

print("saved:", output_path)
```

作成したPythonファイルを `5` フォルダ内でターミナルから実行せよ．

```bash
python src/plot_weekly_temperature.py
```

実行後，`reports/figures/weekly_temperature_tokyo.png` が作成されていることを確認せよ．
````

<!--
for row in rows:
    if row["地点名"] != target_point:
        continue

    if row["最低気温"] == "" or row["最高気温"] == "":
        continue

    dates.append(row["予報日"][5:])
    min_temps.append(int(row["最低気温"]))
    max_temps.append(int(row["最高気温"]))

plt.savefig(output_path, dpi=150)
-->

---

## 可視化に便利なライブラリ

ここまでは，Python標準ライブラリの `csv` と，図を作るための `matplotlib` を使ってきた．
実際のデータ分析では，表形式データを扱いやすくする `pandas` や，少ないコードで見やすい図を作れる `seaborn` もよく使われる．

- `pandas`：CSVを表形式データとして読み込み，列の選択，集計，並べ替えを行いやすくするライブラリ
- `seaborn`：`matplotlib` をもとにした可視化ライブラリで，カテゴリ別・グループ別の図を少ないコードで作成できる

```{tip} 注意
`pandas` や `seaborn` が import できない場合は，授業環境にライブラリが入っていない可能性がある．
その場合でも，この講義の課題は `csv` と `matplotlib` だけで実施できる．
```

````{note} 参考：pandasとseabornで週間の降水確率を可視化する
`notebooks/visualization.ipynb` に「便利なライブラリを使った可視化」という見出しを作り，次のセルを実行してみよ．

**セル1：ライブラリを読み込む**

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Hiragino Sans"
```

**セル2：CSVを読み込む**（`<HOGE>`には適切なディレクトリを指定すること）

```python
weekly_weather_path = "<HOGE>/jma_tokyo_weekly_weather.csv"

weekly_weather_df = pd.read_csv(weekly_weather_path)
weekly_weather_df.head()
```

**セル3：空欄を除外する**

```python
weekly_weather_plot_df = weekly_weather_df.dropna(subset=["降水確率"])
weekly_weather_plot_df
```

**セル4：seabornで折れ線グラフを作る**

```python
fig, ax = plt.subplots(figsize=(8, 5))

sns.lineplot(
    data=weekly_weather_plot_df,
    x="予報日",
    y="降水確率",
    hue="地域名",
    marker="o",
    ax=ax
)

ax.set_title("週間予報の降水確率（seaborn）")
ax.set_xlabel("予報日")
ax.set_ylabel("降水確率（%）")
ax.set_ylim(0, 100)

plt.xticks(rotation=20)
plt.tight_layout()
plt.show()
```

実行後，次を確認せよ．

1. `weekly_weather_df.head()` で表の先頭行が表示されるか
2. `dropna(subset=["降水確率"])` はどの行を除外しているか
3. `hue="地域名"` は図の何を表しているか
4. `csv` と `matplotlib` だけで作る場合と比べて，コードは短くなっているか
````

---

## 図から読み取れることを書く

図を作成したら，図から読み取れることを文章で説明する．
このとき，図から読み取れることと，読み取れないことを分けて書くことが重要である．

### 読み取れることの例

- どの日の降水確率が高いか
- 地域ごとに降水確率の変化がどのように異なるか
- どの日の最高気温が高いか
- 最高気温と最低気温の差がどの程度あるか
- 空欄を除外した図であること

### 読み取れないことの例

- 長期的な気候の特徴
- 他の都道府県でも同じ傾向があるかどうか
- 実際にその天気や気温になったかどうか

今回のデータは，取得時点の週間予報から作成した小さなデータである．
そのため，図から読み取れることは，このデータの範囲に限定して説明する．

````{warning} 課題3：可視化結果を文章で説明する
1. 作成した2つの図から読み取れることを記録する `src/write_visualization_comment.py` を作成し，
WebClass「第8回課題」問3から提出せよ．

提出するのはPythonファイルのみである．作成されるMarkdownファイルは提出しなくてよい．

次のコードの `<FUGAFUGA>` を適切に置き換え，`reports/visualization_comment.md` を作成すること．

```python
from pathlib import Path

output_path = "reports/visualization_comment.md"

comment = """## 第8回 可視化結果の考察

### 週間予報の降水確率

- 図から読み取れること：
- 注意点：

### 東京の週間気温予報

- 図から読み取れること：
- 注意点：
"""

<FUGAFUGA>

print("saved:", output_path)
```

作成したPythonファイルを `5` フォルダ内でターミナルから実行せよ．

```bash
python src/write_visualization_comment.py
```

実行後，`reports/visualization_comment.md` が作成されていることを確認せよ．

`comment` の中には，次の見出しを含め，作成した2つの図から読み取れることを記述すること．

```markdown
## 第8回 可視化結果の考察

### 週間予報の降水確率

- 図から読み取れること：
- 注意点：

### 東京の週間気温予報

- 図から読み取れること：
- 注意点：
```
````

<!--
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
Path(output_path).write_text(comment, encoding="utf-8")
-->

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

## Git管理と集計・可視化

集計や可視化では，出力した表や図そのものだけでなく，それらを作る手順も残すことが重要である．

Gitで管理するとよいものは次の通りである．

- 可視化スクリプト（`src/*.py`）
- 前処理・集計スクリプト（`src/build_weekly_forecast_tables.py`）
- README
- 小さな集計データ
- 最終的に提出する図

一方，作業用NotebookはGitで管理しない．
Notebookで試行錯誤し，最終的に再実行できる処理をPythonファイルとして残す．

今回の処理の流れは，次のように表せる．

```text
data/raw/jma_tokyo_forecast.json
  ↓
  ↓ src/build_weekly_forecast_tables.py
  ↓
data/processed/jma_tokyo_weekly_weather.csv
data/processed/jma_tokyo_weekly_temperature.csv
data/processed/jma_tokyo_weekly_weather_summary.csv
data/processed/jma_tokyo_weekly_temperature_summary.csv
  ↓
  ↓ notebooks/visualization.ipynbで集計結果と図を確認
  ↓ src/plot_weekly_pop.py
  ↓ src/plot_weekly_temperature.py
  ↓
reports/figures/weekly_pop_by_area.png
reports/figures/weekly_temperature_tokyo.png
```

---

## まとめ

- 可視化は，データ分析の流れの中で，データの傾向や違いを確認し，結果を伝えるための工程である
- 図を作る前には，行数，列名，値の例，空欄の有無を確認する
- 集計用データセットを作ると，地域別・地点別の特徴を確認しやすくなる
- 時間に沿った変化を見るときは，折れ線グラフが使いやすい
- 図には，タイトル，軸ラベル，単位，凡例を適切に設定する
- 空欄を除外した場合は，その処理を説明できるようにする
- 図から読み取れることと，読み取れないことを分けて文章にする
- データ観察はNotebookで行い，再実行する本処理はPythonファイルとして保存する

次回は統計的な要約を扱う．

- 可視化で確認した傾向を，平均，分散，相関などの数値で要約する方法を学ぶ
- 図と数値を組み合わせて，データの特徴を説明する

### 課題の提出期限

6月9日(火)23:59まで

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所から提出したものについて加点対象とします．

````{note} 課題4：気温の予報幅を可視化する

`jma_tokyo_weekly_temperature.csv` には，最低気温・最高気温だけでなく，予報の上限・下限も含まれている．
東京の最高気温について，予報値と予報幅を同じ図に表示せよ．

`src/plot_weekly_temperature_range.py` を作成し，WebClass「第8回課題」問4から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 予報幅が広い日はいつか
2. 予報幅が広いことは，どのような意味を持つと考えられるか
3. 折れ線だけの図と比べて，情報は増えたか
````

````{dropdown} 解答例
最高気温の予報値を折れ線で示し，上限と下限の範囲を薄い帯として表示する例である．

```python
import csv
from pathlib import Path

import matplotlib.pyplot as plt

input_path = "data/processed/jma_tokyo_weekly_temperature.csv"
output_path = "reports/figures/weekly_temperature_range_tokyo.png"

plt.rcParams["font.family"] = "Hiragino Sans"
Path("reports/figures").mkdir(parents=True, exist_ok=True)

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

dates = []
max_temps = []
max_lowers = []
max_uppers = []

for row in rows:
    if row["地点名"] != "東京":
        continue

    if row["最高気温"] == "" or row["最高気温下限"] == "" or row["最高気温上限"] == "":
        continue

    dates.append(row["予報日"][5:])
    max_temps.append(int(row["最高気温"]))
    max_lowers.append(int(row["最高気温下限"]))
    max_uppers.append(int(row["最高気温上限"]))

x = list(range(len(dates)))

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(x, max_temps, marker="o", label="最高気温")
ax.fill_between(x, max_lowers, max_uppers, alpha=0.2, label="最高気温の予報幅")

ax.set_title("東京の最高気温予報と予報幅")
ax.set_xlabel("予報日")
ax.set_ylabel("気温（℃）")
ax.set_xticks(x)
ax.set_xticklabels(dates)
ax.legend()

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```
````

````{note} 課題5：信頼度ごとの平均降水確率を可視化する

`jma_tokyo_weekly_weather.csv` の `信頼度` を使い，信頼度ごとの平均降水確率を棒グラフで表示せよ．

`src/plot_weekly_pop_by_reliability.py` を作成し，WebClass「第8回課題」問5から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 信頼度が空欄の行はどう扱ったか
2. 信頼度ごとのデータ数は十分か
3. 平均だけを見てよいか
````

````{dropdown} 解答例
信頼度が `A`，`B`，`C` の行だけを使い，それぞれの平均降水確率を計算して表示する例である．

```python
import csv
from pathlib import Path

import matplotlib.pyplot as plt

input_path = "data/processed/jma_tokyo_weekly_weather.csv"
output_path = "reports/figures/weekly_pop_by_reliability.png"

plt.rcParams["font.family"] = "Hiragino Sans"
Path("reports/figures").mkdir(parents=True, exist_ok=True)

summary = {
    "A": {"合計": 0, "件数": 0},
    "B": {"合計": 0, "件数": 0},
    "C": {"合計": 0, "件数": 0},
}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        reliability = row["信頼度"]

        if reliability not in summary:
            continue

        if row["降水確率"] == "":
            continue

        summary[reliability]["合計"] += int(row["降水確率"])
        summary[reliability]["件数"] += 1

labels = []
values = []

for reliability in ["A", "B", "C"]:
    count = summary[reliability]["件数"]

    if count == 0:
        continue

    labels.append(reliability)
    values.append(summary[reliability]["合計"] / count)

fig, ax = plt.subplots(figsize=(6, 4))

ax.bar(labels, values)
ax.set_title("信頼度ごとの平均降水確率")
ax.set_xlabel("信頼度")
ax.set_ylabel("平均降水確率（%）")
ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```
````

````{note} 課題6：seabornで地点別の最高気温を可視化する

`pandas` と `seaborn` を使い，地点別の最高気温を折れ線グラフで表示せよ．

`src/plot_weekly_max_temperature_by_point_seaborn.py` を作成し，WebClass「第8回課題」問6から提出せよ．

提出するのは作成したPythonファイルのみである．作成されるPNGファイルは提出しなくてよい．

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. `csv` と `matplotlib` だけで作る場合と比べて，コードはどう変わったか
2. `hue="地点名"` は何を表しているか
3. ライブラリを使う利点と注意点は何か
````

````{dropdown} 解答例
`pandas` でCSVを読み込み，`seaborn.lineplot` で地点別に線を分けて表示する例である．

```python
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

input_path = "data/processed/jma_tokyo_weekly_temperature.csv"
output_path = "reports/figures/weekly_max_temperature_by_point_seaborn.png"

plt.rcParams["font.family"] = "Hiragino Sans"
Path("reports/figures").mkdir(parents=True, exist_ok=True)

temperature_df = pd.read_csv(input_path)
temperature_df = temperature_df.dropna(subset=["最高気温"])

fig, ax = plt.subplots(figsize=(8, 5))

sns.lineplot(
    data=temperature_df,
    x="予報日",
    y="最高気温",
    hue="地点名",
    marker="o",
    ax=ax
)

ax.set_title("地点別の週間最高気温予報")
ax.set_xlabel("予報日")
ax.set_ylabel("最高気温（℃）")

plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
```
````
