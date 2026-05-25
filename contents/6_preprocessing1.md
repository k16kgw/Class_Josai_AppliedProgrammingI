# 第6回　データの前処理I

### 前回の復習

- API：プログラムからデータ提供サービスを利用するための窓口
- エンドポイント：APIへ問い合わせるURL
- レスポンス：APIから返ってくる結果
- 多くの API は JSON 形式でデータを返す
- JSON はリストと辞書が入れ子になった階層構造をもつ
- 取得した JSON は `data/raw` に保存し，加工したCSVは `data/processed` に保存する
- 第5回では，気象庁の天気予報JSON（東京都）を取得し，中身を確認した

取得したデータは，そのまま分析に使えるとは限らない．
例えば，次のような問題が含まれることがある．

- 必要な値が深い階層の中にある
- 数値のように見える値が文字列として保存されている
- 日本語の文字列に全角空白や余分な空白が含まれている
- 日時の文字列から日付や時刻を取り出したい
- 1つのJSONの中に複数の表が入っている

**前処理**：取得したデータを分析しやすい形に整える作業

今回は，第5回で取得した `data/raw/jma_tokyo_forecast.json` を使い，前処理の基本を学ぶ．

### 到達目標

取得したデータを分析可能な形に整えるための基礎を学ぶ．

- 前処理がなぜ必要かを説明できる
- JSONの階層構造から必要な項目を取り出せる
- 気象庁の日本語JSONデータから表形式CSVを作成できる
- CSVを読み込み，行数，列名，値の例を確認できる
- 欠損値や空欄を確認できる
- 文字列として読み込まれた数値を整数に変換できる
- 日本語文字列の全角空白を整理できる
- 前処理前のデータと前処理後のデータを分けて保存できる

### 準備

<span style="color:red">今回は第5回で作成したフォルダ `5` 内で作業を続ける．</span>

第5回で取得した次のファイルを使う．

```text
5/data/raw/jma_tokyo_forecast.json
```

````{note} 演習0：作業フォルダとデータを確認する

1. 第5回で作成した `/User/<ユーザ名>/applied_programming_i/5` を開く．
2. 次のディレクトリ構成になっているか確認する．

```text
5/
├── data/
│   ├── raw/
│   │   └── jma_tokyo_forecast.json
│   └── processed/
├── src/
└── README.md
```

3. `README.md` に次の内容を追記する．

```markdown
## 第6回 前処理記録

- 元データ：data/raw/jma_tokyo_forecast.json
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 前処理内容：JSONから天気予報の表を作成し，型変換と文字列整理を行う
- 中間データ：data/raw/jma_tokyo_weather_raw_table.csv
- 前処理後データ：data/processed/jma_tokyo_weather_clean.csv
```

4. `jma_tokyo_forecast.json` がない場合は，以下のZIPファイルをダウンロードして展開し，`jma_tokyo_forecast.json` を `data/raw/` 以下に配置すること．

[jma_tokyo_forecast_json.zip](./analysis/5/data/raw/jma_tokyo_forecast_json.zip)
````

---

## 前処理

データ分析の流れは次のようになる．

```text
データ取得 → 前処理 → 集計・可視化 → 分析 → 報告
```

前処理は，分析の前に行う準備である．
前処理をせずに分析すると，型の誤り，空欄，表記揺れなどによって計算が失敗したり，誤った結果を得たりすることがある．

### 前処理でよく行うこと

- 必要な列だけを取り出す
- JSONを表形式CSVに変換する
- 欠損値や空欄を確認する
- 文字列を数値へ変換する
- 日時文字列から日付や時刻を取り出す
- 日本語文字列の全角空白を整理する
- 処理した内容をREADMEやスクリプトに残す

---

## 使用するデータ

第5回で取得した気象庁の天気予報JSON（東京都）を使う．

- 気象庁ホームページ：https://www.jma.go.jp/
- 天気予報JSON（東京都）：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 地域コード一覧：https://www.jma.go.jp/bosai/common/const/area.json
- 利用規約：https://www.jma.go.jp/jma/kishou/info/coment.html

```{tip} 注意
気象庁ホームページで公開されている情報は，権利表記の記載がない限り「公共データ利用規約（第1.0版）」に準拠した利用条件の下で利用できる．
利用する際は出典を記録すること．
```

