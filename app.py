from flask import Flask, request, jsonify, send_from_directory, redirect, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__, static_folder='')
CORS(app)
app.secret_key = 'scancraft_secret_key'

# --- Database Configuration ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kalyan',  # change to your MySQL password
    'database': 'scancraft_db'
}

# --- Database Setup ---
def init_db():
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password']
    )
    c = conn.cursor()
    c.execute("CREATE DATABASE IF NOT EXISTS scancraft_db")
    conn.database = 'scancraft_db'

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS qr_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_email VARCHAR(255) NOT NULL,
        qr_type VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

init_db()

# --- Serve HTML ---
@app.route('/')
def serve_index():
    if 'user' in session:
        return send_from_directory('', 'index.html')
    return redirect('/login')

@app.route('/login')
def login_page():
    return send_from_directory('', 'login.html')

@app.route('/register')
def register_page():
    return send_from_directory('', 'register.html')

# --- Auth Routes ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = generate_password_hash(data.get('password'))

    try:
        conn = mysql.connector.connect(**db_config)
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "Registration successful"}), 201
    except mysql.connector.errors.IntegrityError:
        return jsonify({"error": "User already exists"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email = %s", (email,))
    row = c.fetchone()
    conn.close()

    if row and check_password_hash(row[0], password):
        session['user'] = email
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# --- QR Generator Route ---
@app.route('/generate', methods=['POST'])
def generate():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    content_type = data.get('type', 'text')
    content = data.get('content', '')

    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()

    if content_type == 'event':
        title = data.get('title', '')
        location = data.get('location', '')
        start = data.get('start', '')
        end = data.get('end', '')
        url = data.get('url', '')

        vcal = f"""BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//QRcdr//QRcdr 4.0//EN\nBEGIN:VEVENT\nLOCATION:{location}\nDTSTART:{start}\nDTEND:{end}\nSUMMARY:{title}\n"""
        if url:
            vcal += f"URL:{url}\n"
        vcal += """CLASS:PUBLIC\nBEGIN:VALARM\nTRIGGER:-PT5M\nACTION:DISPLAY\nDESCRIPTION:Reminder\nEND:VALARM\nEND:VEVENT\nEND:VCALENDAR"""

        c.execute("INSERT INTO qr_data (user_email, qr_type, content) VALUES (%s, %s, %s)",
                  (session['user'], 'event', vcal))
        display = f"Title: {title}\nLocation: {location}\nStart: {start}\nEnd: {end}\nURL: {url}"
        result = vcal
    else:
        c.execute("INSERT INTO qr_data (user_email, qr_type, content) VALUES (%s, %s, %s)",
                  (session['user'], 'text', content))
        display = result = content

    conn.commit()
    conn.close()

    return jsonify({'result': result, 'display': display})

@app.route('/history')
def view_history():
    if 'user' not in session:
        return redirect('/login')

    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()
    c.execute("SELECT qr_type, content, timestamp FROM qr_data WHERE user_email = %s", (session['user'],))
    rows = c.fetchall()
    conn.close()

    return jsonify(rows)

if __name__ == '__main__':
    app.run(debug=True)
