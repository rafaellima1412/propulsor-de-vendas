import os

# Pasta de conteúdo gerado/enviado em runtime pela API (crachás, QR codes, uploads).
# Não confundir com assets de frontend: isso é dado da aplicação, servido em /media.
MEDIA_ROOT = "media"
UPLOAD_FOLDER = os.path.join(MEDIA_ROOT, "uploads")
OUTPUT_FOLDER = os.path.join(MEDIA_ROOT, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
