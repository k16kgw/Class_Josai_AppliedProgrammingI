# 第7回　データの前処理II

### 前回の復習

- 前処理とは，取得したデータを分析しやすい形に整える作業である
- JSONは階層構造をもつため，表形式で扱うには必要な値を取り出してCSV化することがある
- CSVの値は基本的に文字列として読み込まれるため，数値計算には型変換が必要である
- 欠損値には，削除，補完，空欄のまま保持するなど複数の対応がある
- 日本語文字列では，全角空白や余分な空白を整理することがある
- 生データは `data/raw` に残し，前処理後のデータは `data/processed` に保存する

前回は，第5回で取得した気象庁の天気予報JSONから，天気，風，波を取り出して表形式CSVを作成した．
今回は，同じJSONの中に入っている複数の表を取り出し，結合，日付処理，カテゴリ作成，集計用データセットの作成を学ぶ．

```{warning}
第7回では，新しいAPI取得は行わない．
第5回で取得した `data/raw/jma_tokyo_forecast.json` を使う．
```

### 到達目標

データの前処理IIとして，分析目的に合わせたデータセットを作成する方法を学ぶ．

- 1つのJSONの中に含まれる複数の表を区別できる
- 天気表，降水確率表，気温表をそれぞれ作成できる
- 共通するキーを使って表を結合できる
- 結合できないデータを無理に結合しない理由を説明できる
- ISO形式の日時文字列から日付や時刻を取り出せる
- 日本語カテゴリを整理し，集計用のカテゴリを作成できる
- 地域別・天気別の集計データを作成できる

### 準備

今回も，第5回で取得した次のデータを使う．

```text
data/raw/jma_tokyo_forecast.json
```

第6回から続けて作業している場合は，フォルダ `5` をそのまま使ってよい．
第7回用に別フォルダを作る場合は，第5回で取得した `jma_tokyo_forecast.json` をコピーして使う．
どちらの場合も，この講義ノート内のコードは**作業フォルダ直下に `data/raw/jma_tokyo_forecast.json` がある**ことを前提にしている．

````{note} 演習0：READMEに第7回の記録を追記する
`README.md` に次の内容を追記せよ．

```markdown
## 第7回 前処理記録

- 元データ：data/raw/jma_tokyo_forecast.json
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 取得方法：第5回で取得したJSONを使用する
- 前処理内容：
  - 天気表を作成する
  - 降水確率表を作成する
  - 天気表と降水確率表を結合する
  - 日付列と天気カテゴリを作成する
  - 地域別・天気カテゴリ別の集計表を作成する
- 注意：
  - 気温データは地点名で提供されるため，天気表とは別表として扱う
```

`data/raw/jma_tokyo_forecast.json` がない場合は，第5回のデータを用意してから進むこと．
````

---

## 前処理IIで扱うこと

前回は，1つの時系列から1つの表を作ることを中心に扱った．
今回は，1つのJSONの中に入っている複数の表を組み合わせ，分析目的に合う形へ変換する．

主に次の処理を扱う．

- 複数の時系列を別々の表として取り出す
- 共通キーを使って表を横方向に結合する
- 結合できない表を無理に結合しない
- 日時文字列から日付と時刻を取り出す
- 日本語の天気表現を大まかなカテゴリへ変換する
- 地域別・天気別に集計する

### 縦方向の結合と横方向の結合

複数の表を扱うときには，結合の方向を意識する．

```text
縦方向の結合：同じ列をもつ複数の表を，下に追加する
横方向の結合：共通のキーをもつ表から，別の列を追加する
```

今回の授業では，主に横方向の結合を扱う．

```text
天気表
  + 降水確率表
  = 天気と降水確率を含む表
```

ただし，結合にはキーが必要である．
キーとは，2つの表で同じ対象を表していることを示す列である．
今回の天気表と降水確率表では，次の2つをキーとして使う．

- `地域コード`
- `予報時刻`

---

## JSONの中の複数の表

第5回で取得した `jma_tokyo_forecast.json` には，複数の時系列が含まれている．
短期予報である `data[0]` の中には，次の3つの表に相当するデータが入っている．

| 位置 | 主な内容 | 地域の単位 |
| --- | --- | --- |
| `data[0]["timeSeries"][0]` | 天気，風，波 | 東京地方，伊豆諸島北部，伊豆諸島南部，小笠原諸島 |
| `data[0]["timeSeries"][1]` | 降水確率 | 東京地方，伊豆諸島北部，伊豆諸島南部，小笠原諸島 |
| `data[0]["timeSeries"][2]` | 気温 | 東京，大島，八丈島，父島 |