```{tip} 注意
気象庁の天気予報JSONは，気象庁サイトで公開されている日本語データである．
ただし，長期的な仕様固定が保証された正式なAPIドキュメント付きサービスとして利用するものではないため，URLやJSON構造が変更される可能性に注意する．
```

### JSONの主な構造

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

今回は `data[0]["timeSeries"][0]` に入っている**天気，風，波**を取り出し，前処理の基本を扱う．
降水確率や気温は別の時系列として入っているため，第7回で結合や別表としての扱いを学ぶ．

```{tip} 注意
気温データの地域名は「東京地方」ではなく「東京」「大島」「八丈島」「父島」のような地点名で入っている．
天気データの地域名とは完全には一致しないため，今回は無理に同じ表へ結合しないこととする．
```

---

## JSONの構造を確認する

前処理の前に，**データの形を確認する**．
いきなりCSVへ変換するのではなく，どこに何が入っているかを少しずつ調べることが重要である．

````{note} 演習1：JSONの構造を確認する
`src/inspect_jma_structure.py` を次の内容で作成し，`jma_tokyo_forecast.json` の構造を確認せよ．

```python
import json

input_path = "data/raw/jma_tokyo_forecast.json"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

print("一番外側の型:", type(data))
print("一番外側の要素数:", len(data))

forecast = data[0]
print("短期予報のキー:", forecast.keys())
print("発表機関:", forecast["publishingOffice"])
print("発表時刻:", forecast["reportDatetime"])

for i, series in enumerate(forecast["timeSeries"]):
    print("timeSeries番号:", i)
    print("  時刻数:", len(series["timeDefines"]))
    print("  地域:", [area["area"]["name"] for area in series["areas"]])
    print("  最初の地域のキー:", series["areas"][0].keys())
```

実行後，次を確認せよ．

1. `data[0]["timeSeries"]` には何個の要素があるか
2. `timeSeries[0]`，`timeSeries[1]`，`timeSeries[2]` の地域名は同じか
3. `timeSeries[0]` の最初の地域には，どのようなキーがあるか
````

---

## JSONから表形式データを作る

JSONは階層構造をもつため，そのままでは表として扱いにくい．
そこで，必要な値を取り出してCSVに変換する．

今回は，短期予報の `timeSeries[0]` から次の列を持つCSVを作成する．

- `発表機関`
- `発表時刻`
- `地域名`
- `地域コード`
- `予報時刻`
- `天気コード`
- `天気`
- `風`
- `波`

````{note} 演習2：JSONを未整形CSVへ変換する
`src/make_raw_weather_table.py` を次の内容で作成し，`data/raw/jma_tokyo_weather_raw_table.csv` を作成せよ．

```python
import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/raw/jma_tokyo_weather_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
office = forecast["publishingOffice"]
report_datetime = forecast["reportDatetime"]

weather_series = forecast["timeSeries"][0]
time_defines = weather_series["timeDefines"]

rows_out = []

for area in weather_series["areas"]:
    area_name = area["area"]["name"]
    area_code = area["area"]["code"]

    for i, time in enumerate(time_defines):
        rows_out.append({
            "発表機関": office,
            "発表時刻": report_datetime,
            "地域名": area_name,
            "地域コード": area_code,
            "予報時刻": time,
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

実行後，`data/raw/jma_tokyo_weather_raw_table.csv` が作成されていることを確認せよ．
````

### なぜ `data/raw` に保存するのか

このCSVは，JSONから必要な値を取り出しただけの**未整形データ**である．
まだ文字列の整理や型変換をしていないため，`data/raw` に保存する．

```text
data/raw/jma_tokyo_forecast.json
  ↓ src/make_raw_weather_table.py
data/raw/jma_tokyo_weather_raw_table.csv
```

---

## データの概要を確認する

前処理の最初に行うことは，データの状態を確認することである．
まず次の点を見る．

- 行数
- 列名
- 各列の値の例
- 空欄の有無
- 数値として扱いたい列の値
- 日本語文字列の表記

````{note} 演習3：CSVの概要を確認する
`src/inspect_weather_table.py` を次の内容で作成し，未整形CSVの概要を確認せよ．

```python
import csv

input_path = "data/raw/jma_tokyo_weather_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames

print("行数:", len(rows))
print("列名:", fieldnames)

print("先頭3行:")
for row in rows[:3]:
    print(row)
