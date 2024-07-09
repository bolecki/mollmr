from typing import List, Optional

from pydantic import BaseModel

from mollmr.models.message import Message


class Request(BaseModel):
    model: str = 'router'
    messages: List[Message]
    max_tokens: Optional[int] = 1024
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False
