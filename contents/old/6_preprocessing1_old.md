# 第6回　データの前処理I

### 前回の復習

- API：プログラムからデータ提供サービスを利用するための窓口
- APIへの問い合わせ：エンドポイントとパラメタからなる
- 多くの API は JSON 形式でデータを返す
- JSON は階層構造をもつため，必要な値を取り出すにはキーやリストの位置を確認する必要がある
- 取得した JSON は `data/raw` に保存し，分析しやすく加工したCSVは `data/processed` に保存する．
- 気象庁の天気予報JSONを取得して中身を確認した

取得したデータはそのまま分析に使えるとは限らない．例えば
- 値が空欄の箇所がある
- 数値が文字列として保存されている
- 日本語の文字列に余分な空白が含まれている

**前処理**：データを分析しやすい形に整える作業

欠損値，型変換，範囲確認，文字列の整理などの基本を扱う．

### 到達目標

取得したデータを分析可能な形に整えるための基礎を学ぶ．

- 前処理がなぜ必要かを説明できる．
- 日本語のオープンデータから必要な項目を取り出し，表形式CSVを作成できる．
- CSVを読み込み，行数，列名，値の概要を確認できる．
- 欠損値を検出し，削除または補完の考え方を説明できる．
- 文字列として読み込まれた数値を適切な型に変換できる．
- 日本語文字列の表記を整理できる．
- 前処理前のデータと前処理後のデータを分けて保存できる．

### 準備

<span style="color:red">今回は前回のフォルダ `5` 内で作業を実施する．</span>

前回の作業が完了していない場合は次の手続きを参考に，作業フォルダを作成すること．

````{dropdown} 演習0
本講義で使用するフォルダ `/User/<ユーザ名>/applied_programming_i/` 内に，フォルダ `5` を作成し，次の `README.md` ファイルと `.gitignore` ファイルを作成した上で Git の初期化を行うこと．  
データは前回と同じ気象庁の天気予報JSONデータを使用する．  
※ ターミナル・VSCodeのどちらで実施しても構わない．

README.md
```markdown
# 応用プログラミングI 第5・6回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

気象庁の天気予報データを使い，欠損値，型変換，文字列整理を行う．

## ディレクトリ構成

- `data/raw/`：取得直後のJSONや，JSONから取り出した未整形のCSV
- `data/processed/`：欠損値や型を整理したCSV
- `src/`：取得や前処理に用いるプログラム
- `README.md`：出典，取得日，前処理方針などの記録

## データ取得記録

- データ名：気象庁 天気予報JSON（東京都）
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 利用条件：公共データ利用規約（第1.0版）
- 取得日：2026年5月26日
- レスポンス形式：JSON
- 保存先：data/raw/jma_tokyo_forecast.json

## 前処理記録

- 元データ：data/raw/jma_tokyo_forecast.json
- 中間データ：data/raw/jma_tokyo_forecast_raw_table.csv
- 前処理後データ：data/processed/jma_tokyo_forecast_clean.csv
- 確認する項目：欠損値，型変換，日本語文字列の空白，値の範囲
```

.gitignore
```text
.DS_Store
*.swp
*.swo
*~
.vscode/
data/raw
```

また，フォルダ `5` 直下に，次のディレクトリ構成を作成せよ．
```text
5/
├── data/
│   ├── raw/
│   └── processed/
├── src/
└── README.md
```

**データの取得**

`src/fetch_jma_weather.py` を次の内容で作成し，東京都の天気予報JSONを取得する．

```python
import json
from urllib.request import urlopen

url = "https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json"
output_path = "data/raw/jma_tokyo_forecast.json"

with urlopen(url) as response:
    data = json.load(response)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("saved:", output_path)
print("データ型:", type(data))
print("要素数:", len(data))
```

実行後，`data/raw/jma_tokyo_forecast.json` が作成されていることを確認する．

````

---

## 前処理

データ分析において，取得したデータをそのまま使えるとは限らない．  
実際のデータには次のような問題が含まれることがある．

- **欠損値**がある
- 数値が文字列として保存されている
- 日付や時刻の形式がプログラムで扱いにくいものになっている
- 同じ意味の値に**表記揺れ**がある
- 日本語文字列に**全角空白や余分な空白**が含まれている
- **分析に不要な列**が含まれている
- 1つのJSONの中に複数の表が入っている

**前処理**：このような問題を確認し，分析しやすい形に整える作業

### 位置づけ

データ分析の流れは次のようになる．
```text
データ取得 → 前処理 → 集計・可視化 → 分析 → 報告
```

前処理は分析の前に行う準備であり，前処理をせずに分析すると欠損値や型の誤りによって計算が失敗したり，誤った結果を得たりすることがある．

