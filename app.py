from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Database setup
DATABASE = 'qr_records.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS active_records
                 (code TEXT PRIMARY KEY, upi_info TEXT, data TEXT, creation_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS archived_records
                 (code TEXT PRIMARY KEY, upi_info TEXT, data TEXT, creation_date TEXT, deletion_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user[0] == password:  # Compare plaintext passwords (not secure)
            session['username'] = username  # Store username in session
            return redirect('/dashboard')  # Redirect to dashboard after login
        else:
            return "Invalid username or password", 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            return "Username already exists. Please choose a different username.", 400

        # Insert the new user into the database
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        upi_info = request.form['upi_info']
        
        # Automatically generate a unique code (e.g., timestamp)
        code = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Automatically fetch the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate QR code data
        data = f"Code: {code}\nUPI: {upi_info}\nDate: {current_time}"
        
        # Store record in the database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO active_records (code, upi_info, data, creation_date) VALUES (?, ?, ?, ?)",
                  (code, upi_info, data, current_time))
        conn.commit()
        conn.close()
        
        return render_template('generate.html', qr_code_data=data)
    
    return render_template('generate.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Handle POST request (scanned data from frontend)
        scanned_data = request.json.get('data')
        
        # Verify the scanned data
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM active_records WHERE data=?", (scanned_data,))
        record = c.fetchone()
        conn.close()
        
        if record:
            return jsonify(result="Record exists in the database.", record=record)
        else:
            return jsonify(result="Record does not exist in the database.")
    
    # Handle GET request (render the verify page)
    return render_template('verify.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Handle POST request (scanned data from frontend)
        scanned_data = request.json.get('data')
        code = scanned_data.split("\n")[0].split(": ")[1]
        
        # Automatically fetch the deletion date and time
        deletion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Move record to archive
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM active_records WHERE code=?", (code,))
        record = c.fetchone()
        if record:
            c.execute("INSERT INTO archived_records (code, upi_info, data, creation_date, deletion_date) VALUES (?, ?, ?, ?, ?)",
                      (record[0], record[1], record[2], record[3], deletion_time))
            c.execute("DELETE FROM active_records WHERE code=?", (code,))
            conn.commit()
            conn.close()
            return jsonify(result=f"Record with code {code} has been archived and deleted.")
        else:
            return jsonify(result=f"No active record found with code {code}.")
    
    # Handle GET request (render the delete page)
    return render_template('delete.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'), debug=True)