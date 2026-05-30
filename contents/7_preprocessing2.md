# 第7回　データの前処理II

### 前回の復習

- 前処理：取得したデータを**分析しやすい形に整える**作業
- JSONから必要な値を取り出してCSV化した
- データを使用するために必要な手続き
  - 文字列として読み込まれるCSVの値を利用するために**型変換**した
  - 日本語文字列にある全角空白や余分な空白を**半角空白**に統一した
- 生データは `data/raw` に残し，前処理後のデータは `data/processed` に保存した
- データ観察はNotebookで行い，再実行する本処理はPythonファイルとして保存した

第6回では，第5回で取得した気象庁の天気予報JSONから，`timeSeries[0]` の天気，風，波を取り出して表形式CSVを作成した．

第7回では，同じJSONの中に入っている複数の表を扱い，結合・日付処理・カテゴリ作成を行い，分析用データセットを作成する．

```{tip} 注意
第7回では新しいAPI取得は行わず，第5回で取得した `data/raw/jma_tokyo_forecast.json` を使う．
```

### 到達目標

複数の表を組み合わせて分析用データセットを作成する．

- 1つのJSONの中に含まれる複数の表を区別する
- 天気表，降水確率表，気温表をそれぞれ作成する
- 共通するキーを使って表を結合する
- 結合できないデータを無理に結合しない理由を理解する
- 結合後に発生する空欄の理由を理解する
- ISO形式の日時文字列から日付や時刻を取り出す
- 日本語カテゴリを整理し，分析用のカテゴリを作成する

### 準備

<span style="color:red">第5回で作成したフォルダ `5` 内で作業を続ける．</span>

- 第5回で取得した次のファイルを使う．
    ```text
    5/data/raw/jma_tokyo_forecast.json
    ```
    これがない場合は次のリンクからダウンロードして配置すること．

    [jma_tokyo_forecast_json.zip](./analysis/5/data/raw/jma_tokyo_forecast_json.zip)

- 第6回で作成した次のファイルも使う．
    ```text
    5/data/raw/jma_tokyo_weather_raw_table.csv
    ```
    これがない場合は次のリンクからダウンロードして配置すること．

    [jma_tokyo_weather_raw_table_csv.zip](./analysis/5/data/raw/jma_tokyo_weather_raw_table_csv.zip)

````{note} 演習0：作業フォルダとデータを確認する

1. 第5回で作成した `/User/<ユーザ名>/applied_programming_i/5` を開く．
2. 次のディレクトリ構成になっているか確認する．

```text
5/
├── notebooks/
│   ├── preprocessing1.ipynb
│   └── preprocessing2.ipynb（←今回作成するファイル）
├── data/
│   ├── raw/
│   │   ├── jma_tokyo_forecast.json
│   │   └── jma_tokyo_weather_raw_table.csv
│   └── processed/
├── src/
└── README.md
```

3. `notebooks/preprocessing2.ipynb` を新規作成する．
4. `README.md` に次の内容を追記する．

```markdown
## 第7回 前処理記録

- 元データ：data/raw/jma_tokyo_forecast.json
- 第6回で作成したデータ：data/raw/jma_tokyo_weather_raw_table.csv
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 観察用ノートブック：notebooks/preprocessing2.ipynb（Gitでは管理しない）
- 前処理スクリプト：
  - src/make_raw_pop_table.py
  - src/join_weather_pop.py
  - src/build_analysis_table.py
- 前処理内容：
  - 降水確率表を作成する
  - 天気表と降水確率表を結合する
  - 日付列と天気カテゴリを作成する
- 前処理後データ：data/processed/jma_tokyo_weather_pop_clean.csv
- 注意：気温データは地点名で提供されるため，天気表とは別表として扱う
```

5. `.gitignore`に次のように記載されていることを確認する．

```gitignore
.DS_Store
*.swp
*.swo
*~
.vscode/
data/raw

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb
```
````

---

## 実施する処理

- 第6回：1つの時系列から1つの表を作った．
- 第7回：1つのJSONの中に入っている複数の表を組み合わせ，分析目的に合う形へ変換する．

次の処理を扱う．

- 複数の時系列を別々の表として取り出す
- 共通キーを使って表を横方向に結合する
- 結合後に発生する空欄を確認する
- 日時文字列から日付と時刻を取り出す
- 日本語の天気表現を大まかなカテゴリへ変換する

