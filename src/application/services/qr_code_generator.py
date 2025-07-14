import os
from fastapi import UploadFile, File, Form
from PIL import Image
import qrcode
from config.settings import QR_FOLDER,OUTPUT_FOLDER


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

async def generate_folder_with_qr(cpf: str = Form(...), matricula: str = Form(...), folder_image: UploadFile = File(...)):
    qr_path = generate_qr_code(cpf, matricula)

    folder_path = os.path.join(OUTPUT_FOLDER, folder_image.filename)
    with open(folder_path, "wb") as buffer:
        buffer.write(await folder_image.read())

    base_image = Image.open(folder_path).convert("RGB")
    qr_image = Image.open(qr_path).resize((150, 150))

    position = (base_image.width - qr_image.width - 20, base_image.height - qr_image.height - 20)

    base_image.paste(qr_image, position)

    output_filename = f"folder_final_{cpf}_{matricula}.png"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    base_image.save(output_path)

    return output_filename
