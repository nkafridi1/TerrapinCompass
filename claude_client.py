import os
from typing import Generator
from demo_responses import stream_demo_response


DEMO_MODE = not bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


class ClaudeClient:
    MODEL = "claude-sonnet-4-6"

    def __init__(self):
        if not DEMO_MODE:
            import anthropic
            self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        else:
            self._client = None

    def _build_system(self, system_text: str) -> list[dict]:
        return [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]

    def stream_chat(
        self,
        messages: list[dict],
        system: str,
        max_tokens: int = 1500,
        mode: str = "navigator",
    ) -> Generator[str, None, None]:
        if DEMO_MODE:
            last_user = next(
                (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
            )
            yield from stream_demo_response(mode, last_user)
            return

        with self._client.messages.stream(
            model=self.MODEL,
            max_tokens=max_tokens,
            system=self._build_system(system),
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
