from typing import Optional

from dotenv import load_dotenv, find_dotenv
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field, RootModel

try:
    load_dotenv(find_dotenv(".env.dev"))
except ImportError:
    pass


class MusicInfo(BaseModel):
    author: str = Field(description="这首歌的作者")
    title: str = Field(description="这首歌的名字")
    style: Optional[list[str]] = Field(description="这首歌的风格")

class MusicInfoList(RootModel[list[MusicInfo]]):
    root: list[MusicInfo] = Field(description="音乐信息列表")


llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
).with_structured_output(
    MusicInfoList,
    method="json_mode"
)

messages = [
    (
        "system",
        """
            你现在是一个音乐伴侣，你要陪伴用户听歌，帮助用户找歌，帮助用户管理歌单.
            **你的回答需要始终严格的使用JSON**
        """,
    ),
    (
        "human",
        """
            我最近喜欢听庄心妍的《以后的以后》，帮我推荐2首类似风格的歌。
                    
                    
            EXAMPLE JSON OUTPUT:
            [
                {
                    "author": "",
                    "title": "",
                    "style": []
                }
            ]
        """
    ),
]
ai_msg = llm.invoke(messages)
print(ai_msg)

