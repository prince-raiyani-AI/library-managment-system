from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from app import models, schemas, database
from typing import Optional
from datetime import datetime, timedelta
import shutil
import os

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

templates = Jinja2Templates(directory="templates")

# Dependency to get current user from cookie
def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == int(user_id)).first()

@router.get("/", response_class=HTMLResponse)
def get_books(request: Request, db: Session = Depends(database.get_db)):
    books = db.query(models.Book).all()
    user = get_current_user(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "books": books, "user": user})

@router.post("/add")
async def add_book(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    user = get_current_user(request, db)
    if not user or not user.is_staff:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Save image
    file_location = f"static/images/{image.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(image.file, file_object)
    
    image_url = f"/static/images/{image.filename}"

    new_book = models.Book(
        title=title,
        author=author,
        price=price,
        quantity=quantity,
        description=description,
        image_url=image_url
    )
    db.add(new_book)
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/buy/{book_id}")
def buy_book(book_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book or book.quantity < 1:
        # Handle out of stock (flash message ideally, but simple redirect for now)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Create Transaction
    transaction = models.Transaction(
        user_id=user.id,
        book_id=book.id,
        transaction_type="buy",
        amount=book.price
    )
    
    # Update Stock
    book.quantity -= 1
    
    db.add(transaction)
    db.commit()
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/borrow/{book_id}")
def borrow_book(book_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book or book.quantity < 1:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Check if user already has this book borrowed and not returned
    existing_borrow = db.query(models.Transaction).filter(
        models.Transaction.user_id == user.id,
        models.Transaction.book_id == book_id,
        models.Transaction.transaction_type == "borrow",
        models.Transaction.is_returned == False
    ).first()

    if existing_borrow:
        # Prevent double borrowing
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Create Transaction
    due_date = datetime.now() + timedelta(days=14) # 2 weeks borrow period
    transaction = models.Transaction(
        user_id=user.id,
        book_id=book.id,
        transaction_type="borrow",
        amount=0, # No cost for borrowing initially
        due_date=due_date
    )
    
    # Update Stock
    book.quantity -= 1
    
    db.add(transaction)
    db.commit()
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/my-books", response_class=HTMLResponse)
def my_books(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    
    transactions = db.query(models.Transaction).options(joinedload(models.Transaction.book)).filter(models.Transaction.user_id == user.id).order_by(models.Transaction.created_at.desc()).all()
    
    return templates.TemplateResponse("my_books.html", {"request": request, "transactions": transactions, "user": user})

@router.post("/return/{transaction_id}")
def return_book_user(transaction_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == user.id,
        models.Transaction.transaction_type == "borrow",
        models.Transaction.is_returned == False
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or already returned")

    transaction.is_returned = True
    transaction.return_date = datetime.now()

    # Restock book
    book = db.query(models.Book).filter(models.Book.id == transaction.book_id).first()
    if book:
        book.quantity += 1
    
    db.commit()

    return RedirectResponse(url="/books/my-books", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/edit/{book_id}", response_class=HTMLResponse)
def edit_book_page(book_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_staff:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return templates.TemplateResponse("edit_book.html", {"request": request, "book": book, "user": user})

@router.post("/edit/{book_id}")
async def edit_book(
    book_id: int,
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    user = get_current_user(request, db)
    if not user or not user.is_staff:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book.title = title
    book.author = author
    book.price = price
    book.quantity = quantity
    book.description = description

    if image and image.filename:
        file_location = f"static/images/{image.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        book.image_url = f"/static/images/{image.filename}"
    
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/delete/{book_id}")
def delete_book(book_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_staff:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        db.delete(book)
        db.commit()
    except Exception as e:
        db.rollback()
        # If deletion fails (likely due to FK), we could flash a message, but for now redirect.
        print(f"Delete failed: {e}")
        
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