```

実行後，次を確認せよ．

1. 行数はいくつか
2. 列名は何か
3. `天気コード` は文字列として表示されているか
4. `天気`，`風`，`波` の中に全角空白が含まれているか
````

---

## 欠損値を確認する

欠損値とは，本来あるべき値が存在しない状態である．
CSVでは，空欄，`NA`，`null`，`-` などで表されることがある．

今回作成した天気表では，欠損が見つからない可能性もある．
欠損がないことを確認するのも，前処理では重要な作業である．

````{note} 演習4：欠損値を確認する
`src/check_missing_weather.py` を次の内容で作成し，欠損値を確認せよ．

```python
import csv

input_path = "data/raw/jma_tokyo_weather_raw_table.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

missing_count = 0

for row_number, row in enumerate(rows, start=1):
    for key, value in row.items():
        if value in missing_values:
            missing_count += 1
            print("欠損:", row_number, row["地域名"], row["予報時刻"], key)

print("欠損値の個数:", missing_count)
```

実行後，次を確認せよ．

1. 欠損値は何個あるか
2. 欠損値がない場合，その結果をREADMEにどう記録するか
3. 欠損値があるデータでは，削除と保持のどちらが適切か
````

```{note}
第7回で扱う週間予報には，降水確率や信頼度の一部が空欄として入っている．
第6回では，まず欠損確認の方法を身につける．
```

---

## 型変換と範囲確認

CSVの値は基本的に文字列として読み込まれる．
`天気コード` は数字のように見えるが，CSVから読むと文字列である．

```python
weather_code_text = row["天気コード"]
weather_code = int(weather_code_text)
```

数値として扱う前には，次の確認を行う．

- 空欄ではないか
- 整数に変換できるか
- 値の範囲が不自然ではないか

````{note} 演習5：型変換と範囲確認
`src/check_weather_code.py` を次の内容で作成し，`天気コード` を整数として確認せよ．

```python
import csv

input_path = "data/raw/jma_tokyo_weather_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row in rows:
    code_text = row["天気コード"]
    code = int(code_text)

    if code < 100 or code > 450:
        print("天気コードの範囲外:", row["地域名"], row["予報時刻"], code)

print("確認が完了しました")
```

実行後，次を確認せよ．

1. `天気コード` は整数に変換できるか
2. 範囲外として表示された値はあるか
3. 数値変換前と数値変換後では，何が違うか
````

---

## 日本語文字列の整理

日本語の公開データでは，文字列の中に全角空白が含まれることがある．
たとえば，天気の値は次のようになっている場合がある．

```text
晴れ　時々　くもり
```

このままでも人間は読めるが，プログラムで分類や集計を行うときには，空白の違いが問題になることがある．
そこで，文字列の前後の空白を削除し，全角空白を半角空白に置き換える．

```python
text = text.strip().replace("　", " ")
```

````{note} 演習6：文字列整理の動作を確認する
Pythonで次を実行し，全角空白と半角空白の違いを確認せよ．

```python
text1 = "晴れ　時々　くもり"
text2 = "晴れ 時々 くもり"

print(text1 == text2)
print(text1.replace("　", " ") == text2)
```

実行後，次を確認せよ．

1. 1つ目の `print` は何を表示するか
2. 2つ目の `print` は何を表示するか
3. 全角空白を放置すると，集計時にどのような問題が起こるか
````

---

## 前処理済みデータを作成する

ここでは，次の方針で前処理を行う．

- 日本語文字列の前後の空白を削除する
- 全角空白を半角空白に変換する
- `天気コード` を整数に変換する
- `予報時刻` から `予報日` と `予報時` を作成する
- 前処理後のCSVは `data/processed` に保存する

````{warning} 課題1：前処理済みデータを作成する
`src/clean_weather_table.py` を次の内容で作成し，`data/processed/jma_tokyo_weather_clean.csv` を作成せよ．
なお，コード内の `〇〇` には適切な値を入れること．

```python
import csv

input_path = "data/raw/jma_tokyo_weather_raw_table.csv"
output_path = "data/processed/jma_tokyo_weather_clean.csv"

def clean_text(value):
    return value.strip().replace("　", " ")