天気表と降水確率表は，地域コードが同じなので結合しやすい．
一方，気温表は地域の単位が異なるため，そのまま結合すると誤ったデータセットになる可能性がある．

````{note} 演習1：時系列ごとの地域名を確認する
`src/inspect_time_series.py` を次の内容で作成し，時系列ごとの地域名を確認せよ．

```python
import json

input_path = "data/raw/jma_tokyo_forecast.json"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]

for i, series in enumerate(forecast["timeSeries"]):
    area_names = [area["area"]["name"] for area in series["areas"]]
    area_codes = [area["area"]["code"] for area in series["areas"]]

    print("timeSeries番号:", i)
    print("時刻:", series["timeDefines"])
    print("地域名:", area_names)
    print("地域コード:", area_codes)
    print()
```

実行後，次を確認せよ．

1. `timeSeries[0]` と `timeSeries[1]` の地域名は同じか
2. `timeSeries[2]` の地域名は何か
3. 気温表を天気表にそのまま結合してよいか
````

---

## 天気表を作成する

まず，短期予報の `timeSeries[0]` から天気表を作成する．
第6回で作成した表と同じ内容であるが，第7回の結合処理でも使うため，ここで再確認する．

````{note} 演習2：天気表を作成する
`src/build_weather_table.py` を次の内容で作成し，`data/processed/jma_tokyo_weather_short.csv` を作成せよ．

```python
import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/processed/jma_tokyo_weather_short.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
weather_series = forecast["timeSeries"][0]

rows_out = []

for area in weather_series["areas"]:
    area_name = area["area"]["name"]
    area_code = area["area"]["code"]

    for i, forecast_time in enumerate(weather_series["timeDefines"]):
        rows_out.append({
            "発表機関": forecast["publishingOffice"],
            "発表時刻": forecast["reportDatetime"],
            "地域名": area_name,
            "地域コード": area_code,
            "予報時刻": forecast_time,
            "天気コード": area["weatherCodes"][i],
            "天気": area["weathers"][i],
            "風": area["winds"][i],
            "波": area["waves"][i]
        })

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード", "予報時刻",
    "天気コード", "天気", "風", "波"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))
```

実行後，次を確認せよ．

1. 行数はいくつか
2. `地域コード` と `予報時刻` が含まれているか
3. 第6回で作成した表と同じ内容になっているか
````

---

## 降水確率表を作成する

次に，短期予報の `timeSeries[1]` から降水確率表を作成する．
降水確率は `pops` に入っている．

````{note} 演習3：降水確率表を作成する
`src/build_pop_table.py` を次の内容で作成し，`data/processed/jma_tokyo_pop_short.csv` を作成せよ．

```python
import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/processed/jma_tokyo_pop_short.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
pop_series = forecast["timeSeries"][1]

rows_out = []

for area in pop_series["areas"]:
    area_name = area["area"]["name"]
    area_code = area["area"]["code"]

    for i, forecast_time in enumerate(pop_series["timeDefines"]):
        rows_out.append({
            "地域名": area_name,
            "地域コード": area_code,
            "予報時刻": forecast_time,
            "降水確率": area["pops"][i]
        })

fieldnames = ["地域名", "地域コード", "予報時刻", "降水確率"]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))
```

実行後，次を確認せよ．

1. 行数はいくつか
2. `降水確率` は文字列として保存されているか
3. 天気表と同じ `地域コード` が含まれているか
4. 天気表と同じ `予報時刻` がすべて含まれているか
````

```{note}
天気表と降水確率表は，地域は同じでも時刻の刻みが異なる．
そのため，完全には一致しない時刻がある．
これが結合時に空欄が発生する理由になる．
```

---

## 表を結合する

天気表と降水確率表を結合する．
ここでは，天気表を基準にして，対応する降水確率がある場合だけ `降水確率` を追加する．
対応する値がない場合は空欄にする．

このような結合は，天気表の行を残すため**左結合**と呼ばれる．

```text
キー：（地域コード，予報時刻）
```

````{note} 演習4：天気表と降水確率表を結合する
`src/join_weather_pop.py` を次の内容で作成し，`data/processed/jma_tokyo_weather_pop_joined.csv` を作成せよ．

