# Library Management System

A comprehensive Library Management System built with FastAPI and PostgreSQL. This system is designed to manage books, members, and transactions efficiently, providing a seamless experience for both staff and regular users.

## Features

- **User Management**: Separate roles for Staff and Members.
- **Book Management**: Complete inventory management with stock tracking.
- **Transactions**: Support for buying and borrowing books.
- **Dashboard**: Advanced analytics for staff, including sales reports, high-demand books, and low stock alerts.
- **Authentication**: Secure login and registration with PIN protection for staff.
- **Responsive UI**: A premium, dark-themed user interface.

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS (Vanilla), JavaScript
- **Testing**: Pytest

## Database Schema & Relationships

The system uses a relational database (PostgreSQL) with the following schema:

### 1. Users Table (`users`)
-   **id**: Integer (Primary Key)
-   **email**: String (Unique)
-   **password_hash**: String
-   **is_staff**: Boolean (True for Staff, False for Members)
-   **created_at**: DateTime
-   **Relationships**: One-to-Many with `transactions`.

### 2. Books Table (`books`)
-   **id**: Integer (Primary Key)
-   **title**: String
-   **author**: String
-   **price**: Float
-   **quantity**: Integer (Stock)
-   **description**: Text
-   **image_url**: String
-   **created_at**: DateTime
-   **Relationships**: One-to-Many with `transactions`.

### 3. Transactions Table (`transactions`)
-   **id**: Integer (Primary Key)
-   **user_id**: Integer (ForeignKey -> `users.id`)
-   **book_id**: Integer (ForeignKey -> `books.id`)
-   **transaction_type**: String ('buy' or 'borrow')
-   **amount**: Float
-   **due_date**: DateTime (Nullable, for borrows)
-   **return_date**: DateTime (Nullable)
-   **is_returned**: Boolean (Default False)
-   **created_at**: DateTime

## Borrowing Rules

-   **Duration**: Borrowed books are due **14 days** (2 weeks) from the date of borrowing.
-   **Stock**: Borrowing a book reduces its quantity by 1. Returning it increases quantity by 1.
-   **Limits**: Users cannot borrow the same book twice if they currently have an active (unreturned) copy.
-   **Overdue**: Staff can track overdue books in the dashboard.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/prince-raiyani-AI/library-managment-system.git
    cd library-managment-system
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Database**:
    - Update the `SQLALCHEMY_DATABASE_URL` in `app/database.py` with your PostgreSQL credentials like `postgresql://POSTGRES_USERNAME:POSTGRES_PASSWORD@localhost:5432/POSTGRES_DB_NAME`.

5.  **Run the application**:
    ```bash
    uvicorn app.main:app --reload
    ```

6.  **Access the application**:
    - Open your browser and navigate to `http://127.0.0.1:8000`.

## Usage

- **Staff Registration**: Use the PIN `2244` to register as a staff member.
- **Member Registration**: Register freely to browse and borrow/buy books.
- **Dashboard**: Accessible only to staff members for managing the library.

## Docker

1.  **Build the Docker image**:
    ```bash
    docker build -t library-management-system .
    ```

2.  **Run the Docker container**:
    ```bash
    docker run -p 8000:8000 library-management-system
    ```

3.  **Access the application**:
    - Open your browser and navigate to `http://localhost:8000`.

## Docker Compose

1.  **Build and run the containers**:
    ```bash
    docker-compose up --build
    ```

2.  **Access the application**:
    - Open your browser and navigate to `http://localhost:8000`.

## Docker Hub

1.  **Push the Docker image to Docker Hub**:
    ```bash
    docker push library-management-system
    ```

2.  **Pull the Docker image from Docker Hub**:
    ```bash
    docker pull library-management-system
    ```

## GitHub

1.  **Initialize the repository**:
    ```bash
    git init
    ```

2.  **Add the remote repository**:
    ```bash
    git remote add origin <repository_url>
    ```

3.  **Commit and push the changes**:
    ```bash
    git add .
    git commit -m "Initial commit"
    git push -u origin main
    ```

## Docker Hub

-   **Docker Hub**: [library-management-system](https://hub.docker.com/repository/docker/prince024/library-managment-system) - My docker image link

## Application screenshots

<img width="1894" height="905" alt="image" src="https://github.com/user-attachments/assets/c5f5189e-fbf5-4c27-90e1-df61016035b1" />
<img width="1893" height="893" alt="image" src="https://github.com/user-attachments/assets/ff288437-dff9-403c-b2cd-27da222014f9" />
### Admin logged in view
<img width="1894" height="900" alt="image" src="https://github.com/user-attachments/assets/f80cdfb9-880e-4563-afb0-95e026542768" />
<img width="1896" height="905" alt="image" src="https://github.com/user-attachments/assets/ea04cff5-d33e-4015-8403-4200f16ad905" />
<img width="1893" height="905" alt="image" src="https://github.com/user-attachments/assets/eaf11bd0-40c8-49fe-a42f-8cc1027aaac8" />
### Normal user logged in view
<img width="1883" height="903" alt="image" src="https://github.com/user-attachments/assets/f2c18a97-3cdc-4e5a-842b-ef6e6a5558fb" />
<img width="1913" height="898" alt="image" src="https://github.com/user-attachments/assets/d33dbbc5-35dd-41a5-a2d8-abc58899f22b" />

## Reference & Acknowledgements & Resources Used

-   **UI Template**: [DarkPan - Free Bootstrap 5 Admin Template](https://themewagon.com/themes/free-bootstrap-5-admin-template-darkpan/) (Adapted for Jinja2) - (https://themewagon.github.io/darkpan/index.html)
-   **Icons**: [FontAwesome](https://fontawesome.com/) (CDN)
-   **Fonts**: [Google Fonts - Inter](https://fonts.google.com/specimen/Inter)
-   **Authentication**: [Passlib](https://passlib.readthedocs.io/) for password hashing.
-   **Database**: [PostgreSQL](https://www.postgresql.org/)
-   **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
-   **Testing**: [Pytest](https://docs.pytest.org/)
-   **Authentication**: [Passlib](https://passlib.readthedocs.io/) for password hashing.
-   **Reference git repo**: [Library-Management-System-FastAPI](https://github.com/rupsri5/Library-Management-System-FastAPI)
-   **Reference git repo**: [Library-Management-System](https://github.com/kurekhombre/Library-Management-System)

## Contact

-   **Author**: Prince Raiyani
-   **Email**: princeraiyani@vebuin.com
-   **GitHub**: [prince-raiyani-AI](https://github.com/prince-raiyani-AI)
