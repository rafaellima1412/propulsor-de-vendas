from pydantic import BaseModel


class UpdateCampaignDTO(BaseModel):
    title: str | None = None
    paragraph: str | None = None
    post_type: str | None = None
    url: str | None = None
    folder_url: str | None = None
    qrcode_url: str | None = None
    folder_image: str | None = None  # se presente, substitui a imagem da campanha