### 記録

前処理は分析結果に影響を与える判断であるから，前処理で実施した内容を記録することで分析の再現性を保つ．
そのため，前処理は手作業で実施するよりもプログラムとして残すことが望ましい．

---

## オープンデータ

前回と同様，気象庁の天気予報JSONを用いる．
- 天気予報JSON（東京都）：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 気象庁ホームページ：https://www.jma.go.jp/
- 利用規約：https://www.jma.go.jp/jma/kishou/info/coment.html

```{tip} 注意
気象庁ホームページで公開されている情報は，権利表記の記載がない限り「公共データ利用規約（第1.0版）」に準拠した利用条件の下で利用できる．
利用する際は出典を記録すること．
```

```{tip} 注意
このJSONは気象庁サイトで利用されている公開データであり，長期的な仕様固定が保証された正式なAPIドキュメント付きサービスではないため，予告なく仕様が変更されることがある可能性を考慮すること．
```

---

## JSONから表形式データを作る

気象庁のJSONは階層構造をもつ．
前処理を学ぶため，まず必要な値を取り出し，表形式CSVへ変換する．

ここでは，次の列を持つCSVを作成する．

- `発表機関`
- `発表時刻`
- `地域名`
- `地域コード`
- `予報時刻`
- `天気`
- `風`
- `波`
- `降水確率`
- `気温`

降水確率や気温は，天気の時系列とは別の場所に入っている．
そのため，時刻ごとに値を対応させる必要がある．
対応する値がない場合は空欄として保存する．

````{note} 演習3：JSONを未整形CSVへ変換する
`src/make_raw_table.py` を次の内容で作成し，`data/raw/jma_tokyo_forecast_raw_table.csv` を作成せよ．

```python
import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/raw/jma_tokyo_forecast_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
office = forecast["publishingOffice"]
report_datetime = forecast["reportDatetime"]

weather_series = forecast["timeSeries"][0]
pop_series = forecast["timeSeries"][1]
temp_series = forecast["timeSeries"][2]

pop_by_time = {}
for area in pop_series["areas"]:
    area_name = area["area"]["name"]
    for time, pop in zip(pop_series["timeDefines"], area["pops"]):
        pop_by_time[(area_name, time)] = pop

temp_by_time = {}
for area in temp_series["areas"]:
    area_name = area["area"]["name"]
    for time, temp in zip(temp_series["timeDefines"], area["temps"]):
        temp_by_time[(area_name, time)] = temp

rows_out = []

for area in weather_series["areas"]:
    area_name = area["area"]["name"]
    area_code = area["area"]["code"]

    for i, time in enumerate(weather_series["timeDefines"]):
        rows_out.append({
            "発表機関": office,
            "発表時刻": report_datetime,
            "地域名": area_name,
            "地域コード": area_code,
            "予報時刻": time,
            "天気": area["weathers"][i],
            "風": area["winds"][i],
            "波": area["waves"][i],
            "降水確率": pop_by_time.get((area_name, time), ""),
            "気温": temp_by_time.get((area_name, time), "")
        })

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード", "予報時刻",
    "天気", "風", "波", "降水確率", "気温"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))
```

実行後，`data/raw/jma_tokyo_forecast_raw_table.csv` が作成されていることを確認せよ．
````

---

## データの概要を確認する

前処理の最初に行うことは，データの状態を確認することである．
いきなり値を変更するのではなく，まず次の点を見る．

- 行数
- 列名
- 各列の値の例
- 欠損値の有無
- 数値として扱いたい列の値
- 日本語文字列の表記

````{note} 演習4：CSVの概要を確認する
`src/inspect_forecast_table.py` を次の内容で作成し，未整形CSVの概要を確認せよ．

```python
import csv

input_path = "data/raw/jma_tokyo_forecast_raw_table.csv"

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
3. `降水確率` と `気温` は文字列として表示されているか
4. 空欄の値はあるか
````

---

## 欠損値を確認する

欠損値とは，本来あるべき値が存在しない状態である．
今回のCSVでは，対応する予報時刻に降水確率や気温がない場合，空欄として保存される．

````{note} 演習5：欠損値を確認する
`src/check_missing.py` を次の内容で作成し，欠損値を確認せよ．

```python
import csv

input_path = "data/raw/jma_tokyo_forecast_raw_table.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row_number, row in enumerate(rows, start=1):
    for key, value in row.items():
        if value in missing_values:
            print("欠損:", row_number, row["地域名"], row["予報時刻"], key)
