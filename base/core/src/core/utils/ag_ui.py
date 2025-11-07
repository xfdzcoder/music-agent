from ag_ui.core import RunAgentInput, RunStartedEvent, BaseEvent
from ag_ui.encoder import EventEncoder

_encoder = EventEncoder()

def run_start(agent_input: RunAgentInput) -> str:
    return _encoder.encode(
        RunStartedEvent(
            thread_id=agent_input.thread_id,
            run_id=agent_input.run_id
        )
    )


def base(event: BaseEvent):
    return _encoder.encode(event)