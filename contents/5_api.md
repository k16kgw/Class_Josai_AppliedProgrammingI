# 第5回　APIの使い方

### 前回の復習

- オープンデータは，単に閲覧できるデータではなく，再利用条件が明示されたデータである．
- データ取得では，出典，ライセンス，更新頻度，取得時点，形式を確認する必要がある．
- CSV は表形式，JSON は階層構造を表す代表的な形式である．
- 生データと加工データを分けることで，元データと自分の処理結果を区別できる．
- Git では，データそのものだけでなく，取得手順と整理過程を管理することが重要である．

前回は，取得済みのデータファイルをどのように整理し，記録するかを学んだ．
しかし，実際のデータ分析では，ウェブページから手作業でファイルをダウンロードするだけでなく，プログラムからデータ提供サービスへ問い合わせて，必要なデータを取得することが多い．

このようなプログラムから利用するための窓口を API という．
本日は，API の基本的な考え方と，Python を用いて API から JSON データを取得する方法を学ぶ．

### 到達目標

本日は，API の使い方を身につけることを目標とする．
特に，API を単なる便利なデータ取得手段としてではなく，URL，パラメータ，レスポンス，ステータスコードからなる通信の仕組みとして理解する．

- API の役割を説明できる．
- URL，エンドポイント，クエリパラメータの関係を説明できる．
- Python から API にアクセスし，JSON 形式のレスポンスを取得できる．
- 取得した JSON から必要な値を取り出し，CSV として保存できる．
- API 利用時の注意点として，利用規約，アクセス頻度，エラー処理，取得記録の重要性を説明できる．

### 準備

````{note} 演習0
本講義で使用するフォルダ `/User/<ユーザ名>/applied_programming_i/` 内に，本日使用するフォルダ `5` を作成し，次の `README.md` ファイルを作成した上で Git の初期化を行うこと．

```markdown
# 応用プログラミングI 第5回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

API の基本的な仕組みを理解し，Python からデータを取得して保存する．
```
````

**手順**

1. ターミナルを起動
   1. フォルダ移動（`$ cd /User/<ユーザ名>/applied_programming_i/`）
   2. フォルダ `5` を作成（`$ mkdir 5`）
2. VSCodeを起動
   1. フォルダ `/User/<ユーザ名>/applied_programming_i/5` を開く
   2. `README.md` ファイルを作成する
3. Gitの初期化を行う
   1. 左のGitタブを開き「リポジトリを初期化する」を選択する
4. 最初のコミットを行い初期状態を記録する
   1. 全てのファイルをステージング領域に上げる
   2. コミットする（メッセージを忘れずにつけること）

---

## APIとは何か

API は Application Programming Interface の略である．
直訳すれば，アプリケーションをプログラムから利用するためのインターフェースである．

データ分析の文脈では，API は「プログラムからデータ提供サービスに問い合わせるための窓口」と考えるとよい．
人間がブラウザでページを開いてデータを探す代わりに，プログラムが決められた URL へリクエストを送り，サーバからデータを受け取る．

### ファイル取得との違い

前回扱った CSV や JSON ファイルは，すでに存在するファイルを取得して保存する形であった．
一方，API では，利用者が条件を指定して問い合わせることで，その条件に応じたデータが返される．

たとえば，気象データ API では，

- 地点
- 日付
- 取得したい変数
- 単位
- 時間帯

などを指定できる場合がある．

API は，単なるファイルではなく，
$$
D = A(\theta)
$$
のような関数として考えることができる．
ここで，$A$ は API，$\theta$ は問い合わせ条件，$D$ は返されるデータである．

### リクエストとレスポンス

API を利用するとき，利用者側からサーバへ送る問い合わせを**リクエスト**という．
それに対して，サーバから返ってくる結果を**レスポンス**という．

```text
利用者のプログラム  -- リクエスト -->  APIサーバ
利用者のプログラム  <-- レスポンス --  APIサーバ
```

多くの Web API では，HTTP という通信の仕組みが使われる．
ブラウザでウェブページを見るときにも HTTP が使われているため，API 利用はウェブアクセスの一種と考えることができる．

---

## URLとクエリパラメータ

### エンドポイント

API では，問い合わせ先の URL を**エンドポイント**という．
たとえば，Open-Meteo の天気予報 API では，次の URL が予報データ取得のエンドポイントである．

```text
https://api.open-meteo.com/v1/forecast
```

このエンドポイントに対して，緯度，経度，取得したい変数などを指定して問い合わせる．

### クエリパラメータ

URL の `?` 以降に書かれる条件を**クエリパラメータ**という．
複数の条件は `&` でつなぐ．

```text
https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&hourly=temperature_2m
```

この URL では，次の条件を指定している．

