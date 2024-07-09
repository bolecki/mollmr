from fastapi import FastAPI
from mollmr.routes import chat

app = FastAPI(title='MoLLMR')


@app.get('/')
async def root():
    return {'message': 'Hello World!'}


app.include_router(chat.router)
