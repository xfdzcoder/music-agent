import asyncio
import uuid

from dotenv import find_dotenv, load_dotenv
from langchain_core.runnables import RunnableConfig

from chat.llm.graph import init_graph, get_graph
from chat.service.music import load_local_music
from core.context.context import ContextHolder, Context
from core.llm.langfuse.langfuse_manager import langfuse_handler

from core.db.postgres import init_db
from core.llm.memory.postgres import init_memory


async def main():
    init_db()
    init_memory()
    init_graph()
    load_local_music()
    ContextHolder.set(Context(user_id="temp", request_id="11"))

    for event in get_graph().stream(
            input={
                "messages": [
                    {
                        "role": "user",
                        "content": "帮我搜索《于是》这首歌的信息"
                    }
                ],
            },
            context=ContextHolder.get(),
            config=RunnableConfig(
                callbacks=[langfuse_handler],
                configurable={
                    "thread_id": str(uuid.uuid4()),
                    "user_id": "temp"
                }
            ),
            stream_mode=["custom", "values", "debug"]
    ):
        if not isinstance(event, tuple):
            continue
        event_type = event[0]
        event_content = event[1]
        if event_type == "custom":
            print(event_content)





if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass

    asyncio.run(main())
