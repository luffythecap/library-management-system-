from flask import (
    render_template, redirect, url_for, flash, request, session,
    abort, jsonify
)
from app import app
from forms import BookForm, MemberForm, BorrowForm, ReturnForm, SearchForm
from datetime import datetime, timedelta, date 

# Home route
@app.route('/')
def index():
    books = app.config["BOOKS"]
    members = app.config["MEMBERS"]
    borrowings = app.config["BORROWINGS"]

    # Count statistics
    total_books = len(books)
    available_books = sum(1 for book in books if book["status"] == "Available")
    borrowed_books = total_books - available_books
    total_members = len(members)

    # Get recent activity (last 5 borrowings)
    recent_borrowings = sorted(
        borrowings,
        key=lambda x: datetime.strptime(x["borrow_date"], "%Y-%m-%d")
        if isinstance(x["borrow_date"], str) else x["borrow_date"],
        reverse=True
    )[:5]

    # Enhance with book/member info and normalize due_date to date
    for borrow in recent_borrowings:
        book = next((b for b in books if b["id"] == borrow["book_id"]), None)
        member = next((m for m in members if m["id"] == borrow["member_id"]), None)
        if book and member:
            borrow["book_title"] = book["title"]
            borrow["member_name"] = member["name"]
        # Convert due_date to date object if it's a string
        if isinstance(borrow["due_date"], str):
            borrow["due_date"] = datetime.strptime(borrow["due_date"], "%Y-%m-%d").date()
        elif isinstance(borrow["due_date"], datetime):
            borrow["due_date"] = borrow["due_date"].date()

    # Normalize all due_dates in borrowings for comparison
    for borrow in borrowings:
        if isinstance(borrow["due_date"], str):
            borrow["due_date"] = datetime.strptime(borrow["due_date"], "%Y-%m-%d").date()
        elif isinstance(borrow["due_date"], datetime):
            borrow["due_date"] = borrow["due_date"].date()

    today = date.today()  # Only use date for clean comparison

    overdue_count = sum(
        1 for borrow in borrowings
        if borrow["status"] == "Borrowed" and borrow["due_date"] < today
    )

    return render_template(
        'index.html',
        total_books=total_books,
        available_books=available_books,
        borrowed_books=borrowed_books,
        total_members=total_members,
        recent_borrowings=recent_borrowings,
        overdue_count=overdue_count,
        now_date=today
    )

# Book routes
@app.route('/books')
def books_index():
    books = app.config["BOOKS"]
    search_form = SearchForm()
    
    # Get unique categories for filter dropdown
    categories = sorted(list(set(book["category"] for book in books)))
    search_form.category.choices = [('', 'All Categories')] + [(c, c) for c in categories]
    
    # Apply filters if any
    filtered_books = books
    if request.args.get('query'):
        query = request.args.get('query').lower()
        filtered_books = [
            book for book in filtered_books 
            if query in book["title"].lower() or 
               query in book["author"].lower() or 
               query in book["isbn"].lower()
        ]
    
    if request.args.get('category') and request.args.get('category') != '':
        category = request.args.get('category')
        filtered_books = [book for book in filtered_books if book["category"] == category]
    
    if request.args.get('status') and request.args.get('status') != '':
        status = request.args.get('status')
        filtered_books = [book for book in filtered_books if book["status"] == status]
    
    return render_template('books/index.html', books=filtered_books, form=search_form)

@app.route('/books/add', methods=['GET', 'POST'])
def books_add():
    form = BookForm()
    if form.validate_on_submit():
        books = app.config["BOOKS"]
        new_book = {
            "id": app.config["GET_NEXT_BOOK_ID"](),
            "title": form.title.data,
            "author": form.author.data,
            "isbn": form.isbn.data,
            "category": form.category.data,
            "published_year": form.published_year.data,
            "description": form.description.data,
            "status": form.status.data
        }
        books.append(new_book)
        flash('Book added successfully!', 'success')
        return redirect(url_for('books_index'))
    return render_template('books/add.html', form=form)

