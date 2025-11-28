from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, schemas, utils, database
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    staff_pin: str = Form(None),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered"})

    is_staff = False
    if staff_pin:
        if staff_pin == "2244":
            is_staff = True
        else:
            return templates.TemplateResponse("register.html", {"request": request, "error": "Invalid Staff PIN"})

    hashed_password = utils.get_password_hash(password)
    new_user = models.User(email=email, password_hash=hashed_password, is_staff=is_staff)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not utils.verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    # for simplicity we are using a cookie to store the user id and in a real production app, use JWT tokens
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    if user.is_staff:
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    response.set_cookie(key="user_id", value=str(user.id))
    return response

@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_id")
    return response
