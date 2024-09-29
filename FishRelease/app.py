from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import sqlite3
import cv2
import numpy as np
from io import BytesIO
import base64
import os
from ultralytics import YOLO
import math

app = Flask(__name__)
app.secret_key = 'ProjectC-2024-E'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# グローバルにYOLOv8モデルを初期化
MODEL_PATH = r'K:\FishRelease\best_v1.0.pt'
model = YOLO(MODEL_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image/', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return 'No image file', 400
    
    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # YOLOv8を使った画像認識の処理
    processed_img, labels = yolo_detect_objects(img)

    # データベース接続
    conn = sqlite3.connect('fish_rules.db')
    cursor = conn.cursor()

    # ラベルごとに情報を取得
    fish_info = {}
    for label in labels:
        cursor.execute('''
        SELECT fish_type, fish_name, prefecture, release_length, release_rule
        FROM fish_rules
        WHERE fish_type = ?
        ''', (label,))
        rows = cursor.fetchall()
        if rows:
            fish_info[label] = [{'fish_type': row[0], 'fish_name': row[1], 'prefecture': row[2], 'release_length': row[3], 'release_rule': row[4]} for row in rows]

    conn.close()

    # 画像をサーバー上に保存
    img_filename = 'result_image.png'
    img_path = os.path.join(UPLOAD_FOLDER, img_filename)
    cv2.imwrite(img_path, processed_img)
    
    # 結果をセッションに保存
    session['fish_info'] = fish_info
    session['image_filename'] = img_filename

    # 結果表示ページにリダイレクト
    return redirect(url_for('result'))

@app.route('/result')
def result():
    # セッションから結果を取得
    fish_info = session.get('fish_info', {})
    image_filename = session.get('image_filename', '')

    return render_template('result.html', fish_info=fish_info, image_url=url_for('uploaded_file', filename=image_filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def yolo_detect_objects(img):
    results = model(img)
    labels = []

    for result in results:
        boxes = result.boxes.xyxy
        confidences = result.boxes.conf
        class_ids = result.boxes.cls

        for box, class_id in zip(boxes, class_ids):
            x1, y1, x2, y2 = map(int, box)
            color = [int(c) for c in np.random.randint(0, 255, size=(3,))]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            class_name = model.names[int(class_id)]
            text = f"{class_name}"
            cv2.putText(img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # ラベルの追加
            labels.append(class_name)

    return img, labels

@app.route('/length_measurement')
def length_measurement():
    return render_template('length_measurement.html')  # 長さ測定ページ

# 物体Aと物体Bの長さ計算API
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    lineA = data['lineA']
    lineB = data['lineB']
    actual_length_A = float(data['actualLengthA'])

    # ピクセル長を計算
    pixel_length_A = math.sqrt((lineA['x2'] - lineA['x1']) ** 2 + (lineA['y2'] - lineA['y1']) ** 2)
    pixel_length_B = math.sqrt((lineB['x2'] - lineB['x1']) ** 2 + (lineB['y2'] - lineB['y1']) ** 2)

    # 補正係数 (実際の長さ/ピクセル長) から物体Bの実際の長さを計算
    correction_factor = actual_length_A / pixel_length_A
    actual_length_B = pixel_length_B * correction_factor

    # 小数点以下1桁に丸める
    actual_length_B = round(actual_length_B, 1)

    return jsonify({"actualLengthB": actual_length_B})

if __name__ == "__main__":
    app.run(debug=True)
