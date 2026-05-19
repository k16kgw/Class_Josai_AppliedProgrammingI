# 第5回　APIの使い方

### 前回の復習

- オープンデータ：再利用条件が明示されたデータ
- データ取得では，出典，ライセンス，更新頻度，取得時点，形式を確認する必要がある
- データ形式
  - CSV：行と列からなる表形式データ
  - JSON：キーと値の組を基本とする階層構造をもつデータ
- ディレクトリ構造
  - `data/raw`：生データを保存
  - `data/processed`：加工後データを保存
  - `src`：解析のソースコードを保存
- オープンデータを取得したら，まずはじめに行数，列名，先頭行，一部の値を確認して，データの形を把握する
- データ本体だけでなく，README やメタデータを残すことで，後から分析過程を説明しやすくなる

第4回では，公開されているCSVファイルを取得してその中身を眺めた．
今回は，あらかじめ用意されたファイルを取得するだけでなく，プログラムからデータ提供サービスへ問い合わせ，条件に応じたデータを取得する方法を学ぶ．
このようなプログラムから利用するための窓口を API（えーぴーあい）という．

### 到達目標

API の使い方を身につける．  
特に，API を単なる便利なデータ取得手段としてではなく，エンドポイント，パラメタ，レスポンス，ステータスコードからなる通信の仕組みとして理解する．

- API の役割を理解する
- URL，エンドポイント，パラメタの関係を理解する
- Python から Web 上の JSON データにアクセスし，レスポンスを保存できる．
- 取得した JSON のキーや値を確認し，データの中身を簡単に眺められる．
- JSON の階層構造から必要な値を取り出せる．
- API 利用時の注意点として，利用規約，アクセス頻度，エラー処理，APIキーの管理を説明できる．

### 準備

````{note} 演習0
本講義で使用するフォルダ `/User/<ユーザ名>/applied_programming_i/` 内に，本日使用するフォルダ `5` を作成し，次の `README.md` ファイルと `.gitignore` ファイルを作成した上で Git の初期化を行うこと．  
※ ターミナル・VSCodeのどちらで実施しても構わない．