### NotebookとPythonファイルの使い分け

第6回と同様に，今回も次のように使い分ける．

- `notebooks/preprocessing2.ipynb`：JSONの構造，結合キー，空欄，カテゴリ化の結果などを逐次確認するために使う
- `src/*.py`：確認済みの処理を再実行できる形で保存するために使う
- `README.md`：どのデータを使い，どのような前処理を行ったかを文章で記録する

<!--
授業中はNotebookで途中結果を確認し，提出や再実行に必要な処理はPythonファイルとして保存する．
Notebookは作業用ファイルであり，Gitでは管理しない．
-->

### 縦方向の結合と横方向の結合

複数の表を扱うときには，結合の方向を意識する．

```text
縦方向の結合：同じ列をもつ複数の表を，下に追加する
横方向の結合：共通のキーをもつ表から，別の列を追加する
```

ここでは主に横方向の結合を扱う．

```text
天気表 ← 降水確率表 = 天気と降水確率を含む表
```

結合にはキーが必要である．

**キー**：2つの表で同じ対象を表していることを示す列

ここの天気表と降水確率表では，次の2つをキーとして使う．

- `地域コード`
- `予報時刻`

---

## 使用するデータ

第5回で取得した気象庁の天気予報JSON（東京都）を使う．

- 気象庁ホームページ：https://www.jma.go.jp/
- 天気予報JSON（東京都）：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 地域コード一覧：https://www.jma.go.jp/bosai/common/const/area.json
- 利用規約：https://www.jma.go.jp/jma/kishou/info/coment.html

```{tip} 注意（再掲）
気象庁ホームページで公開されている情報は，権利表記の記載がない限り「公共データ利用規約（第1.0版）」に準拠した利用条件の下で利用できる．
利用する際は出典を記録すること．
```

```{tip} 注意（再掲）
気象庁の天気予報JSONは，気象庁サイトで公開されている日本語データである．
ただし，長期的な仕様固定が保証された正式なAPIドキュメント付きサービスとして利用するものではないため，URLやJSON構造が変更される可能性に注意する．
```

### JSONの中の複数の表

`jma_tokyo_forecast.json` には，複数の時系列が含まれている．
短期予報 `data[0]` の中には，次の3つの表に相当するデータが含まれる．

| 位置 | 主な内容 | 地域の単位 |
| --- | --- | --- |
| `data[0]["timeSeries"][0]` | 天気，風，波 | 東京地方，伊豆諸島北部，伊豆諸島南部，小笠原諸島 |
| `data[0]["timeSeries"][1]` | 降水確率 | 東京地方，伊豆諸島北部，伊豆諸島南部，小笠原諸島 |
| `data[0]["timeSeries"][2]` | 気温 | 東京，大島，八丈島，父島 |

天気表と降水確率表は，地域コードが同じなので結合しやすい．  
一方，気温表は地域の単位が異なるため，そのまま結合すると誤ったデータセットになる可能性がある．

```{tip} 注意
気温データの地域名は「東京地方」ではなく「東京」「大島」「八丈島」「父島」のような地点名で入っている．
天気データの地域名とは完全には一致しないため，今回は気温データを天気表へ無理に結合しないこととする．
```

---

## JSONの中の表を確認する

まず，`timeSeries` ごとに地域名，地域コード，時刻がどのように入っているかを確認する．
表を結合するときは，列名だけでなく，**値の意味が一致しているか**を確認することが重要である．

````{note} 演習1：時系列ごとの地域名を確認する
`notebooks/preprocessing2.ipynb` に「時系列ごとの地域名を確認する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：作業中のディレクトリを確認する**

```bash
!pwd
```

**セル2：JSONを読み込む**（`<HOGE>`には適切なディレクトリを指定すること）

```python
import json

input_path = "<HOGE>/jma_tokyo_forecast.json"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)
```

**セル3：時系列ごとの地域名と地域コードを確認する**

```python
forecast = data[0]

for i, series in enumerate(forecast["timeSeries"]):
    area_names = [area["area"]["name"] for area in series["areas"]]
    area_codes = [area["area"]["code"] for area in series["areas"]]

    print("timeSeries番号:", i)
    print("時刻数:", len(series["timeDefines"]))
    print("時刻:", series["timeDefines"])
    print("地域名:", area_names)
    print("地域コード:", area_codes)
    print()
```

実行後，次を確認せよ．

