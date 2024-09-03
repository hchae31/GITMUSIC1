import logging
import os
from datetime import datetime

from fastapi import Form, HTTPException
from sqlalchemy import select, insert, or_, func, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import contains_eager, Session, joinedload

from app.model.board import Board, BoardFile, Reply
from app.schema.board import BoardCreate

UPLOAD_PATH = 'D:/test/'


def get_board_data(title: str = Form(...), userid: str = Form(...),
                   contents: str = Form(...)):
    return BoardCreate(userid=userid, title=title, contents=contents)


async def process_upload(files):
    attachs = []  # 업로드된 파일정보를 저장하기 위해 리스트 생성
    today = datetime.today().strftime('%Y%m%d%H%M%S')  # UUID 생성 (유니크한 고유 식별값 생성)

    for file in files:
        if file.filename != '' and file.size > 0:
            nfname = f'{today}-{file.filename}'
            fname = os.path.join(UPLOAD_PATH, nfname)  # 업로드할 파일경로 생성
            content = await file.read()  # 업로드할 파일의 내용을 비동기로 읽음
            with open(fname, 'wb') as f:
                f.write(content)
            logging.info(f"File saved at: {fname}")
            attach = [nfname, file.size]  # 업로드된 파일 정보를 리스트에 저장
            attachs.append(attach)

    return attachs


class FileService:
    @staticmethod
    def insert_board(fl, attachs, db):
        try:
            with db.begin():
                stmt = insert(Board).values(userid=fl.userid,
                                            title=fl.title, contents=fl.contents)
                result = db.execute(stmt)

                # 방금 생성한 레코드의 기본키 값 : inserted_primary_key
                inserted_bno = result.inserted_primary_key[0]

                for attach in attachs:
                    data = {'fname': attach[0], 'fsize': attach[1],
                            'bno': inserted_bno}
                    stmt = insert(BoardFile).values(data)
                    result = db.execute(stmt)

                db.commit()

                return result

        except SQLAlchemyError as ex:
            print(f'▶▶▶ insert_board 오류발생 : {str(ex)}')
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to insert board data")


class BoardService:
    @staticmethod
    def select_board(db, cpg):
        try:
            stbno = (cpg - 1) * 25
            # 총 계시글 수 조회
            from sqlalchemy import func
            cnt = db.execute(func.count(Board.bno)).scalar()

            stmt = select(Board.bno, Board.title, Board.userid,
                          Board.regdate, Board.views) \
                .order_by(Board.bno.desc()).offset(stbno).limit(25)

            result = db.execute(stmt)
            return result, cnt

        except SQLAlchemyError as ex:
            print(f'▶▶▶ select_board에서 오류 발생 : {str(ex)}')

    @staticmethod
    def find_board(db, ftype, fkey, cpg):
        try:
            stbno = (cpg - 1) * 25
            stmt = select(Board.bno, Board.title, Board.userid, Board.regdate, Board.views)

            myfilter = Board.title.like(fkey)
            if ftype == 'userid': myfilter = Board.userid.like(fkey)
            elif ftype == 'contents': myfilter = Board.contents.like(fkey)
            elif ftype == 'titcont': myfilter = or_(Board.title.like(fkey), Board.contents.like(fkey))

            cnt = db.query(func.count(Board.bno)).filter(myfilter).scalar()
            stmt = stmt.filter(myfilter) \
                .order_by(Board.bno.desc()).offset(stbno).limit(25)
            result = db.execute(stmt)
            return result, cnt

        except SQLAlchemyError as ex:
            print(f'▶▶▶ find_board 오류 발생 : {str(ex)}')

    @staticmethod
    def selectone_board(bno, db):
        try:
            stmt = update(Board).where(Board.bno == bno).values(views=Board.views + 1)
            db.execute(stmt)

            stmt = select(Board).outerjoin(Board.replys) \
                .options(contains_eager(Board.replys)) \
                .where(Board.bno == bno) \
                .order_by(Reply.rpno)

            result = db.execute(stmt)
            db.commit()
            return result.scalars().first()

        except SQLAlchemyError as ex:
            print(f'▶▶▶ selectone_board에서 오류 발생 : {str(ex)}')
            db.rollback()

    @staticmethod
    def selectfile_board(bno: int, db: Session):
        try:
            # 게시글과 첨부파일을 함께 조회
            board = db.query(Board).options(joinedload(Board.files)).filter(Board.bno == bno).one_or_none()
            return board
        except Exception as ex:
            print(f'▶▶▶ selectone_board에서 오류 발생 : {str(ex)}')
            return None

    @staticmethod
    def insert_reply(db, rp):
        try:
            stmt = select(func.coalesce(func.max(Reply.rno), 0) + 1)
            next_rno = db.execute(stmt).scalar_one()
            stmt = insert(Reply).values(userid=rp.userid, reply=rp.reply,
                                        bno=rp.bno, rpno=next_rno)
            result = db.execute(stmt)
            db.commit()
            return result

        except SQLAlchemyError as ex:
            print(f'▶▶▶ insert_reply에서 오류 발생 : {str(ex)}')
            db.rollback()

    @staticmethod
    def insert_rreply(db, rp):
        try:
            stmt = insert(Reply).values(userid=rp.userid, reply=rp.reply,
                                        bno=rp.bno, rpno=rp.rpno)
            result = db.execute(stmt)
            db.commit()
            return result

        except SQLAlchemyError as ex:
            print(f'▶▶▶ insert_rreply에서 오류 발생 : {str(ex)}')
            db.rollback()

    @staticmethod
    def delete_board(db, bno):
        try:
            stmt = delete(Board).where(Board.bno == bno)
            result = db.execute(stmt)
            db.commit()
            return result

        except SQLAlchemyError as ex:
            print(f'▶▶▶ delete_board에서 오류 발생 : {str(ex)}')
            db.rollback()

    @staticmethod
    def update_board(db: Session, board: Board) -> bool:
        try:
            # 게시글 수정
            stmt = update(Board) \
                .values(title=board.title, userid=board.userid,
                        contents=board.contents, regdate=datetime.now()) \
                .where(Board.bno == board.bno)
            result = db.execute(stmt)
            db.commit()

            # 결과 확인
            if result.rowcount > 0:
                return True
            else:
                return False

        except SQLAlchemyError as ex:
            print(f'▶▶▶ update_board에서 오류 발생 : {str(ex)}')
            db.rollback()
            return False
