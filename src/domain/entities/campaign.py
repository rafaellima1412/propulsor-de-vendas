from pydantic import BaseModel
from datetime import datetime, timezone

class Campaign(BaseModel):
    id: int
    title: str
    paragraph: str
    post_type: str
    url: str
    image: str
    folder_url: str
    qrcode_url: str
    data_criacao: datetime = datetime.now(timezone.utc)