```python
import csv

weather_path = "data/processed/jma_tokyo_weather_short.csv"
pop_path = "data/processed/jma_tokyo_pop_short.csv"
output_path = "data/processed/jma_tokyo_weather_pop_joined.csv"

with open(pop_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    pop_rows = list(reader)

pop_by_key = {}
for row in pop_rows:
    key = (row["地域コード"], row["予報時刻"])
    pop_by_key[key] = row["降水確率"]

rows_out = []

with open(weather_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row["地域コード"], row["予報時刻"])
        row["降水確率"] = pop_by_key.get(key, "")
        rows_out.append(row)

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード", "予報時刻",
    "天気コード", "天気", "風", "波", "降水確率"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))
```

実行後，次を確認せよ．

1. 結合後の行数は天気表と同じか
2. `降水確率` が入っている行は何行あるか
3. `降水確率` が空欄の行はなぜ発生したか
4. 結合に使ったキーは何か
````

---

## 結合後の欠損値を確認する

結合後には，対応する値がないために空欄が発生することがある．
これは必ずしもデータの誤りではない．
今回の場合，天気と降水確率の予報時刻が完全には一致しないため，空欄が生じる．

````{note} 演習5：結合後の空欄を確認する
`src/check_joined_missing.py` を次の内容で作成し，結合後の空欄を確認せよ．

```python
import csv

input_path = "data/processed/jma_tokyo_weather_pop_joined.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

missing_pop = 0

for row in rows:
    if row["降水確率"] in missing_values:
        missing_pop += 1
        print("降水確率なし:", row["地域名"], row["予報時刻"])

print("降水確率が空欄の行数:", missing_pop)
print("全体の行数:", len(rows))
```

実行後，次を確認せよ．

1. `降水確率` が空欄の行数はいくつか
2. どの予報時刻で空欄が発生しているか
3. 空欄の行を削除すると，どの情報が失われるか
````

---

## 日時と天気カテゴリを作成する

分析しやすいデータセットにするため，次の列を追加する．

- `予報日`：`予報時刻` の日付部分
- `予報時`：`予報時刻` の時刻部分
- `天気カテゴリ`：天気の文字列を大まかに分類したもの

天気カテゴリは，次のルールで作成する．

```text
雨を含む → 雨
雪を含む → 雪
晴を含む → 晴
くもりを含む → くもり
それ以外 → その他
```

カテゴリ化は便利である一方，情報を単純化する処理である．
たとえば「晴れ　時々　雨」を「雨」に分類するか「晴」に分類するかは，分析目的によって判断が変わる．

````{warning} 課題1：分析用データセットを作成する
`src/build_analysis_table.py` を次の内容で作成し，`data/processed/jma_tokyo_weather_pop_ready.csv` を作成せよ．
なお，コード内の `〇〇` には適切な値を入れること．

```python
import csv

input_path = "data/processed/jma_tokyo_weather_pop_joined.csv"
output_path = "data/processed/jma_tokyo_weather_pop_ready.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

def clean_text(value):
    return value.strip().replace("　", " ")

def to_int_or_blank(value):
    value = clean_text(value)
    if value in missing_values:
        return ""
    return int(value)

def weather_category(weather):
    weather = clean_text(weather)
    if "雨" in weather:
        return "雨"
    if "雪" in weather:
        return "雪"
    if "晴" in weather:
        return "晴"
    if "くもり" in weather:
        return "くもり"
    return "その他"

rows_out = []

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        forecast_time = clean_text(row["予報時刻"])
        weather = clean_text(row["天気"])

        rows_out.append({
            "発表機関": clean_text(row["発表機関"]),
            "発表時刻": clean_text(row["発表時刻"]),
            "地域名": clean_text(row["地域名"]),
            "地域コード": clean_text(row["地域コード"]),
            "予報時刻": forecast_time,
            "予報日": forecast_time[:10],
            "予報時": forecast_time[11:16],
            "天気コード": int(clean_text(row["天気コード"])),
            "天気": weather,
            "天気カテゴリ": weather_category(weather),
            "風": clean_text(row["風"]),
            "波": clean_text(row["波"]),
            "降水確率": to_int_or_blank(row["降水確率"])
        })

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード",
    "予報時刻", "予報日", "予報時",
    "天気コード", "天気", "天気カテゴリ",
    "風", "波", "降水確率"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("出力行数:", 〇〇)
```

次の内容をWebClass「第7回課題」問1から提出せよ．

1. `src/build_analysis_table.py`
2. `data/processed/jma_tokyo_weather_pop_ready.csv`
3. README.mdに追記した前処理方針
````

