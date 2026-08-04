import os
from urllib.parse import urlparse

import httpx
import qrcode
from PIL import Image

from config.settings import BASE_DIR, MEDIA_ROOT, OUTPUT_FOLDER, QR_FOLDER


def generate_qr_code(cpf: str, matricula: str) -> str:
    data = f"CPF: {cpf} | Matrícula: {matricula}"
    filename = f"qr_{cpf.replace('.', '').replace('-', '')}_{matricula}.png"
    file_path = os.path.join(QR_FOLDER, filename)

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)

    return file_path


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


async def _download_image(image_url: str, destination_dir: str, fallback_name: str) -> str:
    """Baixa a imagem informada pelo front (URL externa) e salva localmente.

    Retorna o caminho do arquivo salvo em disco.
    """
    filename = os.path.basename(urlparse(image_url).path) or fallback_name

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(image_url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ValueError(f"Não foi possível baixar a imagem informada em folder_image: {exc}") from exc

    destination_path = os.path.join(destination_dir, filename)
    with open(destination_path, "wb") as buffer:
        buffer.write(response.content)

    return destination_path


async def generate_folder_with_qr(cpf: str, matricula: str, folder_image: str) -> str:
    """Resolve a imagem base (folder_image), cola o QR code gerado a partir
    do cpf/matrícula por cima dela, e salva o resultado.

    `folder_image` pode ser:
    - um caminho local já servido pelo backend (ex: "/media/uploads/x.png",
      devolvido por POST /campanhas/upload-imagem) — lido direto do disco;
    - uma URL externa de verdade — baixada via HTTP (fluxo antigo, mantido
      por compatibilidade).
    """
    qr_path = generate_qr_code(cpf, matricula)

    folder_path = resolve_local_media_path(folder_image)
    if folder_path is None:
        folder_path = await _download_image(
            folder_image,
            destination_dir=OUTPUT_FOLDER,
            fallback_name=f"folder_{cpf}_{matricula}.png",
        )

    try:
        base_image = Image.open(folder_path).convert("RGB")
    except Exception as exc:
        raise ValueError("O arquivo em folder_image não é uma imagem válida.") from exc

    qr_image = Image.open(qr_path).resize((150, 150))

    position = (base_image.width - qr_image.width - 20, base_image.height - qr_image.height - 20)

    base_image.paste(qr_image, position)

    output_filename = f"folder_final_{cpf}_{matricula}.png"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    base_image.save(output_path)

    return output_filename