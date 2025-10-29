#!/usr/bin/env python3
# =======================================================
# 🧠 Brain Tumor Detection using Roboflow Inference API
# Author: Muhammadiyev Bahrombek
# Date: 2025-10-27
# =======================================================

from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import sys

# ================= CONFIGURATION =================
API_URL = "https://serverless.roboflow.com"
API_KEY = "RD4PgVC57x7SlRltBqxg"
MODEL_ID = "bhrmi/1"
OUTPUT_DIR = "detections"
# ==================================================

# Rangli terminal chiqishlari uchun
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    END = "\033[0m"

# Log funksiyasi
def log_info(msg): print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")
def log_success(msg): print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")
def log_warn(msg): print(f"{Colors.YELLOW}[WARNING]{Colors.END} {msg}")
def log_error(msg): print(f"{Colors.RED}[ERROR]{Colors.END} {msg}")

# Roboflow client
CLIENT = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

def detect_tumor(image_path):
    if not os.path.exists(image_path):
        log_error(f"Fayl topilmadi: {image_path}")
        return

    try:
        log_info("Rasm tahlil qilinmoqda...")

        # Model orqali natija olish
        result = CLIENT.infer(image_path, model_id=MODEL_ID)
        predictions = result.get("predictions", [])

        # Rasmni yuklash
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        if not predictions:
            log_warn("🧠 O'simta topilmadi ❌")
            return

        log_success(f"🧠 O'simta aniqlandi! (soni: {len(predictions)})")

        # Har bir obyekt uchun bounding box chizish
        for i, pred in enumerate(predictions, 1):
            x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
            x1, y1 = x - w / 2, y - h / 2
            x2, y2 = x + w / 2, y + h / 2

            label = pred.get("class", "tumor")
            confidence = pred.get("confidence", 0) * 100

            draw.rectangle([x1, y1, x2, y2], outline="red", width=4)
            text = f"{label} ({confidence:.1f}%)"
            draw.text((x1 + 5, y1 + 5), text, fill="red")

            log_info(f"→ Box {i}: {text} [{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]")

        # Natija papkasini yaratish
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Sana-vaqt bilan fayl nomi
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detected_{timestamp}.jpg"
        output_path = os.path.join(OUTPUT_DIR, filename)

        # Saqlash
        image.save(output_path)
        log_success(f"💾 Natija saqlandi: {output_path}")

    except Exception as e:
        log_error(f"Xatolik yuz berdi: {e}")


if __name__ == "__main__":
    print(f"{Colors.BLUE}\n=== 🧠 Brain Tumor Detector v1.0 ==={Colors.END}")

    if len(sys.argv) < 2:
        log_warn("Foydalanish: python brain_tumor_detector.py <rasm_manzili>")
        sys.exit(0)

    image_path = sys.argv[1]
    detect_tumor(image_path)
