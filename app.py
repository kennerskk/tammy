from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth
import hashlib

# Initialize Firebase
cred = credentials.Certificate('mydb-for-my-online-game-firebase-adminsdk-7wr7k-0d103647a0.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mydb-for-my-online-game-default-rtdb.firebaseio.com'
})

# Initialize Flask
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# Set a secret key for session management

# Define routes

@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/login', methods=['POST'])
def do_login():
    name = request.form['name']
    password = request.form['password']

    # Hash password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Check if user exists and password is correct
    ref = db.reference('users')
    users = ref.order_by_child('name').equal_to(name).get()
    if users:
        for user_key, user_data in users.items():
            if user_data['password'] == hashed_password:
                # User authenticated, set session and redirect to dashboard
                session['user'] = name
                return redirect(url_for('dashboard'))

    # If user does not exist or password is incorrect, show error message and redirect to login page
    flash('Invalid username or password', 'error')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    else:
        # If user is not logged in, redirect to login page
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Clear session and redirect to login page
    session.pop('user', None)
    return redirect(url_for('login'))
@app.route('/')
def register():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def do_register():
    name = request.form['name']
    password = request.form['password']

    ref = db.reference('users')
    user_exists = ref.order_by_child('name').equal_to(name).get()
    if user_exists:
        flash('Username already exists!', 'error')
        return redirect(url_for('register'))
    
    # Check if the password meets certain criteria (e.g., minimum length)
    if len(password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return redirect(url_for('register'))
    
    # Hash password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Store data in Firebase
    ref = db.reference('users')
    new_user = ref.push({
        'name': name,
        'password': hashed_password
    })

    return redirect(url_for('login'))

    
if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0', port=80)