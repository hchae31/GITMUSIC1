import logging
import os
from math import ceil
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.dbfactory import get_db
from app.model.board import Board, BoardFile
from app.schema.board import BoardCreate, NewReply
from app.service.board import BoardService, get_board_data, process_upload, FileService, UPLOAD_PATH

board_router = APIRouter()
templates = Jinja2Templates(directory='views/templates')


@board_router.get('/list/{cpg}', response_class=HTMLResponse)
async def list(req: Request, cpg: int, db: Session = Depends(get_db)):
    try:
        stpgb = int((cpg - 1) / 10) * 10 + 1
        bdlist, cnt = BoardService.select_board(db, cpg)
        allpage = ceil(cnt / 25)
        return templates.TemplateResponse('board/list.html',
                                          {'request': req, 'bdlist': bdlist, 'cpg': cpg,
                                           'stpgb': stpgb, 'allpage': allpage, 'baseurl': '/board/list/'})
    except Exception as ex:
        print(f'▷▷▷ list에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.get("/list/{ftype}/{fkey}/{cpg}", response_class=HTMLResponse)
async def find(req: Request, cpg: int, ftype: str, fkey: str, db: Session = Depends(get_db)):
    try:
        stpgb = int((cpg - 1) / 10) * 10 + 1
        bdlist, cnt = BoardService.find_board(db, ftype, '%'+fkey+'%', cpg)
        allpage = ceil(cnt / 25)
        return templates.TemplateResponse('board/list.html',
                                          {'request': req, 'bdlist': bdlist, 'cpg': cpg,
                                           'stpgb': stpgb, 'allpage': allpage,
                                           'baseurl': f'/board/list/{ftype}/{fkey}/'})
    except Exception as ex:
        print(f'▷▷▷ find에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.get("/write", response_class=HTMLResponse)
async def write(req: Request):
    if 'logined_uid' not in req.session:  # 로그인하지 않으면 글쓰기 금지
        return RedirectResponse('/member/login', 303)

    return templates.TemplateResponse('board/write.html', {'request': req})


@board_router.post('/write')
async def writeok(board: BoardCreate = Depends(get_board_data),
                  files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        print(board)
        attachs = await process_upload(files)
        print(attachs)
        if FileService.insert_board(board, attachs, db):
            return RedirectResponse('/board/list/1', 303)

    except Exception as ex:
        print(f'▷▷▷writeok 오류발생 {str(ex)}')
        return RedirectResponse('/member/error', 303)


@board_router.get("/view/{bno}", response_class=HTMLResponse)
async def view(req: Request, bno: int, db: Session = Depends(get_db)):
    try:
        boards = BoardService.selectone_board(bno, db)
        current_userid = req.session.get('logined_uid')
        is_author = (str(current_userid) == str(boards.userid))
        return templates.TemplateResponse('board/view.html',
                                          {'request': req, 'boards': boards, 'is_author': is_author})

    except Exception as ex:
        print(f'▷▷▷ view에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.post("/reply", response_class=HTMLResponse)
async def replyok(reply: NewReply, db: Session = Depends(get_db)):
    try:
        if BoardService.insert_reply(db, reply):
            return RedirectResponse(f'/board/view/{reply.bno}', 303)
    except Exception as ex:
        print(f'▷▷▷ replyok에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.post("/rreply", response_class=HTMLResponse)
async def rreplyok(reply: NewReply, db: Session = Depends(get_db)):
    try:
        if BoardService.insert_rreply(db, reply):
            return RedirectResponse(f'/board/view/{reply.bno}', 303)
    except Exception as ex:
        print(f'▷▷▷ rreplyok에서 오류 발생: {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)


@board_router.delete("/view/{bno}")
async def delete_board(bno: int, db: Session = Depends(get_db)):
    try:
        result = BoardService.delete_board(db, bno)
        if result.rowcount > 0:
            return {"message": "게시물이 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="게시물이 존재하지 않거나 이미 삭제되었습니다.")
    except SQLAlchemyError as ex:
        print(f'▷▷▷ delete_board에서 오류 발생: {str(ex)}')
        raise HTTPException(status_code=500, detail=f"삭제 중 오류가 발생했습니다: {str(ex)}")


@board_router.get("/update/{bno}")
async def get_update_page(bno: int, request: Request, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.bno == bno).one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    return templates.TemplateResponse('board/update.html', {'request': request, 'board': board})


@board_router.post('/update/{bno}')
async def update_board(bno: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    title = form.get('title')
    contents = form.get('contents')
    userid = request.session.get('logined_uid')

    if userid is None:
        raise HTTPException(status_code=401, detail="사용자 인증이 필요합니다.")

    try:
        board = Board(
            bno=bno,
            title=title,
            userid=userid,
            contents=contents
        )
        affected_rows = BoardService.update_board(db, board)

        if affected_rows > 0:
            return RedirectResponse(url=f"/board/view/{bno}", status_code=303)
        else:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    except SQLAlchemyError as ex:
        print(f'▶▶▶ update_board에서 오류 발생: {str(ex)}')
        raise HTTPException(status_code=500, detail="업데이트 중 오류가 발생했습니다.")

# 글삭제 시 db에서도 삭제
@board_router.delete("/board/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    logging.info(f"Attempting to delete post with ID: {post_id}")

    # Fetch the board
    post = db.query(Board).filter(Board.bno == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    logging.info(f"Found post: {post}")

    # Delete the post (cascades to delete associated files)
    db.delete(post)
    db.commit()

    logging.info(f"Post with ID: {post_id} deleted")

    # Optional: Clean up files from the file system
    for file in post.files:
        file_path = os.path.join(UPLOAD_PATH, file.fname)
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")

    return {"detail": "Post and associated files deleted"}