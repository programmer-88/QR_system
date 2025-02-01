from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
DATABASE = 'qr_records.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS active_records
                 (code TEXT PRIMARY KEY, upi_info TEXT, data TEXT, creation_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS archived_records
                 (code TEXT PRIMARY KEY, upi_info TEXT, data TEXT, creation_date TEXT, deletion_date TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
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
    app.run(host='192.168.1.162', port=5000, ssl_context=('cert.pem', 'key.pem'), debug=True)