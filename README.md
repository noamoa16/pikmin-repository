# Pikmin Repository

昔作成したウェブサイトをGitHubに移行しました。

[**アクセスはこちら！**](https://noamoa16.github.io/pikmin-repository/)

|フォルダ|内容|
|----|----|
|docs|Flaskによって自動生成された文書|
|templates|文書のテンプレート|
|static|JavaScirpt / CSS / 画像|
|data|洞窟調査などのデータ|
|tools|便利ツールなど|

## 開発者向け

### 要件
- Python 3
  - Python 3.12.0で動作確認済み
  - 古いバージョンだと動作しない可能性あり

### 必要なモジュールのインストール
`pip install -r requirements.txt`

### ローカルサーバーでのテスト
`python server.py`

### ビルド(文書の自動生成)
`python freeze.py`
