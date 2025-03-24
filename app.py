from flask import Flask, render_template, request
import sqlite3 as sql
from hashlib import sha256

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'

@app.route('/')
# function for rendering index.html (home page)
def index():
    return render_template('index.html')

#call when user presses submit button. checks if username & password is valid

@app.route('/login', methods = ['POST', 'GET'])
def login():
    email = request.form['email']
    encoded_email = email.encode('utf-8')
    hashed_email = sha256(encoded_email)
    hex_email = hashed_email.hexdigest()

    password = request.form['password']
    encoded_password = password.encode('utf-8')
    hashed_password = sha256(encoded_password)
    hex_password = hashed_password.hexdigest()

    pass


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


