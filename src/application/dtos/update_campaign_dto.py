from pydantic import BaseModel


class UpdateCampaignDTO(BaseModel):
    title: str | None = None
    paragraph: str | None = None
    time_ids: list[int]
    post_type: str | None = None
    url: str | None = None
    folder_url: str | None = None
    qrcode_url: str | None = None
    folder_image: str | None = None  
    # URL enviada pelo front; se presente, 
    # substitui a imagem atual 
    # (sem QR — isso só acontece no compartilhamento)