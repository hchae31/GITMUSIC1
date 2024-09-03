from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from app.dbfactory import get_db
from app.model.payment import Payment

payment_router = APIRouter()
templates = Jinja2Templates(directory='views/templates')

@payment_router.get("/payment")
async def payment(request: Request):
    return templates.TemplateResponse("/member/myinfo.html", {"request": request})

@payment_router.post("/payment_success")
async def payment_success(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    merchant_uid = data.get('merchant_uid')
    imp_uid = data.get('imp_uid')

    if not merchant_uid or not imp_uid:
        raise HTTPException(status_code=400, detail="Invalid payment data received")

    userid = request.session.get('logined_uid')

    # 기존 결제 기록이 있는 경우
    existing_payment = db.query(Payment).filter(Payment.userid == userid).order_by(Payment.reg_date.desc()).first()

    if existing_payment and existing_payment.reg_date > datetime.now():
        new_reg_date = existing_payment.reg_date + timedelta(days=31)
    else:
        new_reg_date = datetime.now() + timedelta(days=31)

    new_payment = Payment(
        userid=userid,
        payment_date=datetime.now(),
        reg_date=new_reg_date
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return {
        "status": "success",
        "payment_id": new_payment.pno,
        "new_payment_date": new_payment.payment_date.strftime('%Y-%m-%d'),
        "new_reg_date": new_payment.reg_date.strftime('%Y-%m-%d')
    }