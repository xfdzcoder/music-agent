import asyncio
import uuid


from ag_ui.core import RunStartedEvent, EventType, RunAgentInput, TextMessageStartEvent, TextMessageContentEvent, \
    TextMessageEndEvent, RunFinishedEvent, UserMessage
from ag_ui.encoder import EventEncoder
from dotenv import find_dotenv, load_dotenv
from langchain_deepseek import ChatDeepSeek


async def event_generator(input_data: RunAgentInput):  # 定义异步生成器函数，用于生成事件流
    # Create an event encoder to properly format SSE events
    encoder = EventEncoder()  # 创建事件编码器实例，用于正确格式化SSE事件

    # Send run started event
    yield encoder.encode(  # 生成并编码运行开始事件
        RunStartedEvent(  # 创建运行开始事件对象
            type=EventType.RUN_STARTED,  # 设置事件类型为运行开始
            thread_id=input_data.thread_id,  # 使用输入数据中的线程ID
            run_id=input_data.run_id  # 使用输入数据中的运行ID
        )
    )

    deepseek = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # Generate a message ID for the assistant's response
    message_id = str(uuid.uuid4())  # 生成一个UUID作为消息ID，确保每条消息都有唯一标识

    # Send text message start event
    yield encoder.encode(  # 生成并编码文本消息开始事件
        TextMessageStartEvent(  # 创建文本消息开始事件对象
            type=EventType.TEXT_MESSAGE_START,  # 设置事件类型为文本消息开始
            message_id=message_id,  # 设置消息ID
            role="assistant"  # 设置角色为助手，表示这是AI助手的回复
        )
    )

    # Process the streaming response and send content events
    with deepseek.client.stream(model="deepseek-chat",
        messages=[{"role": "user", "content": input_data.messages[-1].content}]) as stream:
        for event in stream:  # 遍历流式响应中的每个数据块
            if event.type != "chunk":
                continue
            chunk = event.chunk
            if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:  # 检查数据块是否包含内容
                content = chunk.choices[0].delta.content  # 获取数据块中的内容
                yield encoder.encode(  # 生成并编码文本消息内容事件
                    TextMessageContentEvent(  # 创建文本消息内容事件对象
                        type=EventType.TEXT_MESSAGE_CONTENT,  # 设置事件类型为文本消息内容
                        message_id=message_id,  # 设置消息ID，与开始事件相同
                        delta=content  # 设置增量内容，即当前数据块的文本
                    )
                )

        # Send text message end event
        yield encoder.encode(  # 生成并编码文本消息结束事件
            TextMessageEndEvent(  # 创建文本消息结束事件对象
                type=EventType.TEXT_MESSAGE_END,  # 设置事件类型为文本消息结束
                message_id=message_id  # 设置消息ID，与开始事件相同
            )
        )

        # Send run finished event
        yield encoder.encode(  # 生成并编码运行结束事件
            RunFinishedEvent(  # 创建运行结束事件对象
                type=EventType.RUN_FINISHED,  # 设置事件类型为运行结束
                thread_id=input_data.thread_id,  # 使用输入数据中的线程ID
                run_id=input_data.run_id  # 使用输入数据中的运行ID
            )
        )


async def run_agent(input_data: RunAgentInput):
    async for event in event_generator(input_data):
        print(event)

if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass

    input_data = RunAgentInput(
        thread_id="111",
        run_id="222",
        messages=[
            UserMessage(content="hello", id="111")
        ],
        state=None,
        tools=[],
        context=[],
        forwarded_props=[]
    )
    asyncio.run(run_agent(input_data))