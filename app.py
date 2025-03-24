from flask import Flask, render_template, request, url_for, redirect
import sqlite3 as sql
#import hashlib
import bcrypt

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

#home page immediately renders login page
@app.route('/')
def index():
    return render_template('login.html')

#login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_email(email): #check if email is in Users table
            if check_password(email, password): #verify password
                return redirect(url_for('filler'))  #redirect to next page
            else:
                error = 'Incorrect password. Please try again.'
                return render_template('login.html', error=error)
        else:
            error = 'Email not found. Please try again.'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

#dummy page meant to demonstrate successful login
@app.route('/filler', methods=['POST', 'GET'])
def filler():
    return "Login successful!"

#does email exist in Users
def check_email(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(1) FROM Users WHERE email = ?', (email,))
    result = cursor.fetchone()
    connection.close()

    return result[0] > 0 if result else False

#check if password is valid (passwords were generated using SHA256 + salt from the bcrypt library)
def check_password(email, password):

    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT hash FROM Users WHERE email = ?', (email,)) #retrieve corresponding hashed password from Users table
    result = cursor.fetchone()
    connection.close()
   
    if result:
        stored_hash = result[0]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash) #check if hashed password matches the one in the Users table
    return False


if __name__ == "__main__":
    app.run(debug=True)