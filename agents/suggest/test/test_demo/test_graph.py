def main():
    from dotenv import find_dotenv
    from dotenv import load_dotenv

    try:
        load_dotenv(find_dotenv(".env.test"))
    except ImportError:
        pass

    from llm.graph import graph
    from model.model import MusicInfoList
    from base.core.src.graph import SuggestState
    from model.model import MusicInfo
    from base.core.src.langfuse_manager import langfuse_handler
    from langchain_core.runnables import RunnableConfig

    state = SuggestState(messages=[], input_music_list=MusicInfoList(root=[MusicInfo(name="任我行", author="陈奕迅")]))
    final_state = graph.invoke(state, config=RunnableConfig(callbacks=[langfuse_handler]),)
    print(final_state)
    print(f"最终推荐歌曲：{final_state.get('output_music_list')}")
    print(f"最终推荐歌曲数量：{len(final_state.get('output_music_list').root)}")


if __name__ == '__main__':
    main()