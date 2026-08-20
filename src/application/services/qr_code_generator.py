import os
from urllib.parse import urlparse

import qrcode
from PIL import Image

from config.settings import BASE_DIR, MEDIA_ROOT


def build_qr_image(data: str, size: int) -> Image.Image:
    """Gera um QR code em memória (sem salvar em disco) com o texto
    informado, já redimensionado pro tamanho pedido em pixels (quadrado)."""
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").get_image().convert("RGB")
    return img.resize((size, size), Image.Resampling.NEAREST)


def resolve_local_media_path(folder_image: str) -> str | None:
    """Se `folder_image` for um caminho servido pelo próprio backend em
    /media (ex: resultado de POST /campanhas/upload-imagem), resolve pro
    caminho real em disco. Retorna None se não for um caminho local — nesse
    caso o chamador deve baixar via HTTP normalmente."""
    parsed = urlparse(folder_image)
    if parsed.netloc:
        # É uma URL absoluta (http://... ou https://...); só tratamos como
        # "local" se apontar pro próprio host de mídia — por simplicidade e
        # segurança, exigimos caminho relativo (ex: "/media/uploads/x.png").
        return None

    if not parsed.path.startswith("/media/"):
        return None

    relative_path = parsed.path.removeprefix("/media/")
    local_path = os.path.join(BASE_DIR, MEDIA_ROOT, relative_path)

    # Evita path traversal (ex: folder_image="/media/../../etc/passwd").
    media_root_abs = os.path.abspath(os.path.join(BASE_DIR, MEDIA_ROOT))
    local_path_abs = os.path.abspath(local_path)
    if not local_path_abs.startswith(media_root_abs + os.sep):
        return None

    return local_path_abs if os.path.isfile(local_path_abs) else None
