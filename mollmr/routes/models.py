import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from mollmr.routes.chat import MOLLMR_PREFIX, llm_router

router = APIRouter()


@router.get('/v1/models')
async def models():
    return JSONResponse({
        'data': [
            {
                'id': MOLLMR_PREFIX + name,
                'object': 'model',
                'owned_by': 'organization-owner',
                'permission': [
                    {}
                ]
            } for name in (['router'] + list(llm_router.mixtures.keys()))
        ],
            'object': 'list'
        })