<!--
print("出力行数:", len(rows_out))
-->

---

## 集計用データセットを作成する

最後に，地域別・天気カテゴリ別の件数を集計する．
これは，前処理済みデータから分析用のデータセットを作る処理である．

````{warning} 課題2：地域別・天気カテゴリ別に集計する
`src/summarize_weather.py` を次の内容で作成し，`data/processed/weather_summary_by_area.csv` を作成せよ．
なお，コード内の `〇〇` には適切な値を入れること．

```python
import csv

input_path = "data/processed/jma_tokyo_weather_pop_ready.csv"
output_path = "data/processed/weather_summary_by_area.csv"

summary = {}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        key = (row["地域名"], row["天気カテゴリ"])

        if key not in summary:
            summary[key] = {
                "件数": 0,
                "降水確率あり件数": 0,
                "降水確率合計": 0
            }

        summary[key]["件数"] += 1

        if row["降水確率"] != "":
            summary[key]["降水確率あり件数"] += 1
            summary[key]["降水確率合計"] += int(row["降水確率"])

rows_out = []

for (area_name, category), values in summary.items():
    if values["降水確率あり件数"] == 0:
        average_pop = ""
    else:
        average_pop = values["降水確率合計"] / values["降水確率あり件数"]

    rows_out.append({
        "地域名": area_name,
        "天気カテゴリ": category,
        "件数": values["件数"],
        "降水確率あり件数": values["降水確率あり件数"],
        "平均降水確率": average_pop
    })

rows_out.sort(key=lambda row: (row["地域名"], row["天気カテゴリ"]))

fieldnames = ["地域名", "天気カテゴリ", "件数", "降水確率あり件数", "平均降水確率"]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("出力行数:", 〇〇)
```

次の内容をWebClass「第7回課題」問2から提出せよ．

1. `src/summarize_weather.py`
2. `data/processed/weather_summary_by_area.csv`
3. 集計結果から分かることをREADME.mdに2文以上で記載したもの
````
<!--
print("出力行数:", len(rows_out))
-->

---

## 気温データを別表として扱う

気温データは，`data[0]["timeSeries"][2]` に入っている．
ただし，天気表や降水確率表とは地域の単位が異なる．

天気表の地域名：

```text
東京地方，伊豆諸島北部，伊豆諸島南部，小笠原諸島
```

気温表の地点名：

```text
東京，大島，八丈島，父島
```

この2つは，名前もコードも一致しない．
そのため，気温を天気表へ結合したい場合は，別途「どの地点がどの予報地域を代表するか」を示す対応表が必要になる．
対応表なしに名前だけで結合すると，分析結果の意味が曖昧になる．

````{note} 演習6：気温表を別表として作成する
`src/build_temperature_table.py` を次の内容で作成し，`data/processed/jma_tokyo_temperature_short.csv` を作成せよ．

```python
import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/processed/jma_tokyo_temperature_short.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
temp_series = forecast["timeSeries"][2]

rows_out = []

for area in temp_series["areas"]:
    point_name = area["area"]["name"]
    point_code = area["area"]["code"]

    for i, forecast_time in enumerate(temp_series["timeDefines"]):
        rows_out.append({
            "発表機関": forecast["publishingOffice"],
            "発表時刻": forecast["reportDatetime"],
            "地点名": point_name,
            "地点コード": point_code,
            "予報時刻": forecast_time,
            "気温": int(area["temps"][i])
        })

fieldnames = ["発表機関", "発表時刻", "地点名", "地点コード", "予報時刻", "気温"]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))
```

実行後，次を確認せよ．

1. `地点名` にはどのような値が入っているか
2. `地点コード` は天気表の `地域コード` と一致しているか
3. 気温表を天気表へ結合するには，どのような追加情報が必要か
````

---

## 前処理の判断

今回の前処理では，複数の判断を行った．

- 第5回で取得したJSONだけを使用した
- 短期予報の `timeSeries[0]` を天気表として取り出した
- 短期予報の `timeSeries[1]` を降水確率表として取り出した
- `地域コード` と `予報時刻` をキーとして天気表と降水確率表を結合した
- 対応する降水確率がない場合は空欄のまま保持した
- 気温表は地域単位が異なるため，別表として扱った
- ISO形式の時刻から日付と時刻を取り出した
- 天気の詳細表現を大まかなカテゴリへ変換した
- 地域別・天気カテゴリ別に件数を集計した

