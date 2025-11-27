from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app import models, database
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

templates = Jinja2Templates(directory="templates")

def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == int(user_id)).first()

@router.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_staff:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    # --- Analytics Logic ---
    
    # 1. Sales Visuals (Total Money, Total Books Sold)
    total_sales_amount = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.transaction_type == "buy").scalar() or 0.0
    total_books_sold = db.query(func.count(models.Transaction.id)).filter(models.Transaction.transaction_type == "buy").scalar() or 0
    
    # 2. High Demand Books (Sold in past 3 days)
    three_days_ago = datetime.now() - timedelta(days=3)
    high_demand_books = db.query(
        models.Book,
        func.count(models.Transaction.id).label("sales_count")
    ).join(models.Transaction).filter(
        models.Transaction.transaction_type == "buy",
        models.Transaction.created_at >= three_days_ago
    ).group_by(models.Book.id).order_by(func.count(models.Transaction.id).desc()).limit(5).all()

    # 3. Low Stock Books (Quantity < 5)
    low_stock_books = db.query(models.Book).filter(models.Book.quantity < 5).all()

    # 4. Overdue/Deadline Tracking
    # People who have missed deadlines or are close (due within 2 days)
    now = datetime.now()
    two_days_from_now = now + timedelta(days=2)
    
    overdue_transactions = db.query(models.Transaction).options(joinedload(models.Transaction.user), joinedload(models.Transaction.book)).filter(
        models.Transaction.transaction_type == "borrow",
        models.Transaction.is_returned == False,
        models.Transaction.due_date < now
    ).all()
    
    upcoming_due_transactions = db.query(models.Transaction).options(joinedload(models.Transaction.user), joinedload(models.Transaction.book)).filter(
        models.Transaction.transaction_type == "borrow",
        models.Transaction.is_returned == False,
        models.Transaction.due_date >= now,
        models.Transaction.due_date <= two_days_from_now
    ).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "total_sales_amount": total_sales_amount,
        "total_books_sold": total_books_sold,
        "high_demand_books": high_demand_books,
        "low_stock_books": low_stock_books,
        "overdue_transactions": overdue_transactions,
        "upcoming_due_transactions": upcoming_due_transactions
    })

@router.post("/return/{transaction_id}")
def return_book(transaction_id: int, request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_staff:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction or transaction.transaction_type != "borrow":
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.is_returned = True
    transaction.return_date = datetime.now()
    
    # Restock book
    book = db.query(models.Book).filter(models.Book.id == transaction.book_id).first()
    if book:
        book.quantity += 1
        
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/users", response_class=HTMLResponse)
def get_users(request: Request, db: Session = Depends(database.get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_staff:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    
    users = db.query(models.User).order_by(models.User.created_at.desc()).all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users, "user": user})
