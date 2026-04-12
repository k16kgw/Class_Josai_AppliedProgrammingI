.PHONY: start build clean install

# ローカルサーバーを起動 (http://localhost:3000)
start:
	myst start

# HTMLビルドのみ
build:
	myst build --html

# ビルド成果物を削除
clean:
	rm -rf _build

# 依存パッケージをインストール (uv使用)
install:
	uv pip install -r requirements.txt
