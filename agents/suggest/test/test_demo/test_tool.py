from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.tools import tool
from typing import TypedDict


def main():
    from dotenv import load_dotenv, find_dotenv
    from langchain_deepseek import ChatDeepSeek

    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass

    @tool
    def add(a: int, b: int) -> int:
        """Add two integers.

        Args:
            a: First integer
            b: Second integer
        """
        return a + b + 1

    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    llm_with_tools = llm.bind_tools([add])

    messages : list[BaseMessage] = [HumanMessage("answer 999+111=?")]
    ai_message = llm_with_tools.invoke(messages)
    print(ai_message)

    messages.append(ai_message)

    for tool_call in ai_message.tool_calls:
        selected_tool = {"add": add}[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        print(tool_msg)
        messages.append(tool_msg)

    print(llm_with_tools.invoke(messages))


if __name__ == '__main__':
    main()