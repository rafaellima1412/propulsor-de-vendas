from pydantic import BaseModel


class UpdateCampaignDTO(BaseModel):
    title: str | None
    paragraph: str | None
    time_ids: list[int]
    post_type: str | None
    url: str | None
    folder_url: str | None
    qrcode_url: str | None
