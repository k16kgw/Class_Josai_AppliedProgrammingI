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
├── notebooks/
│   └── preprocessing1.ipynb
├── data/
│   ├── raw/
│   │   └── jma_tokyo_forecast.json
│   └── processed/
├── src/
└── README.md
```

3. `notebooks/`，`src/`，`data/processed/` がない場合は作成する．
4. JupyterLabまたはVS Codeで `notebooks/preprocessing1.ipynb` を新規作成する．
5. `README.md` に次の内容を追記する．

```markdown
## 第6回 前処理記録

- 元データ：data/raw/jma_tokyo_forecast.json
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 観察用ノートブック：notebooks/preprocessing1.ipynb（Gitでは管理しない）
- 前処理スクリプト：src/make_raw_weather_table.py，src/clean_weather_table.py
- 前処理内容：JSONから天気予報の表を作成し，型変換と文字列整理を行う
- 中間データ：data/raw/jma_tokyo_weather_raw_table.csv
- 前処理後データ：data/processed/jma_tokyo_weather_clean.csv
```

6. `.gitignore`ファイルに次を追記すること．

```gitignore
# Jupyter Notebook
.ipynb_checkpoints
*.ipynb
```

7. `jma_tokyo_forecast.json` がない場合は，以下のZIPファイルをダウンロードして展開し，`jma_tokyo_forecast.json` を `data/raw/` 以下に配置すること．

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
- データ観察はノートブックに残し，再現する本処理はPythonファイルに残す

### NotebookとPythonファイルの使い分け

Jupyter Notebook（`.ipynb`）は，セルごとに実行しながらデータの中身を観察できるため，前処理の初期段階に向いている．
一方で，`.ipynb` はデータ構造としてはJSON形式のファイルであり，実行結果・実行順序・表示状態・メタデータなども一緒に保存されるため，Gitで管理すると差分が読みにくくなり，conflictしたときの修正も難しくなることがある．

従って `.ipynb` 関連のファイルはgitで管理しないこととし，次のように使い分ける．

- `notebooks/preprocessing1.ipynb`：データの構造，行数，列名，値の例，欠損値，型変換などを逐次確認するために使う
- `src/*.py`：確認済みの処理を再実行できる形で保存するために使う
- `README.md`：どのデータを使い，どのような前処理を行ったかを文章で記録する

<!--
`notebooks/preprocessing1.ipynb` は作業用ファイルとして使うため，Gitでは管理しない．
本講義用の `.gitignore` では，`*.ipynb` を無視する設定にしている．
授業中の観察結果はNotebookに残してよいが，提出や再実行に必要な処理は，最終的に `.py` ファイルとして保存すること．
Notebookを `notebooks/` にまとめておくと，作業用ファイルと本解析用の `src/` を区別しやすくなる．
 -->

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
`notebooks/preprocessing1.ipynb` に「JSONの構造確認」という見出しを作り，次のセルを順番に実行して `jma_tokyo_forecast.json` の構造を確認せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

**セル2：JSONを読み込む**（`<HOGE>`に適切なディレクトリを指定すること）

```python
import json

# `!pwd`の結果を元に`jma_tokyo_forecast.json`のパスを指定する
input_path = "<HOGE>/jma_tokyo_forecast.json"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)
```

**セル3：一番外側の構造を確認する**

```python
print("一番外側の型:", type(data))
print("一番外側の要素数:", len(data))
```

**セル4：短期予報の基本情報を確認する**

```python
forecast = data[0]
print("短期予報のキー:", forecast.keys())
print("発表機関:", forecast["publishingOffice"])
print("発表時刻:", forecast["reportDatetime"])
```

**セル5：`timeSeries` の中身を確認する**

```python
for i, series in enumerate(forecast["timeSeries"]):
    print("timeSeries番号:", i)
    print("  時刻数:", len(series["timeDefines"]))
    print("  地域:", [area["area"]["name"] for area in series["areas"]])
    print("  最初の地域のキー:", series["areas"][0].keys())
```

`forecast["timeSeries"]` 以下の構造は，おおよそ次のようになっている．

```text
forecast["timeSeries"]
├── timeSeries[0]：天気，風，波
│   ├── timeDefines：予報時刻のリスト
│   └── areas：地域ごとの予報
│       ├── area
│       │   ├── name：地域名
│       │   └── code：地域コード
│       ├── weatherCodes：天気コードのリスト
│       ├── weathers：天気のリスト
│       ├── winds：風のリスト
│       └── waves：波のリスト
├── timeSeries[1]：降水確率
│   ├── timeDefines：予報時刻のリスト
│   └── areas：地域ごとの降水確率
│       ├── area
│       │   ├── name：地域名
│       │   └── code：地域コード
│       └── pops：降水確率のリスト
└── timeSeries[2]：気温
    ├── timeDefines：予報時刻のリスト
    └── areas：地点ごとの気温
        ├── area
        │   ├── name：地点名
        │   └── code：地点コード
        └── temps：気温のリスト
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

````{tip} 注意：変換したCSVの保存先
ここではJSONから必要な値を取り出したCSVファイルを作成する．
このCSVファイルはJSONのデータの数値は変更していない**未整形データ**であり，まだ文字列の整理や型変換をしていないため，`data/raw` に保存すること

```text
data/raw/jma_tokyo_forecast.json
  ↓
  ↓ notebooks/preprocessing1.ipynbで構造を確認
  ↓ src/make_raw_weather_table.py
  ↓
data/raw/jma_tokyo_weather_raw_table.csv
```
````

````{note} 演習2：JSONから表の行を確認する
`notebooks/preprocessing1.ipynb` に「JSONを未整形CSVへ変換する」という見出しを作り，次のセルを順番に実行せよ．
Notebookでは，JSONのどの階層から値を取り出すかを確認する．
ここではCSVファイルは作成せず，表にしたときの1行がどのような辞書になるかを確認する．

**セル1：必要なライブラリとパスを準備する**（`<HOGE>`には演習1を参考に適切なディレクトリを指定すること）

```python
import csv
import json

input_path = "<HOGE>/jma_tokyo_forecast.json"
output_path = "<HOGE>/jma_tokyo_weather_raw_table.csv"
```

**セル2：JSONを読み込む**

```python
with open(input_path, encoding="utf-8") as f:
    data = json.load(f)
```

**セル3：取り出す階層を確認する**

```python
forecast = data[0]
office = forecast["publishingOffice"]
report_datetime = forecast["reportDatetime"]

weather_series = forecast["timeSeries"][0]
time_defines = weather_series["timeDefines"]

print("発表機関:", office)
print("発表時刻:", report_datetime)
print("予報時刻:", time_defines)
print("地域数:", len(weather_series["areas"]))
print("地域名:", [area["area"]["name"] for area in weather_series["areas"]])
```

**セル4：表の行を作成する**

```python
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

print("作成した行数:", len(rows_out))
rows_out[:3] #始め3行のみ表示
```
````

````{warning} 課題1：JSONから未整形CSVを作成する
演習2で確認した内容をもとに，`src/make_raw_weather_table.py` を作成せよ．
次のコードの `<FUGAFUGA>` を適切に書き換え（複数行必要），`data/raw/jma_tokyo_weather_raw_table.csv` を作成すること．

Notebookで確認した `forecast`，`weather_series`，`time_defines`，`area`，`time`，`i` の中身を見ながら埋めること．

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

<FUGAFUGA>

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード", "予報時刻",
    "天気コード", "天気", "風", "波"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames) #辞書を CSV に変換するものとする
    writer.writeheader() #ヘッダを書き込む
    writer.writerows(rows_out) #rows_out内の辞書をヘッダを参照しながら書き込む

print("saved:", output_path)
print("rows:", len(rows_out))
```

作成したPythonファイルをターミナルで実行せよ．

```bash
python src/make_raw_weather_table.py
```

実行後，`data/raw/jma_tokyo_weather_raw_table.csv` が作成されていることを確認せよ．

次のファイルをWebClass「第6回課題」問1・問2から提出せよ．

1. `src/make_raw_weather_table.py`
2. `data/raw/jma_tokyo_weather_raw_table.csv`
````

以降の演習では，課題1で作成した `data/raw/jma_tokyo_weather_raw_table.csv` を使う．

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
`notebooks/preprocessing1.ipynb` に「CSVの概要を確認する」という見出しを作り，次のセルを順番に実行して未整形CSVの概要を確認せよ．

**セル1：CSVを読み込む**（`<HOGE>`には演習1を参考に適切なディレクトリを指定すること）

```python
import csv

input_path = "<HOGE>/jma_tokyo_weather_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames
```

**セル2：行数と列名を確認する**

```python
print("行数:", len(rows))
print("列名:", fieldnames)
```

**セル3：先頭3行を確認する**

```python
print("先頭3行:")
for row in rows[:3]:
    print(row)
```

実行後，次を確認せよ．

1. 行数はいくつか
2. 列名は何か
3. `天気コード` は文字列として表示されているか
4. `天気`，`風`，`波` の中に全角空白（Unicodeで`\u3000`）が含まれているか
````

---

## 欠損値を確認する

欠損値とは，本来あるべき値が存在しない状態である．
CSVでは，空欄，`NA`，`null`，`-` などで表されることがある．

今回作成した天気表では，欠損が見つからない可能性もある．
欠損がないことを確認するのも，前処理では重要な作業である．

````{note} 演習4：欠損値を確認する
`notebooks/preprocessing1.ipynb` に「欠損値を確認する」という見出しを作り，次のセルを順番に実行して欠損値を確認せよ．

**セル1：欠損値として扱う文字列を決める**（`<HOGE>`には演習1を参考に適切なディレクトリを指定すること）

```python
import csv

input_path = "<HOGE>/jma_tokyo_weather_raw_table.csv"
missing_values = {"", "NA", "N/A", "null", "-"}
```

**セル2：CSVを読み込む**

```python
with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
```

**セル3：欠損値を探す**

```python
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
<!--
````{dropdown} 解答例
2. 欠損値がない場合は，READMEに次のように記録するとよい．

```markdown
### 欠損値の確認

- 確認対象：data/raw/jma_tokyo_weather_raw_table.csv
- 欠損値として扱った値：空文字，NA，N/A，null，-
- 確認結果：欠損値は0個であった
- 対応：削除や補完は行わない
```

3. 欠損値がある場合，削除と保持のどちらが適切かは分析目的によって変わる．
重要な列が欠損していて，欠損した行を除いても分析に大きな影響がない場合は削除を検討する．
一方で，欠損そのものに意味がある場合や，他の列の情報を残したい場合は保持を検討する．
判断した理由をREADMEに記録することが重要である．
````
 -->
```{tip} 注意
第7回で扱う週間予報には，降水確率や信頼度の一部が空欄として入っている．
第6回では，まず欠損確認の方法を身につける．
```

---

## 型変換と範囲確認

CSVの値は基本的に文字列として読み込まれる．
`天気コード` は数字のように見えるが，CSVから読むと文字列である．

```python
type(row["天気コード"])
```

従って次のような型変換により数値として扱うこととする．

```python
weather_code_text = row["天気コード"]
weather_code = int(weather_code_text)
```

ただし，数値として扱う前に次を確認する．

- 空欄ではないか
- 整数に変換できるか
- 値の範囲が不自然ではないか

````{note} 演習5：型変換と範囲確認
`notebooks/preprocessing1.ipynb` に「型変換と範囲確認」という見出しを作り，次のセルを順番に実行して `天気コード` を整数として確認せよ．

**セル1：CSVを読み込む**（`<HOGE>`には演習1を参考に適切なディレクトリを指定すること）

```python
import csv

input_path = "<HOGE>/jma_tokyo_weather_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
```

**セル2：文字列から整数への変換を1件だけ確認する**

```python
code_text = rows[0]["天気コード"]
code = int(code_text)

print("変換前:", code_text, type(code_text))
print("変換後:", code, type(code))
```

**セル3：すべての行で範囲を確認する**

次を実行して「確認が完了しました」のみが表示されれば，範囲外の天気コードが存在しないことが確認できる．

```python
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

JSONファイルやNotebookの表示では，同じ値が次のように見えることがある．

```text
くもり\u3000時々\u3000晴れ\u3000夜遅く\u3000雨
```

`\u3000` は，全角空白を表すUnicodeの表記である．
JSONでは，日本語や記号を `\u` から始まる文字コードとして表示する場合がある．
したがって，`\u3000` は文字列の一部として見えるが，意味としては「全角の空白」である．

このままでも人間は読めるが，プログラムで分類や集計を行うときには，空白の違いが問題になることがある．
例えば見た目が同じデータでも違うデータとして扱われてしまう可能性がある．
そこで，<span style="color:red">文字列の前後の空白を削除し，全角空白を半角空白に置き換える</span>．

```python
text = text.strip().replace("　", " ")
```

````{note} 演習6：文字列整理の動作を確認する
`notebooks/preprocessing1.ipynb` に「文字列整理の動作を確認する」という見出しを作り，次のセルを実行して全角空白と半角空白の違いを確認せよ．

**セル1**

```python
text1 = "晴れ　時々　くもり"
text2 = "晴れ 時々 くもり"

print(text1 == text2)
print(text1.replace("　", " ") == text2)
```

**セル2：`\u3000` と全角空白が同じ文字を表していることを確認する**

```python
text3 = "くもり\u3000時々\u3000晴れ\u3000夜遅く\u3000雨"

print(text3)
print(repr(text3))
print(text3.replace("\u3000", " "))
```

実行後，次を確認せよ．

1. セル1の `print` は何を表示するか
2. セル2の `print` は何を表示するか
3. `print(text3)` と `repr(text3)` の表示はどのように違うか
4. 全角空白を放置すると，集計時にどのような問題が起こるか
````
<!--
````{dropdown} 解答例
1. セル1の1つ目の `print` は `False` を表示する．
見た目は似ているが，`text1` には全角空白，`text2` には半角空白が入っているため，同じ文字列として扱われない．
2つ目の `print` は `True` を表示する．
`text1.replace("　", " ")` によって，全角空白が半角空白に置き換えられるためである．

2. セル2では，おおよそ次のように表示される．

```text
くもり　時々　晴れ　夜遅く　雨
'くもり\\u3000時々\\u3000晴れ\\u3000夜遅く\\u3000雨'
くもり 時々 晴れ 夜遅く 雨
```

3. `print(text3)` は，人間が読む文字列として表示するため，`\u3000` は全角空白として見える．
一方，`repr(text3)` はPythonが内部表現を確認しやすい形で表示するため，全角空白が `\u3000` として見えることがある．

4. 全角空白を放置すると，見た目が同じような天気でも別の文字列として扱われることがある．
たとえば，`"晴れ　時々　くもり"` と `"晴れ 時々 くもり"` は別の値として集計されるため，分類や件数の集計結果が分かれてしまう．
そのため，前処理では全角空白を半角空白にそろえる．
````
 -->
---

## 前処理済みデータを作成する

ここでは，次の方針で前処理を行う．

- 日本語文字列の前後の空白を削除する
- 全角空白を半角空白に変換する
- `天気コード` を整数に変換する
- `予報時刻` から `予報日` と `予報時` を作成する
- 前処理後のCSVは `data/processed` に保存する

````{note} 演習7：前処理後の行をNotebookで確認する
`notebooks/preprocessing1.ipynb` に「前処理済みデータを確認する」という見出しを作り，次のセルを順番に実行して，前処理の内容を確認せよ．
ここでは前処理後の行をNotebook上で観察する．
確認できた処理は，次の課題でPythonファイルにまとめる．

**セル1：必要なライブラリ，パス，文字列整理関数を準備する**（`<HOGE>`には<span style="color:red">扱うデータの性質を考慮して</span>適切なディレクトリを指定すること）

```python
import csv

input_path = "<HOGE>/jma_tokyo_weather_raw_table.csv"
output_path = "<HOGE>/jma_tokyo_weather_clean.csv"

def clean_text(value):
    return value.strip().replace("　", " ")
```

**セル2：未整形CSVを読み込み，前処理後の行を作成する**

```python
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
```

**セル3：前処理後の行を確認する**

```python
print("出力予定行数:", len(rows_out))
rows_out[:3]
```

**セル4：出力する列名を確認する**

```python
fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード",
    "予報時刻", "予報日", "予報時",
    "天気コード", "天気", "風", "波"
]

fieldnames
```
````

````{warning} 課題2：前処理済みデータをPythonファイルで作成する
演習7で確認した内容をもとに，`src/clean_weather_table.py` を作成せよ．
次のコードの `<HOGEHOGE>` と `<FUGAFUGA>` を適切に置き換え，`data/processed/jma_tokyo_weather_clean.csv` を作成すること．

特に，`予報日` と `予報時` は，Notebookで確認した `予報時刻` の文字列から取り出す．

```python
import csv

input_path = "data/raw/jma_tokyo_weather_raw_table.csv"
output_path = "data/processed/jma_tokyo_weather_clean.csv"

def clean_text(value):
    return <HOGEHOGE>

rows_out = []

<FUGAFUGA>

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
print("出力行数:", len(rows_out))
```

作成したPythonファイルをターミナルで実行せよ．

```bash
python src/clean_weather_table.py
```

次のファイルをWebClass「第6回課題」問3・問4から提出せよ．

1. `src/clean_weather_table.py`
2. `data/processed/jma_tokyo_weather_clean.csv`
````

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

- 前処理スクリプト（`src/*.py`）
- README
- メタデータ
- 小規模なサンプルデータ
- 前処理方針の記録

一方，作業用Notebook，サイズの大きいデータ，ライセンス上再配布できないデータは，Gitで管理しない方がよい場合がある．
本講義では `.gitignore` に `*.ipynb` を記載し，Notebookはローカルでの観察用として扱う．

今回の処理の流れは，次のように表せる．

```text
data/raw/jma_tokyo_forecast.json
  ↓
  ↓ notebooks/preprocessing1.ipynbで構造を確認
  ↓ src/make_raw_weather_table.py
  ↓
data/raw/jma_tokyo_weather_raw_table.csv
  ↓
  ↓ notebooks/preprocessing1.ipynbで概要・欠損・型・文字列を確認
  ↓ src/clean_weather_table.py
  ↓
data/processed/jma_tokyo_weather_clean.csv
```

---

## まとめ

- 前処理：取得したデータを**分析しやすい形に整える**作業
- JSONは階層構造をもつため，**必要な値を取り出してCSV化する**ことがある
- 前処理の前には，行数，列名，値の例，欠損値，数値として扱う列，日本語文字列を確認する
- CSVの値は基本的に文字列として読み込まれるため，数値計算には**型変換**が必要である
- 日本語文字列では，**全角空白や余分な空白を整理**することがある
- 生データは `data/raw` に残し，前処理後のデータは `data/processed` に保存する
- データ観察はNotebookで行い，再実行する本処理はPythonファイルとして保存する

次回：データの前処理II

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

````{dropdown} 解答例
次のように，`timeSeries[2]` から気温データを取り出すことができる．

```python
import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/raw/jma_tokyo_temperature_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
office = forecast["publishingOffice"]
report_datetime = forecast["reportDatetime"]

temperature_series = forecast["timeSeries"][2]
time_defines = temperature_series["timeDefines"]

rows_out = []

for area in temperature_series["areas"]:
    point_name = area["area"]["name"]
    point_code = area["area"]["code"]

    for i, time in enumerate(time_defines):
        rows_out.append({
            "発表機関": office,
            "発表時刻": report_datetime,
            "地点名": point_name,
            "地点コード": point_code,
            "予報時刻": time,
            "気温": area["temps"][i]
        })

fieldnames = ["発表機関", "発表時刻", "地点名", "地点コード", "予報時刻", "気温"]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))
```

1. 地点名には，たとえば `東京`，`大島`，`八丈島`，`父島` のような値が入っている．
2. 天気データの `地域名` は `東京地方`，`伊豆諸島北部`，`伊豆諸島南部`，`小笠原諸島` のような地域名であり，気温データの `地点名` とは一致しない．
3. 結合するには，たとえば `東京地方` と `東京`，`伊豆諸島北部` と `大島`，`伊豆諸島南部` と `八丈島`，`小笠原諸島` と `父島` のように，地域名と地点名を対応させる表が必要である．
````

````{note} 発展課題2：文字列整理の効果を確認する

`jma_tokyo_weather_raw_table.csv` と `jma_tokyo_weather_clean.csv` を比較し，`天気`，`風`，`波` の空白がどのように変わったか確認せよ．

次の問いに答えよ．

1. 全角空白は半角空白に変わっているか
2. 文字列整理後の方が読みやすいか
3. 集計や分類を行うとき，文字列整理はなぜ必要か
````

````{dropdown} 解答例
次のように，未整形データと前処理済みデータを並べて確認できる．

```python
import csv

raw_path = "data/raw/jma_tokyo_weather_raw_table.csv"
clean_path = "data/processed/jma_tokyo_weather_clean.csv"

with open(raw_path, encoding="utf-8") as f:
    raw_rows = list(csv.DictReader(f))

with open(clean_path, encoding="utf-8") as f:
    clean_rows = list(csv.DictReader(f))

for raw_row, clean_row in zip(raw_rows, clean_rows):
    print("地域名:", raw_row["地域名"])
    print("予報時刻:", raw_row["予報時刻"])
    print("天気 raw  :", repr(raw_row["天気"]))
    print("天気 clean:", repr(clean_row["天気"]))
    print("風 raw    :", repr(raw_row["風"]))
    print("風 clean  :", repr(clean_row["風"]))
    print("波 raw    :", repr(raw_row["波"]))
    print("波 clean  :", repr(clean_row["波"]))
    print("---")
```

1. 前処理済みデータでは，全角空白が半角空白に変わっている．たとえば `くもり　時々　晴れ` は `くもり 時々 晴れ` のようになる．
2. 文字列整理後の方が，空白の幅がそろうため読みやすい．また，プログラムで扱うときにも表記の違いを減らせる．
3. 集計や分類では，文字が1つでも違うと別の値として扱われる．そのため，全角空白と半角空白が混ざっていると，本来同じ種類として数えたい値が別々に集計される可能性がある．
````

<!--
## 参考：Pythonファイルの完成例

以下は，本解析を `.py` ファイルとして実行するための完成例である．
授業中は `notebooks/preprocessing1.ipynb` でセルごとに途中結果を確認し，確認できた処理をPythonファイルにまとめる．

### src/inspect_jma_structure.py

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

### src/make_raw_weather_table.py

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

### src/inspect_weather_table.py

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

### src/check_missing_weather.py

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

### src/check_weather_code.py

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

### src/clean_weather_table.py

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
print("出力行数:", len(rows_out))
```
-->