1. `timeSeries[0]` と `timeSeries[1]` の地域名は同じか
2. `timeSeries[0]` と `timeSeries[1]` の地域コードは同じか
3. `timeSeries[2]` の地域名は何か
4. 気温表を天気表にそのまま結合してよいか
````

---

## 降水確率を結合した表にする

### 降水確率表を作成する

第6回では，`timeSeries[0]` から天気表を作成した．
今回は，`timeSeries[1]` から降水確率表を作成する．
降水確率は `pops` に入っている．

作成するCSVは，次の列を持つ．

- `地域名`
- `地域コード`
- `予報時刻`
- `降水確率`

````{tip} 注意：変換したCSVの保存先
ここではJSONから必要な値を取り出したCSVファイルを作成する．
このCSVファイルは，まだ型変換をしていない**未整形データ**であるため，`data/raw` に保存すること．

```text
data/raw/jma_tokyo_forecast.json
  ↓
  ↓ notebooks/preprocessing2.ipynbで構造を確認
  ↓ src/make_raw_pop_table.py
  ↓
data/raw/jma_tokyo_pop_raw_table.csv
```
````

````{note} 演習2：降水確率表の行をNotebookで確認する
`notebooks/preprocessing2.ipynb` に「降水確率表を確認する」という見出しを作り，次のセルを順番に実行せよ．
ここではCSVファイルは作成せず，表にしたときの行をNotebook上で確認する．

**セル1：必要なライブラリとパスを準備する**（`<HOGE>`には演習1を参考に適切なディレクトリを指定すること）

```python
import csv
import json

input_path = "<HOGE>/jma_tokyo_forecast.json"
output_path = "<HOGE>/jma_tokyo_pop_raw_table.csv"
```

**セル2：JSONを読み込む**

```python
with open(input_path, encoding="utf-8") as f:
    data = json.load(f)
```

**セル3：降水確率が入っている階層を確認する**

```python
forecast = data[0]
pop_series = forecast["timeSeries"][1]

print("予報時刻:",          pop_series["timeDefines"])
print("地域数:",        len(pop_series["areas"]))
print("最初の地域のキー:",    pop_series["areas"][0].keys())
print("最初の地域の地域名:",  pop_series["areas"][0]["area"])
print("最初の地域の降水確率:",pop_series["areas"][0]["pops"])
print("地域名一覧:", [area["area"]["name"] for area in pop_series["areas"]])
```

**セル4：表の行を作成する**

```python
rows_out = []

for area in pop_series["areas"]:
    area_name = area["area"]["name"]
    area_code = area["area"]["code"]

    for i, time in enumerate(pop_series["timeDefines"]):
        rows_out.append({
            "地域名": area_name,
            "地域コード": area_code,
            "予報時刻": time,
            "降水確率": area["pops"][i]
        })

print("作成した行数:", len(rows_out))
rows_out[:6]
```

実行後，次を確認せよ．

1. 降水確率表の行数はいくつか
2. `降水確率` は文字列として表示されているか
3. 第6回で作成した天気表と同じ `地域コード` が含まれているか
````

````{warning} 課題1：降水確率の未整形CSVを作成する
1. 演習2で確認した内容をもとに，`src/make_raw_pop_table.py` を作成し，
<span style="color:red">
WebClass「第7回課題」問1から提出せよ．
</span>

次のコードの `<FUGAFUGA>` を適切に書き換え（複数行必要），`data/raw/jma_tokyo_pop_raw_table.csv` を作成し，Notebookで確認した `pop_series`，`area`，`time`，`i` の中身を見ながら埋めること．

```python
import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/raw/jma_tokyo_pop_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
pop_series = forecast["timeSeries"][1]

rows_out = []

<FUGAFUGA>

fieldnames = ["地域名", "地域コード", "予報時刻", "降水確率"]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))
```

作成したPythonファイルを `5` フォルダ内でターミナルから実行せよ．

```bash
python src/make_raw_pop_table.py
```

実行後，`data/raw/jma_tokyo_pop_raw_table.csv` が作成されていることを確認せよ．
````

### 表を結合する

第6回で作成した**天気表**と課題1で作成した**降水確率表**を結合する．
ここでは次の結合ルールにしたがって表を結合する．
- 天気表を基準にして，同じ `地域コード`，`予報時刻` に対応する降水確率がある場合だけ `降水確率` を追加する．
- 対応する値がない場合は空欄にする．

