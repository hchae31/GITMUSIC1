import os
import random

import aiofiles
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError, BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, StreamingResponse, HTMLResponse, JSONResponse, FileResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from app.dbfactory import get_db, SessionLocal
from app.model.member import Member
from app.model.music import MusicVideo, Music, Storage
from app.schema.music import NewStorage
from app.service.music import MusicService, MusicVideoService, Mp3Service

music_router= APIRouter()

templates = Jinja2Templates(directory='views/templates')

# 음악 메인페이지
@music_router.get('/index')
async def index(req: Request, db: Session = Depends(get_db)):
    try:
        mlist = MusicService.select_music(db)
        return templates.TemplateResponse('/music/index.html', {'request': req, 'mlist': mlist})
    except Exception as ex:
        print(f'▷▷▷ music_list 오류발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

# 장르 - dance
@music_router.get('/dance')
async def dance(req: Request, db: Session = Depends(get_db)):
    try:
        mlist = MusicService.get_music_genre(db, 'dance')
        return templates.TemplateResponse('/music/dance.html', {'request': req, 'mlist': mlist})
    except Exception as ex:
        print(f'▷▷▷ dance_list 오류발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

# 장르 - hiphop
@music_router.get('/hiphop')
async def hiphop(req: Request, db: Session = Depends(get_db)):
    try:
        mlist = MusicService.get_music_genre(db, 'hiphop')
        return templates.TemplateResponse('/music/hiphop.html', {'request': req, 'mlist': mlist})
    except Exception as ex:
        print(f'▷▷▷ dance_list 오류발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

# 장르 - ballad
@music_router.get('/ballad')
async def ballad(req: Request, db: Session = Depends(get_db)):
    try:
        mlist = MusicService.get_music_genre(db, 'ballad')
        return templates.TemplateResponse('/music/ballad.html', {'request': req, 'mlist': mlist})
    except Exception as ex:
        print(f'▷▷▷ ballad_list 오류발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

# 국가별 - kpop
@music_router.get('/kpop')
async def kpop(req: Request, db: Session = Depends(get_db)):
    try:
        mlist = MusicService.get_music_country(db, 'kpop')
        return templates.TemplateResponse('/music/kpop.html', {'request': req, 'mlist': mlist})
    except Exception as ex:
        print(f'▷▷▷ kpop_list 오류발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

# 국가별 - jpop
@music_router.get('/jpop')
async def jpop(req: Request, db: Session = Depends(get_db)):
    try:
        mlist = MusicService.get_music_country(db, 'jpop')
        return templates.TemplateResponse('/music/jpop.html', {'request': req, 'mlist': mlist})
    except Exception as ex:
        print(f'▷▷▷ jpop_list 오류발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

# 국가별 - pop
@music_router.get('/pop')
async def kpop(req: Request, db: Session = Depends(get_db)):
    try:
        mlist = MusicService.get_music_country(db, 'pop')
        return templates.TemplateResponse('/music/pop.html', {'request': req, 'mlist': mlist})
    except Exception as ex:
        print(f'▷▷▷ pop_list 오류발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

# 제목 or 가수로 검색
@music_router.get('/search')
async def search(req: Request, query: str = '',db: Session = Depends(get_db)):
    try:
        mlist = MusicService.get_music_search(db, title=query, singer=query)
        return templates.TemplateResponse('/music/search.html', {'request': req, 'mlist': mlist})
    except Exception as ex:
        print(f'▷▷▷ search 오류발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

@music_router.get('/music')
async def music(req: Request):
    return templates.TemplateResponse('/music/music.html', {'request': req})

@music_router.get('/musicvideo')
async def musicvideo(req: Request):
    return templates.TemplateResponse('music/musicvideo.html', {'request': req})

@music_router.get('/test')
async def test(req: Request):
    return templates.TemplateResponse('music/test.html', {'request': req})

# 음악 플레이
@music_router.get('/mp3play/{mno}', response_class=HTMLResponse)
async def mp3play(mno: int, db: Session = Depends(get_db) ):

    MUSIC_PATH = 'd:/test/music/'
    music_fname = Mp3Service.music_mp3(db, mno)

    file_path = os.path.join(MUSIC_PATH, music_fname)

    async def iterfile():
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(64 * 1024):
                yield chunk

    return StreamingResponse(iterfile(),media_type='audio/mp3')

# 음악 이미지
@music_router.get('/musiccover/{mno}', response_class=HTMLResponse)
async def musiccover(mno: int, db: Session = Depends(get_db) ):

    MUSICIMAGE_PATH = 'd:/test/musicimage/'
    mp3_image = Mp3Service.selectone_musicimage(db, mno)

    file_path = os.path.join(MUSICIMAGE_PATH, mp3_image )

    return FileResponse(file_path, media_type='image/jpeg')

# 뮤비 랜덤 불러오기
@music_router.get('/random_mvno', response_class=JSONResponse)
async def random_mvno(db: Session = Depends(get_db)):
    mvno = MusicVideoService.get_random_mvno(db)
    if mvno is None:
        return JSONResponse(content={"error": "No music videos available"}, status_code=404)
    return JSONResponse(content={"mvno": mvno})

@music_router.get('/mp4play/{mvno}', response_class=HTMLResponse)
async def mp4play(mvno: int, db: Session = Depends(get_db) ):

    MV_PATH = 'd:/test/mv/'
    mv_fname = MusicVideoService.selectone_file(db, mvno)

    file_path = os.path.join(MV_PATH, mv_fname)

    async def iterfile():
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(64 * 1024):
                yield chunk

    return StreamingResponse(iterfile(), media_type='video/mp4')

# 뮤비 커버이미지
@music_router.get('/mvcover/{mvno}', response_class=HTMLResponse)
async def mvcover(mvno: int, db: Session = Depends(get_db) ):

    IMAGE_PATH = 'd:/test/mvimage/'
    mv_image = MusicVideoService.selectone_mvimage(db, mvno)

    file_path = os.path.join(IMAGE_PATH, mv_image )

    return FileResponse(file_path, media_type='image/jpeg')

# 뮤비 가사
@music_router.get('/mvlyrics/{mvno}', response_class=HTMLResponse)
async def mvlyrics(mvno: int, db: Session = Depends(get_db) ):

    mv_lyrics = MusicVideoService.selectone_mvlyrics(db, mvno)

    file_path = os.path.join(mv_lyrics)

    return HTMLResponse(content=file_path, media_type='text/html')

# 뮤비 하단의 3개 이미지에 대한 랜덤 처리
@music_router.get('/random_mvnos', response_class=JSONResponse)
async def random_mvnos(db: Session = Depends(get_db)):
    # Get all mvno values
    stmt = select(MusicVideo.mvno)
    results = db.execute(stmt).scalars().all()

    # Check if we have enough data
    if not results or len(results) < 3:
        return JSONResponse(content={"error": "Not enough music videos available"}, status_code=404)

    # Randomly select 3 unique mvno values
    random_mvnos = random.sample(results, 3)

    return JSONResponse(content={"mvnos": random_mvnos})

# FastAPI 엔드포인트에서 호출
@music_router.get('/music/index')
async def index(db: Session = Depends(get_db)):
    music_list = MusicService.get_random_music_list(db)
    return {"mlist": music_list}

# 보관함 목록
@music_router.get("/storage", response_class=JSONResponse)
async def view_storage(req: Request, db: Session = Depends(get_db)):
    userid = req.session.get('logined_uid')
    if not userid:
        return RedirectResponse(url='/member/login', status_code=303)

    # Fetch songs in user's storage
    storage_items = db.query(Storage).join(Music).filter(Storage.userid == userid).all()

    return templates.TemplateResponse('/music/storage.html', {'request': req, 'storage_items': storage_items})

# 보관함 추가
@music_router.post("/add_to_storage")
async def add_to_storage(req: Request, db: Session = Depends(get_db)):
    data = await req.json()
    mno = data.get('mno')
    userid = req.session.get('logined_uid')

    if not mno:
        raise HTTPException(status_code=400, detail="Invalid song ID.")

    if not userid:
        raise HTTPException(status_code=403, detail="User not logged in.")

    music = db.query(Music).filter(Music.mno == mno).first()
    if not music:
        raise HTTPException(status_code=404, detail="Music not found.")

    new_storage = Storage(userid=userid, mno=mno)
    db.add(new_storage)
    db.commit()

    return JSONResponse(content={'message': '선택하신 곡을 보관함에 추가하였습니다!'}, status_code=200)

#보관함 전체 추가 (현재 페이지의 곡들만)
@music_router.post("/add_all_storage")
async def add_all_storage(req: Request, db: Session = Depends(get_db)):
    try:
        data = await req.json()
        music_ids = data.get('music_ids')
        userid = req.session.get('logined_uid')

        if not music_ids or not isinstance(music_ids, list):
            raise HTTPException(status_code=400, detail="Invalid music IDs format.")

        if not userid:
            raise HTTPException(status_code=403, detail="User not logged in.")

        for mno in music_ids:
            music = db.query(Music).filter(Music.mno == mno).first()
            if music:
                new_storage = Storage(userid=userid, mno=mno)
                db.add(new_storage)

        db.commit()
        return JSONResponse(content={'message': '모든 곡을 보관함에 추가하였습니다!'}, status_code=200)
    except HTTPException as e:
        print(f"HTTPException: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while adding to storage.")

# 무작위 재생 (현재 페이지의 곡들 중 무작위 재생)
@music_router.post("/play_random")
async def play_random(req: Request, db: Session = Depends(get_db)):

    data = await req.json()
    music_ids = data.get('music_ids')

    if not music_ids:
        raise HTTPException(status_code=400, detail="No music IDs provided.")

    all_music = db.query(Music).filter(Music.mno.in_(music_ids)).all()
    if not all_music:
        raise HTTPException(status_code=404, detail="No music found.")

    random_music = random.choice(all_music)

    response_data = {
        'mno': random_music.mno,
        'title': random_music.title,
        'singer': random_music.singer,
        'genre': random_music.genre,
        'year': random_music.year,
        'country': random_music.country,
        'ment': random_music.ment
    }
    return JSONResponse(content=response_data, status_code=200)

# 보관함 삭제
@music_router.post('/remove_from_storage')
async def remove_from_storage(req: Request, db: Session = Depends(get_db)):
    try:
        data = await req.json()
        sno = data.get('sno')

        if not sno:
            raise HTTPException(status_code=400, detail="Invalid storage ID.")

        # 로그인 아이디 확인
        userid = req.session.get('logined_uid')
        if not userid:
            raise HTTPException(status_code=403, detail="User not logged in.")

        # 보관함 목록
        storage_entry = db.query(Storage).filter(Storage.sno == sno, Storage.userid == userid).first()
        if not storage_entry:
            raise HTTPException(status_code=404, detail="Storage entry not found.")

        # 보관함에서 삭제
        db.delete(storage_entry)
        db.commit()

        return JSONResponse(content={'message': '보관함에서 삭제되었습니다.'}, status_code=200)

    except Exception as e:
        print(f'Error removing from storage: {e}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 보관함 전체 삭제
@music_router.post('/remove_all_storage')
async def remove_all_storage(req: Request, db: Session = Depends(get_db)):
    try:
        userid = req.session.get('logined_uid')
        if not userid:
            raise HTTPException(status_code=403, detail="User not logged in.")

        db.query(Storage).filter(Storage.userid == userid).delete(synchronize_session=False)
        db.commit()
        return JSONResponse(content={'message': '모든 곡이 삭제되었습니다'}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail="모든 곡을 삭제하는데 문제가 발생했습니다.")
