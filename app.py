from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:mysecretpassword@postgres-service/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'a_random_secret_key_hussen'  # Set a secret key for session management

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Todo(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    content = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String)
    status = db.Column(db.String)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle new todo creation
        content = request.form['content']
        due_date = parse_date(request.form.get('due_date'))
        priority = request.form.get('priority') if request.form.get('priority') else None
        status = request.form.get('status') if request.form.get('status') else None

        new_todo = Todo(content=content, due_date=due_date, priority=priority, status=status, user_id=session['user_id'])
        db.session.add(new_todo)
        db.session.commit()

        return redirect(url_for('index'))

    # Display the existing todos
    user_id = session['user_id']
    todos = Todo.query.filter_by(user_id=user_id).all()
    return render_template('index.html', todos=todos)

@app.route('/register', methods=['GET', 'POST'])
def register():
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


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()

#         if user and user.check_password(password):
#             session['user_id'] = user.id
#             flash('Login successful!', 'success')
#             return redirect(url_for('index'))
#         else:
#             flash('Invalid username or password.', 'error')

#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:
            print("User found: ", user.username)
            if user.check_password(password):
                print("Password correct")
                session['user_id'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                print("Password incorrect")
        else:
            print("User not found")

        flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/update/<todo_id>', methods=['GET', 'POST'])
def update_todo(todo_id):
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
    todo = Todo.query.get_or_404(todo_id)
    if 'user_id' not in session or todo.user_id != session['user_id']:
        return redirect(url_for('login'))

    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
    except ValueError:
        return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)