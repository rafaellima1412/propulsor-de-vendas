from pydantic import BaseModel


class CampanhaCreateDTO(BaseModel):
    title: str
    paragraph: str
    image: str | None = None
    cpf_usuario: str
    matricula: str
    folder_image: str
    post_type: str | None = None
    url: str | None = None
    folder_url: str | None = None
    qrcode_url: str | None = None
