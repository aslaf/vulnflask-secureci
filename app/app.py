from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "dev-secret"  # weak secret for demo
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT,
      password TEXT,
      role TEXT
    );
    CREATE TABLE IF NOT EXISTS products(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      description TEXT,
      price REAL
    );
    """)
    try:
        db.execute("INSERT INTO users (username,password,role) VALUES ('admin','adminpass','admin')")
        db.execute("INSERT INTO users (username,password,role) VALUES ('alice','password','user')")
        db.execute("INSERT INTO products (name,description,price) VALUES ('Widget','<b>Great widget</b>',9.99)")
        db.execute("INSERT INTO products (name,description,price) VALUES ('Gadget','<script>alert(1)</script>',19.99)")
        db.commit()
    except Exception:
        pass
    db.close()

@app.route('/')
def index():
    db = get_db()
    items = db.execute("SELECT * FROM products").fetchall()
    return render_template('index.html', products=items)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # ❌ Vulnerable SQL Injection
        db = get_db()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        user = db.execute(query).fetchone()
        if user:
            session['user'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/search')
def search():
    q = request.args.get('q','')
    db = get_db()
    # ❌ SQLi via string interpolation
    rows = db.execute(f"SELECT * FROM products WHERE name LIKE '%{q}%'").fetchall()
    return render_template('search.html', products=rows, q=q)

@app.route('/admin')
def admin():
    # ❌ Broken access control: anyone can access
    return render_template('admin.html', user=session.get('user','guest'))

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
