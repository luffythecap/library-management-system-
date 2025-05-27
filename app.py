import os
import logging
from flask import Flask
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "library_management_secret")

# Initialize in-memory data structures for MVP
books = [
    {
        "id": 1,
        "title": "Python Programming",
        "author": "John Smith",
        "isbn": "978-1234567890",
        "category": "Programming",
        "published_year": 2020,
        "status": "Available",
        "description": "A comprehensive guide to Python programming language."
    },
    {
        "id": 2,
        "title": "Web Development with Flask",
        "author": "Jane Doe",
        "isbn": "978-0987654321",
        "category": "Web Development",
        "published_year": 2019,
        "status": "Available",
        "description": "Learn to build web applications using Flask framework."
    }
]

members = [
    {
        "id": 1,
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "phone": "123-456-7890",
        "join_date": datetime.now().strftime("%Y-%m-%d"),
        "membership_status": "Active"
    }
]

# Borrowing records format:
# {id, book_id, member_id, borrow_date, due_date, return_date, status}
borrowings = []

# Functions to generate new IDs
def get_next_book_id():
    return max([book["id"] for book in books], default=0) + 1

def get_next_member_id():
    return max([member["id"] for member in members], default=0) + 1

def get_next_borrowing_id():
    return max([b["id"] for b in borrowings], default=0) + 1

# Export data structures so they can be imported elsewhere
app.config["BOOKS"] = books
app.config["MEMBERS"] = members
app.config["BORROWINGS"] = borrowings
app.config["GET_NEXT_BOOK_ID"] = get_next_book_id
app.config["GET_NEXT_MEMBER_ID"] = get_next_member_id
app.config["GET_NEXT_BORROWING_ID"] = get_next_borrowing_id
