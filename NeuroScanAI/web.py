#!/usr/bin/env python3
# =======================================================
# 🧠 Brain Tumor Detection Web Application
# Author: Muhammadiyev Bahrombek
# Date: 2025-10-27
# =======================================================

from flask import Flask, render_template_string, request, jsonify
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import os

app = Flask(__name__)

# ================= CONFIGURATION =================
API_URL = "https://serverless.roboflow.com"
API_KEY = "RD4PgVC57x7SlRltBqxg"
MODEL_ID = "bhrmi/1"
# ==================================================

CLIENT = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 NeuroScan AI - Brain Tumor Detector</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #581c87 50%, #0f172a 100%);
            min-height: 100vh;
            color: white;
            overflow-x: hidden;
        }

        .animated-bg {
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            z-index: 0;
            overflow: hidden;
        }

        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.3;
            animation: float 8s ease-in-out infinite;
        }

        .orb1 {
            width: 300px;
            height: 300px;
            background: #8b5cf6;
            top: 10%;
            left: 5%;
        }

        .orb2 {
            width: 400px;
            height: 400px;
            background: #06b6d4;
            top: 30%;
            right: 5%;
            animation-delay: 2s;
        }

        .orb3 {
            width: 350px;
            height: 350px;
            background: #ec4899;
            bottom: 10%;
            left: 30%;
            animation-delay: 4s;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(30px, 30px); }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 1;
        }

        .header {
            text-align: center;
            margin-bottom: 60px;
        }

        .logo-container {
            display: inline-flex;
            align-items: center;
            gap: 15px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            padding: 3px;
            border-radius: 50px;
            margin-bottom: 20px;
        }

        .logo-inner {
            background: #0f172a;
            padding: 15px 40px;
            border-radius: 50px;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .logo-icon {
            font-size: 48px;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        h1 {
            font-size: 48px;
            font-weight: 900;
            background: linear-gradient(135deg, #06b6d4, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            color: #cbd5e1;
            font-size: 20px;
            margin-top: 15px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #06b6d4;
            font-size: 14px;
            margin-top: 15px;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 50px;
        }

        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            padding: 40px;
            transition: all 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(139, 92, 246, 0.3);
        }

        .card-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-subtitle {
            color: #94a3b8;
            font-size: 14px;
            margin-bottom: 25px;
        }

        .upload-area {
            border: 3px dashed rgba(139, 92, 246, 0.5);
            border-radius: 20px;
            padding: 60px 20px;
            text-align: center;
            cursor: pointer;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(6, 182, 212, 0.1));
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .upload-area:hover {
            border-color: rgba(139, 92, 246, 0.8);
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(6, 182, 212, 0.2));
        }

        .upload-area::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.2), transparent);
            transform: translateX(-100%);
            transition: transform 0.6s;
        }

        .upload-area:hover::before {
            transform: translateX(100%);
        }

        .upload-icon {
            font-size: 64px;
            background: linear-gradient(135deg, #8b5cf6, #06b6d4);
            padding: 25px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }

        .upload-area:hover .upload-icon {
            transform: scale(1.1) rotate(5deg);
        }

        #imageInput {
            display: none;
        }

        .preview-container {
            text-align: center;
        }

        #imagePreview {
            max-width: 100%;
            max-height: 400px;
            border-radius: 15px;
            border: 2px solid rgba(139, 92, 246, 0.3);
            margin: 20px 0;
        }

        .btn {
            width: 100%;
            padding: 18px;
            border: none;
            border-radius: 15px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .btn-primary {
            background: linear-gradient(135deg, #8b5cf6, #ec4899, #06b6d4);
            color: white;
            margin-top: 20px;
        }

        .btn-primary:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(139, 92, 246, 0.5);
        }

        .btn-primary::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #06b6d4, #8b5cf6, #ec4899);
            transition: left 0.3s;
        }

        .btn-primary:hover::before {
            left: 0;
        }

        .btn-primary span {
            position: relative;
            z-index: 1;
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .loading {
            text-align: center;
            padding: 60px 20px;
        }

        .spinner {
            width: 80px;
            height: 80px;
            border: 4px solid rgba(139, 92, 246, 0.3);
            border-top-color: #8b5cf6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 30px;
            position: relative;
        }

        .spinner::after {
            content: '🧠';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 32px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .dots {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }

        .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #06b6d4;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .dot:nth-child(2) {
            background: #8b5cf6;
            animation-delay: 0.2s;
        }

        .dot:nth-child(3) {
            background: #ec4899;
            animation-delay: 0.4s;
        }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        .result-box {
            border-radius: 20px;
            padding: 30px;
            margin-top: 20px;
            backdrop-filter: blur(20px);
        }

        .result-detected {
            background: rgba(239, 68, 68, 0.2);
            border: 2px solid rgba(239, 68, 68, 0.5);
            animation: pulse-red 2s ease-in-out infinite;
        }

        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            50% { box-shadow: 0 0 30px 10px rgba(239, 68, 68, 0); }
        }

        .result-clean {
            background: rgba(34, 197, 94, 0.2);
            border: 2px solid rgba(34, 197, 94, 0.5);
        }

        .result-icon {
            font-size: 48px;
            padding: 20px;
            border-radius: 15px;
            display: inline-block;
            margin-bottom: 20px;
        }

        .icon-detected {
            background: #ef4444;
        }

        .icon-clean {
            background: #22c55e;
        }

        .result-title {
            font-size: 32px;
            font-weight: 900;
            margin-bottom: 20px;
        }

        .prediction-item {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            margin-top: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .confidence-bar {
            background: rgba(239, 68, 68, 0.3);
            height: 10px;
            border-radius: 10px;
            margin-top: 10px;
            overflow: hidden;
        }

        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #ef4444, #dc2626);
            border-radius: 10px;
            transition: width 1s ease;
        }

        .info-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
            margin-top: 40px;
        }

        .info-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .info-card:hover {
            transform: translateY(-10px);
            border-color: rgba(139, 92, 246, 0.5);
        }

        .info-icon {
            font-size: 48px;
            padding: 20px;
            border-radius: 15px;
            display: inline-block;
            margin-bottom: 15px;
            transition: transform 0.3s ease;
        }

        .info-card:hover .info-icon {
            transform: scale(1.1) rotate(5deg);
        }

        .icon-cyan {
            background: linear-gradient(135deg, #06b6d4, #8b5cf6);
        }

        .icon-purple {
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
        }

        .icon-pink {
            background: linear-gradient(135deg, #ec4899, #06b6d4);
        }

        @media (max-width: 768px) {
            .main-grid, .info-cards {
                grid-template-columns: 1fr;
            }
            h1 {
                font-size: 32px;
            }
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="animated-bg">
        <div class="orb orb1"></div>
        <div class="orb orb2"></div>
        <div class="orb orb3"></div>
    </div>

    <div class="container">
        <div class="header">
            <div class="logo-container">
                <div class="logo-inner">
                    <div class="logo-icon">🧠</div>
                    <h1>NeuroScan AI</h1>
                    <div style="font-size: 32px;">✨</div>
                </div>
            </div>
            <p class="subtitle">Sun'iy intellekt yordamida miya o'simtalarini aniqlash platformasi</p>
            <div class="badge">
                <span style="font-size: 20px;">📊</span>
                <span>AI-Powered Medical Imaging</span>
            </div>
        </div>

        <div class="main-grid">
            <!-- Upload Section -->
            <div class="card">
                <div class="card-title">
                    <span style="font-size: 24px;">📤</span>
                    Rasm yuklash
                </div>
                <div class="card-subtitle">MRI yoki CT skan yuklang</div>

                <div class="upload-area" onclick="document.getElementById('imageInput').click()">
                    <div class="upload-icon">📤</div>
                    <h3 style="margin-bottom: 10px;">Faylni tanlang</h3>
                    <p style="color: #94a3b8;">PNG, JPG, JPEG (MAX. 10MB)</p>
                    <input type="file" id="imageInput" accept="image/*">
                </div>

                <button id="analyzeBtn" class="btn btn-primary hidden" onclick="analyzeImage()">
                    <span>🧠 AI Tahlil Boshlash ✨</span>
                </button>
            </div>

            <!-- Preview/Results Section -->
            <div class="card">
                <div id="emptyState">
                    <div style="text-align: center; padding: 80px 20px;">
                        <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(6, 182, 212, 0.2)); padding: 40px; border-radius: 50%; display: inline-block; margin-bottom: 20px;">
                            <div style="font-size: 64px;">🧠</div>
                        </div>
                        <p style="color: #94a3b8; font-size: 18px;">Tahlil natijalari bu yerda ko'rsatiladi</p>
                    </div>
                </div>

                <div id="previewState" class="hidden">
                    <div class="card-title">
                        <span style="font-size: 24px;">✨</span>
                        Yuklangan rasm
                    </div>
                    <div class="preview-container">
                        <img id="imagePreview" alt="Preview">
                    </div>
                </div>

                <div id="loadingState" class="hidden">
                    <div class="loading">
                        <div class="spinner"></div>
                        <h2 style="font-size: 24px; margin-bottom: 10px;">AI Tahlil Jarayoni</h2>
                        <p style="color: #94a3b8;">Rasm qayta ishlanmoqda...</p>
                        <div class="dots">
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                        </div>
                    </div>
                </div>

                <div id="resultState" class="hidden"></div>
            </div>
        </div>

        <!-- Info Cards -->
        <div class="info-cards">
            <div class="info-card">
                <div class="info-icon icon-cyan">🧠</div>
                <h3 style="margin-bottom: 10px;">AI Technology</h3>
                <p style="color: #94a3b8; font-size: 14px;">Zamonaviy sun'iy intellekt algoritmlari asosida ishlaydigan tizim</p>
            </div>
            <div class="info-card">
                <div class="info-icon icon-purple">⚡</div>
                <h3 style="margin-bottom: 10px;">Tezkor tahlil</h3>
                <p style="color: #94a3b8; font-size: 14px;">Bir necha soniyada natija olish imkoniyati</p>
            </div>
            <div class="info-card">
                <div class="info-icon icon-pink">✨</div>
                <h3 style="margin-bottom: 10px;">Yuqori aniqlik</h3>
                <p style="color: #94a3b8; font-size: 14px;">Ilg'or neural network modellari yordamida aniqlash</p>
            </div>
        </div>
    </div>

    <script>
        const imageInput = document.getElementById('imageInput');
        const imagePreview = document.getElementById('imagePreview');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const emptyState = document.getElementById('emptyState');
        const previewState = document.getElementById('previewState');
        const loadingState = document.getElementById('loadingState');
        const resultState = document.getElementById('resultState');

        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    emptyState.classList.add('hidden');
                    previewState.classList.remove('hidden');
                    loadingState.classList.add('hidden');
                    resultState.classList.add('hidden');
                    analyzeBtn.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        });

        async function analyzeImage() {
            const file = imageInput.files[0];
            if (!file) return;

            emptyState.classList.add('hidden');
            previewState.classList.add('hidden');
            loadingState.classList.remove('hidden');
            resultState.classList.add('hidden');
            analyzeBtn.classList.add('hidden');

            const formData = new FormData();
            formData.append('image', file);

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                loadingState.classList.add('hidden');
                resultState.classList.remove('hidden');

                if (data.detected) {
                    let predictionsHTML = '';
                    data.predictions.forEach((pred, idx) => {
                        predictionsHTML += `
                            <div class="prediction-item">
                                <p style="font-weight: bold; margin-bottom: 10px;">
                                    <span style="color: #fca5a5;">O'simta #${idx + 1}:</span> ${pred.class || 'tumor'}
                                </p>
                                <p style="color: #fca5a5; margin-bottom: 10px;">
                                    Ishonch darajasi: <span style="font-weight: bold; font-size: 18px;">${pred.confidence}%</span>
                                </p>
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${pred.confidence}%"></div>
                                </div>
                            </div>
                        `;
                    });

                    resultState.innerHTML = `
                        <div class="card-title">
                            <span style="font-size: 24px;">📊</span>
                            Tahlil natijasi
                        </div>
                        <div class="preview-container">
                            <img src="data:image/jpeg;base64,${data.image}" style="max-width: 100%; max-height: 300px; border-radius: 15px; border: 2px solid rgba(6, 182, 212, 0.5); margin: 20px 0;">
                        </div>
                        <div class="result-box result-detected">
                            <div class="result-icon icon-detected">❌</div>
                            <div class="result-title" style="color: #fca5a5;">⚠️ O'simta aniqlandi!</div>
                            <div style="background: rgba(239, 68, 68, 0.3); padding: 15px; border-radius: 10px; margin: 20px 0;">
                                <p style="font-size: 20px;">Soni: <span style="font-weight: 900; font-size: 28px;">${data.count}</span></p>
                            </div>
                            ${predictionsHTML}
                            <div style="background: rgba(239, 68, 68, 0.3); padding: 15px; border-radius: 10px; margin-top: 20px;">
                                <p style="font-size: 14px;">⚕️ Zudlik bilan tibbiy mutaxassis bilan maslahatlashing</p>
                            </div>
                        </div>
                        <button class="btn btn-secondary" onclick="resetForm()" style="margin-top: 20px;">Yangi tahlil boshlash</button>
                    `;
                } else {
                    resultState.innerHTML = `
                        <div class="card-title">
                            <span style="font-size: 24px;">📊</span>
                            Tahlil natijasi
                        </div>
                        <div class="preview-container">
                            <img src="data:image/jpeg;base64,${data.image}" style="max-width: 100%; max-height: 300px; border-radius: 15px; border: 2px solid rgba(6, 182, 212, 0.5); margin: 20px 0;">
                        </div>
                        <div class="result-box result-clean">
                            <div class="result-icon icon-clean">✅</div>
                            <div class="result-title" style="color: #86efac;">✅ O'simta aniqlanmadi</div>
                            <p style="font-size: 18px; margin: 20px 0; color: #d1fae5;">
                                AI tahlil natijasiga ko'ra, rasmda o'simta belgisi topilmadi.
                            </p>
                            <div style="background: rgba(34, 197, 94, 0.3); padding: 15px; border-radius: 10px;">
                                <p style="font-size: 14px; color: #d1fae5;">
                                    ℹ️ Bu natija dastlabki tekshiruv. Aniq tashxis uchun shifokor bilan maslahatlashing.
                                </p>
                            </div>
                        </div>
                        <button class="btn btn-secondary" onclick="resetForm()" style="margin-top: 20px;">Yangi tahlil boshlash</button>
                    `;
                }
            } catch (error) {
                loadingState.classList.add('hidden');
                resultState.classList.remove('hidden');
                resultState.innerHTML = `
                    <div style="background: rgba(239, 68, 68, 0.2); border: 2px solid rgba(239, 68, 68, 0.5); border-radius: 20px; padding: 30px;">
                        <div style="font-size: 48px; margin-bottom: 20px;">⚠️</div>
                        <h3 style="color: #fca5a5; font-size: 24px; margin-bottom: 10px;">Xatolik yuz berdi</h3>
                        <p style="color: #fca5a5;">${error.message}</p>
                    </div>
                    <button class="btn btn-secondary" onclick="resetForm()" style="margin-top: 20px;">Qayta urinish</button>
                `;
            }
        }

        function resetForm() {
            imageInput.value = '';
            emptyState.classList.remove('hidden');
            previewState.classList.add('hidden');
            loadingState.classList.add('hidden');
            resultState.classList.add('hidden');
            analyzeBtn.classList.add('hidden');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

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
        
        # Bounding box chizish
        draw = ImageDraw.Draw(image)
        
        for pred in predictions:
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
        
        # Natijani qaytarish
        response_data = {
            'detected': len(predictions) > 0,
            'count': len(predictions),
            'predictions': [
                {
                    'class': pred.get('class', 'tumor'),
                    'confidence': round(pred.get('confidence', 0) * 100, 1)
                }
                for pred in predictions
            ],
            'image': img_str
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧠 NeuroScan AI - Brain Tumor Detection Web App")
    print("="*60)
    print("\n📊 Server ishga tushmoqda...")
    print("🌐 Brauzerda oching: http://127.0.0.1:5000")
    print("⚡ Ctrl+C bosib to'xtatish mumkin")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)