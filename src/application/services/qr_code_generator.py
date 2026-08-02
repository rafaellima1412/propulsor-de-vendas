import os
from urllib.parse import urlparse

import httpx
import qrcode
from PIL import Image

from config.settings import OUTPUT_FOLDER, QR_FOLDER


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


async def _download_image(image_url: str, destination_dir: str, fallback_name: str) -> str:
    """Baixa a imagem informada pelo front (URL) e salva localmente.

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
    """Baixa a imagem (folder_image é uma URL enviada pelo front), cola o QR
    code gerado a partir do cpf/matrícula por cima dela, e salva o resultado.
    """
    qr_path = generate_qr_code(cpf, matricula)

    folder_path = await _download_image(
        folder_image,
        destination_dir=OUTPUT_FOLDER,
        fallback_name=f"folder_{cpf}_{matricula}.png",
    )

    try:
        base_image = Image.open(folder_path).convert("RGB")
    except Exception as exc:
        raise ValueError("O arquivo baixado em folder_image não é uma imagem válida.") from exc

    qr_image = Image.open(qr_path).resize((150, 150))

    position = (base_image.width - qr_image.width - 20, base_image.height - qr_image.height - 20)

    base_image.paste(qr_image, position)

    output_filename = f"folder_final_{cpf}_{matricula}.png"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    base_image.save(output_path)

    return output_filename