- `latitude=35.6895`：緯度
- `longitude=139.6917`：経度
- `hourly=temperature_2m`：1時間ごとの気温

一般に，API への問い合わせは
$$
\text{URL} = \text{endpoint} + \text{parameters}
$$
と考えることができる．

### パラメータを辞書で管理する

Python では，パラメータを文字列として直接つなげるよりも，辞書として管理する方が安全である．

```python
params = {
    "latitude": 35.6895,
    "longitude": 139.6917,
    "hourly": "temperature_2m",
    "timezone": "Asia/Tokyo"
}
```

このように書くことで，どの条件を指定しているかが分かりやすくなる．

---

## HTTPステータスコード

API からのレスポンスには，通信が成功したかどうかを示すステータスコードが含まれる．

代表的なものは次の通りである．

- `200`：成功
- `400`：リクエストの指定が誤っている
- `401`：認証が必要，または認証に失敗
- `403`：アクセスが許可されていない
- `404`：指定したエンドポイントが見つからない
- `429`：短時間にアクセスしすぎている
- `500`：サーバ側のエラー

API を使うプログラムでは，データを取り出す前に，通信が成功したかどうかを確認することが重要である．

---

## JSONレスポンス

多くの API は，レスポンスを JSON 形式で返す．
JSON は第4回で扱ったように，キーと値の組を基本とする階層構造をもつデータ形式である．

API から返ってくる JSON は，たとえば次のような構造をもつ．

```json
{
  "latitude": 35.7,
  "longitude": 139.7,
  "hourly": {
    "time": ["2026-05-10T00:00", "2026-05-10T01:00"],
    "temperature_2m": [18.3, 18.1]
  },
  "hourly_units": {
    "temperature_2m": "°C"
  }
}
```

ここでは，`hourly` の中に `time` と `temperature_2m` が入っている．
つまり，必要な値を取り出すには，JSON の階層をたどる必要がある．

```python
times = data["hourly"]["time"]
temperatures = data["hourly"]["temperature_2m"]
```

---

## PythonからAPIを使う

Python では，標準ライブラリの `urllib` と `json` を使って API にアクセスできる．
ここでは追加のライブラリをインストールしなくても実行できる方法を使う．

### 基本形

```python
import json
from urllib.parse import urlencode
from urllib.request import urlopen

endpoint = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 35.6895,
    "longitude": 139.6917,
    "hourly": "temperature_2m",
    "timezone": "Asia/Tokyo"
}

url = endpoint + "?" + urlencode(params)

with urlopen(url) as response:
    data = json.load(response)

print(data)
```

### URLエンコード

URL には，そのまま書くと問題が起こる文字がある．
そのため，パラメータを URL に入れられる形へ変換する必要がある．
この変換を URL エンコードという．

Python では，`urllib.parse.urlencode` を使うことで，辞書をクエリ文字列に変換できる．

```python
from urllib.parse import urlencode

params = {
    "latitude": 35.6895,
    "longitude": 139.6917,
    "hourly": "temperature_2m"
}

query = urlencode(params)
print(query)
```

---

## API利用時の注意点

### 利用規約とライセンス

API は自由に使えるように見えても，利用規約やライセンスが定められている．
商用利用，取得頻度，再配布，出典表示などに条件がある場合がある．

データ取得前に，次の点を確認する．

- 利用目的に制限があるか
- APIキーが必要か
- 取得回数やアクセス頻度に制限があるか
- 取得したデータを再配布できるか
- 出典表示が必要か

### アクセス頻度

短時間に大量のリクエストを送ると，サーバに負荷をかける．
また，API によってはアクセス制限が設けられており，制限を超えると一時的に利用できなくなることがある．

授業の演習では，必要な回数だけ実行すること．
繰り返し実行する場合は，取得済みのデータを保存し，同じデータを何度も取得しない工夫をする．

### エラー処理

API は常に成功するとは限らない．
ネットワークの問題，パラメータの誤り，サーバ側の障害などによってエラーが起こることがある．

そのため，実用的なプログラムでは，次のような確認が必要になる．

- ステータスコードは成功を表しているか
- 期待したキーが JSON に含まれているか
- 欠損値が含まれていないか
- 取得結果を保存できたか

---

## 基本操作

### ディレクトリ構成を作る

```bash
mkdir -p data/raw
mkdir -p data/processed
mkdir -p src
```

### API取得記録を書く

`README.md` には，次のような項目を記録する．

```markdown
## API取得記録

- API名：
- エンドポイント：
- 取得日：
- パラメータ：
- レスポンス形式：
- ライセンス・利用条件：
- メモ：
```

### Pythonファイルを実行する

```bash
python src/fetch_weather.py
```