```

実行後，次を確認せよ．

1. どの列に欠損値があるか
2. 欠損値はなぜ発生していると考えられるか
3. 欠損値を削除すべきか，空欄のまま保持すべきか
````

欠損値は，必ずしも誤りではない．
今回のように，予報の種類によって提供される時刻が異なるために空欄になる場合もある．
欠損の理由を考えてから処理方針を決めることが重要である．

---

## 型変換と範囲確認

CSVの値は基本的に文字列として読み込まれる．
そのため，降水確率や気温を計算に使う場合は，数値へ変換する必要がある．

```python
pop = int(row["降水確率"])
temp = int(row["気温"])
```

ただし，空欄を `int` に変換するとエラーになる．
そのため，変換前に欠損値かどうかを確認する．

また，降水確率は通常0から100までの値である．
数値に変換した後，範囲が自然かどうかを確認する．

````{note} 演習6：型変換と範囲確認
`src/check_numeric.py` を次の内容で作成し，降水確率と気温を数値として確認せよ．

```python
import csv

input_path = "data/raw/jma_tokyo_forecast_raw_table.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for row in rows:
    pop_text = row["降水確率"]
    temp_text = row["気温"]

    if pop_text not in missing_values:
        pop = int(pop_text)
        if pop < 0 or pop > 100:
            print("降水確率の範囲外:", row["地域名"], row["予報時刻"], pop)

    if temp_text not in missing_values:
        temp = int(temp_text)
        if temp < -50 or temp > 50:
            print("気温の範囲外:", row["地域名"], row["予報時刻"], temp)

print("確認が完了しました")
```

実行後，次を確認せよ．

1. 降水確率は0から100の範囲にあるか
2. 気温に極端な値はあるか
3. 空欄を数値変換しようとすると何が起きるか
````

---

## 日本語文字列の整理

日本語の公開データでは，文字列の中に全角空白が含まれることがある．
たとえば，天気の値は次のようになっている場合がある．

```text
晴れ　時々　くもり
```

このままでも人間は読めるが，プログラムで分類や集計を行うときには，空白の揺れが問題になることがある．
そこで，文字列の前後の空白を削除し，全角空白を半角空白に置き換える．

```python
text = text.strip().replace("　", " ")
```

---

## 前処理済みデータを作成する

ここでは，次の方針で前処理を行う．

- 日本語文字列の前後の空白を削除する
- 全角空白を半角空白に変換する
- `降水確率` と `気温` は，空欄でなければ整数に変換する
- 空欄は空欄のまま残す
- 列名は日本語のまま残す

今回は欠損値を削除しない．
理由は，欠損が「データの誤り」ではなく，予報時刻と予報項目の対応の違いから生じている可能性があるためである．

````{warning} 課題2
`src/clean_forecast_table.py` を次の内容で作成し，`data/processed/jma_tokyo_forecast_clean.csv` を作成せよ．  
なお，コード内の`〇〇`には適切な値を入れること．

```python
import csv

input_path = "data/raw/jma_tokyo_forecast_raw_table.csv"
output_path = "data/processed/jma_tokyo_forecast_clean.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

def clean_text(value):
    return value.strip().replace("　", " ")

def to_int_or_blank(value):
    value = clean_text(value)
    if value in missing_values:
        return ""
    return int(value)

rows_out = []

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        rows_out.append({
            "発表機関": clean_text(row["発表機関"]),
            "発表時刻": clean_text(row["発表時刻"]),
            "地域名": clean_text(row["地域名"]),
            "地域コード": clean_text(row["地域コード"]),
            "予報時刻": clean_text(row["予報時刻"]),
            "天気": clean_text(row["天気"]),
            "風": clean_text(row["風"]),
            "波": clean_text(row["波"]),
            "降水確率": to_int_or_blank(row["降水確率"]),
            "気温": to_int_or_blank(row["気温"])
        })

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード", "予報時刻",
    "天気", "風", "波", "降水確率", "気温"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("出力行数:", 〇〇)
```

次の内容をWebClass「第6回課題」問2から提出せよ．

1. `src/clean_forecast_table.py`
2. `data/processed/jma_tokyo_forecast_clean.csv`
3. README.mdに追記した前処理方針
````

<!--
print("出力行数:", len(rows_out))
-->

---

## 前処理の判断

前処理では，正解が1つに決まらないことが多い．
たとえば，欠損値を削除するか補完するかは，分析目的によって変わる．

### 削除が適切な場合

- 欠損が少ない
- 欠損した行を除いても分析に大きな影響がない
- 重要な列が欠損している
- 補完するとかえって誤解を生む

### 補完が適切な場合

- 欠損が多く，削除するとデータが大きく減る
- 欠損の理由が分かっている
- 平均値や中央値で補うことに意味がある
- 欠損を別カテゴリとして扱える

### 今回のデータの場合

今回の気象庁データでは，降水確率や気温の空欄が必ずしも誤りとは限らない．
天気，降水確率，気温は，それぞれ別の時系列として提供されている．
したがって，空欄を単純に削除すると，天気の情報まで失われる可能性がある．

このように，前処理では値だけでなく，データの生成過程や構造を理解することが重要である．

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

重要なのは，次の関係を後から説明できることである．

```text
data/raw/jma_tokyo_forecast.json
  ↓ src/make_raw_table.py