このような結合は，左側の表の行を残すため**左結合**と呼ばれる．

```{tip} 注意
結合したファイルはデータの値は変更していないため生データとして扱う．
```
```{tip} 注意
天気表と降水確率表は地域コードは同じでも時刻の刻みが異なるため，完全には一致しない時刻があり，その行には空欄が発生する．
```

````{note} 演習3：結合キーをNotebookで確認する
`notebooks/preprocessing2.ipynb` に「天気表と降水確率表を結合する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：CSVを読み込む**（`<HOGE>`には演習1を参考に適切なディレクトリを指定すること）

```python
import csv

weather_path = "<HOGE>/jma_tokyo_weather_raw_table.csv"
pop_path = "<HOGE>/jma_tokyo_pop_raw_table.csv"

with open(weather_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    weather_rows = list(reader)

with open(pop_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    pop_rows = list(reader)

print("天気表の行数:", len(weather_rows))
print("降水確率表の行数:", len(pop_rows))
```

**セル2：地域と予報時刻の違いを確認する**

```python
weather_area_codes = sorted({row["地域コード"] for row in weather_rows})
pop_area_codes     = sorted({row["地域コード"] for row in pop_rows})

weather_times = sorted({row["予報時刻"] for row in weather_rows})
pop_times     = sorted({row["予報時刻"] for row in pop_rows})

print("天気表の地域コード:",     weather_area_codes)
print("降水確率表の地域コード:",  pop_area_codes)
print("地域コードは同じか:",     weather_area_codes == pop_area_codes)
print()

print("天気表の予報時刻:")
for time in weather_times:
    print(" ", time)

print("降水確率表の予報時刻:")
for time in pop_times:
    print(" ", time)

print()
print("両方にある予報時刻:",         sorted(set(weather_times) & set(pop_times)))
print("天気表にだけある予報時刻:",    sorted(set(weather_times) - set(pop_times)))
print("降水確率表にだけある予報時刻:", sorted(set(pop_times) - set(weather_times)))
```

実行すると，地域コードは同じでも，予報時刻の一覧は完全には一致しないことが確認できる．
このため，`地域コード` と `予報時刻` をキーにして結合すると，対応する降水確率がない天気表の行が発生する．

**セル3：降水確率表を検索しやすい形にする**

```python
pop_by_key = {}

for row in pop_rows:
    key = (row["地域コード"], row["予報時刻"])
    pop_by_key[key] = row["降水確率"]

list(pop_by_key.items())[:5]
```

**セル4：天気表へ降水確率を追加する**

```python
rows_out = []

for row in weather_rows:
    key = (row["地域コード"], row["予報時刻"])
    row["降水確率"] = pop_by_key.get(key, "")
    rows_out.append(row)

print("結合後の行数:", len(rows_out))
rows_out[:5]
```

**セル5：降水確率が入った行数を確認する**

```python
has_pop = 0

for row in rows_out:
    if row["降水確率"] != "":
        has_pop += 1

print("降水確率が入っている行数:", has_pop)
print("降水確率が空欄の行数:", len(rows_out) - has_pop)
```

実行後，次を確認せよ．

1. 結合後の行数は天気表と同じか
2. `降水確率` が入っている行は何行あるか
3. `降水確率` が空欄の行はなぜ発生したか
4. 結合に使ったキーは何か
````

````{warning} 課題2：天気表と降水確率表を結合する
1. 演習3で確認した内容をもとに，`src/join_weather_pop.py` を作成し，
<span style="color:red">
WebClass「第7回課題」問2から提出せよ．
</span>

次のコードの `<HOGEHOGE>` と `<FUGAFUGA>` を適切に置き換え，`data/raw/jma_tokyo_weather_pop_raw_table.csv` を作成すること．

```python
import csv

weather_path = "data/raw/jma_tokyo_weather_raw_table.csv"
pop_path = "data/raw/jma_tokyo_pop_raw_table.csv"
output_path = "data/raw/jma_tokyo_weather_pop_raw_table.csv"

with open(weather_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    weather_rows = list(reader)

with open(pop_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    pop_rows = list(reader)

pop_by_key = {}

<HOGEHOGE>

rows_out = []

<FUGAFUGA>

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

作成したPythonファイルを `5` フォルダ内でターミナルから実行せよ．

```bash
python src/join_weather_pop.py
```

実行後，`data/raw/jma_tokyo_weather_pop_raw_table.csv` が作成されていることを確認せよ．
````

### 結合後の空欄を確認する

結合後には，対応する値がないために空欄が発生することがある．
これは必ずしもデータの誤りではない．
今回の場合，天気と降水確率の予報時刻が完全には一致しないため，空欄が生じる．

````{note} 演習4：結合後の空欄を確認する
`notebooks/preprocessing2.ipynb` に「結合後の空欄を確認する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：結合後のCSVを読み込む**（`<HOGE>`には演習1を参考に適切なディレクトリを指定すること）

```python
import csv

