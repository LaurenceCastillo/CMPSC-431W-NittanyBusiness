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

#IMPORTANT: all of this needs to be adjusted to fit assignment

@app.route('/name', methods=['POST', 'GET'])
# function for rendering all elements of input.html and its input form
def name():
    error_name = None
    # handles database retrieval and table display after form submission
    if request.method == 'POST':
        result = input_name(request.form['FirstName'], request.form['LastName'])
        if result:
            return render_template('input.html', error=error_name, result=result)
        else:
            error = 'invalid input name'
    return render_template('input.html', error=error_name)

# handles query for inserting and displaying table from input.html page
def input_name(first_name, last_name):
    connection = sql.connect('database.db')
    connection.execute('CREATE TABLE IF NOT EXISTS users(pid INTEGER PRIMARY KEY AUTOINCREMENT, firstname TEXT, lastname TEXT);')
    connection.execute('INSERT INTO users (firstname, lastname) VALUES (?,?);', (first_name, last_name))
    connection.commit()
    cursor = connection.execute('SELECT * FROM users;')
    return cursor.fetchall()

@app.route('/delete', methods=['POST', 'GET'])
# function for rendering all elements of delete.html and its input form
def delete():
    error_delete = None
    connection3 = sql.connect('database.db')
    # handles database retrieval and table display on page load
    if request.method == 'GET':
        result_get = getdata()
        return render_template('delete.html', error=error_delete, result=result_get)

    # handles database retrieval and table display after form submission
    if request.method == 'POST':
        result_del = delete_name(request.form['FirstName'], request.form['LastName'])
        if result_del:
            return render_template('delete.html', error=error_delete, result=result_del)
        else:
            error = 'invalid input name'
    return render_template('delete.html', error=error_delete)

# handles query for displaying table on delete.html page load
def getdata():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM users;')
    return cursor.fetchall()

# handles query for deleting patient and updating table from delete.html page
def delete_name(first_name, last_name):
    connection = sql.connect('database.db')
    connection.execute ('DELETE FROM users WHERE firstname=? AND lastname=?;', (first_name, last_name))
    connection.commit()
    cursor = connection.execute('SELECT * FROM users;')
    return cursor.fetchall()

if __name__ == "__main__":
    app.run()


