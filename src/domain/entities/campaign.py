from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class Campaign(BaseModel):
    id: int
    title: str
    paragraph: str
    image: str | None = None
    usuario_id: int | None = None
    times: list[int] | None = []
    post_type: str | None = None
    url: str | None = None
    folder_url: str | None = None
    qrcode_url: str | None = None
    is_active: bool = True
    data_criacao: datetime | None = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(from_attributes=True)
