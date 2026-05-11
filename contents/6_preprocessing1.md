# 第6回　データの前処理I

### 前回の復習

- API は，プログラムからデータ提供サービスを利用するための窓口である．
- API への問い合わせは，エンドポイントとクエリパラメータによって構成される．
- 多くの API は JSON 形式でデータを返す．
- 取得した JSON は `data/raw` に保存し，分析しやすく加工した CSV は `data/processed` に保存する．
- API 利用時には，利用規約，アクセス頻度，エラー処理，APIキーの管理に注意する．

前回までに，オープンデータや API からデータを取得し，JSON や CSV として保存する方法を学んだ．
しかし，取得したデータは，そのまま分析に使えるとは限らない．
値が欠けていたり，数値が文字列として保存されていたり，同じ行が重複していたり，極端な値が含まれていたりすることがある．

このようなデータを分析しやすい形に整える作業を**前処理**という．
本日は，前処理のうち，欠損値，型変換，外れ値，重複，列名整理などの基本を扱う．

### 到達目標

本日は，データの前処理Iとして，取得したデータを分析可能な形に整えるための基礎を学ぶ．

- 前処理がなぜ必要かを説明できる．
- CSVを読み込み，行数，列名，値の概要を確認できる．
- 欠損値を検出し，削除または補完の考え方を説明できる．
- 文字列として読み込まれた数値を適切な型に変換できる．
- 重複行や外れ値の候補を確認できる．
- 前処理前のデータと前処理後のデータを分けて保存できる．

### 準備

````{note} 演習0
本講義で使用するフォルダ `/User/<ユーザ名>/applied_programming_i/` 内に，本日使用するフォルダ `6` を作成し，次の `README.md` ファイルを作成した上で Git の初期化を行うこと．

```markdown
# 応用プログラミングI 第6回

- 氏名：<氏名>
- 学籍番号：<学籍番号>

## 今日の目標

欠損値，型変換，重複，外れ値を確認し，データを分析しやすい形に整える．
```
````

**手順**

1. ターミナルを起動
   1. フォルダ移動（`$ cd /User/<ユーザ名>/applied_programming_i/`）
   2. フォルダ `6` を作成（`$ mkdir 6`）
2. VSCodeを起動
   1. フォルダ `/User/<ユーザ名>/applied_programming_i/6` を開く
   2. `README.md` ファイルを作成する
3. Gitの初期化を行う
   1. 左のGitタブを開き「リポジトリを初期化する」を選択する
4. 最初のコミットを行い初期状態を記録する
   1. 全てのファイルをステージング領域に上げる
   2. コミットする（メッセージを忘れずにつけること）

---

## 前処理とは何か

データ分析では，取得したデータをそのまま使えるとは限らない．
実際のデータには，次のような問題が含まれることがある．

- 欠損値がある
- 数値が文字列として保存されている
- 日付の形式が統一されていない
- 同じ行が重複している
- 表記揺れがある
- 極端に大きい値や小さい値がある
- 列名が分かりにくい
- 分析に不要な列が含まれている

このような問題を確認し，分析しやすい形に整える作業が前処理である．

### 前処理の位置づけ

データ分析の流れは，次のように考えられる．

```text
データ取得 → 前処理 → 集計・可視化 → 分析 → 報告
```

前処理は，分析の前に行う準備である．
前処理をせずに分析すると，欠損値や型の誤りによって計算が失敗したり，誤った結果を得たりすることがある．

たとえば，気温の列が文字列として読み込まれていると，平均値を計算できない．
また，欠損値を無視して平均を計算すると，データの意味を誤って解釈する可能性がある．

### 前処理は記録する

前処理は，単なる作業ではなく，分析結果に影響を与える判断である．
どの行を削除したか，どの値を補完したか，どの列を作成したかを記録しなければ，後から分析を再現できない．

したがって，前処理は手作業ではなく，できるだけプログラムとして残すことが望ましい．

$$
D_{\mathrm{processed}} = T(D_{\mathrm{raw}})
$$

ここで，$D_{\mathrm{raw}}$ は生データ，$T$ は前処理，$D_{\mathrm{processed}}$ は前処理後のデータである．

---

## データ確認の基本

前処理の最初に行うことは，データの状態を確認することである．
いきなり値を変更するのではなく，まず次の点を見る．