input_path = "<HOGE>/jma_tokyo_weather_pop_raw_table.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
```

**セル2：降水確率が空欄の行を確認する**

```python
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

```{tip} カテゴリ化の写像としての理解
カテゴリ化は写像として全単射でないことに注意する．
全単射でないデータ操作は逆像を構成できない．
つまりデータを直接書き換えてしまうと失われた情報の復元ができないため，元データは `data/raw` に残しつつ，操作したデータは `data/processed` に管理する必要がある．
```

### 予報時刻から日付と時刻を取り出す

今回の `予報時刻` は，次のような文字列として入っている．

```text
2026-05-19T11:00:00+09:00
```

この形式では，先頭の10文字が日付を表し，`T` の後の5文字が時刻を表している．
したがって，文字列の一部を取り出すことで，`予報日` と `予報時` を作成できる．

```text
2026-05-19T11:00:00+09:00
^^^^^^^^^^  ^^:^^
予報日       予報時
```

Pythonでは，文字列の一部を取り出すためにスライスを使う．

```python
forecast_time = "2026-05-19T11:00:00+09:00"

forecast_date = forecast_time[:10]
forecast_hour = forecast_time[11:16]

print(forecast_date)
print(forecast_hour)
```

実行結果は次のようになる．

```text
2026-05-19
11:00
```

ここで，`forecast_time[:10]` は「先頭から10文字目の直前まで」を取り出すという意味である．
また，`forecast_time[11:16]` は「11番目から16番目の直前まで」を取り出すという意味である．

```{tip} 注意
Pythonの文字列の位置は0から数える．
したがって，`2026-05-19T11:00:00+09:00` の `T` は10番目にあり，時刻の `11:00` は11番目から始まる．
```

このように日付と時刻を別の列に分けておくと，日付ごとに集計したり，時刻ごとに比較したりしやすくなる．

````{note} 演習5：分析用データの行をNotebookで確認する
`notebooks/preprocessing2.ipynb` に「分析用データを確認する」という見出しを作り，次のセルを順番に実行せよ．
ここでは前処理後の行をNotebook上で観察する．
確認できた処理は，次の課題でPythonファイルにまとめる．

**セル1：必要なライブラリ，パス，関数を準備する**（`<HOGE>`には<span style="color:red">扱うデータの性質を考慮して</span>適切なディレクトリを指定すること）

```python
import csv

input_path = "<HOGE>/jma_tokyo_weather_pop_raw_table.csv"
output_path = "<HOGE>/jma_tokyo_weather_pop_clean.csv"
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
```

**セル2：前処理後の行を作成する**

```python
rows_out = []

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        forecast_time = clean_text(row["予報時刻"])
        weather = clean_text(row["天気"])

        rows_out.append({
            "発表機関":    clean_text(row["発表機関"]),
            "発表時刻":    clean_text(row["発表時刻"]),
            "地域名":      clean_text(row["地域名"]),
            "地域コード":   clean_text(row["地域コード"]),
            "予報時刻":    forecast_time,
            "予報日":      forecast_time[:10],
            "予報時":      forecast_time[11:16],
            "天気コード":   int(clean_text(row["天気コード"])),
            "天気":        weather,
            "天気カテゴリ": weather_category(weather),
            "風":          clean_text(row["風"]),
            "波":          clean_text(row["波"]),
            "降水確率": to_int_or_blank(row["降水確率"])
        })

print("出力予定行数:", len(rows_out))
rows_out[:5]
```

**セル3：出力する列名を確認する**

```python
fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード",
    "予報時刻", "予報日", "予報時",
    "天気コード", "天気", "天気カテゴリ",
    "風", "波", "降水確率"
]

fieldnames
```
````

````{warning} 課題3：分析用データセットをPythonファイルで作成する
1. 演習5で確認した内容をもとに，`src/build_analysis_table.py` を作成し，
<span style="color:red">
WebClass「第7回課題」問3から提出せよ．
</span>

