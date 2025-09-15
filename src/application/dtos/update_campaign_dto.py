from typing import Optional, List

from pydantic import BaseModel


class UpdateCampaignDTO(BaseModel):
    title: Optional[str]
    paragraph: Optional[str]
    time_ids: List[int]
    post_type: Optional[str]
    url: Optional[str]
    folder_url: Optional[str]
    qrcode_url: Optional[str]