import os

from PIL import Image

from config.settings import OUTPUT_FOLDER

# Cada formato é (largura, altura) do recorte final. O recorte é sempre um
# "center crop" — pega o maior retângulo possível nessa proporção, centrado
# na imagem original, depois redimensiona pro tamanho alvo. Assim o QR code
# (colado no canto inferior direito na geração original) nunca fica cortado
# fora, já que ele fica perto do centro vertical/horizontal na maioria dos
# recortes plausíveis.
SOCIAL_FORMATS: dict[str, tuple[int, int]] = {
    "feed": (1080, 1080),  # Instagram/Facebook feed, quadrado
    "stories": (1080, 1920),  # Instagram/Facebook Stories, WhatsApp status
    "post": (1200, 630),  # Link preview / post horizontal (Facebook, LinkedIn)
}


class SocialVariantError(ValueError):
    pass


def _center_crop(image: Image.Image, target_ratio: float) -> Image.Image:
    width, height = image.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        # imagem mais "larga" que o alvo — corta as laterais
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        return image.crop((left, 0, left + new_width, height))
    else:
        # imagem mais "alta" que o alvo — corta topo/base
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        return image.crop((0, top, width, top + new_height))


def generate_social_variant(image_path: str, formato: str) -> str:
    """Gera (ou reaproveita, se já existir) um recorte da imagem final da
    campanha no formato pedido. Retorna o caminho do arquivo em disco."""
    if formato not in SOCIAL_FORMATS:
        raise SocialVariantError(f"Formato '{formato}' não suportado. Use um de: {', '.join(SOCIAL_FORMATS)}.")

    if not os.path.isfile(image_path):
        raise SocialVariantError("Imagem original da campanha não foi encontrada.")

    target_width, target_height = SOCIAL_FORMATS[formato]

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{base_name}_{formato}.png"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    if os.path.isfile(output_path):
        return output_path

    with Image.open(image_path) as img:
        cropped = _center_crop(img.convert("RGB"), target_width / target_height)
        resized = cropped.resize((target_width, target_height))
        resized.save(output_path)

    return output_path