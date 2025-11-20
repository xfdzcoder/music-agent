from pydantic import BaseModel


class PromptParam(BaseModel):
    input: str