次のコードの `<HOGEHOGE1>`，`<HOGEHOGE2>`，`<HOGEHOGE3>`，`<FUGAFUGA>` を適切に置き換え，`data/processed/jma_tokyo_weather_pop_clean.csv` を作成すること．

```python
import csv

input_path = "data/raw/jma_tokyo_weather_pop_raw_table.csv"
output_path = "data/processed/jma_tokyo_weather_pop_clean.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

def clean_text(value):
    <HOGEHOGE1>

def to_int_or_blank(value):
    <HOGEHOGE2>

def weather_category(weather):
    <HOGEHOGE3>

rows_out = []

<FUGAFUGA>

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
print("出力行数:", len(rows_out))
```

作成したPythonファイルを `5` フォルダ内でターミナルから実行せよ．

```bash
python src/build_analysis_table.py
```

実行後，`data/processed/jma_tokyo_weather_pop_clean.csv` が作成されていることを確認せよ．
````

---

## 前処理の判断

今回の前処理では，複数の判断を行った．

- 第5回で取得したJSONだけを使用した
- 第6回で作成した天気表を利用した
- 短期予報の `timeSeries[1]` を降水確率表として取り出した
- `地域コード` と `予報時刻` をキーとして天気表と降水確率表を結合した
- 対応する降水確率がない場合は空欄のまま保持した
- 気温表は地域単位が異なるため，別表として扱った
- ISO形式の時刻から日付と時刻を取り出した
- 天気の詳細表現を大まかなカテゴリへ変換した

これらはすべて，分析結果に影響を与える判断である．
したがって，READMEやスクリプトに，どのような方針で処理したかを残す必要がある．

特にカテゴリ化は，情報を整理すると同時に情報を失う処理でもある．
「晴れ　時々　雨」を雨に分類するか，晴に分類するかによって，その後の分析結果は変わる．
分析目的に応じて分類ルールを説明できることが重要である．

---

## Git管理と前処理

第7回では，多くの中間ファイルが作成される．
すべてをGitで管理する必要はないが，少なくとも次のものは残すとよい．

- 前処理スクリプト（`src/*.py`）
- README
- 前処理後データや小さな処理結果
- 小さなマスタデータや対応表を作成した場合はそのファイル

一方，作業用Notebook，取得直後のJSON，サイズの大きいデータ，ライセンス上再配布できないデータは，Gitで管理しない方がよい場合がある．
本講義では `.gitignore` に `*.ipynb` を記載し，Notebookはローカルでの観察用として扱う．

今回の処理の流れは，次のように表せる．

```text
data/raw/jma_tokyo_forecast.json
  ↓
  ↓ notebooks/preprocessing2.ipynbで構造を確認
  ↓ src/make_raw_pop_table.py
  ↓
data/raw/jma_tokyo_pop_raw_table.csv

data/raw/jma_tokyo_weather_raw_table.csv
data/raw/jma_tokyo_pop_raw_table.csv
  ↓
  ↓ notebooks/preprocessing2.ipynbで結合キーを確認
  ↓ src/join_weather_pop.py
  ↓
data/raw/jma_tokyo_weather_pop_raw_table.csv
  ↓
  ↓ notebooks/preprocessing2.ipynbで空欄・日付・カテゴリを確認
  ↓ src/build_analysis_table.py
  ↓
data/processed/jma_tokyo_weather_pop_clean.csv
```

---

## まとめ

- 前処理IIでは，複数表の作成，結合，日付処理，カテゴリ作成を扱った
- 1つのJSONの中にも，複数の表に相当するデータが入っていることがある
- 横方向の結合は，共通のキーを使って別の列を追加する処理である
- 結合できるかどうかは，列名だけでなく，地域や時刻の意味が一致しているかで判断する
- 結合によって発生する空欄は，必ずしもデータの誤りではない
- ISO形式の日時文字列から，日付や時刻を取り出すことで分析しやすくなる
- 日本語の天気表現をカテゴリ化すると扱いやすくなるが，分類ルールを説明する必要がある
- データ観察はNotebookで行い，再実行する本処理はPythonファイルとして保存する

次回は集計用データセット作成と可視化を扱う．

- 週間予報データをもとに，地域別・地点別の集計用データセットを作成する
- 表だけでは把握しにくい傾向を図として表現する方法を学ぶ

