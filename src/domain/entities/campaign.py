
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone

class Campaign(BaseModel):
    id: int
    title: str
    paragraph: str
    image: str | None = None
    times: Optional[List[int]] = []
    post_type: Optional[str] = None
    url: Optional[str] = None
    folder_url: Optional[str] = None
    qrcode_url: Optional[str] = None
    is_active: bool = True
    data_criacao: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)
