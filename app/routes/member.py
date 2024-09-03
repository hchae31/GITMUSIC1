from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.dbfactory import get_db
from app.model.member import Member
from app.schema.member import NewMember
from app.service.member import MemberService

member_router = APIRouter()
templates = Jinja2Templates(directory='views/templates')

@member_router.get('/join', response_class=HTMLResponse)
async def join(req: Request):
    return templates.TemplateResponse('/member/join.html',{'request': req})

@member_router.post('/join', response_class=HTMLResponse)
async def joinok(member: NewMember, db: Session = Depends(get_db)):
    try:
        if MemberService.check_captcha(member):
            print(member)
            result = MemberService.insert_member(db, member)
            print('처리결과 : ', result.rowcount)

            if result.rowcount > 0: # 회원가입이 성공적으로 완료되면
                return RedirectResponse(url='/member/login', status_code=303)
        else:
            return RedirectResponse(url='/member/error', status_code=303)

    except Exception as ex:
        print(f'▷▷▷ joinok 오류 발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

@member_router.get('/login', response_class=HTMLResponse)
async def login(req: Request):
    return templates.TemplateResponse('/member/login.html',{'request': req})

@member_router.post('/login', response_class=HTMLResponse)
async def loginok(req: Request, db: Session = Depends(get_db)):
    data = await req.json() # 클라이언트가 보낸 데이터를 request 객체로 받음
    try:
        print('전송한 데이터 :', data)
        redirect_url = '/member/login'

        if MemberService.login_member(db, data): # 로그인 성공시
            req.session['logined_uid'] = data.get('userid') # 세션에 아이디 저장하고
            redirect_url = '/music/index' # myinfo 로 이동

        return RedirectResponse(url=redirect_url, status_code=303)

    except Exception as ex:
        print(f'▷▷▷ loginok 오류 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

@member_router.get('/logout', response_class=HTMLResponse)
async def error(req: Request):
    req.session.clear()     # 생성된 세션객체 제거
    return RedirectResponse('/', status_code=303)

@member_router.get('/myinfo', response_class=HTMLResponse)
async def myinfo(req: Request, db: Session = Depends(get_db)):
    try:
        if 'logined_uid' not in req.session:   # 로그인하지 않았다면
            return RedirectResponse('/member/login', status_code=303)

        # 로그인 했다면 아이디로 회원정보 조회 후 myinfo에 출력
        myinfo = MemberService.selectone_member(db, req.session['logined_uid'])
        print('-->', myinfo)
        return templates.TemplateResponse('/member/myinfo.html',{'request': req, 'myinfo': myinfo})

    except Exception as ex:
        print(f'▷▷▷ myinfo 오류 발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

@member_router.get('/error', response_class=HTMLResponse)
async def error(req: Request):
    return templates.TemplateResponse('/member/error.html',{'request': req})

@member_router.get('/loginfail', response_class=HTMLResponse)
async def error(req: Request):
    return templates.TemplateResponse('/member/loginfail.html',{'request': req})

@member_router.get('/check_userid')
async def check_userid(userid: str, db: Session = Depends(get_db)):
    try:
        stmt = select(Member.userid).where(Member.userid == userid)
        result = db.execute(stmt).scalars().first()

        if result:
            return {"exists": True}
        else:
            return {"exists": False}

    except Exception as ex:
        print(f"Error checking user ID: {str(ex)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")