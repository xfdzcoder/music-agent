from pydantic import BaseModel


class PromptParam(BaseModel):
    pass


class ChatParam(PromptParam):
    input: str


class CurrentTitleParam(PromptParam):
    current_title: str
