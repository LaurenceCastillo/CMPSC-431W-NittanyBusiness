from flask import Flask, render_template, request, url_for, redirect
import sqlite3 as sql
import hashlib  # Using hashlib instead of bcrypt for simplicity and speed

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

# HOME page route
@app.route('/')
def index():
    return render_template('login.html')

# LOGIN page route
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # This should match the name attribute in HTML

        if check_email(email):
            if check_password(email, password):
                return redirect(url_for('filler'))  # Redirect to dashboard or next page
            else:
                error = 'Incorrect password. Please try again.'
                return render_template('login.html', error=error)
        else:
            error = 'Email not found. Please try again.'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

# Dummy page after login
@app.route('/filler', methods=['POST', 'GET'])
def filler():
    return "Login successful! Welcome to the dashboard."

# Email checker function
def check_email(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(1) FROM Users WHERE email = ?', (email,))
    result = cursor.fetchone()
    connection.close()

    return result[0] > 0 if result else False

# Password checker function (using SHA256 hash)
def check_password(email, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()

    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT hash FROM Users WHERE email = ?', (email,))
    result = cursor.fetchone()
    connection.close()

    if result and hashed == result[0]:
        return True
    return False

# Optional: Function to hash password when adding new users
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    app.run(debug=True)