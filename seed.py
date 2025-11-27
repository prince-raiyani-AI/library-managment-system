from app.database import SessionLocal, engine, Base
from app import models, utils
from datetime import datetime
import random

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_data():
    # 1. Create Staff User
    staff_email = "staff@library.com"
    if not db.query(models.User).filter(models.User.email == staff_email).first():
        staff_user = models.User(
            email=staff_email,
            password_hash=utils.get_password_hash("admin123"),
            is_staff=True
        )
        db.add(staff_user)
        print(f"Created Staff User: {staff_email}")

    # 2. Create Member User
    member_email = "member@library.com"
    if not db.query(models.User).filter(models.User.email == member_email).first():
        member_user = models.User(
            email=member_email,
            password_hash=utils.get_password_hash("user123"),
            is_staff=False
        )
        db.add(member_user)
        print(f"Created Member User: {member_email}")

    # 3. Seed Books (15-20 books)
    books_data = [
        {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "price": 10.99, "quantity": 5, "description": "A novel set in the Jazz Age."},
        {"title": "To Kill a Mockingbird", "author": "Harper Lee", "price": 12.50, "quantity": 8, "description": "A novel about racial injustice in the Deep South."},
        {"title": "1984", "author": "George Orwell", "price": 15.00, "quantity": 10, "description": "A dystopian social science fiction novel."},
        {"title": "Pride and Prejudice", "author": "Jane Austen", "price": 9.99, "quantity": 6, "description": "A romantic novel of manners."},
        {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "price": 11.00, "quantity": 4, "description": "A story about teenage angst and alienation."},
        {"title": "The Hobbit", "author": "J.R.R. Tolkien", "price": 14.95, "quantity": 12, "description": "A fantasy novel about the quest of Bilbo Baggins."},
        {"title": "Fahrenheit 451", "author": "Ray Bradbury", "price": 13.50, "quantity": 7, "description": "A dystopian novel about a future where books are outlawed."},
        {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "price": 25.00, "quantity": 3, "description": "An epic high-fantasy novel."},
        {"title": "Animal Farm", "author": "George Orwell", "price": 8.99, "quantity": 15, "description": "A satirical allegorical novella."},
        {"title": "Brave New World", "author": "Aldous Huxley", "price": 14.00, "quantity": 9, "description": "A dystopian novel set in a futuristic World State."},
        {"title": "The Alchemist", "author": "Paulo Coelho", "price": 16.00, "quantity": 20, "description": "A novel about following your dreams."},
        {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "price": 19.99, "quantity": 25, "description": "A fantasy novel about a young wizard."},
        {"title": "The Da Vinci Code", "author": "Dan Brown", "price": 18.00, "quantity": 11, "description": "A mystery thriller novel."},
        {"title": "The Kite Runner", "author": "Khaled Hosseini", "price": 13.99, "quantity": 6, "description": "A novel about friendship and redemption."},
        {"title": "Life of Pi", "author": "Yann Martel", "price": 12.99, "quantity": 8, "description": "A fantasy adventure novel."},
        {"title": "The Book Thief", "author": "Markus Zusak", "price": 14.50, "quantity": 5, "description": "A historical novel set in Nazi Germany."},
        {"title": "Gone Girl", "author": "Gillian Flynn", "price": 15.99, "quantity": 10, "description": "A psychological thriller."},
        {"title": "The Hunger Games", "author": "Suzanne Collins", "price": 11.50, "quantity": 14, "description": "A dystopian novel about a televised death match."},
    ]

    for book in books_data:
        if not db.query(models.Book).filter(models.Book.title == book["title"]).first():
            new_book = models.Book(
                title=book["title"],
                author=book["author"],
                price=book["price"],
                quantity=book["quantity"],
                description=book["description"],
                image_url="" # Placeholder
            )
            db.add(new_book)
            print(f"Added Book: {book['title']}")

    db.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
