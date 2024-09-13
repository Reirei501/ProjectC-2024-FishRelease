import sqlite3

def create_db():
    conn = sqlite3.connect('fish_rules.db')
    cursor = conn.cursor()

    # テーブル作成SQL文
    cursor.execute('''
    CREATE TABLE fish_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fish_type TEXT NOT NULL,
        fish_name TEXT NOT NULL,
        prefecture TEXT NOT NULL,
        release_length INTEGER NOT NULL,  -- 修正：カンマ追加
        release_rule TEXT NOT NULL
    )
    ''')

    # データの挿入例
    fish_data = [
        ('takabe', 'タカベ', '東京都', 10, '以下'),
        ('buri', 'ブリ', '東京都', 15, '以下'),
        ('unagi', 'ウナギ', '東京都', 24, '以下'),
        ('unagi', 'ウナギ', '神奈川県', 24, '以下'),
        ('buri', 'ブリ', '神奈川県', 15, '以下'),
        ('hirame', 'ヒラメ', '神奈川県', 35, '以下'),
        ('madai', 'マダイ', '神奈川県', 20, '以下'),
        ('madai', 'マダイ', '千葉県', 20, '以下'),
        ('kinnmedai', 'キンメダイ', '千葉県', 22, '以下'),
        ('hirame', 'ヒラメ', '千葉県', 30, '以下'),
        ('hirame', 'ヒラメ', '茨城県', 30, '未満'),
        ('unagi', 'ウナギ', '茨城県', 23, '以下'),
        ('sake', 'サケ', '茨城県', 15, '以下'),
        ('masu', 'マス', '茨城県', 15, '以下'),
        ('unagi', 'ウナギ', '静岡県', 13, '以下'),
        ('buri', 'ブリ', '静岡県', 15, '以下'),
        ('hirame', 'ヒラメ', '静岡県', 30, '以下'),
        ('madai', 'マダイ', '静岡県', 17, '以下'),
        ('madai', 'マダイ', '福井県', 13, '未満'),
        ('hirame', 'ヒラメ', '福井県', 25, '以下'),
        ('kurodai', 'クロダイ', '愛知県', 15, '以下'),
        ('madai', 'マダイ', '愛知県', 13, '以下'),
        ('torafugu', 'トラフグ', '愛知県', 25, '以下'),
        ('madai', 'マダイ', '新潟県', 14, '未満'),
        ('sirogisu', 'シロギス', '新潟県', 12, '未満'),
        ('hirame', 'ヒラメ', '新潟県', 30, '未満'),
        ('magarei', 'マガレイ', '新潟県', 13, '未満'),
        ('usumebaru', 'ウスメバル', '新潟県', 12, '未満'),
        ('unagi', 'ウナギ', '新潟県', 40, '未満'),
        # 他のデータも追加
    ]
    cursor.executemany('''
    INSERT INTO fish_rules (fish_type, fish_name, prefecture, release_length, release_rule)
    VALUES (?, ?, ?, ?, ?)
    ''', fish_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