README.md
```markdown
# 応用プログラミングI 第5回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

API の基本的な仕組みを理解し，Python からデータを取得して保存する．
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

**手順**
```{dropdown} A. ターミナルで実施する場合
1. ターミナルを起動する．
2. フォルダに移動する．`$ cd /User/<ユーザ名>/applied_programming_i`
3. フォルダ`5`を作成する．`$ mkdir 5`
4. フォルダ`5`に移動する．`$ cd 5`
5. 初期化する．`$ git init`
6. README.mdを作成する．`$ vim README.md`でファイルの中身を記入する．
7. .gitignoreを作成する．`$ vim .gitignore`でファイルの中身を記入する．
8. 全てのファイルをステージ領域に入れる．`$ git add .`
9. ステージ領域のファイルをコミットする．`$ git commit -m "first commit"`
```

```{dropdown} B. VSCodeで実施する場合
1. VSCodeを起動する．
2. メニューバー＞ファイル＞フォルダーを開く
3. `/User/<ユーザ名>/applied_programming_i`に移動して「新しいフォルダを作成」をクリック
4. `5`フォルダを作成して選択
5. 左のgitタブ＞「リポジトリを初期化する」を選択
6. README.mdを作成する．
7. .gitignoreを作成する．
8. 全てのファイルをステージ領域に入れる．（`+`をクリック）
9. ステージ領域のファイルをコミットする．（メッセージを記入して「コミット」をクリック）
```
````

---

## API

**API** (Application Programming Interface)：プログラムからデータ提供サービスに問い合わせるための窓口

人間がブラウザでページを開いてデータを探す代わりに，プログラムが決められたURLへリクエストを送りサーバからデータを受け取る際の窓口となるのがAPI．

### データの取得

第4回で扱ったCSVファイルは，公開されている1つのファイルを取得する形であった．
一方，APIでは，利用者が条件を指定して問い合わせることで，**条件に応じたデータ**が返される．

例）天気予報のデータでは次のような条件を指定できる場合がある．

- 地域
- 予報の種類
- 日時
- 取得したい変数

前回：データの入ったファイルを取得して利用した．  
今回：条件を指定し，それに応じてデータを取得して利用する．

**API**：指定の問い合わせ条件に対してデータを返す機能
$$
\text{API}: \text{問い合わせ条件} \mapsto \text{データ}
$$

### リクエストとレスポンス

**リクエスト**：API を利用するときに利用者側からサーバへ送る問い合わせ  
**レスポンス**：リクエストに対して，サーバから返ってくる結果

```text
利用者のプログラム  -- リクエスト -->  APIサーバ
利用者のプログラム  <-- レスポンス --  APIサーバ
```

この通信にはHTTPが多く使われる．
ブラウザでウェブページを見るときにも HTTP が使われているため，API 利用はウェブアクセスの一種とも言える．

---

## URLとパラメタ

### エンドポイント

**エンドポイント**：問い合わせ先のURL

気象庁の天気予報JSONでは，東京都の天気予報を次のURLから取得できる．

```text
https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
```

### パラメタ

URLの一部や `?` 以降のクエリパラメタによって取得条件を指定する．

気象庁の天気予報JSONでは，URL末尾の `130000` が地域を表すコードである．

例）東京都：`130000`

```text
https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
```

この形式では，
$$
\text{URL} = \text{endpoint} + \text{area code}
$$
と考えられる．

なお，地域コードの一覧は次のJSONから確認できる．

```text
https://www.jma.go.jp/bosai/common/const/area.json
```

**クエリパラメタ**：URL の `?` 以降に付けて，サーバへ問い合わせ条件を渡すための指定

````{tip} 例
```text
https://example.com/api/search?area=tokyo&date=2026-05-19
```
`?` 以降の `area=tokyo&date=2026-05-19` がクエリパラメタ
- `area=tokyo`：地域として`tokyo`を指定
- `date=2026-05-19`：日付として`2026-05-19`を指定
````

---

## レスポンス

### HTTPステータスコード

API からのレスポンスには，通信が成功したかどうかを示すステータスコードが含まれる．

代表的なステータスコード

- `200`：成功
- `400`：リクエストの指定が誤っている
- `401`：認証が必要，または認証に失敗
- `403`：アクセス権限がない
- `404`：指定したエンドポイントが見つからない
- `429`：短時間にアクセスしすぎている（DDos攻撃の対策）
- `500`：サーバ側のエラー
- `504`：サーバからのレスポンスがなくタイムアウト

### JSONレスポンス

多くの API はレスポンスを JSON 形式で返す．

※ JSON：キーと値 (key & values) の組を基本とする階層構造をもつデータ形式

気象庁の天気予報JSONは，大まかには次のような構造をもつ．

```json
[
  {
    "publishingOffice": "気象庁",
    "reportDatetime": "2026-05-12T11:00:00+09:00",
    "timeSeries": [
      {
        "timeDefines": ["2026-05-12T11:00:00+09:00", "2026-05-13T00:00:00+09:00"],
        "areas": [
          {
            "area": {"name": "東京地方", "code": "130010"},
            "weathers": ["晴れ", "晴れ 時々 くもり"],
            "winds": ["南の風", "北の風 後 南東の風"]
          }
        ]
      }
    ]
  }
]
```

一番外側はリストであり，その中に辞書が入っている．
さらに，`timeSeries` の中に時刻や地域ごとの予報が入っている．

---

## 利用時の注意点

### 利用規約とライセンス

API や Web 上のデータには**利用規約**や**ライセンス**が定められている．

````{tip} 例：気象庁ホームページの公開データ

気象庁ホームページで公開されている情報の利用規約は [https://www.jma.go.jp/jma/kishou/info/coment.html](https://www.jma.go.jp/jma/kishou/info/coment.html) から確認する．

権利表記の記載がない限り「公共データ利用規約（第1.0版）」に準拠した利用条件の下で利用できる．
利用する際は出典を記載する必要がある．

出典記載例：
```text
出典：気象庁ホームページ（https://www.jma.go.jp/）
```
````

### アクセス頻度

- 短時間に大量のリクエストを送るとサーバに負荷がかかるため，<span style="color:red">リクエストの頻度には注意が必要</span>である．
- APIによってはアクセス制限が設けられており，制限を超えると一時的に利用できなくなることがある．
- 繰り返し実行する場合は，取得済みのデータを保存し，同じデータを何度も取得しないように工夫する．

### APIキー

- 利用者を識別するための **APIキー** が必要になることがある．
- APIキーはパスワードに近い性質をもつため，公開リポジトリや提出ファイルに直接書いてはいけない．

※ 気象庁の天気予報JSONでは APIキーは不要

---

## 実データ

ここでは**気象庁の天気予報JSONデータ**を取得する．
特に**東京都の天気予報**を取得し，発表機関，発表時刻，地域名，天気，風，降水確率などを確認する．

- 気象庁ホームページ：https://www.jma.go.jp/
- 天気予報JSON（東京都）：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 地域コード一覧：https://www.jma.go.jp/bosai/common/const/area.json
- 利用規約：https://www.jma.go.jp/jma/kishou/info/coment.html

---

## データの保存と整理

APIで取得したデータも生データと加工データを分けて保存する．

```text
project/
├── data/
│   ├── raw/
│   └── processed/
├── src/
└── README.md
```

- `data/raw/`：APIから取得した直後のJSON
- `data/processed/`：必要な値だけを取り出したCSV
- `src/`：取得や変換に用いるプログラム
- `README.md`：API名，エンドポイント，取得日，地域コードなどの記録

````{note} 演習1
1. `/User/<ユーザ名>/applied_programming_i/5` のフォルダ直下に次のディレクトリ構成を作成せよ．

```text
5/
├── data/
│   ├── raw/
│   └── processed/
├── src/
└── README.md
```

2. README.mdに次の形式に則ってAPI取得記録を記載せよ．

```markdown
## ディレクトリ構成

