from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:mysecretpassword@postgres-service/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    content = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String)
    status = db.Column(db.String)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form['content']
        due_date = parse_date(request.form.get('due_date'))
        priority = request.form.get('priority') if request.form.get('priority') else None
        status = request.form.get('status') if request.form.get('status') else None

        new_todo = Todo(content=content, due_date=due_date, priority=priority, status=status)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('index'))

    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

@app.route('/update/<todo_id>', methods=['GET', 'POST'])
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
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







# from flask import Flask, request, render_template, redirect, url_for
# from cassandra.cluster import Cluster
# from cassandra.auth import PlainTextAuthProvider
# from cassandra.query import SimpleStatement
# from uuid import uuid4
# from datetime import datetime
# import uuid
# import os

# app = Flask(__name__)
# # todos = []  # Temporary list to store todo items

# # Cassandra connection setup
# CASSANDRA_HOST = 'cassandra-service'  # Kubernetes service name for Cassandra
# cluster = Cluster([CASSANDRA_HOST], port=9042)
# session = cluster.connect()

# # Create keyspace and table if they don't exist
# session.execute("""
#     CREATE KEYSPACE IF NOT EXISTS todo_keyspace
#     WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1}
# """)

# session.execute("""
#     CREATE TABLE IF NOT EXISTS todo_keyspace.todos (
#         id UUID PRIMARY KEY,
#         content TEXT,
#         due_date TIMESTAMP,
#         priority TEXT,
#         status TEXT,
#         tags SET<TEXT>
#     )
# """)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     sort_by = request.args.get('sort_by', 'due_date')  # Default sort by due date
    
#     if request.method == 'POST':
#         content = request.form['content']
#         due_date = request.form['due_date'] or None
#         priority = request.form['priority'] if request.form['priority'] else None
#         status = request.form['status'] if request.form['status'] else None
#         tags = set(request.form.getlist('tags')) or set()

#         insert_todo(content, due_date, priority, status, tags)
#         return redirect(url_for('index'))
    
#     todos = get_all_todos()
#     return render_template('index.html', todos=todos)

# @app.route('/update/<todo_id>', methods=['GET', 'POST'])
# def update_todo(todo_id):
#     # Fetch the current data for the todo item
#     todo = get_todo_by_id(todo_id)

#     if request.method == 'POST':
#         content = request.form.get('content')
#         due_date = request.form.get('due_date')
#         priority = request.form.get('priority')
#         status = request.form.get('status')
#         tags = set(request.form.getlist('tags'))

#         update_todo_item(todo_id, content, due_date, priority, status, tags)
#         return redirect(url_for('index'))
#     else:
#         # Render a form pre-populated with todo item data
#         return render_template('update.html', todo=todo)

# @app.route('/delete/<todo_id>', methods=['POST'])
# def delete_todo(todo_id):
#     delete_todo_item(todo_id)
#     return redirect(url_for('index'))



# def insert_todo(content, due_date=None, priority=None, status=None, tags=None):
#     session.execute(
#         """
#         INSERT INTO todo_keyspace.todos (id, content, due_date, priority, status, tags)
#         VALUES (%s, %s, %s, %s, %s, %s)
#         """,
#         (uuid4(), content, due_date, priority, status, tags or set())
#     )


# def format_date(date):
#     if date is not None:
#         return date.strftime("%B %d, %Y")
#     return None

# def get_all_todos():
#     query = "SELECT * FROM todo_keyspace.todos"
#     result = session.execute(query)
#     return [
#         {
#             "id": row.id,
#             "content": row.content,
#             "due_date": format_date(row.due_date),
#             "priority": row.priority,
#             "status": row.status,
#             "tags": row.tags
#         } for row in result
#     ]

# # Function to get a single todo item by its ID
# def get_todo_by_id(todo_id):
#     # Convert the string to a UUID object
#     todo_uuid = uuid.UUID(todo_id)
    
#     query = "SELECT * FROM todo_keyspace.todos WHERE id=%s"
#     result = session.execute(query, [todo_uuid])
#     return result[0] if result else None

# # Function to update a todo item
# def update_todo_item(todo_id, content, due_date, priority, status, tags):
#     # Convert the string to a UUID object
#     todo_uuid = uuid.UUID(todo_id)

#     query = """
#     UPDATE todo_keyspace.todos
#     SET content=%s, due_date=%s, priority=%s, status=%s, tags=%s
#     WHERE id=%s
#     """
#     session.execute(query, [content, due_date, priority, status, tags, todo_uuid])

# # Function to delete a todo item
# def delete_todo_item(todo_id):
#     # Convert the string to a UUID object
#     todo_uuid = uuid.UUID(todo_id)

#     query = "DELETE FROM todo_keyspace.todos WHERE id=%s"
#     session.execute(query, [todo_uuid])




# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