```{warning}
実行時にネットワークに接続している必要がある．
また，API の仕様変更や一時的な障害によって，授業資料と同じ結果が返らない場合がある．
そのため，取得日と取得条件を必ず記録すること．
```

````{note} 演習1
次のディレクトリ構成を作成せよ．

```text
5/
├── data/
│   ├── raw/
│   └── processed/
├── src/
└── README.md
```

作成後，`README.md` に次の内容を追記してコミットせよ．

```markdown
## API取得記録

- API名：Open-Meteo Forecast API
- エンドポイント：https://api.open-meteo.com/v1/forecast
- 取得日：<今日の日付>
- パラメータ：東京の緯度・経度，1時間ごとの気温
- レスポンス形式：JSON
```
````

```{warning} 課題1
次の手続きを行うこと．

1. `data/raw`，`data/processed`，`src` の3つのディレクトリを作成する
2. `README.md` に「API取得記録」の項目を作成する
3. `git status` を実行する
4. すべての変更をコミットする
5. `git log --oneline` を実行する

`README.md` の内容と，`git log --oneline` の出力をスクリーンショットに撮り，WebClass「第5回課題」問1から提出せよ．
```

---

## APIからJSONを取得する

````{note} 演習2
`src/fetch_weather.py` を次の内容で作成し，東京の1時間ごとの気温データを取得せよ．

```python
import json
from urllib.parse import urlencode
from urllib.request import urlopen

endpoint = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 35.6895,
    "longitude": 139.6917,
    "hourly": "temperature_2m",
    "timezone": "Asia/Tokyo"
}

url = endpoint + "?" + urlencode(params)

with urlopen(url) as response:
    data = json.load(response)

with open("data/raw/weather_tokyo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("saved:", "data/raw/weather_tokyo.json")
print("latitude:", data["latitude"])
print("longitude:", data["longitude"])
print("hourly keys:", data["hourly"].keys())
```

実行後，次を確認せよ．

1. `data/raw/weather_tokyo.json` が作成されているか
2. `hourly` の中にどのキーが含まれているか
3. 取得した JSON はどのような階層構造をもつか
````

この演習では，取得した JSON を `data/raw` に保存する．
これは，API から取得した直後のデータを生データとして残すためである．

---

## JSONから必要な値を取り出す

API のレスポンスには，多くの情報が含まれる．
分析では，その中から必要な値を取り出す必要がある．

````{note} 演習3
`src/inspect_weather.py` を次の内容で作成し，保存済みの JSON から最初の10件を表示せよ．

```python
import json

with open("data/raw/weather_tokyo.json", encoding="utf-8") as f:
    data = json.load(f)

times = data["hourly"]["time"]
temperatures = data["hourly"]["temperature_2m"]

for time, temperature in zip(times[:10], temperatures[:10]):
    print(time, temperature)
```

実行後，次を確認せよ．

1. `time` はどのような形式で表されているか
2. `temperature_2m` の単位はどこに書かれているか
3. `zip` は何をしているか
````

`zip(times, temperatures)` は，時刻のリストと気温のリストを対応づけるために使っている．
表データとして考えれば，時刻と気温の2列を作る準備をしていることになる．

---

## JSONをCSVに変換する

API から取得した JSON は階層構造をもつため，そのままでは表形式の分析に使いにくい場合がある．
そこで，必要な値を取り出して CSV として保存する．

````{note} 演習4
`src/weather_to_csv.py` を次の内容で作成し，`data/processed/weather_tokyo_temperature.csv` を作成せよ．

```python
import csv
import json

input_path = "data/raw/weather_tokyo.json"
output_path = "data/processed/weather_tokyo_temperature.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

times = data["hourly"]["time"]
temperatures = data["hourly"]["temperature_2m"]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["time", "temperature_2m"])
    writer.writeheader()

    for time, temperature in zip(times, temperatures):
        writer.writerow({
            "time": time,
            "temperature_2m": temperature
        })

print("saved:", output_path)
```

実行後，次を確認せよ．

1. `data/processed/weather_tokyo_temperature.csv` が作成されているか
2. CSV の列名は何か
3. JSON のどの部分を CSV に変換したか
````

```{warning} 課題2
次の手続きを行うこと．

1. `src/fetch_weather.py` を実行し，`data/raw/weather_tokyo.json` を作成する
2. `src/weather_to_csv.py` を実行し，`data/processed/weather_tokyo_temperature.csv` を作成する
3. `README.md` に次の内容を追記する
   - 使用した API
   - エンドポイント
   - 指定したパラメータ
   - 作成した raw データ
   - 作成した processed データ
4. 変更をコミットする

`README.md` と `data/processed/weather_tokyo_temperature.csv` を，WebClass「第5回課題」問2から提出せよ．
```

---

## APIキー

