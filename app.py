from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3, base64, uuid
from serial_comm import FingerScanner

app = Flask(__name__)
app.secret_key = "secure_vote_secret"

# ----------------- DATABASE -----------------
def get_db():
    conn = sqlite3.connect("voting_system.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            reg_no TEXT,
            fingerprint_template TEXT UNIQUE,
            session_token TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id INTEGER,
            candidate TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ----------------- ROUTES -----------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------- ENROLL ----------
@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        reg_no = data.get('reg_no')

        if not name or not reg_no:
            return jsonify({'status': 'fail', 'message': 'Name and Register Number are required.'})

        scanner = FingerScanner()
        res = scanner.enroll(reg_no)
        scanner.close()

        if res['status'] == 'ok' and res['template']:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id FROM voters WHERE reg_no=?", (reg_no,))
            if cur.fetchone():
                conn.close()
                return jsonify({'status': 'fail', 'message': 'This Register Number is already enrolled.'})

            session_token = str(uuid.uuid4())
            cur.execute("INSERT INTO voters (name, reg_no, fingerprint_template, session_token) VALUES (?, ?, ?, ?)",
                        (name, reg_no, res['template'], session_token))
            conn.commit()
            voter_id = cur.lastrowid
            conn.close()

            session['voter_id'] = voter_id
            session['session_token'] = session_token

            return jsonify({'status': 'ok', 'message': f'✅ {name} ({reg_no}) enrolled successfully!'})
        else:
            return jsonify({'status': 'fail', 'message': res['message']})

    return render_template('enroll.html')

# ---------- AUTH ----------
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        reg_no = data.get('reg_no')

        if not name or not reg_no:
            return jsonify({'status': 'fail', 'message': 'Name and Register Number required for authentication.'})

        scanner = FingerScanner()
        res = scanner.verify(reg_no)
        scanner.close()

        if res['status'] == 'ok' and res['match']:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id FROM voters WHERE name=? AND reg_no=?", (name, reg_no))
            voter = cur.fetchone()
            conn.close()

            if not voter:
                return jsonify({'status': 'fail', 'message': 'Voter not found. Please enroll first.'})

            voter_id = voter['id']
            session_token = str(uuid.uuid4())

            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE voters SET session_token=? WHERE id=?", (session_token, voter_id))
            conn.commit()
            conn.close()

            session['voter_id'] = voter_id
            session['session_token'] = session_token

            return jsonify({'status': 'ok', 'message': f'✅ Welcome {name}! Fingerprint verified.'})
        else:
            return jsonify({'status': 'fail', 'message': 'Fingerprint mismatch. Try again.'})

    return render_template('auth.html')

# ---------- VOTE ----------
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        if 'voter_id' not in session or 'session_token' not in session:
            return jsonify({'status': 'fail', 'message': 'Not authenticated.'})

        voter_id = session['voter_id']
        candidate = request.form.get('candidate')

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM votes WHERE voter_id=?", (voter_id,))
        if cur.fetchone():
            conn.close()
            return jsonify({'status': 'fail', 'message': 'You have already voted.'})

        cur.execute("INSERT INTO votes (voter_id, candidate) VALUES (?, ?)", (voter_id, candidate))
        conn.commit()
        conn.close()

        # clear session for logout
        session.clear()

        return jsonify({
            'status': 'ok',
            'message': '✅ Your vote has been successfully recorded! Redirecting to home page...'
        })

    if 'voter_id' not in session:
        return redirect(url_for('home'))

    return render_template('vote.html')

# ---------- RESULTS ----------
@app.route('/results')
def results():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT candidate, COUNT(*) as votes FROM votes GROUP BY candidate")
    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