これらはすべて，分析結果に影響を与える判断である．
したがって，READMEやスクリプトに，どのような方針で処理したかを残す必要がある．

特にカテゴリ化は，情報を整理すると同時に情報を失う処理でもある．
「晴れ　時々　雨」を雨に分類するか，晴に分類するかによって，集計結果は変わる．
分析目的に応じて分類ルールを説明できることが重要である．

---

## Git管理と前処理

第7回では，多くの中間ファイルが作成される．
すべてをGitで管理する必要はないが，少なくとも次のものは残すとよい．

- 前処理スクリプト
- README
- 最終的な集計データ
- 小さなマスタデータや対応表を作成した場合はそのファイル

一方，取得直後のJSONは更新される可能性があるため，`.gitignore` で `data/raw` を除外している場合はGit管理対象にならない．
その場合でも，取得URL，取得日，取得スクリプトを残しておけば再取得しやすい．

今回の処理の流れは，次のように表せる．

```text
data/raw/jma_tokyo_forecast.json
  ↓ src/build_weather_table.py
data/processed/jma_tokyo_weather_short.csv

data/raw/jma_tokyo_forecast.json
  ↓ src/build_pop_table.py
data/processed/jma_tokyo_pop_short.csv

data/processed/jma_tokyo_weather_short.csv
data/processed/jma_tokyo_pop_short.csv
  ↓ src/join_weather_pop.py
data/processed/jma_tokyo_weather_pop_joined.csv
  ↓ src/build_analysis_table.py
data/processed/jma_tokyo_weather_pop_ready.csv
  ↓ src/summarize_weather.py
data/processed/weather_summary_by_area.csv
```

---

## まとめ

- 前処理IIでは，複数表の作成，結合，日付処理，カテゴリ作成，集計用データセット作成を扱った
- 1つのJSONの中にも，複数の表に相当するデータが入っていることがある
- 横方向の結合は，共通のキーを使って別の列を追加する処理である
- 結合できるかどうかは，列名だけでなく，地域や時刻の意味が一致しているかで判断する
- ISO形式の日時文字列から，日付や時刻を取り出すことで集計しやすくなる
- 日本語の天気表現をカテゴリ化すると集計しやすくなるが，分類ルールを説明する必要がある
- 分析目的に応じた最終データセットを作ることが，前処理の重要な役割である

次回は可視化を扱う．

- 前処理済みデータをもとに，表だけでは把握しにくい傾向を図として表現する方法を学ぶ
- 今回作成した地域別・天気カテゴリ別集計のようなデータは，棒グラフで確認できる

### 課題の提出期限

<span style="color: red; ">6月2日(火)23:59まで</span>

---

## 自主学習用の発展問題

````{note} 発展課題1：週間予報を表にする

`data[1]["timeSeries"][0]` から週間予報の表を作成せよ．

出力ファイル名は次とする．

```text
data/processed/jma_tokyo_weekly_weather.csv
```

出力列は次の通りとする．

```text
地域名,地域コード,予報時刻,天気コード,降水確率,信頼度
```

次の問いに答えよ．

1. `降水確率` が空欄の行はあるか
2. `信頼度` が空欄の行はあるか
3. 空欄は削除すべきか，そのまま残すべきか
````

````{note} 発展課題2：天気カテゴリのルールを変える

現在のカテゴリ化では，`雨` を含む天気を最優先で「雨」に分類している．
このルールを変更し，`晴` を含む場合は優先的に「晴」に分類するようにせよ．

次の問いに答えよ．

1. どの関数を変更すればよいか
2. 集計結果は変わるか
3. どちらの分類ルールが分析目的に合っていると思うか
````

````{note} 発展課題3：日付別に集計する

`jma_tokyo_weather_pop_ready.csv` を用いて，`予報日` と `天気カテゴリ` ごとの件数を集計せよ．

出力ファイル名は次とする．

```text
data/processed/weather_summary_by_date.csv
```

出力列は次の3列とする．

```text
予報日,天気カテゴリ,件数
```
````

````{note} 発展課題4：気温との対応表を考える

気温表の地点名と天気表の地域名を対応させる表を作るとしたら，どのような列が必要か考えよ．

例：

```text
地点名,地点コード,対応する地域名,対応する地域コード,対応理由
```

次の問いに答えよ．

1. 「東京」はどの地域を代表すると考えられるか
2. 「大島」「八丈島」「父島」はどの地域と関係が深いか
3. 対応表を作るとき，主観的な判断をどのように記録すべきか
````
