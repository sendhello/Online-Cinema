from pydantic import BaseModel, Field


class Index(BaseModel):
    index: str = Field(alias='_index')
    id: str = Field(alias='_id')
    source: dict = Field(alias='_source')
