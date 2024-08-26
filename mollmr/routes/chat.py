import json

from fastapi import APIRouter
from mollmr.models.request import Request
from starlette.responses import StreamingResponse

from mollmr.models.mixture import Mixture
from mollmr.models.router import Router as LLMRouter


MOLLMR_PREFIX = 'mollmr/'

router = APIRouter()

llm_router = LLMRouter.load_from_config()


@router.post('/v1/chat/completions')
async def chat_completions(request: Request):
    original_model = request.model
    request.model = request.model.replace(MOLLMR_PREFIX, '')
    mixture: Mixture = await llm_router.get_mixture_for_request(request)
    print('Using mixture: ', mixture.name)
    response = await mixture.generate(request=request)
    if request.stream:

        async def stream_response():
            async for chunk in response:
                chunk_data = chunk.to_dict()
                chunk_data['model'] = original_model
                yield f'data: {json.dumps(chunk_data)}\n\n'
            yield 'data: [DONE]\n\n'

        return StreamingResponse(stream_response(), media_type='text/event-stream')
    else:
        response.model = original_model
        return response
