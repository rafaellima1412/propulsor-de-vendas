import os

UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/outputs"
QR_FOLDER = "static/qrcodes"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
print(BASE_DIR)
