from flask import Flask, render_template, request, url_for, redirect
import sqlite3 as sql
#from hashlib import sha256
import bcrypt #extremely slow for security reasons. consider tradeoff of speed vs security
import csv

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
        #salt = bcrypt.gensalt() #will strengthen the generated hash value
        #hashed_password = bcrypt.hashpw(password.encode('utf-8'),salt)

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
    cursor.execute('SELECT COUNT(1) FROM Users WHERE email = ?;', (email,))

    result = cursor.fetchone()
    connection.close()

    if result: #check if cursor retrieved a row
        return True
    return False

def check_password(email,password): #compare entered plaintext password to hashed password in Users table
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT password FROM Users WHERE email = ?;', (email,))

    result = cursor.fetchone()
    connection.close()


    if bcrypt.checkpw(password,result[0]):
        return True
    return False


#read Users.csv and hash passwords before inserting in sql table

def hash_password(password):
    salt = bcrypt.gensalt() #will strengthen the generated hash value
    hashed_password = bcrypt.hashpw(password.encode('utf-8'),salt)
    return hashed_password


#Note: commenting database setup out because it takes 15-20 minutes to run and only needs to be done once

#connect = sql.connect('database.db')
#cursor = connect.cursor()
#with open('NittanyBusinessDataset_v3/Users.csv', mode = 'r', encoding = 'utf-8-sig') as file:
#    csv = csv.DictReader(file)
#    cursor.execute('CREATE TABLE IF NOT EXISTS Users(email CHAR(30) PRIMARY KEY, password CHAR(100));') #Note: Not to be confused with users table leftover from web exercise

#    connect.execute('BEGIN TRANSACTION;')
#    for row in csv:
#        email = row['email']
#        password = row['password']

#        hashed_password = hash_password(password)
        
#        try:
#            cursor.execute('INSERT INTO Users (email,password) VALUES (?, ?);', (email,hashed_password))
            
            #cursor.execute('UPDATE users SET password = ? WHERE email = ?'(hashed_password,email))
#        except sql.IntegrityError: #if email already exists (assuming email is set as UNIQUE)
#            continue
    
#    connect.commit()

if __name__ == "__main__":
    app.run()