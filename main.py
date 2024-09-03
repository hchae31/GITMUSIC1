from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.dbfactory import db_startup, db_shutdown
from app.routes.board import board_router
from app.routes.member import member_router
from app.routes.music import music_router
from app.routes.order import order_router
from app.routes.payment import payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_startup()
    yield
    await db_shutdown()
app = FastAPI(lifespan=lifespan)

# 세션처리를 위해 미들웨어 설정
# pip install itsdangerous
app.add_middleware(SessionMiddleware, secret_key='20240822110005')

templates = Jinja2Templates(directory="views/templates") # jinja2 설정
app.mount('/static', StaticFiles(directory='views/static'), name='static')
app.mount("/files", StaticFiles(directory="D:/test"), name="files")

app.include_router(member_router, prefix='/member')
app.include_router(board_router, prefix='/board')
app.include_router(music_router, prefix='/music')
app.include_router(payment_router, prefix='/payment')
app.include_router(order_router, prefix='/order')

@app.get("/", response_class=HTMLResponse)
async def index(req: Request):
    return templates.TemplateResponse('/order/order.html', {'request': req})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)


