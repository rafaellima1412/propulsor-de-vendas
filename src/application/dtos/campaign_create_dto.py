from pydantic import BaseModel


class CampanhaCreateDTO(BaseModel):
    title: str
    paragraph: str
    image: str | None = None
    cpf_usuario: str | None = None
    matricula: str | None = None
    folder_image: str
    local_id: int | None = None
    post_type: str | None = None
    url: str | None = None
    folder_url: str | None = None
    qrcode_url: str | None = None
