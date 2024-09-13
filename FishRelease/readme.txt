myenv - 実行したら出たもの
static - 実行したら出たもの
templates - indexとresultのページある
database - データベース作成用python
app.py - アプリ
requirements.txt - インストールしたらyolo使えるようになる
best_v1.0.pt - 自作認識モデル。今は12種類の魚が認識できる
fish_rules.db - 作成したデータベース
yolov8s.pt - 実行したら出たもの。app.pyで他のモデルに変更可能


実行する方法：
pythonとpipがあるか確認。なかったらインストール。(確認コード：pip --version)
cmdを開いて以下のコードを実行する：
pip install flask opencv-python-headless numpy ultralytics
cd パス（アプリのあるフォルダ）
pip install -r requirements.txt
python app.py
ローカルホスト(http://127.0.0.1:5000/)にアクセスする

