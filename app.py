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

# YOLOv8モデルを初期化
MODEL_PATH = 'best_v2.0.pt'
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
    session['labels'] = labels

    # 最初のラベルをセッションに保存
    if labels:
        session['fish_name'] = labels[0]

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
    detections = []  # ラベルと信頼度を保存するリスト

    for result in results:
        boxes = result.boxes.xyxy
        confidences = result.boxes.conf
        class_ids = result.boxes.cls

        for box, confidence, class_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = map(int, box)
            color = [int(c) for c in np.random.randint(0, 255, size=(3,))]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            class_name = model.names[int(class_id)]
            text = f"{class_name} ({confidence:.2f})"
            cv2.putText(img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            detections.append((class_name, float(confidence)))

    session['detections'] = detections  # セッションに全ての検出結果を保存

    return img, [label for label, _ in detections]

@app.route('/length_measurement')
def length_measurement():
    return render_template('length_measurement.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    lineA = data['lineA']
    lineB = data['lineB']
    actual_length_A = float(data['actualLengthA'])

    pixel_length_A = math.sqrt((lineA['x2'] - lineA['x1']) ** 2 + (lineA['y2'] - lineA['y1']) ** 2)
    pixel_length_B = math.sqrt((lineB['x2'] - lineB['x1']) ** 2 + (lineB['y2'] - lineB['y1']) ** 2)

    correction_factor = actual_length_A / pixel_length_A
    actual_length_B = pixel_length_B * correction_factor

    # 小数点以下1桁に丸める
    actual_length_B = round(actual_length_B, 1)

    session['actual_length_B'] = actual_length_B

    return jsonify({"actualLengthB": actual_length_B})

def get_release_length(fish_type, prefecture):
    try:
        with sqlite3.connect('fish_rules.db') as conn:
            cursor = conn.cursor()
            
            # データベースからrelease_lengthを検索
            cursor.execute("""
                SELECT release_length FROM fish_rules 
                WHERE fish_type = ? AND prefecture = ?
            """, (fish_type, prefecture))
            
            result = cursor.fetchone()
            
            return result[0] if result else None
            
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")
        return None

@app.route('/release/', methods=['GET', 'POST'])
def release():
    fish_name = session.get('labels', [""])[0]
    fish_length = session.get('actual_length_B', 0)

    return render_template('release.html', fish_name=fish_name, fish_length=fish_length)

@app.route('/check_release/', methods=['POST'])
def check_release():
    data = request.get_json()
    fish_name = data['fish_name']  # フォームから送信された魚の名前
    fish_length = float(data['fish_length'])  # フォームから送信された魚の長さ
    prefecture = data['prefecture']  # フォームから選択された都道府県

    # データベースからリリース基準の長さを取得
    release_length = get_release_length(fish_name, prefecture)
    
    if release_length is not None:
        if fish_length <= release_length:
            return jsonify({"result": "release_required"})
        else:
            return jsonify({"result": "release_not_required"})
    else:
        return jsonify({"result": "no_data"})

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000)
