import os
import base64
import secrets
from io import BytesIO
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash, abort
)
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
import sqlite3

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Iltimos, avval kirish qiling."

DB_NAME = "users.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        if row:
            return User(row[0], row[1])
    return None

API_URL = "https://serverless.roboflow.com"
API_KEY = "RD4PgVC57x7SlRltBqxg"
MODEL_ID = "bhrmi/1"
CLIENT = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Barcha maydonlar to'ldirilishi shart!")
            return redirect(url_for("register"))
        try:
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute(
                    "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                    (username, password, datetime.utcnow().isoformat())
                )
                conn.commit()
            flash("Muvaffaqiyatli roʻyxatdan oʻtdingiz! Endi kirishingiz mumkin.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Bu foydalanuvchi nomi allaqachon mavjud.")
            return redirect(url_for("register"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.execute("SELECT id, username, password FROM users WHERE username=?", (username,))
            row = cur.fetchone()
        if row and row[2] == password:
            user = User(row[0], row[1])
            login_user(user)
            return redirect(url_for("app_page"))
        flash("Noto'g'ri foydalanuvchi nomi yoki parol.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/app")
@login_required
def app_page():
    return render_template("app.html")

@login_required
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Rasm topilmadi'}), 400

        file = request.files['image']

        # Rasmni ochish
        image = Image.open(file.stream).convert('RGB')

        # Vaqtinchalik faylga saqlash
        temp_path = 'temp_image.jpg'
        image.save(temp_path)

        # Roboflow API orqali tahlil
        result = CLIENT.infer(temp_path, model_id=MODEL_ID)
        predictions = result.get("predictions", [])

        # Rasm o'lchamlarini olish
        img_width, img_height = image.size
        img_area = img_width * img_height

        # 50% dan katta bo'lgan bashoratlarni shalab tashlash (filtrlash)
        filtered_predictions = []
        for pred in predictions:
            x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
            bbox_area = w * h
            # Agar bbox maydoni rasim maydonining 50% dan katta bo'lsa, shalab tashla (chizma)
            if bbox_area / img_area > 0.1:
                continue  # Bu predni e'tiborsiz qoldir, chizma va hisobga olma
            filtered_predictions.append(pred)

        # Bounding box chizish (faqat filtrlanganlar uchun, ya'ni 50% dan kichik yoki teng bo'lganlar)
        draw = ImageDraw.Draw(image)

        for pred in filtered_predictions:
            x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
            x1, y1 = x - w / 2, y - h / 2
            x2, y2 = x + w / 2, y + h / 2

            # To'rtburchak chizish
            draw.rectangle([x1, y1, x2, y2], outline="red", width=4)

            # Label qo'shish
            label = f"{pred.get('class', 'tumor')} ({pred.get('confidence', 0) * 100:.1f}%)"
            draw.text((x1 + 5, y1 + 5), label, fill="red")

        # Rasmni base64 ga o'girish
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Vaqtinchalik faylni o'chirish
        os.remove(temp_path)

        # Natijani qaytarish (faqat filtrlanganlar, ya'ni kichikroqlar)
        response_data = {
            'detected': len(filtered_predictions) > 0,
            'count': len(filtered_predictions),
            'predictions': [
                {
                    'class': pred.get('class', 'tumor'),
                    'confidence': round(pred.get('confidence', 0) * 100, 1)
                }
                for pred in filtered_predictions
            ],
            'image': img_str
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧠 NeuroScan AI – Ishga tushmoqda...")
    print("🌐 http://127.0.0.1:5001")
    print("="*60 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5001)