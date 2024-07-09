from typing import Optional

from openai import AsyncOpenAI

from mollmr.models.request import Request
from mollmr.models.message import Message


class Model:
    name: str
    base_url: str
    api_key: str
    description: Optional[str]
    client: AsyncOpenAI

    def __init__(
        self,
        name: str,
        base_url: str = 'http://localhost:1234/v1',
        api_key: str = 'wef',
        description: Optional[str] = None,
    ):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.description = description
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    async def generate(self, request: Request, stream=False):
        return await self.client.chat.completions.create(
            model=self.name,
            messages=[{'role': m.role, 'content': m.content} for m in request.messages],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=stream,
        )

    async def prompt(self, prompt: str, stream=False):
        request = Request(
            model=self.name,
            messages=[Message(role='user', content=prompt)],
            max_tokens=512,
            temperature=0.1,
            stream=stream
        )

        return await self.generate(request=request, stream=stream)
