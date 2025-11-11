from dotenv import load_dotenv, find_dotenv
from langchain_core.runnables import RunnableConfig


if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass

    from langchain_core.output_parsers import JsonOutputParser

    from chat.node.remember import ShouldRememberResult
    from core.llm.llm import deepseek
    from core.logger.logger import logger
    from core.langfuse.langfuse_manager import langfuse_handler

    msg = [
        ("system", """
                    <requirement>你需要鉴别用户的输入是否包含重要信息应当被记录。包括但不限于：用户个人信息、喜恶、工作领域。</requirement>
            
                    <output-style>
                    你的回答必须严格遵循 JSON 模式，示例输出：
                    {"should_remember": true}
                    </output-style>
        """),
        ("user", "我的名字是 Tom")
    ]

    structured_llm = deepseek.with_structured_output(ShouldRememberResult, method="json_mode")
    for chunk in structured_llm.stream(msg, config=RunnableConfig(callbacks=[langfuse_handler])):
        logger.info(chunk)

    logger.info("=====================")
    chat_chain = deepseek | JsonOutputParser()
    result = None
    for chunk in chat_chain.stream(msg):
        result = chunk
        logger.info(f"should_remember: {result}")
    logger.info(f"end should_remember: {result}")