@app.route('/books/<int:id>')
def books_view(id):
    books = app.config["BOOKS"]
    book = next((book for book in books if book["id"] == id), None)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('books_index'))
    
    # Get borrowing history for this book
    borrowings = app.config["BORROWINGS"]
    members = app.config["MEMBERS"]
    book_borrowings = [b for b in borrowings if b["book_id"] == id]
    
    # Add member names to borrowings
    for borrow in book_borrowings:
        member = next((m for m in members if m["id"] == borrow["member_id"]), None)
        if member:
            borrow["member_name"] = member["name"]
    
    return render_template('books/view.html', book=book, borrowings=book_borrowings)

@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def books_edit(id):
    books = app.config["BOOKS"]
    book = next((book for book in books if book["id"] == id), None)
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('books_index'))
    
    form = BookForm(obj=None)
    
    if request.method == 'GET':
        form.title.data = book["title"]
        form.author.data = book["author"]
        form.isbn.data = book["isbn"]
        form.category.data = book["category"]
        form.published_year.data = book["published_year"]
        form.description.data = book["description"]
        form.status.data = book["status"]
    
    if form.validate_on_submit():
        book["title"] = form.title.data
        book["author"] = form.author.data
        book["isbn"] = form.isbn.data
        book["category"] = form.category.data
        book["published_year"] = form.published_year.data
        book["description"] = form.description.data
        book["status"] = form.status.data
        
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books_index'))
    
    return render_template('books/edit.html', form=form, book=book)

@app.route('/books/delete/<int:id>', methods=['POST'])
def books_delete(id):
    books = app.config["BOOKS"]
    borrowings = app.config["BORROWINGS"]
    
    # Check if book is currently borrowed
    is_borrowed = any(
        b["book_id"] == id and b["status"] == "Borrowed" 
        for b in borrowings
    )
    
    if is_borrowed:
        flash('Cannot delete book that is currently borrowed', 'danger')
        return redirect(url_for('books_index'))
    
    book_idx = next((i for i, book in enumerate(books) if book["id"] == id), None)
    if book_idx is not None:
        del books[book_idx]
        flash('Book deleted successfully!', 'success')
    else:
        flash('Book not found', 'danger')
    
    return redirect(url_for('books_index'))

# Member routes
@app.route('/members')
def members_index():
    members = app.config["MEMBERS"]
    search_query = request.args.get('query', '').lower()
    
    if search_query:
        filtered_members = [
            member for member in members 
            if search_query in member["name"].lower() or 
               search_query in member["email"].lower() or 
               search_query in member["phone"].lower()
        ]
    else:
        filtered_members = members
    
    return render_template('members/index.html', members=filtered_members)

@app.route('/members/add', methods=['GET', 'POST'])
def members_add():
    form = MemberForm()
    if form.validate_on_submit():
        members = app.config["MEMBERS"]
        new_member = {
            "id": app.config["GET_NEXT_MEMBER_ID"](),
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "membership_status": form.membership_status.data
        }
        members.append(new_member)
        flash('Member added successfully!', 'success')
        return redirect(url_for('members_index'))
    return render_template('members/add.html', form=form)

@app.route('/members/<int:id>')
def members_view(id):
    members = app.config["MEMBERS"]
    member = next((member for member in members if member["id"] == id), None)
    if not member:
        flash('Member not found', 'danger')
        return redirect(url_for('members_index'))
    
    # Get borrowing history for this member
    borrowings = app.config["BORROWINGS"]
    books = app.config["BOOKS"]
    member_borrowings = [b for b in borrowings if b["member_id"] == id]
    
    # Add book titles to borrowings
    for borrow in member_borrowings:
        book = next((b for b in books if b["id"] == borrow["book_id"]), None)
        if book:
            borrow["book_title"] = book["title"]
        # Convert due_date from string to date object if it's not already
        if isinstance(borrow["due_date"], str):
            borrow["due_date"] = datetime.strptime(borrow["due_date"], "%Y-%m-%d").date()
    
    # Calculate statistics
    total_borrowed = len(member_borrowings)
    currently_borrowed = sum(1 for b in member_borrowings if b["status"] == "Borrowed")
    today = date.today()
    overdue_books = sum(
        1 for b in member_borrowings 
        if b["status"] == "Borrowed" and b["due_date"] < today
    )
    
    return render_template(
        'members/view.html', 
        member=member, 
        borrowings=member_borrowings,
        total_borrowed=total_borrowed,
        currently_borrowed=currently_borrowed,
        overdue_books=overdue_books,
        now_date=today  # ✅ Pass current date to template
    )

@app.route('/members/edit/<int:id>', methods=['GET', 'POST'])
def members_edit(id):
    members = app.config["MEMBERS"]
    member = next((member for member in members if member["id"] == id), None)
    if not member:
        flash('Member not found', 'danger')
        return redirect(url_for('members_index'))
    
    form = MemberForm(obj=None)
    
    if request.method == 'GET':
        form.name.data = member["name"]
        form.email.data = member["email"]
        form.phone.data = member["phone"]
        form.membership_status.data = member["membership_status"]
    
    if form.validate_on_submit():
        member["name"] = form.name.data
        member["email"] = form.email.data
        member["phone"] = form.phone.data
        member["membership_status"] = form.membership_status.data
        
        flash('Member updated successfully!', 'success')
        return redirect(url_for('members_index'))
    
    return render_template('members/edit.html', form=form, member=member)

@app.route('/members/delete/<int:id>', methods=['POST'])
def members_delete(id):
    members = app.config["MEMBERS"]
    borrowings = app.config["BORROWINGS"]
    
    # Check if member has any active borrowings
    has_active_borrowings = any(
        b["member_id"] == id and b["status"] == "Borrowed" 
        for b in borrowings
    )
    
    if has_active_borrowings:
        flash('Cannot delete member with active borrowings', 'danger')
        return redirect(url_for('members_index'))
    
    member_idx = next((i for i, member in enumerate(members) if member["id"] == id), None)
    if member_idx is not None:
        del members[member_idx]
        flash('Member deleted successfully!', 'success')
    else:
        flash('Member not found', 'danger')
    
    return redirect(url_for('members_index'))

# Borrowing routes
@app.route("/borrow")
def borrow_index():
    borrowings = app.config["BORROWINGS"]
    books = app.config["BOOKS"]
    members = app.config["MEMBERS"]
    
    borrowings_with_details = []
    for borrow in borrowings:
        book = next((b for b in books if b["id"] == borrow["book_id"]), None)
        member = next((m for m in members if m["id"] == borrow["member_id"]), None)

        if book and member:
            borrowing_copy = borrow.copy()
            borrowing_copy["book_title"] = book["title"]
            borrowing_copy["member_name"] = member["name"]
            
            # ✅ Safe handling for due_date
            due_date = borrow["due_date"]
            if isinstance(due_date, str):
                borrowing_copy["due_date_obj"] = datetime.strptime(due_date, "%Y-%m-%d").date()
            elif isinstance(due_date, datetime):
                borrowing_copy["due_date_obj"] = due_date.date()
            else:
                borrowing_copy["due_date_obj"] = due_date

            borrowings_with_details.append(borrowing_copy)
    
    borrowings_with_details.sort(
        key=lambda x: datetime.strptime(x["borrow_date"], "%Y-%m-%d"), 
        reverse=True
    )
    
    now_date = datetime.now().date()

    return render_template(
        'borrow/index.html',
        borrowings=borrowings_with_details,
        now_date=now_date
    )


@app.route('/borrow/add', methods=['GET', 'POST'])
def borrow_add():
    books = app.config["BOOKS"]
    members = app.config["MEMBERS"]
    
    # Filter only available books
    available_books = [book for book in books if book["status"] == "Available"]
    # Filter only active members
    active_members = [member for member in members if member["membership_status"] == "Active"]
    
    form = BorrowForm()
    form.book_id.choices = [(book["id"], f"{book['title']} by {book['author']}") for book in available_books]
    form.member_id.choices = [(member["id"], member["name"]) for member in active_members]
    
    # Set default dates
    if request.method == 'GET':
        form.borrow_date.data = datetime.now()
        form.due_date.data = datetime.now() + timedelta(days=14)
    
    if form.validate_on_submit():
        borrowings = app.config["BORROWINGS"]
        
        # Add new borrowing record
        new_borrowing = {
            "id": app.config["GET_NEXT_BORROWING_ID"](),
            "book_id": form.book_id.data,
            "member_id": form.member_id.data,
            "borrow_date": form.borrow_date.data.strftime("%Y-%m-%d"),
            "due_date": form.due_date.data.strftime("%Y-%m-%d"),
            "return_date": None,
            "status": "Borrowed"
        }
        borrowings.append(new_borrowing)
        
        # Update book status
        book = next((book for book in books if book["id"] == form.book_id.data), None)
        if book:
            book["status"] = "Borrowed"
        
        flash('Book borrowed successfully!', 'success')
        return redirect(url_for('borrow_index'))
    
    return render_template('borrow/add.html', form=form)