### 課題の提出期限

<span style="color: red; ">6月2日(火)23:59まで</span>

---

## おまけ：気温データを別表として扱う

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

````{note} おまけ演習：気温表を別表として確認する
`notebooks/preprocessing2.ipynb` に「気温表を別表として確認する」という見出しを作り，次のセルを順番に実行せよ．

**セル1：気温データの階層を確認する**

```python
temp_series = forecast["timeSeries"][2]

print("予報時刻:", temp_series["timeDefines"])
print("地点名:", [area["area"]["name"] for area in temp_series["areas"]])
print("地点コード:", [area["area"]["code"] for area in temp_series["areas"]])
print("最初の地点の気温:", temp_series["areas"][0]["temps"])
```

**セル2：気温表の行を作成する**

```python
temperature_rows = []

for area in temp_series["areas"]:
    point_name = area["area"]["name"]
    point_code = area["area"]["code"]

    for i, time in enumerate(temp_series["timeDefines"]):
        temperature_rows.append({
            "発表機関": forecast["publishingOffice"],
            "発表時刻": forecast["reportDatetime"],
            "地点名": point_name,
            "地点コード": point_code,
            "予報時刻": time,
            "気温": int(area["temps"][i])
        })

print("気温表の行数:", len(temperature_rows))
temperature_rows[:5]
```

実行後，次を確認せよ．

1. `地点名` にはどのような値が入っているか
2. `地点コード` は天気表の `地域コード` と一致しているか
3. 気温表を天気表へ結合するには，どのような追加情報が必要か
````

---

## 自主学習用の発展問題

課題を全てこなし時間が余った場合に取り組んでください．
WebClassの提出場所から提出したものについて加点対象とします．

````{note} 課題4：天気カテゴリのルールを変える

現在のカテゴリ化では，`雨` を含む天気を最優先で「雨」に分類している．
このルールを変更し，`晴` を含む場合は優先的に「晴」に分類するようにせよ．

`src/build_analysis_table.py` を変更し，
<span style="color:red">
WebClass「第7回課題」問4から提出せよ．
</span>

提出するのは変更したPythonファイルのみである．作成されるCSVファイルは提出しなくてよい．

次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. どの関数を変更すればよいか
2. カテゴリの分布は変わるか
3. どちらの分類ルールが分析目的に合っていると思うか
````

````{note} 課題5：気温との対応表を考える

気温表の地点名と天気表の地域名を対応させる表を作るとしたら，どのような列が必要か考えよ．

`src/make_temperature_area_map.py` を作成し，
<span style="color:red">
WebClass「第7回課題」問5から提出せよ．
</span>

提出するのは作成したPythonファイルのみである．作成されるCSVファイルは提出しなくてよい．

例：

```text
地点名,地点コード,対応する地域名,対応する地域コード,対応理由
```

作成するPythonファイルでは，対応表を `data/processed/temperature_area_map.csv` として出力すること．

次のコードを参考に，対応表の内容を自分で考えて作成すること．

```python
import csv
from pathlib import Path

output_path = "data/processed/temperature_area_map.csv"

rows_out = [
    {
        "地点名": "東京",
        "地点コード": "44132",
        "対応する地域名": "<HOGE>",
        "対応する地域コード": "<HOGE>",
        "対応理由": "<HOGE>"
    },
    {
        "地点名": "大島",
        "地点コード": "44172",
        "対応する地域名": "<HOGE>",
        "対応する地域コード": "<HOGE>",
        "対応理由": "<HOGE>"
    },
    {
        "地点名": "八丈島",
        "地点コード": "44263",
        "対応する地域名": "<HOGE>",
        "対応する地域コード": "<HOGE>",
        "対応理由": "<HOGE>"
    },
    {
        "地点名": "父島",
        "地点コード": "44301",
        "対応する地域名": "<HOGE>",
        "対応する地域コード": "<HOGE>",
        "対応理由": "<HOGE>"
    }
]

fieldnames = ["地点名", "地点コード", "対応する地域名", "対応する地域コード", "対応理由"]

Path(output_path).parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
```

実行後，次の点を確認し，必要に応じてPythonファイル内のコメントに残すこと．

1. 「東京」はどの地域を代表すると考えられるか
2. 「大島」「八丈島」「父島」はどの地域と関係が深いか
3. 対応表を作るとき，主観的な判断をどのように記録すべきか
````
