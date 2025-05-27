from datetime import datetime, timedelta

# Models are defined here for reference, but we're using in-memory dictionaries
# for the MVP instead of a database ORM

class Book:
    def __init__(self, id, title, author, isbn, category, published_year, status="Available", description=""):
        self.id = id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.published_year = published_year
        self.status = status  # "Available", "Borrowed"
        self.description = description

class Member:
    def __init__(self, id, name, email, phone, join_date=None, membership_status="Active"):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.join_date = join_date or datetime.now().strftime("%Y-%m-%d")
        self.membership_status = membership_status  # "Active", "Inactive"

class Borrowing:
    def __init__(self, id, book_id, member_id, borrow_date=None, due_date=None):
        self.id = id
        self.book_id = book_id
        self.member_id = member_id
        self.borrow_date = borrow_date or datetime.now().strftime("%Y-%m-%d")
        # Default due date is 14 days from borrow date
        if due_date:
            self.due_date = due_date
        else:
            borrow_datetime = datetime.strptime(self.borrow_date, "%Y-%m-%d")
            self.due_date = (borrow_datetime + timedelta(days=14)).strftime("%Y-%m-%d")
        self.return_date = None
        self.status = "Borrowed"  # "Borrowed", "Returned", "Overdue"
