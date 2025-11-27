from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import auth, books, dashboard

# Create the database tables
# This will create all tables defined in models.py if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application
app = FastAPI(
    title="Library Management System",
    description="A comprehensive system for managing library books, members, and transactions.",
    version="1.0.0"
)

# Mount the static directory
# This allows serving static files like CSS and JavaScript
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the routers
# These routers handle the API endpoints for different features
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(dashboard.router)

from fastapi import Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app import models

templates = Jinja2Templates(directory="templates")

def get_current_user(request: Request, db: Session):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == int(user_id)).first()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, q: str = None, db: Session = Depends(get_db)):
    """
    Root endpoint to render the home page with optional search.
    """
    query = db.query(models.Book)
    if q:
        search = f"%{q}%"
        query = query.filter(or_(models.Book.title.ilike(search), models.Book.author.ilike(search)))
    
    books = query.all()
    user = get_current_user(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "books": books, "user": user, "query": q})