- 行数
- 列名
- 各列の値の例
- 欠損値の有無
- 数値列の最小値・最大値
- 重複行の有無

### CSVの読み込み

Python の標準ライブラリ `csv` を用いると，CSVファイルを読み込める．

```python
import csv

with open("data/raw/students_raw.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print("行数:", len(rows))
print("列名:", reader.fieldnames)
print("最初の行:", rows[0])
```

### 文字列として読み込まれる

CSVの値は，基本的に文字列として読み込まれる．
たとえば，CSV上で `80` と書かれていても，Pythonでは `"80"` という文字列として扱われる．

数値計算を行うには，`int` や `float` を使って型変換する必要がある．

```python
score = int("80")
temperature = float("18.5")
```

---

## 欠損値

欠損値とは，本来あるべき値が存在しない状態である．
CSVでは，空欄，`NA`，`N/A`，`null`，`-` などで表されることがある．

### 欠損値の例

```csv
id,name,score,attendance
1,Aoki,80,14
2,Ito,,13
3,Ueda,75,
4,Endo,NA,12
```

この例では，`score` や `attendance` に欠損値がある．

### 欠損値を検出する

次のように，空文字や `NA` を欠損として判定できる．

```python
missing_values = {"", "NA", "N/A", "null", "-"}

for row in rows:
    for key, value in row.items():
        if value in missing_values:
            print("欠損:", row["id"], key)
```

### 欠損値への対応

欠損値への対応には，主に次の方法がある．

- 欠損を含む行を削除する
- 欠損を含む列を使わない
- 平均値や中央値などで補完する
- 「不明」というカテゴリとして扱う
- 欠損であること自体を情報として扱う

どの方法がよいかは，データの意味と分析目的によって異なる．
機械的に削除すればよいわけではない．

---

## 型変換

型変換とは，文字列として読み込まれた値を，整数，浮動小数点数，日付など，分析に適した型へ変換することである．

### 整数への変換

```python
score = int(row["score"])
```

### 小数への変換

```python
temperature = float(row["temperature"])
```

### 変換できない値

欠損値や不正な値があると，`int` や `float` による変換は失敗する．

```python
int("")
```

このような場合には，変換前に欠損値かどうかを確認する必要がある．

```python
value = row["score"]

if value == "":
    score = None
else:
    score = int(value)
```

ここで `None` は，Pythonで「値がない」ことを表す特別な値である．

---

## 重複

重複とは，同じ内容の行が複数回現れることである．
データ取得や結合の過程で，同じ観測が重複して入ることがある．

### 重複の例

```csv
id,name,score
1,Aoki,80
2,Ito,90
2,Ito,90
3,Ueda,75
```

この例では，`id=2` の行が重複している．

### 重複を検出する

```python
seen = set()

for row in rows:
    row_id = row["id"]
    if row_id in seen:
        print("重複:", row_id)
    else:
        seen.add(row_id)
```

重複を削除するかどうかは，データの意味によって判断する．
同じ人が複数回観測されたデータであれば，重複ではなく別の観測である可能性もある．

---

## 外れ値

外れ値とは，他の値と比べて極端に大きい，または小さい値である．
外れ値は，入力ミスの場合もあれば，本当に珍しい現象を表している場合もある．

### 外れ値の例

```csv
id,name,score
1,Aoki,80
2,Ito,90
3,Ueda,75
4,Endo,1000
```

この例では，`score=1000` は通常のテスト点数としては不自然である．

### 範囲で確認する

テスト点数が0点以上100点以下であると分かっている場合，次のように外れ値候補を確認できる．

```python
score = int(row["score"])

if score < 0 or score > 100:
    print("外れ値候補:", row["id"], score)
```

外れ値を見つけた場合，すぐに削除するのではなく，まず原因を考える．

- 入力ミスか
- 単位が違うのか
- 欠損値を特殊な値で表しているのか
- 本当に極端な観測なのか

---

## 列名と表記の整理

列名が分かりにくいと，後の分析でミスが起こりやすい．
たとえば，`Score`，`score `，`得点` が混在していると，プログラムから扱いにくい．

### 列名の方針

授業では，次のような列名を推奨する．

- 英数字を使う
- 小文字を使う
- 空白を使わない
- 単語の区切りには `_` を使う
- 意味が分かる名前にする

例：

```text
student_id
name
score
attendance
temperature_2m
```

列名は，分析結果の読みやすさにも影響する．

