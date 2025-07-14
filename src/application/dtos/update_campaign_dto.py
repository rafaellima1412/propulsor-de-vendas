from typing import Optional

from pydantic import BaseModel


class UpdateCampaignDTO(BaseModel):
    title: str
    paragraph: str
    post_type: Optional[str]
    url: Optional[str]
    folder_url: Optional[str]
    qrcode_url: Optional[str]