- data/raw：生データを保存する
- data/processed：加工済みデータを保存する
- src：解析用コードを保存する

## API取得記録

- データ名：気象庁 天気予報JSON（東京都）
- 出典：気象庁ホームページ
- URL：https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
- 利用条件：公共データ利用規約（第1.0版）
- 取得日：2026年5月19日
- 地域コード：130000
- レスポンス形式：JSON
- 保存先：data/raw/jma_tokyo_forecast.json
- メモ：東京都の天気予報．取得時点によって結果が変わる．
```

3. 最後に，変更したファイルを全てコミットせよ．（コミットする前にファイルを保存できているか確認すること）

````

---

## Pythonを用いたAPIデータの取得

- 標準ライブラリの `urllib` と `json` を使って Web 上の JSON データにアクセスする．

````{warning} 課題1：気象庁JSONを取得する
- `src/fetch_jma_weather.py` を後述の内容で作成し，東京都の天気予報JSONを取得せよ．
- ただし2箇所の「〇〇」には適切なURLやパスを記入すること．
- 作成した`fetch_jma_weather.py`をWebClass「第5回課題」問1から提出せよ．

```python
import json
from urllib.request import urlopen

url = "〇〇"
output_path = "〇〇/jma_tokyo_forecast.json"

with urlopen(url) as response:
    data = json.load(response)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("url:", url)
print("saved:", output_path)
print("データ型:", type(data))
print("要素数:", len(data))
```

実行後，`data/raw/jma_tokyo_forecast.json` が作成されていることを確認せよ．
````
<!-- 
````{dropdown} <span style="color:red">解答例</span>
```python
import json
from urllib.request import urlopen

url = "https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json"
output_path = "data/raw/jma_tokyo_forecast.json"

with urlopen(url) as response:
    data = json.load(response)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("url:", url)
print("saved:", output_path)
print("データ型:", type(data))
print("要素数:", len(data))
```
````
 -->

---

## データの中身を眺める

APIからデータを取得したら，まず中身を眺める．

確認する項目
- 一番外側のデータ型は何か → リスト or 辞書
- リストの場合，要素数と対応する変数は何か
- 辞書の場合，キーは何か
- リストや辞書が入れ子になっていれば，中のデータ型は何か
- 分析に使いそうな変数を見つけた場合，変数名と意味をREADMEに記録する

中身の確認には jupyter note book が有効である．

````{note} 演習2
1. VSCodeまたはAnacondaでjupyter note bookを開き，次を実施せよ．

```python
import json

input_path = "data/raw/jma_tokyo_forecast.json"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)
```

変数 `data` に `jma_tokyo_forecast.json` のデータが展開されているので，`data` の中身を少しずつ確認する．

2. `data` の型と一番外側の要素数を確認する．
```python
print(type(data))
print(len(data))
```
3. `data`がリストの場合，最初の要素を確認し，これを変数`first`に入れる．
```python
first = data[0]
data[0]
```
4. 2と同じように`first`の型と外側の要素数を確認する．
```python
print(type(first))
print(len(first))
```
5. `first`が辞書の場合，どのようなキーを持つかを確認する．
```python
first.keys()
```
````

````{warning} 課題2：JSONの概要を確認する
`src/inspect_jma_weather.py` を次の内容で作成し，JSONの概要を確認せよ．  
なお，key名などは演習2で作成したnote bookで調べると良い．  
ただし，コード内の`<dataの最初の要素>`，`<firstのキー一覧>`，`<first内の時系列データ>`，`<time_series内の東京地方のデータ>`には適切な変数または式を挿入すること．

※ `<>`ごと挿入すること（`<>`は削除すること）

```python
import json

input_path = "data/raw/jma_tokyo_forecast.json"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

first = <dataの最初の要素>
print("最初の要素のキー:", <firstのキー一覧>)
print("発表機関:", first["publishingOffice"])
print("発表時刻:", first["reportDatetime"])