data/raw/jma_tokyo_forecast_raw_table.csv
  ↓ src/clean_forecast_table.py
data/processed/jma_tokyo_forecast_clean.csv
```

---

## まとめ

- 前処理とは，取得したデータを分析しやすい形に整える作業である．
- 前処理の前には，行数，列名，値の例，欠損値，数値として扱う列，日本語文字列を確認する．
- JSONは階層構造をもつため，表形式で扱うには必要な値を取り出してCSV化することがある．
- CSVの値は基本的に文字列として読み込まれるため，数値計算には型変換が必要である．
- 欠損値には，削除，補完，空欄のまま保持するなど複数の対応がある．
- 日本語文字列では，全角空白や余分な空白を整理することがある．
- 生データは `data/raw` に残し，前処理後のデータは `data/processed` に保存する．
- 前処理の方針は，READMEやスクリプトとして記録する．

次回はデータの前処理IIを扱う．

- 複数地域のデータをまとめる方法，日付やカテゴリの扱い，集計用データセットの作成を学ぶ．
- 今回扱った欠損値，型変換，文字列整理を土台として，より分析目的に近いデータセットを作成する．

### 課題の提出期限

<span style="color: red; ">5月26日(火)23:59まで</span>

---

## 自主学習用の発展問題

````{note} 発展課題1：欠損値の扱いを比較する

`jma_tokyo_forecast_raw_table.csv` について，次の2つの方針で前処理した場合を比較せよ．

1. `降水確率` または `気温` が欠損している行を削除する
2. 欠損値を空欄のまま保持する

次の問いに答えよ．

1. 出力される行数はどう変わるか．
2. 天気の情報はどれだけ残るか．
3. どちらの方針が適切だと思うか．その理由を説明せよ．
````

```{dropdown} 解答例

欠損を含む行を削除すると，降水確率や気温がない予報時刻の行が失われる．
その結果，天気や風の情報まで削除される可能性がある．

一方，欠損値を空欄のまま保持すると，数値計算には注意が必要だが，天気や風などの他の情報を残せる．
今回のように，予報項目によって時刻の対応が異なるデータでは，空欄のまま保持する方が自然な場合がある．
```

````{note} 発展課題2：文字列整理の効果を確認する

次の2つの文字列は，人間には似て見えるが，プログラム上は異なる文字列である．

```python
"晴れ　時々　くもり"
"晴れ 時々 くもり"
```

次の問いに答えよ．

1. どこが異なるか．
2. `replace("　", " ")` は何をしているか．
3. 文字列の表記揺れを放置すると，集計時にどのような問題が起こるか．
````

```{dropdown} 解答例

1. 1つ目は全角空白を含み，2つ目は半角空白を含む．
2. `replace("　", " ")` は，全角空白を半角空白に置き換える処理である．
3. 同じ意味の天気が別カテゴリとして集計される可能性がある．たとえば，「晴れ　時々　くもり」と「晴れ 時々 くもり」が別々に数えられてしまう．
```

````{note} 発展課題3：前処理を関数として考える

本文では，前処理を
$$
D_{\mathrm{processed}} = T(D_{\mathrm{raw}})
$$
と表した．

次の問いに答えよ．

1. 今回の $D_{\mathrm{raw}}$ は何を表すか．
2. 今回の $T$ は何を表すか．
3. 今回の $D_{\mathrm{processed}}$ は何を表すか．
4. この考え方は，再現可能性にどのように役立つか．
````

```{dropdown} 解答例

1. $D_{\mathrm{raw}}$ は，気象庁から取得したJSON，またはそこから作成した未整形CSVを表す．
2. $T$ は，JSONから表形式へ変換し，空白整理，型変換，欠損値の扱いを行う処理を表す．
3. $D_{\mathrm{processed}}$ は，前処理後の `jma_tokyo_forecast_clean.csv` を表す．
4. 前処理を関数として考えると，どの入力にどの処理を適用して，どの出力を得たかを明確にできる．そのため，後から同じ処理を再実行しやすくなる．
```
