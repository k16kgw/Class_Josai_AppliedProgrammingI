# 第1回：ガイダンスとPython環境構築

## ガイダンス

- 科目の概要・目的・到達目標を確認する
- 成績評価方法・講義の進め方を把握する
- Python実行環境を構築する

## Python とは

**Python** はシンプルな文法を持つ汎用プログラミング言語である．

- 科学技術計算（NumPy，SciPy）
- データ分析（Pandas）
- 機械学習（scikit-learn，PyTorch）
- Web開発（Django，Flask）

など幅広い分野で使われており，特に理工学・データサイエンス分野で標準的なツールとなっている．

## 環境構築

### uv のインストール

本講義では Python パッケージ管理に **uv** を使用する．

```bash
# macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Python のインストール

```bash
uv python install 3.12
```

### 仮想環境の作成と有効化

```bash
# プロジェクトディレクトリで実行
uv venv
source .venv/bin/activate
```

### 必要なパッケージのインストール

```bash
uv pip install numpy matplotlib pandas scipy jupyterlab
```

## はじめての Python

### Hello, World!

```python
print("Hello, World!")
```

### 計算

```python
# 四則演算
print(1 + 2)   # 3
print(10 / 3)  # 3.3333...
print(10 // 3) # 3（整数除算）
print(10 % 3)  # 1（余り）
print(2 ** 10) # 1024（べき乗）
```

### 変数への代入

```python
x = 3.14
name = "Python"
flag = True

print(x)
print(name)
print(type(x))  # <class 'float'>
```

## JupyterLab の起動

```bash
jupyter lab
```

ブラウザが開き，`.ipynb` ファイルでインタラクティブにコードを実行できる．

## まとめ

- Python は科学技術計算に広く使われる汎用言語
- uv で環境を管理し，JupyterLab で対話的に実行する
- 次回は変数・データ型・演算子を詳しく学ぶ