rows_out = []

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        forecast_time = clean_text(row["予報時刻"])

        rows_out.append({
            "発表機関": clean_text(row["発表機関"]),
            "発表時刻": clean_text(row["発表時刻"]),
            "地域名": clean_text(row["地域名"]),
            "地域コード": clean_text(row["地域コード"]),
            "予報時刻": forecast_time,
            "予報日": forecast_time[:10],
            "予報時": forecast_time[11:16],
            "天気コード": int(clean_text(row["天気コード"])),
            "天気": clean_text(row["天気"]),
            "風": clean_text(row["風"]),
            "波": clean_text(row["波"])
        })

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード",
    "予報時刻", "予報日", "予報時",
    "天気コード", "天気", "風", "波"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("出力行数:", 〇〇)
```

次の内容をWebClass「第6回課題」問1から提出せよ．

1. `src/clean_weather_table.py`
2. `data/processed/jma_tokyo_weather_clean.csv`
3. README.mdに追記した前処理方針
````
<!--
print("出力行数:", len(rows_out))
-->

---

## 前処理の判断

前処理では，正解が1つに決まらないことが多い．
たとえば，欠損値を削除するか，空欄のまま保持するかは分析目的によって変わる．

### 削除が適切な場合

- 欠損が少ない
- 欠損した行を除いても分析に大きな影響がない
- 重要な列が欠損している
- 補完するとかえって誤解を生む

### 保持が適切な場合

- 欠損の理由がデータの構造から説明できる
- 欠損そのものに意味がある
- 別の処理であとから結合や補完を行う
- 他の列の情報を残したい

今回の気象庁データでは，天気，降水確率，気温がそれぞれ別の時系列として提供されている．
したがって，すべてを最初から1つの表に入れようとすると，時刻や地域名が合わず，空欄が多くなったり誤った結合をしたりする可能性がある．
前処理では，値だけでなく，データの構造を理解することが重要である．

---

## Git管理と前処理

前処理では，`data/raw` と `data/processed` を分けることが特に重要である．
生データを直接上書きすると，どのような処理をしたのか確認できなくなる．

Gitで管理するとよいものは次の通りである．

- 前処理スクリプト
- README
- メタデータ
- 小規模なサンプルデータ
- 前処理方針の記録

一方，サイズの大きいデータやライセンス上再配布できないデータは，Gitで管理しない方がよい場合がある．

今回の処理の流れは，次のように表せる．

```text
data/raw/jma_tokyo_forecast.json
  ↓ src/make_raw_weather_table.py
data/raw/jma_tokyo_weather_raw_table.csv
  ↓ src/clean_weather_table.py
data/processed/jma_tokyo_weather_clean.csv
```

---

## まとめ

- 前処理とは，取得したデータを分析しやすい形に整える作業である
- JSONは階層構造をもつため，必要な値を取り出してCSV化することがある
- 前処理の前には，行数，列名，値の例，欠損値，数値として扱う列，日本語文字列を確認する
- CSVの値は基本的に文字列として読み込まれるため，数値計算には型変換が必要である
- 日本語文字列では，全角空白や余分な空白を整理することがある
- 生データは `data/raw` に残し，前処理後のデータは `data/processed` に保存する
- 前処理の方針は，READMEやスクリプトとして記録する

次回はデータの前処理IIを扱う．

- 第5回で取得した同じJSONを使い，降水確率の表，気温の表，週間予報の表を作成する
- 複数の表を結合する方法，日付やカテゴリの扱い，集計用データセットの作成を学ぶ

### 課題の提出期限

<span style="color: red; ">5月26日(火)23:59まで</span>

---

## 自主学習用の発展問題

````{note} 発展課題1：気温データを別表として取り出す

`data[0]["timeSeries"][2]` から，次の列を持つCSVを作成せよ．

```text
発表機関,発表時刻,地点名,地点コード,予報時刻,気温
```

次の問いに答えよ．

1. 地点名にはどのような値が入っているか
2. 天気データの `地域名` と気温データの `地点名` は一致しているか
3. 気温データを天気データに結合するには，どのような対応表が必要か
````

````{note} 発展課題2：文字列整理の効果を確認する

`jma_tokyo_weather_raw_table.csv` と `jma_tokyo_weather_clean.csv` を比較し，`天気`，`風`，`波` の空白がどのように変わったか確認せよ．

次の問いに答えよ．

1. 全角空白は半角空白に変わっているか
2. 文字列整理後の方が読みやすいか
3. 集計や分類を行うとき，文字列整理はなぜ必要か
````
