from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

order_router = APIRouter()
templates = Jinja2Templates(directory='views/templates')

@order_router.get("/", response_class=HTMLResponse)
async def order(req: Request):
    return templates.TemplateResponse('order/order.html', {'request': req})