---

## 基本操作

### ディレクトリ構成を作る

```bash
mkdir -p data/raw
mkdir -p data/processed
mkdir -p src
```

### 練習用CSVを作る

`data/raw/students_raw.csv` を作成する．

```csv
id,name,score,attendance
1,Aoki,80,14
2,Ito,90,15
3,Ueda,,13
4,Endo,1000,12
5,Kato,75,
5,Kato,75,
6,Sato,NA,10
7,Tanaka,68,11
```

### READMEに記録する

```markdown
## 前処理記録

- 元データ：data/raw/students_raw.csv
- 前処理後データ：data/processed/students_clean.csv
- 確認した項目：欠損値，型変換，重複，外れ値
- 実行スクリプト：src/clean_students.py
```

````{note} 演習1
次のディレクトリ構成を作成せよ．

```text
6/
├── data/
│   ├── raw/
│   └── processed/
├── src/
└── README.md
```

作成後，`data/raw/students_raw.csv` に上の練習用CSVを入力し，README に前処理記録の項目を作成せよ．
````

```{warning} 課題1
次の手続きを行うこと．

1. `data/raw`，`data/processed`，`src` の3つのディレクトリを作成する
2. `data/raw/students_raw.csv` を作成する
3. `README.md` に「前処理記録」の項目を作成する
4. すべての変更をコミットする
5. `git log --oneline` を実行する

`README.md` の内容と，`git log --oneline` の出力をスクリーンショットに撮り，WebClass「第6回課題」問1から提出せよ．
```

---

## データの概要を確認する

````{note} 演習2
`src/inspect_students.py` を次の内容で作成し，練習用CSVの概要を確認せよ．

```python
import csv

input_path = "data/raw/students_raw.csv"

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames

print("行数:", len(rows))
print("列名:", fieldnames)
print("最初の3行:")

for row in rows[:3]:
    print(row)
```

実行後，次を確認せよ．

1. 行数はいくつか
2. 列名は何か
3. 値は文字列として表示されているか
````

---

## 欠損値と外れ値を確認する

````{note} 演習3
`src/check_students.py` を次の内容で作成し，欠損値，重複，外れ値候補を確認せよ．

```python
import csv

input_path = "data/raw/students_raw.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

seen_ids = set()

for row in rows:
    student_id = row["id"]

    if student_id in seen_ids:
        print("重複ID:", student_id)
    else:
        seen_ids.add(student_id)

    for key, value in row.items():
        if value in missing_values:
            print("欠損:", student_id, key)

    score_text = row["score"]
    if score_text not in missing_values:
        score = int(score_text)
        if score < 0 or score > 100:
            print("外れ値候補:", student_id, score)
```

実行後，次を確認せよ．

1. どの行に欠損値があるか
2. どのIDが重複しているか
3. 外れ値候補はどれか
````

---

## 前処理済みデータを作成する

ここでは，次の方針で前処理を行う．

- `score` が欠損している行は削除する
- `attendance` が欠損している場合は `0` とする
- `score` が0未満または100より大きい行は削除する
- `id` が重複している行は，最初の1件だけ残す
- `score` と `attendance` は整数に変換する

この方針は，あくまで授業用の例である．
実際の分析では，欠損値や外れ値をどう扱うかを，データの意味に基づいて判断する必要がある．

````{note} 演習4
`src/clean_students.py` を次の内容で作成し，`data/processed/students_clean.csv` を作成せよ．

```python
import csv

input_path = "data/raw/students_raw.csv"
output_path = "data/processed/students_clean.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

rows_out = []
seen_ids = set()

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        student_id = row["id"]

        if student_id in seen_ids:
            continue
        seen_ids.add(student_id)

        score_text = row["score"]
        attendance_text = row["attendance"]

        if score_text in missing_values:
            continue

        score = int(score_text)

        if score < 0 or score > 100:
            continue

        if attendance_text in missing_values:
            attendance = 0
        else:
            attendance = int(attendance_text)

        rows_out.append({
            "id": int(student_id),
            "name": row["name"],
            "score": score,
            "attendance": attendance
        })

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["id", "name", "score", "attendance"]
    )
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("出力行数:", len(rows_out))
```

実行後，`data/processed/students_clean.csv` の内容を確認せよ．
````

