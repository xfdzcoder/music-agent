import asyncio
import uuid
from datetime import datetime

from ag_ui.core import RunAgentInput, EventType, RunStartedEvent, StateSnapshotEvent, StateDeltaEvent, \
    TextMessageStartEvent, TextMessageContentEvent, TextMessageEndEvent, RunFinishedEvent
from ag_ui.encoder import EventEncoder
from langchain_core.messages import HumanMessage
from starlette.responses import StreamingResponse

from chat.llm.graph import get_graph


# @router.post("")
async def langgraph_research_endpoint(input_data: RunAgentInput):
    """
    基于 LangGraph 的研究处理端点。

    该端点实现了一个研究代理，通过 LangGraph 工作流处理用户查询，并使用 AG-UI 协议将实时更新流回前端。
    该实现遵循流式服务器发送事件（SSE）模式，以提供关于研究进度的持续反馈。

    工作流由几个阶段组成：
    1. 研究过程的初始化和状态
    2. 带有可见进度指示器的信息收集
        3. 收集信息的分析与组织
        4. 生成详细的研究报告
        5. 提交最终结果或错误报告

    在这些阶段中，使用 stateDeltaEvent 不断更新前端状态，向用户显示进度，提供响应式体验。

    Args:
        input_data (RunAgentInput): 包含对话线程数据，包括：
            - thread_id: 对话线程的唯一标识符
            - run_id: 此特定代理运行的唯一标识符
            - messages: 对话中先前的消息列表

    返回：
        StreamingResponse: 包含服务器发送事件（Server-Sent Events）的流式 HTTP 响应，用于向前端更新进度和结果
    """

    async def event_generator():
        """
        异步生成器，用于生成 AG-UI 协议事件流。

        该生成器实现了核心研究工作流程逻辑，并在整个过程中将符合协议的事件流传输到前端进行更新。
        它处理：
            - 研究会话的初始化
            - 所有研究阶段的进度报告
            - 实际研究中的 LangGraph 工作流执行
            - 结果处理和错误处理
            - 完成信号

        输出：
            字节：遵循 AG-UI 协议编码的服务器发送事件
        """
        # 创建事件编码器以正确格式化 SSE 事件
        encoder = EventEncoder()

        # 从最新消息中提取研究查询
        query = input_data.messages[-1].content
        message_id = str(uuid.uuid4())

        print(f"[DEBUG] LangGraph Research started with query: {query}")

        # 使用 AG-UI 协议的 RunStartedEvent 通知前端代理已开始处理
        # 这表示代理已开始处理
        yield encoder.encode(
            RunStartedEvent(
                type=EventType.RUN_STARTED,
                thread_id=input_data.thread_id,
                run_id=input_data.run_id
            )
        )

        # 设置初始状态快照（与原始端点相同）
        # 这将建立完整的状态结构，稍后将逐步更新
        # 状态包括以下部分：
        # - 状态：用于跟踪研究过程的整体状态
        # - research: 关于研究操作本身的详细信息
        # - processing: 进度和结果跟踪
        # - ui: 前端 UI 配置
        yield encoder.encode(
            StateSnapshotEvent(
                message_id=message_id,
                snapshot={
                    "status": {
                        "phase": "initialized",  # Current phase of research process
                        "error": None,  # Error tracking, null if no errors
                        "timestamp": datetime.now().isoformat()  # When process started
                    },
                    "research": {
                        "query": query,  # The user's original research question
                        "stage": "not_started",  # Current research stage
                        "sources_found": 0,  # Number of sources discovered
                        "sources": [],  # List of research sources
                        "completed": False  # Whether research is complete
                    },
                    "processing": {
                        "progress": 0,  # Progress from 0.0 to 1.0
                        "report": None,  # Final research report
                        "completed": False,  # Whether processing is complete
                        "inProgress": False  # Whether processing is ongoing
                    },
                    "ui": {
                        "showSources": False,  # Whether to show sources panel
                        "showProgress": True,  # Whether to show progress indicators
                        "activeTab": "chat"  # Which UI tab is currently active
                    }
                }
            )
        )

        # 更新状态以显示研究开始 - 信息收集阶段
        # 这将 UI 过渡到显示研究正在积极收集信息
        # JSON 补丁操作更新状态中的特定部分：
        # - 将状态阶段更改为"gathering_information"
        # - 将研究阶段更新为"搜索中"
        # - 将处理状态设置为进行中
        # - 将初始进度设置为 15%
        yield encoder.encode(
            StateDeltaEvent(
                message_id=message_id,
                delta=[
                    {
                        "op": "replace",
                        "path": "/status/phase",
                        "value": "gathering_information"
                    },
                    {
                        "op": "replace",
                        "path": "/research/stage",
                        "value": "searching"
                    },
                    {
                        "op": "replace",
                        "path": "/processing/inProgress",
                        "value": True
                    },
                    {
                        "op": "replace",
                        "path": "/processing/progress",
                        "value": 0.15
                    }
                ]
            )
        )

        # 模拟信息收集阶段中的增量进度
        # 在生产系统中，这对应于实际搜索进度
        # 我们添加小的进度更新，以向用户提供响应式反馈
        for i in range(2):
            progress = 0.15 + ((i + 1) / 20)  # Increment progress by 5% each iteration
            await asyncio.sleep(0.2)  # Small delay to simulate work and create visual feedback
            yield encoder.encode(
                StateDeltaEvent(
                    message_id=message_id,
                    delta=[
                        {
                            "op": "replace",
                            "path": "/processing/progress",
                            "value": round(progress, 2)
                        }
                    ]
                )
            )
            print(f"[DEBUG] Building LangGraph research graph for query: {query}")

        # 更新状态以指示分析阶段已开始 - 数据组织阶段
        # 这将使 UI 显示初始数据收集已完成
        # 系统现在正在组织和分析收集到的信息
        yield encoder.encode(
            StateDeltaEvent(
                message_id=message_id,
                delta=[
                    # Update phase to analyzing_information
                    {
                        "op": "replace",
                        "path": "/status/phase",
                        "value": "analyzing_information"
                    },
                    # Update stage to organizing_data
                    {
                        "op": "replace",
                        "path": "/research/stage",
                        "value": "organizing_data"
                    },
                    # Update progress to 30%
                    {
                        "op": "replace",
                        "path": "/processing/progress",
                        "value": 0.3
                    }
                ]
            )
        )

        # 在数据组织阶段模拟更多进度更新
        for i in range(2):
            progress = 0.3 + ((i + 1) / 20)
            await asyncio.sleep(0.2)  # Small delay to simulate work
            yield encoder.encode(
                StateDeltaEvent(
                    message_id=message_id,
                    delta=[
                        {
                            "op": "replace",
                            "path": "/processing/progress",
                            "value": round(progress, 2)
                        }
                    ]
                )
            )

        # 更新状态以指示报表生成已开始
        yield encoder.encode(
            StateDeltaEvent(
                message_id=message_id,
                delta=[
                    # Update phase to generating_report
                    {
                        "op": "replace",
                        "path": "/status/phase",
                        "value": "generating_report"
                    },
                    # Update stage to creating_detailed_report
                    {
                        "op": "replace",
                        "path": "/research/stage",
                        "value": "creating_detailed_report"
                    },
                    # Update progress to 40%
                    {
                        "op": "replace",
                        "path": "/processing/progress",
                        "value": 0.4
                    }
                ]
            )
        )

        # 通过详细的报告生成阶段模拟进度
        # 每个阶段代表报告创建过程的不同部分
        report_stages = [
            "outlining_report", "drafting_executive_summary", "writing_introduction",
            "compiling_key_findings", "developing_analysis", "forming_conclusions",
            "finalizing_report"
        ]

        # Calculate progress intervals to show smooth advancement
        start_progress = 0.4
        end_progress = 0.9
        interval = (end_progress - start_progress) / len(report_stages)

        # Update state for each report generation stage
        for i, stage in enumerate(report_stages):
            progress = start_progress + (interval * i)
            await asyncio.sleep(0.3)  # Small delay to simulate work
            yield encoder.encode(
                StateDeltaEvent(
                    message_id=message_id,
                    delta=[
                        # Update to current report generation stage
                        {
                            "op": "replace",
                            "path": "/research/stage",
                            "value": stage
                        },
                        # Update progress accordingly
                        {
                            "op": "replace",
                            "path": "/processing/progress",
                            "value": round(progress, 2)
                        }
                    ]
                )
            )

        try:
            print(f"[DEBUG] Executing LangGraph workflow")
            # Execute the LangGraph workflow with the query
            # Convert the AG-UI message to a LangChain message type
            # Different LangGraph versions have different methods to run graphs
            try:
                # Try newer LangGraph API first
                result = get_graph().invoke([HumanMessage(content=query)])
                print(f"[DEBUG] LangGraph invoke API succeeded")
            except AttributeError as e:
                print(f"[DEBUG] LangGraph invoke API failed, trying older API: {str(e)}")
                # Fall back to older LangGraph API
                result = get_graph()([HumanMessage(content=query)])
                print(f"[DEBUG] LangGraph older API succeeded")

            print(f"[DEBUG] LangGraph result type: {type(result)}, content: {str(result)[:100]}...")

            if isinstance(result, list) and len(result) > 0:
                # Get the report from the AI message content
                print(f"[DEBUG] Result is a list with {len(result)} items")
                report_item = result[0]
                print(f"[DEBUG] First item type: {type(report_item)}")

                if hasattr(report_item, 'content'):
                    report_content = report_item.content
                    print(f"[DEBUG] Report content extracted, length: {len(report_content)}")

                    # Update state to indicate search and analysis is complete
                    yield encoder.encode(
                        StateDeltaEvent(
                            message_id=message_id,
                            delta=[
                                {
                                    "op": "replace",
                                    "path": "/status/phase",
                                    "value": "completed"
                                },
                                {
                                    "op": "replace",
                                    "path": "/research/stage",
                                    "value": "report_complete"
                                },
                                {
                                    "op": "replace",
                                    "path": "/research/completed",
                                    "value": True
                                },
                                {
                                    "op": "replace",
                                    "path": "/processing/completed",
                                    "value": True
                                },
                                {
                                    "op": "replace",
                                    "path": "/processing/inProgress",
                                    "value": False
                                },
                                {
                                    "op": "replace",
                                    "path": "/processing/progress",
                                    "value": 1.0
                                },
                                {
                                    "op": "replace",
                                    "path": "/processing/report",
                                    "value": report_content
                                }
                            ]
                        )
                    )

                    # Send the text message with the report content
                    yield encoder.encode(
                        TextMessageStartEvent(
                            type=EventType.TEXT_MESSAGE_START,
                            message_id=message_id,
                            role="assistant"
                        )
                    )

                    yield encoder.encode(
                        TextMessageContentEvent(
                            type=EventType.TEXT_MESSAGE_CONTENT,
                            message_id=message_id,
                            delta=report_content
                        )
                    )

                    yield encoder.encode(
                        TextMessageEndEvent(
                            type=EventType.TEXT_MESSAGE_END,
                            message_id=message_id
                        )
                    )
                else:
                    print(f"[DEBUG] Result item has no content attribute: {report_item}")
                    error_msg = "Research results format is invalid."
                    yield encoder.encode(
                        StateDeltaEvent(
                            message_id=message_id,
                            delta=[
                                {
                                    "op": "replace",
                                    "path": "/status/phase",
                                    "value": "completed"
                                },
                                {
                                    "op": "replace",
                                    "path": "/status/error",
                                    "value": error_msg
                                },
                                {
                                    "op": "replace",
                                    "path": "/research/stage",
                                    "value": "error"
                                },
                                {
                                    "op": "replace",
                                    "path": "/research/completed",
                                    "value": False
                                },
                                {
                                    "op": "replace",
                                    "path": "/processing/completed",
                                    "value": True
                                },
                                {
                                    "op": "replace",
                                    "path": "/processing/inProgress",
                                    "value": False
                                },
                                {
                                    "op": "replace",
                                    "path": "/processing/progress",
                                    "value": 0
                                }
                            ]
                        )
                    )
            else:
                # Handle case where no result was returned
                print(f"[DEBUG] LangGraph result is not a list or is empty: {result}")
                error_msg = "No research results were generated."
                yield encoder.encode(
                    StateDeltaEvent(
                        message_id=message_id,
                        delta=[
                            {
                                "op": "replace",
                                "path": "/status/phase",
                                "value": "completed"
                            },
                            {
                                "op": "replace",
                                "path": "/status/error",
                                "value": error_msg
                            },
                            {
                                "op": "replace",
                                "path": "/research/stage",
                                "value": "error"
                            },
                            {
                                "op": "replace",
                                "path": "/research/completed",
                                "value": False
                            },
                            {
                                "op": "replace",
                                "path": "/processing/completed",
                                "value": True
                            },
                            {
                                "op": "replace",
                                "path": "/processing/inProgress",
                                "value": False
                            },
                            {
                                "op": "replace",
                                "path": "/processing/progress",
                                "value": 0
                            }
                        ]
                    )
                )
        except Exception as e:
            # Handle errors in the LangGraph workflow
            print(f"[DEBUG] LangGraph workflow exception: {str(e)}")
            error_msg = f"Research process failed: {str(e)}"
            yield encoder.encode(
                StateDeltaEvent(
                    message_id=message_id,
                    delta=[
                        {
                            "op": "replace",
                            "path": "/status/phase",
                            "value": "completed"
                        },
                        {
                            "op": "replace",
                            "path": "/status/error",
                            "value": error_msg
                        },
                        {
                            "op": "replace",
                            "path": "/research/stage",
                            "value": "error"
                        },
                        {
                            "op": "replace",
                            "path": "/research/completed",
                            "value": False
                        },
                        {
                            "op": "replace",
                            "path": "/processing/completed",
                            "value": True
                        },
                        {
                            "op": "replace",
                            "path": "/processing/inProgress",
                            "value": False
                        },
                        {
                            "op": "replace",
                            "path": "/processing/progress",
                            "value": 0
                        }
                    ]
                )
            )

        # Complete the run
        yield encoder.encode(
            RunFinishedEvent(
                type=EventType.RUN_FINISHED,
                thread_id=input_data.thread_id,
                run_id=input_data.run_id
            )
        )

    # Return a streaming response containing SSE events from the generator
    # The event_generator function yields events that are encoded according to the SSE protocol
    # The media_type specifies that this is a stream of server-sent events
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )