from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from datetime import datetime

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    author = StringField('Author', validators=[DataRequired(), Length(min=1, max=100)])
    isbn = StringField('ISBN', validators=[DataRequired(), Length(min=10, max=20)])
    category = StringField('Category', validators=[DataRequired(), Length(min=1, max=50)])
    published_year = IntegerField('Published Year', validators=[
        DataRequired(),
        NumberRange(min=1000, max=datetime.now().year, message="Must be a valid year")
    ])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    status = SelectField('Status', choices=[('Available', 'Available'), ('Borrowed', 'Borrowed')])

class MemberForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    membership_status = SelectField('Membership Status', 
                                   choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

class BorrowForm(FlaskForm):
    book_id = SelectField('Book', validators=[DataRequired()], coerce=int)
    member_id = SelectField('Member', validators=[DataRequired()], coerce=int)
    borrow_date = DateField('Borrow Date', format='%Y-%m-%d', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])

class ReturnForm(FlaskForm):
    borrowing_id = HiddenField('Borrowing ID', validators=[DataRequired()])
    return_date = DateField('Return Date', format='%Y-%m-%d', validators=[DataRequired()])

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    category = SelectField('Category', validators=[Optional()], choices=[])
    status = SelectField('Status', validators=[Optional()], choices=[
        ('', 'All Status'),
        ('Available', 'Available'),
        ('Borrowed', 'Borrowed')
    ])