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

## APIとは何か

API は Application Programming Interface の略である．
データ分析の文脈では，**プログラムからデータ提供サービスに問い合わせるための窓口**と考えるとよい．

人間がブラウザでページを開いてデータを探す代わりに，プログラムが決められたURLへリクエストを送り，サーバからデータを受け取る．

### ファイル取得との違い

第4回で扱ったCSVファイルは，公開されている1つのファイルを取得する形であった．
一方，APIでは，利用者が条件を指定して問い合わせることで，その条件に応じたデータが返される．

たとえば，天気予報のデータでは次のような条件を指定できる場合がある．

- 地域
- 予報の種類
- 日時
- 取得したい変数

前回：データの入ったファイルを取得して利用した．  
今回：条件を指定し，それに応じてデータを取得して利用する．

API は指定の問い合わせ条件に対するデータを返す機能である．
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

多くの Web API では，HTTP という通信の仕組みが使われる．
ブラウザでウェブページを見るときにも HTTP が使われているため，API 利用はウェブアクセスの一種である．

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
のように考えられる．

なお，地域コードの一覧は次のJSONから確認できる．

```text
https://www.jma.go.jp/bosai/common/const/area.json
```

---

## HTTPステータスコード

API からのレスポンスには，通信が成功したかどうかを示すステータスコードが含まれる．

代表的なステータスコード

- `200`：成功
- `400`：リクエストの指定が誤っている
- `401`：認証が必要，または認証に失敗
- `403`：アクセスが許可されていない
- `404`：指定したエンドポイントが見つからない
- `429`：短時間にアクセスしすぎている
- `500`：サーバ側のエラー

APIを使うプログラムでは，データを取り出す前に通信が成功したかを確認した方が良い．

---

## JSONレスポンス

多くの API は，レスポンスを JSON 形式で返す．

※ JSON：キーと値 (key & values) の組を基本とする階層構造をもつデータ形式

気象庁の天気予報JSONは，大まかに次のような構造をもつ．

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

## API利用時の注意点

### 利用規約とライセンス

API や Web 上のデータは自由に使えるように見えても，利用規約やライセンスが定められている．
気象庁ホームページで公開されている情報は，権利表記の記載がない限り「公共データ利用規約（第1.0版）」に準拠した利用条件の下で利用できる．
利用する際は出典を記載する必要がある．

出典記載例：

```text
出典：気象庁ホームページ（https://www.jma.go.jp/）
```

### アクセス頻度

短時間に大量のリクエストを送ると，サーバに負荷をかける．
また，APIによってはアクセス制限が設けられており，制限を超えると一時的に利用できなくなることがある．

授業の演習では，必要な回数だけ実行すること．
繰り返し実行する場合は，取得済みのデータを保存し，同じデータを何度も取得しない工夫をする．

### APIキー

API によっては，利用者を識別するための APIキーが必要になる．
APIキーはパスワードに近い性質をもつため，公開リポジトリや提出ファイルに直接書いてはいけない．

授業で扱う気象庁の天気予報JSONでは APIキーは不要である．
しかし，今後別の API を使う場合には，キーの扱いに注意する必要がある．

```{warning}
気象庁の天気予報JSONは，日本語で扱いやすく，APIキーなしで取得できる．
ただし，長期的な仕様の固定を保証する正式なAPIドキュメントが整備されているわけではないため，URLやJSON構造が変更される可能性がある．
授業では，公開されているJSONデータをAPIの学習用題材として利用する．
```

---

## 実データ

実際に公開されている日本語のJSONデータを取得して中身を確認する．
ここでは**気象庁の天気予報JSON**を用いる．
特に**東京都の天気予報**を取得し，発表機関，発表時刻，地域名，天気，風，降水確率などを確認する．

気象庁ホームページ：
```text
https://www.jma.go.jp/
```

天気予報JSON（東京都）：
```text
https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json
```

地域コード一覧：
```text
https://www.jma.go.jp/bosai/common/const/area.json
```

利用規約：
```text
https://www.jma.go.jp/jma/kishou/info/coment.html
```

---

## データの保存と整理

第4回と同様に，APIで取得したデータも生データと加工データを分けて保存する．

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
`/User/<ユーザ名>/applied_programming_i/5` のフォルダ直下に次のディレクトリ構成を作成せよ．

```text
5/
├── data/
│   ├── raw/
│   └── processed/
├── src/
└── README.md
```
````

````{warning} 課題1
README.mdに次の形式に則ってAPI取得記録を記載せよ．
その上で変更したファイルを全てコミットせよ．（コミットする前にファイルを保存できているか確認すること）
なお「〇〇」には適切な説明を記載すること．  
作成した`README.md`ファイルはWebClass「第5回課題」問1から提出すること．

```markdown
## ディレクトリ構成

- data/raw：〇〇
- data/processed：〇〇
- src：〇〇

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
````

---

## Pythonを用いたAPIデータの取得

Python では，標準ライブラリの `urllib` と `json` を使って Web 上の JSON データにアクセスできる．
ここでは追加のライブラリをインストールしなくても実行できる方法を使う．

````{note} 演習2：気象庁JSONを取得する
`src/fetch_jma_weather.py` を次の内容で作成し，東京都の天気予報JSONを取得せよ．

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

実行後，`data/raw/jma_tokyo_forecast.json` が作成されていることを確認せよ．
````

---

## データの中身を眺める

APIからデータを取得したら，すぐに分析するのではなく，まず中身を眺める．
ここでの目的は，厳密な分析ではなく，JSONの構造を理解することである．

最初に確認する項目は次の通りである．

- 一番外側のデータ型
- リストの要素数
- 最初の要素が持つキー
- 発表機関
- 発表時刻
- `timeSeries` の構造
- 地域名，天気，風，波などの値

````{note} 課題2：JSONの概要を確認する
`src/inspect_jma_weather.py` を次の内容で作成し，JSONの概要を確認せよ．  
なお，コード内の`<最初の要素>` `<キー一覧>` `<時系列>` `<地域データ>`には適切な変数または式を挿入すること．

```python
import json

input_path = "data/raw/jma_tokyo_forecast.json"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

first = <最初の要素>

print("一番外側のデータ型:", type(data))
print("リストの要素数:", len(data))
print("最初の要素のキー:")
print(<キー一覧>)

print("発表機関:", first["publishingOffice"])
print("発表時刻:", first["reportDatetime"])

time_series = <時系列>
print("timeSeries[0]のキー:")
print(time_series.keys())
print("予報時刻:")
print(time_series["timeDefines"])

area = <地域データ>
print("地域:")
print(area["area"])
print("天気:")
print(area["weathers"])
print("風:")
print(area["winds"])
```

実行後，次を確認せよ．（確認するだけで良い）

1. 一番外側はリストか，辞書か
2. 最初の要素にはどのようなキーがあるか
3. 発表機関と発表時刻はどこに書かれているか
4. `timeSeries[0]` にはどのような情報が含まれているか
5. 天気や風は日本語でどのように記録されているか

`src/inspect_jma_weather.py`を実行した出力結果をスクリーンショットに取り，WebClass「第5回課題」問2へ提出せよ．
````

<!--
first = data[0]
print(first.keys())
time_series = first["timeSeries"][0]
area = time_series["areas"][0]
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