```{warning} 課題2
次の手続きを行うこと．

1. `src/inspect_students.py` を実行し，データの概要を確認する
2. `src/check_students.py` を実行し，欠損値，重複，外れ値候補を確認する
3. `src/clean_students.py` を実行し，`data/processed/students_clean.csv` を作成する
4. `README.md` に次の内容を追記する
   - 検出した欠損値
   - 検出した重複
   - 検出した外れ値候補
   - 前処理で採用した方針
5. 変更をコミットする

`README.md` と `data/processed/students_clean.csv` を，WebClass「第6回課題」問2から提出せよ．
```

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

### 外れ値の扱い

外れ値は，単純に削除すべきものではない．
外れ値が重要な現象を表している場合もある．

たとえば，気温データで極端に高い値があった場合，センサーの故障かもしれないが，本当に猛暑日だった可能性もある．
外れ値を扱うときは，データの出典，単位，観測方法を確認する必要がある．

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
data/raw/students_raw.csv
  ↓ src/clean_students.py
data/processed/students_clean.csv
```

---

## まとめ

- 前処理とは，取得したデータを分析しやすい形に整える作業である．
- 前処理の前には，行数，列名，値の例，欠損値，重複，外れ値候補を確認する．
- CSVの値は基本的に文字列として読み込まれるため，数値計算には型変換が必要である．
- 欠損値には，削除，補完，不明カテゴリとして扱うなど複数の対応がある．
- 外れ値はすぐに削除せず，データの意味を確認する必要がある．
- 生データは `data/raw` に残し，前処理後のデータは `data/processed` に保存する．
- 前処理の方針は，READMEやスクリプトとして記録する．

次回はデータの前処理IIを扱う．

- 複数の表を結合する方法，日付やカテゴリの扱い，集計用データセットの作成を学ぶ．
- 今回扱った欠損値，型変換，外れ値確認を土台として，より分析目的に近いデータセットを作成する．

### 課題の提出期限

<span style="color: red; ">5月26日(火)23:59まで</span>

---

## 自主学習用の発展問題

````{note} 発展課題1：欠損値の扱いを比較する

`students_raw.csv` について，次の2つの方針で前処理した場合を比較せよ．

1. `score` が欠損している行を削除する
2. `score` が欠損している行を平均値で補完する

次の問いに答えよ．

1. 出力される行数はどう変わるか．
2. 平均点はどう変わるか．
3. どちらの方針が適切だと思うか．その理由を説明せよ．
````

```{dropdown} 解答例

欠損を削除すると，欠損を含む行は分析対象から外れる．
一方，平均値で補完すると行数は保たれるが，本来観測されていない値を人工的に作ることになる．

どちらが適切かは，欠損の理由によって変わる．
たとえば，単なる入力漏れであり，欠損が少ないなら削除してもよい場合がある．
欠損が多い場合には，削除によってデータが偏る可能性があるため，補完を検討する．
```

````{note} 発展課題2：外れ値の原因を考える

`score=1000` のような値が見つかった場合，次の問いに答えよ．

1. どのような原因が考えられるか．
2. すぐに削除することの問題点は何か．
3. READMEには何を記録すべきか．
````

```{dropdown} 解答例

1. 入力ミス，単位の違い，満点の設定の違い，欠損値を特殊な値で表した，などが考えられる．
2. 本当に重要な観測である可能性を消してしまうことがある．また，削除基準が不明だと分析を再現できない．
3. 外れ値候補として検出した値，確認した理由，削除または保持した判断，その判断理由を記録する．
```

````{note} 発展課題3：前処理を関数として考える

本文では，前処理を
$$
D_{\mathrm{processed}} = T(D_{\mathrm{raw}})
$$
と表した．

次の問いに答えよ．

1. $D_{\mathrm{raw}}$ は何を表すか．
2. $T$ は何を表すか．
3. $D_{\mathrm{processed}}$ は何を表すか．
4. この考え方は，再現可能性にどのように役立つか．
````

```{dropdown} 解答例

1. $D_{\mathrm{raw}}$ は取得直後の生データを表す．
2. $T$ は欠損値処理，型変換，重複削除，外れ値処理などの前処理を表す．
3. $D_{\mathrm{processed}}$ は前処理後の分析しやすいデータを表す．
4. 前処理を関数として考えると，どの入力にどの処理を適用して，どの出力を得たかを明確にできる．そのため，後から同じ処理を再実行しやすくなる．
```
