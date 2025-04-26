from flask import Flask, render_template, request, url_for, redirect
import sqlite3 as sql
# import hashlib
import bcrypt

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'


# home page immediately renders login page
@app.route('/')
def index():
    return render_template('login.html')


# login button
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_email(email):  # check if email is in Users table
            if check_password(email, password):  # verify password
                #return render_template('landing.html')  # redirect to next page
                
                # direct to page depending on role
                role =  get_role(email)
                if role == 'Buyer':
                    return render_template('buyer.html')
                elif role == 'Seller':
                    return render_template('seller.html')
                elif role == 'Help Desk':
                    return render_template('helpdesk.html')

            else:
                error = 'Incorrect password. Please try again.'
                return render_template('login.html', error=error)
        else:
            error = 'Email not found. Please try again.'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


# make link to signup page
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    return render_template('signup.html')

@app.route('/categories', methods=['POST', 'GET']) #should be repeatedly called when clicking on subcategories
#start with root node "All"
#after clicking, display all top level categories
def categories():
    if request.method == 'GET': #Show root node "All" after navigating from the landing page
        return render_template('categories.html')

    else: #if POST, display subcategories/products
        category = request.form['category']

        with sql.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT category_name FROM Categories WHERE parent_category = ?'(category,))
            cursor.execute('SELECT product_title FROM Products WHERE category = ?'(category,))

            categories_products = cursor.fetchall #TODO check if this code actually works. I haven't tested it yet.
    return render_template('categories.html', categories_prodcts = categories_products)


# does email exist in Users
def check_email(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(1) FROM Users WHERE email = ?', (email,))
    result = cursor.fetchone()
    connection.close()

    return result[0] > 0 if result else False


# check if password is valid (passwords were generated using SHA256 + salt from the bcrypt library)
def check_password(email, password):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT hash FROM Users WHERE email = ?',
                   (email,))  # retrieve corresponding hashed password from Users table
    result = cursor.fetchone()
    connection.close()

    if result:
        stored_hash = result[0]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'),
                              stored_hash)  # check if hashed password matches the one in the Users table
    return False


def hash_password(password):
    salt = bcrypt.gensalt()  # will strengthen the generated hash value
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def get_role(email): # this function assumes that each user only has one role
    #NOTE untested

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()

        #cursor.execute('SELECT email FROM Users WHERE email = ?',(email,))
        #result = cursor.fetchone()
        #stored_email = result[0]

        cursor.execute('SELECT buyer_email FROM Buyer WHERE buyer_email = ?',(email,))
        result = cursor.fetchone()
        stored_buyer = result[0]
        if stored_buyer > 0:
            return 'Buyer'

        cursor.execute('SELECT seller_email FROM Seller WHERE seller_email = ?',(email,))
        result = cursor.fetchone()
        stored_seller = result[0]
        if stored_seller > 0:
            return 'Seller'

        cursor.execute('SELECT email FROM HelpDesk WHERE email = ?',(email,))
        result = cursor.fetchone()
        stored_helpdesk = result[0]
        if stored_helpdesk > 0:
            return 'Help Desk'
        
    return None # if code isn't working as intended



# Note: commenting database setup out because it takes 15-20 minutes to run and only needs to be done once

# connect = sql.connect('database.db')
# cursor = connect.cursor()
# with open('NittanyBusinessDataset_v3/Users.csv', mode = 'r', encoding = 'utf-8-sig') as file:
#    csv = csv.DictReader(file)
#    cursor.execute('CREATE TABLE IF NOT EXISTS Users(email CHAR(30) PRIMARY KEY, password CHAR(100));')

#    connect.execute('BEGIN TRANSACTION;')
#    for row in csv:
#        email = row['email']
#        password = row['password']

#        hashed_password = hash_password(password)

#        try:
#            cursor.execute('INSERT INTO Users (email,password) VALUES (?, ?);', (email,hashed_password))
#        except sql.IntegrityError: #if email already exists
#            continue
#    connect.commit()

if __name__ == "__main__":
    app.run(debug=True)

# TODO // the functionality stuff for each webpage
# Use this account from dataset to log in!!
# o5mrsfw0@nittybiz.com	TbIF16hoUqGl