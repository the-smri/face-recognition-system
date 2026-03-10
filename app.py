from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
from datetime import datetime
from db_config import init_db, get_db_connection
from face_engine import register_user, recognize_faces

app = Flask(__name__)
app.secret_key = 'super_secret_attendance_system'

# Ensure required directories exist
for folder in ['dataset', 'encodings', 'database', 'models', 'attendance']:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Initialize database
init_db()

# --- Page Routes ---

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/recognize')
def recognize():
    return render_template('recognize.html')

@app.route('/history')
def history():
    return render_template('history.html')

# --- API Routes ---

@app.route('/api/stats')
def api_stats():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
    today_attendance = c.fetchone()[0]
    
    c.execute("SELECT id, student_id, name, created_at FROM users ORDER BY id DESC LIMIT 5")
    recent_users = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return jsonify({
        "total_users": total_users,
        "today_attendance": today_attendance,
        "recent_users": recent_users
    })

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    name = data.get('name')
    student_id = data.get('student_id')
    images = data.get('images', [])
    
    if not name or not student_id or not images:
        return jsonify({"error": "Missing required fields"}), 400
        
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE student_id = ?", (student_id,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "User with this ID already exists"}), 400
        
    success, msg = register_user(name, student_id, images)
    
    if success:
        c.execute("INSERT INTO users (name, student_id) VALUES (?, ?)", (name, student_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": msg})
    else:
        conn.close()
        return jsonify({"error": msg}), 400

@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    data = request.json
    base64_image = data.get('image')
    
    if not base64_image:
        return jsonify({"error": "No image provided"}), 400
        
    faces = recognize_faces(base64_image)
    
    conn = get_db_connection()
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    for face in faces:
        if face["name"] != "Unknown":
            # Check if this user was already marked today
            c.execute("SELECT id FROM users WHERE student_id = ?", (face["student_id"],))
            user_row = c.fetchone()
            if user_row:
                user_id = user_row["id"]
                c.execute("SELECT id FROM attendance WHERE user_id = ? AND date = ?", (user_id, today))
                if not c.fetchone():
                    # Mark attendance
                    c.execute("INSERT INTO attendance (user_id, date, time, status) VALUES (?, ?, ?, ?)",
                              (user_id, today, current_time, "Present"))
                    conn.commit()
                    face["status"] = "Marked"
                else:
                    face["status"] = "Already marked today"
    
    conn.close()
    return jsonify({"faces": faces})

@app.route('/api/history')
def api_history():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT a.date, a.time, u.student_id, u.name, a.status 
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC, a.time DESC
    ''')
    
    records = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify(records)

@app.route('/api/export')
def api_export():
    conn = get_db_connection()
    df = pd.read_sql_query('''
        SELECT a.date as Date, a.time as Time, u.student_id as "Student ID", u.name as Name, a.status as Status
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC, a.time DESC
    ''', conn)
    conn.close()
    
    export_path = 'attendance/export.csv'
    df.to_csv(export_path, index=False)
    
    return send_file(export_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
