from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from datetime import datetime
import os

app = Flask(__name__)
# Configuration for SQLAlchemy with PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:mysecretpassword@postgres-service/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'a_random_secret_key_hussen'  # Set a secret key for session management

db = SQLAlchemy(app)

class User(db.Model):
    """
    User model representing a user in the database.
    Attributes:
        id (str): Unique identifier for the user.
        username (str): Username of the user.
        password_hash (str): Hashed password for the user.
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        """Sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)

class Todo(db.Model):
    """
    Todo model representing a to-do item in the database.
    Attributes:
        id (str): Unique identifier for the to-do item.
        content (str): The content of the to-do item.
        due_date (datetime.date): The due date of the to-do item.
        priority (str): The priority of the to-do item.
        status (str): The status of the to-do item.
        user_id (str): The user ID of the to-do item's owner.
    """
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    content = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String)
    status = db.Column(db.String)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Route for the main page of the application. Shows the todo list for the logged-in user and
    allows the creation of new todo items.
    GET: Renders the todo list.
    POST: Processes new todo item form submissions.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        content = request.form['content']
        due_date = parse_date(request.form.get('due_date'))
        priority = request.form.get('priority') if request.form.get('priority') else None
        status = request.form.get('status') if request.form.get('status') else None

        new_todo = Todo(content=content, due_date=due_date, priority=priority, status=status, user_id=session['user_id'])
        db.session.add(new_todo)
        db.session.commit()

        return redirect(url_for('index'))

    # Display all todos for the logged-in user
    user_id = session['user_id']
    todos = Todo.query.filter_by(user_id=user_id).all()
    return render_template('index.html', todos=todos)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for user registration.
    GET: Renders the registration form.
    POST: Processes the registration form, creates a new user if successful.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user is None:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.', 'error')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for user login.
    GET: Renders the login form.
    POST: Processes the login form, authenticates the user if successful.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Route for user logout. Ends the user session and redirects to the login page.
    """
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/update/<todo_id>', methods=['GET', 'POST'])
def update_todo(todo_id):
    """
    Route for updating an existing todo item.
    Args:
        todo_id (str): The ID of the todo item to update.
    GET: Renders the update form for the todo item.
    POST: Processes the update form and updates the todo item.
    """
    todo = Todo.query.get_or_404(todo_id)
    if 'user_id' not in session or todo.user_id != session['user_id']:
        return redirect(url_for('login'))

    if request.method == 'POST':
        todo.content = request.form.get('content', todo.content)
        todo.due_date = parse_date(request.form.get('due_date')) or todo.due_date
        todo.priority = request.form.get('priority') or todo.priority
        todo.status = request.form.get('status') or todo.status

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update.html', todo=todo)

@app.route('/delete/<todo_id>', methods=['POST'])
def delete_todo(todo_id):
    """
    Route for deleting an existing todo item.
    Args:
        todo_id (str): The ID of the todo item to delete.
    POST: Deletes the specified todo item.
    """
    todo = Todo.query.get_or_404(todo_id)
    if 'user_id' not in session or todo.user_id != session['user_id']:
        return redirect(url_for('login'))

    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

def parse_date(date_str):
    """
    Parses a string into a datetime.date object.
    Args:
        date_str (str): The date string to parse.
    Returns:
        datetime.date: The parsed date, or None if parsing fails.
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
    except ValueError:
        return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)