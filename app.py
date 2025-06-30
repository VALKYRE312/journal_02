from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 🔒 Needed for session management

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}, "entries": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# 🔽 All your routes go here 🔽
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    user = session['user']
    user_entries = data["entries"].get(user, [])
    return render_template('journal.html', entries=user_entries)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = load_data()
        email = request.form['email']
        password = request.form['password']
        if email in data['users']:
            return "User already exists."
        data['users'][email] = generate_password_hash(password)
        data['entries'][email] = []
        save_data(data)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = load_data()
        email = request.form['email']
        password = request.form['password']
        user_pass_hash = data['users'].get(email)
        if user_pass_hash and check_password_hash(user_pass_hash, password):
            session['user'] = email
            return redirect(url_for('home'))
        return "Invalid credentials."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/add_entry', methods=['POST'])
def add_entry():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    data = load_data()
    email = session['user']
    entry_id = request.form.get('entry_id')
    
    image = request.files.get('image')
    image_filename = None
    if image and image.filename != '':
        image_filename = image.filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
            # Ensure unique ID
    existing_ids = [e['id'] for e in data['entries'][email]]
    new_id = max(existing_ids, default=0) + 1
    
    
    new_entry = {
         'id': new_id,
        'title': request.form['title'],
        'content': request.form['content'],
        'date': datetime.now().strftime("%B %d, %Y"),
        'tags': request.form['tags'].split(','),
        'mood': request.form['mood'],
        'image': image_filename
    }
    if entry_id:  # ✨ EDIT MODE
        for entry in data['entries'][email]:
            if str(entry['id']) == str(entry_id):
                entry.update(new_entry)
                break
    else:  # ✨ ADD NEW ENTRY
        # assign new unique ID
        existing_ids = [e['id'] for e in data['entries'][email]]
        new_entry['id'] = max(existing_ids, default=0) + 1
        data['entries'][email].append(new_entry)
        
    
    save_data(data)
    return redirect(url_for('home'))

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    data = load_data()
    email = session['user']
    data['entries'][email] = [e for e in data['entries'][email] if e['id'] != entry_id]
    save_data(data)
    return redirect(url_for('home'))

@app.route('/entry/<int:entry_id>')
def view_entry(entry_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = load_data()
    email = session['user']
    entry = next((e for e in data['entries'][email] if e['id'] == entry_id), None)
    if entry:
        return jsonify(entry)
    return jsonify({'error': 'Entry not found'}), 404

# 🔚 Then finally:
if __name__ == '__main__':
    app.run(debug=True)