time_series = <first内の時系列データ>
print("timeSeries[0]のキー:", time_series[0].keys())
print("予報時刻:", time_series[0]["timeDefines"])

area = <time_series内の東京地方のデータ>
print("地域:", area["area"])
print("天気:", area["weathers"])
print("風:", area["winds"])
```

`src/inspect_jma_weather.py`を実行した出力結果をコピーし，WebClass「第5回課題」問2へ提出せよ．
````

````{warning} 課題3：気温を確認する
気象庁のJSONでは，気温の情報は `timeSeries` 3番目要素`[2]`の `temps` に含まれている．
このうち4番目要素`[3]`が明日の最高気温とされている．  
本課題実施時の気象庁APIにおける東京の明日の最高気温はいくつか調べ，調べた温度をWebClass「第5回課題」問3から解答せよ．
````
<!-- 
```python
data[0]["timeSeries"][2]["areas"][0]["temps"][3]
```
 -->

---

## まとめ

- API は，プログラムからデータ提供サービスを利用するための窓口である．
- API への問い合わせは，エンドポイントとパラメタによって構成される．
- リクエストに対してサーバから返る結果をレスポンスという．
- 多くの API は JSON 形式でデータを返す．
- JSON は階層構造をもつため，必要な値を取り出すにはキーやリストの位置を確認する必要がある．
- API の返すデータは取得時点や指定パラメタによって変わるため，取得条件を記録する必要がある．
- 取得した JSON は `data/raw` に保存し，分析しやすく加工したCSVは `data/processed` に保存する．
- API利用時には，利用規約，アクセス頻度，エラー処理，APIキーの管理に注意する．

次回はデータの前処理Iを扱う．

- 欠損値，外れ値，型変換など，取得したデータを分析可能な形に整えるための基本的な処理を学ぶ．
- 今回作成したような API 由来のデータも，分析前には構造や値の確認が必要である．

### 課題の提出物

WebClass「第5回課題」の問1へ課題1で作成した`README.md`を，問2へ課題2の出力結果を提出せよ．

### 課題の提出期限

<span style="color: red; ">5月19日(火)23:59まで</span>

---

## 自主学習用の発展問題

### 地域コードを確認する

````{note} 発展演習1：地域コードを変更する
地域コード一覧を確認し，東京都以外の地域コードを1つ選べ．

```text
https://www.jma.go.jp/bosai/common/const/area.json
```

次の問いに答えよ．

1. 選んだ地域名は何か．
2. 地域コードは何か．
3. URLのどの部分を書き換えればよいか．
````

### JSONをCSVに変換する

APIから取得したJSONは階層構造をもつため，そのままでは表形式の分析に使いにくい場合がある．
そこで，必要な値を取り出してCSVとして保存する．

````{note} 発展演習2：天気予報をCSVに変換する
`src/jma_weather_to_csv.py` を次の内容で作成し，`data/processed/jma_tokyo_weather.csv` を作成せよ．

```python
import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/processed/jma_tokyo_weather.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
time_series = forecast["timeSeries"][0]
time_defines = time_series["timeDefines"]
areas = time_series["areas"]

rows_out = []

for area in areas:
    area_name = area["area"]["name"]
    area_code = area["area"]["code"]
    weathers = area["weathers"]
    winds = area["winds"]
    waves = area["waves"]

    for i, time in enumerate(time_defines):
        rows_out.append({
            "time": time,
            "area_name": area_name,
            "area_code": area_code,
            "weather": weathers[i],
            "wind": winds[i],
            "wave": waves[i]
        })

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["time", "area_name", "area_code", "weather", "wind", "wave"]
    )
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))
```

実行後，次を確認せよ．

1. `data/processed/jma_tokyo_weather.csv` が作成されているか
2. CSV の列名は何か
3. JSON のどの部分を CSV に変換したか
````

### 降水確率を取り出す

````{note} 発展演習3：降水確率を確認する
気象庁のJSONでは，降水確率は `timeSeries[1]` の `pops` に含まれている．
`data[0]["timeSeries"][1]` を確認し，東京地方の降水確率を表示せよ．

次の問いに答えよ．

1. `timeDefines` はどのような時刻を表しているか．
2. `pops` の値は何を表しているか．
3. 天気の情報が入っていた `timeSeries[0]` と構造はどう違うか．
````

### API取得を再現可能にする

````{note} 発展演習4：READMEを更新する
API から取得したデータを用いて分析する場合，README に次の内容を追記せよ．

- 実行したスクリプト名
- 実行日
- 取得したURL
- 保存したJSONファイル
- 作成したCSVファイル
- 取得し直した場合に結果が変わる可能性
````