API によっては，利用者を識別するための APIキーが必要になる．
APIキーはパスワードに近い性質をもつため，公開リポジトリや提出ファイルに直接書いてはいけない．

### APIキーを扱うときの注意

- APIキーを Git にコミットしない
- スクリーンショットに APIキーが写らないようにする
- 他人の APIキーを使わない
- 利用しなくなった APIキーは削除または無効化する

授業で扱う Open-Meteo の基本的な利用では APIキーは不要である．
しかし，今後別の API を使う場合には，キーの扱いに注意する必要がある．

---

## Git管理とAPI取得

API を使う場合も，第4回と同じく，取得結果だけでなく取得手順を記録することが重要である．

Gitで管理するとよいものは次の通りである．

- API 取得用スクリプト
- JSON を CSV に変換するスクリプト
- README
- メタデータ
- 小さなサンプルデータ

一方，次のものは Git 管理に注意が必要である．

- APIキー
- 個人情報を含むデータ
- サイズの大きい取得結果
- ライセンス上，再配布できないデータ

特に API の場合，取得時点によって結果が変わることがある．
したがって，プログラムだけでなく，取得日時とパラメータも記録しておく必要がある．

---

## まとめ

- API は，プログラムからデータ提供サービスを利用するための窓口である．
- API への問い合わせは，エンドポイントとクエリパラメータによって構成される．
- リクエストに対してサーバから返る結果をレスポンスという．
- 多くの API は JSON 形式でデータを返す．
- Python では，`urllib` と `json` を使って API にアクセスできる．
- 取得した JSON は `data/raw` に保存し，分析しやすく加工した CSV は `data/processed` に保存する．
- API 利用時には，利用規約，アクセス頻度，エラー処理，APIキーの管理に注意する．

次回はデータの前処理Iを扱う．

- 欠損値，外れ値，型変換など，取得したデータを分析可能な形に整えるための基本的な処理を学ぶ．
- 今回作成したような API 由来のデータも，分析前には構造や値の確認が必要である．

### 課題の提出期限

<span style="color: red; ">5月19日(火)23:59まで</span>

---

## 自主学習用の発展問題

````{note} 発展課題1：APIのURLを分解する

次の URL を，エンドポイントとクエリパラメータに分解せよ．

```text
https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&hourly=temperature_2m&timezone=Asia/Tokyo
```

次の問いに答えよ．

1. エンドポイントはどこか．
2. 指定されているパラメータ名をすべて書け．
3. 緯度と経度を変更すると，取得結果はどのように変わるか．
````

```{dropdown} 解答例

1. エンドポイントは `https://api.open-meteo.com/v1/forecast` である．
2. パラメータ名は `latitude`，`longitude`，`hourly`，`timezone` である．
3. 緯度と経度は地点を表すため，変更すると別の場所の気象データが返る．

**解説**

API の URL は，問い合わせ先と問い合わせ条件に分けて読むことが重要である．
同じエンドポイントでも，パラメータを変えることで取得されるデータが変化する．
```

````{note} 発展課題2：エラーの原因を考える

次のようなエラーが起こったとする．

```text
HTTP Error 400: Bad Request
```

次の問いに答えよ．

1. ステータスコード `400` は何を意味するか．
2. どのような原因が考えられるか．
3. まず何を確認すべきか．
````

```{dropdown} 解答例

1. `400` は，リクエストの指定が誤っていることを表す．
2. 必須パラメータが足りない，パラメータ名を間違えた，値の形式が不正である，などが考えられる．
3. API のドキュメントを確認し，エンドポイント，必須パラメータ，値の形式を見直す．

**解説**

API を使うとき，エラーはよく起こる．
重要なのは，エラーを単なる失敗として扱うのではなく，ステータスコードやレスポンス本文から原因を推測することである．
```

````{note} 発展課題3：API取得を再現可能にする

API から取得したデータを用いて分析する場合，次の問いに答えよ．

1. README に記録すべき情報は何か．
2. なぜ取得日時が重要か．
3. API から取得したデータを毎回取り直す場合と，保存済みデータを使う場合の違いは何か．
````

```{dropdown} 解答例

1. API名，エンドポイント，パラメータ，取得日時，レスポンス形式，ライセンス，取得用スクリプト名などを記録する．
2. API の返すデータは更新されることがあるため，同じプログラムでも取得日時が異なると結果が変わる可能性がある．
3. 毎回取り直す場合は最新のデータを使えるが，再現性が下がることがある．保存済みデータを使う場合は，過去の分析結果を再現しやすいが，最新情報ではない可能性がある．

**解説**

API は動的なデータ取得手段である．
そのため，ファイルを一度ダウンロードする場合以上に，取得条件と取得時点の記録が重要になる．
```
