from flask import Flask, render_template, request, url_for, redirect
import sqlite3 as sql
#from hashlib import sha256
import bcrypt

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'

@app.route('/')
# function for rendering index.html (home page)
def index():
    return render_template('index.html')

#call when user presses submit button. checks if username & password is valid

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']

        password = request.form['password']
        salt = bcrypt.gensalt() #will strengthen the generated hash value
        hashed_password = bcrypt.hashpw(password.encode('utf-8'),salt)

        if check_email(email):
            if check_password(email,hashed_password):
                #navigate to next page
                return redirect(url_for('home')) #insert name of page here
            else:
                #notify that password is incorrect
                error = 'Incorrect password. Please try again.'
                return render_template('login.html', error = error)
            
        else:
            #notify that email is incorrect
            error = 'Email not found. Please try again.'
            return render_template('login.html', error = error)
    

def check_email(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(1) FROM Users WHERE email = ?', (email,))

    result = cursor.fetchone()
    connection.close()

    if result: #check if cursor retrieved a row
        return True
    return False

def check_password(email, hashed_password):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT password FROM Users WHERE email = ?', (email,))

    result = cursor.fetchone()
    connection.close()

    if bcrypt.checkpw(hashed_password,result[0]):
        return True
    return False

if __name__ == "__main__":
    app.run()