@app.route('/borrow/return/<int:id>', methods=['GET', 'POST'])
def borrow_return(id):
    borrowings = app.config["BORROWINGS"]
    borrowing = next((b for b in borrowings if b["id"] == id), None)
    
    if not borrowing:
        flash('Borrowing record not found', 'danger')
        return redirect(url_for('borrow_index'))
    
    if borrowing["status"] == "Returned":
        flash('This book has already been returned', 'warning')
        return redirect(url_for('borrow_index'))
    
    form = ReturnForm(obj=None)
    form.borrowing_id.data = id
    
    if request.method == 'GET':
        form.return_date.data = datetime.now()
    
    if form.validate_on_submit():
        # Update borrowing record
        borrowing["return_date"] = form.return_date.data.strftime("%Y-%m-%d")
        borrowing["status"] = "Returned"
        
        # Update book status
        books = app.config["BOOKS"]
        book = next((book for book in books if book["id"] == borrowing["book_id"]), None)
        if book:
            book["status"] = "Available"
        
        flash('Book returned successfully!', 'success')
        return redirect(url_for('borrow_index'))
    
    # Get book and member details for display
    books = app.config["BOOKS"]
    members = app.config["MEMBERS"]
    book = next((b for b in books if b["id"] == borrowing["book_id"]), None)
    member = next((m for m in members if m["id"] == borrowing["member_id"]), None)
    
    return render_template(
        'borrow/return.html', 
        form=form, 
        borrowing=borrowing,
        book=book,
        member=member
    )

# Reports routes
@app.route('/reports/overdue')
def reports_overdue():
    borrowings = app.config["BORROWINGS"]
    books = app.config["BOOKS"]
    members = app.config["MEMBERS"]
    
    today = datetime.now().date()  # Get today's date without time
    overdue_borrowings = []

    for b in borrowings:
        if b["status"] == "Borrowed":
            # Ensure due_date is a datetime.date object
            due_date = b["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()  # Convert string to date
            elif isinstance(due_date, datetime):
                due_date = due_date.date()  # Convert datetime to date
            
            # Check if due_date is before today (i.e., overdue)
            if due_date < today:
                b_copy = b.copy()  # Avoid modifying the original data
                
                # Add book and member details
                book = next((bk for bk in books if bk["id"] == b["book_id"]), None)
                member = next((m for m in members if m["id"] == b["member_id"]), None)

                if book and member:
                    b_copy["book_title"] = book["title"]
                    b_copy["book_author"] = book["author"]
                    b_copy["member_name"] = member["name"]
                    b_copy["member_email"] = member["email"]
                    b_copy["member_phone"] = member["phone"]
                    b_copy["days_overdue"] = (today - due_date).days

                    overdue_borrowings.append(b_copy)

    # Sort by most overdue first
    overdue_borrowings.sort(key=lambda x: x.get("days_overdue", 0), reverse=True)
    
    return render_template('reports/overdue.html', borrowings=overdue_borrowings)

@app.route('/reports/available')
def reports_available():
    books = app.config["BOOKS"]
    
    # Filter only available books
    available_books = [book for book in books if book["status"] == "Available"]
    
    # Apply category filter if provided
    category = request.args.get('category', '')
    if category:
        available_books = [book for book in available_books if book["category"] == category]
    
    # Get all unique categories for filter
    categories = sorted(list(set(book["category"] for book in books)))
    
    return render_template(
        'reports/available.html', 
        books=available_books,
        categories=categories,
        selected_category=category
    )
