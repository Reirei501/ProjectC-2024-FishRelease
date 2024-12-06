static - アップロードされた画像を保存する場所
templates - htmlのある場所
database - データベース作成用python
app.py - アプリ
requirements.txt - インストールすべきものが書いてある
best_v2.0.pt - 自作認識モデル。46種類の魚が認識できる
best_v3.0.pt - 自作認識モデル。毎種類40枚→80枚
fish_rules.db - 作成したデータベース
yolov8s.pt - 使ってるyoloモデル。app.pyで他のモデルに変更可能


実行する方法：
pythonとpipがあるか確認。なかったらインストール。(確認コード：pip --version)
cmdを開いて以下のコードを実行する：
cd パス（アプリのあるフォルダ）
pip install -r requirements.txt
python app.py
ローカルホストにアクセスする→
http://127.0.0.1:5000/

