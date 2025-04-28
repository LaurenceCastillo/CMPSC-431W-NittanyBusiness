import sqlite3 as sql
import bcrypt
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for Flask session

# Home Page - Login
@app.route('/')
def index():
    return render_template('login.html')

# LOGIN
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_email(email):
            if check_password(email, password):
                session['email'] = email  # Save user email to session
                role = get_role(email)
                if role == 'Buyer':
                    return render_template('BuyerPage.html')
                elif role == 'Seller':
                    return render_template('SellerPage.html')
                else:
                    return render_template('login.html', error='Role not found.')
            else:
                error = 'Incorrect password. Please try again.'
                return render_template('login.html', error=error)
        else:
            error = 'Email not found. Please try again.'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

# SIGNUP
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        role = request.form['role']

        hashed_pw = hash_password(password)

        with sql.connect('database.db') as connection:
            cursor = connection.cursor()

            # Insert into Users
            cursor.execute('INSERT INTO Users (email, hash) VALUES (?, ?)', (email, hashed_pw))

            if role == 'Buyer':
                # Buyer-specific fields
                buyer_bname = request.form['buyer_bname']
                zipcode = request.form['zipcode']
                street_num = request.form['street_num']
                street_name = request.form['street_name']
                credit_card_num = request.form['credit_card_num']
                card_type = request.form['card_type']
                expire_month = request.form['expire_month']
                expire_year = request.form['expire_year']
                security_code = request.form['security_code']

                addr_id = f"ADDR_{email}"

                cursor.execute('INSERT INTO Address (addr_ID, zipcode, street_num, street_name) VALUES (?, ?, ?, ?)',
                               (addr_id, zipcode, street_num, street_name))

                cursor.execute('INSERT INTO Buyer (buyer_email, buyer_bname, buyer_addr_ID) VALUES (?, ?, ?)',
                               (email, buyer_bname, addr_id))

                cursor.execute('INSERT INTO Credit_Cards (credit_card_num, card_type, expire_month, expire_year, security_code, owner_email) VALUES (?, ?, ?, ?, ?, ?)',
                               (credit_card_num, card_type, expire_month, expire_year, security_code, email))

            elif role == 'Seller':
                # Seller-specific fields
                seller_bname = request.form['seller_bname']
                zipcode = request.form['zipcode']
                street_num = request.form['street_num']
                street_name = request.form['street_name']
                bank_rno = request.form['bank_rno']
                bank_accno = request.form['bank_accno']

                addr_id = f"ADDR_{email}"

                cursor.execute('INSERT INTO Address (addr_ID, zipcode, street_num, street_name) VALUES (?, ?, ?, ?)',
                               (addr_id, zipcode, street_num, street_name))

                cursor.execute('INSERT INTO Seller (seller_email, seller_bname, seller_addr_ID, bank_rno, bank_accno, balance) VALUES (?, ?, ?, ?, ?, ?)',
                               (email, seller_bname, addr_id, bank_rno, bank_accno, 0))

            connection.commit()

        return redirect(url_for('index'))
    else:
        return render_template('signup.html')
    
# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# CHECK EMAIL
def check_email(email):
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(1) FROM Users WHERE email = ?', (email,))
        result = cursor.fetchone()
    return result[0] > 0 if result else False

# CHECK PASSWORD
def check_password(email, password):
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT hash FROM Users WHERE email = ?', (email,))
        result = cursor.fetchone()
    if result:
        stored_hash = result[0]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    return False

# HASH PASSWORD
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# GET USER ROLE
def get_role(email):
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()

        cursor.execute('SELECT buyer_email FROM Buyer WHERE buyer_email = ?', (email,))
        result = cursor.fetchone()
        if result:
            return 'Buyer'

        cursor.execute('SELECT seller_email FROM Seller WHERE seller_email = ?', (email,))
        result = cursor.fetchone()
        if result:
            return 'Seller'

    return None



#TASK 2: CATEGORY HEIRARCHY
@app.route('/browse_products', methods=['POST', 'GET']) #should be repeatedly called when clicking on subcategories
def browse_products():
    if request.method == 'GET': #Initial navigation to page.
        #TODO in html file: Show root node "All" after navigating from the landing page
        return render_template('categories.html')

    else: #if POST, display subcategories/products. This would be after clicking "All"
        category = request.form['category']

        with sql.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT category_name FROM Categories WHERE parent_category = ?',(category,))
            subcategories = cursor.fetchall()

            cursor.execute('SELECT product_title FROM Products WHERE category = ?',(category,))
            products = cursor.fetchall()

            categories_products = {'subcategories': subcategories, 'products': products} #TODO check if this code actually works. I haven't tested it yet.
    return render_template('categories.html', categories_products = categories_products) #all products and categories are stored in a tuple

#TASK 3: PRODUCT LISTING MANAGEMENT
@app.route('/manage_products', methods = ['POST','GET'])
def view_products():

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Products WHERE seller_email = ?',(email,))
        contents = cursor.fetchall
    
    return render_template('view_product.html', contents = contents)

@app.route('/add_listing', methods = ['POST','GET'])
def add_listing(): #TODO: ADJUST addlisting.html to fit the schema
    if request.method == 'POST':
        user_email = email
        id = request.form['listing_id'] #TODO: consider autoincrementing in sql instead of guessing an ID until unique
        category = request.form['category_name']
        product_title = request.form['product_title']
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        quantity = request.form['quantity']
        price = request.form['price']
        status = 1 #status 1 indicates active
        
        with sql.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO Products VALUES (?,?,?,?,?,?,?,?,?)',
                           (user_email, id, category, product_title, product_name, product_description, quantity, price, status))
            connection.commit()
    else:
        return render_template('addlisting.html')
    
@app.route('/remove_listing', methods = ['POST','GET'])
def remove_listing():
    if request.method == 'POST':
        id = request.form['listing_id']
        
        with sql.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE Products SET status = 0 WHERE listing_ID = ?',(id,)) #status 0 indicates inactive
            connection.commit()
    return render_template('removelisting.html')


#TASK 4: ORDER MANAGEMENT
@app.route('/product_info', methods = ['POST', 'GET'])
def product_info():
    id = request.form['listing_id']
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Products WHERE listing_ID = ?'(id,))
        info = cursor.fetchall
    return render_template('product_info.html', info = info)


@app.route('/review_order', methods = ['POST', 'GET'])
def place_order():
    id = request.form['listing_id']
    quantity = request.form['quantity']
    requested_quantity = request.form['requested_quantity']

    if quantity - requested_quantity < 0: #check if quantity exceeds stock
        message = "Not enough items in stock"
        return render_template('product_info.html', message = message)

    price = request.form['product_price']
    total = requested_quantity * int(price) #because price is stored as varchar

    with sql.connect('database.db') as connection: #TODO: consider implementing a way to prevent user from buying more than available quantity
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Products WHERE listing_ID = ?'(id,))
        info = cursor.fetchall

    return render_template('secure_checkout.html', info = info, total = total, quantity = requested_quantity)

@app.route('/secure_checkout', methods = ['POST', 'GET']) #TODO: COMPLETE FUNCTION
def secure_checkout():
    id = request.form['listing_id']
    quantity = request.form['quantity']
    requested_quantity = request.form['requested_quantity']
    price = request.form['product_price']
    total = requested_quantity * int(price) #because price is stored as varchar

    with sql.connect('database.db') as connection: #TODO: consider implementing a way to prevent user from buying more than available quantity
        cursor = connection.cursor()

        if quantity - requested_quantity == 0: #if sold out, change status to 2
            cursor.execute('UPDATE Products SET quantity = quantity - ?, status =  2 WHERE listing_ID = ?',(requested_quantity, id,))

        else:
            cursor.execute('UPDATE Products SET quantity = quantity - ? WHERE listing_ID = ?',(requested_quantity, id,))
        cursor.execute('UPDATE Products SET status = 2 WHERE listing_id = ? AND quantity = quantity - ?',(id, requested_quantity,))
        cursor.execute('SELECT * FROM Products WHERE listing_ID = ?'(id,))
        info = cursor.fetchall
        connection.commit()

    pass

    #TASK 5: 

    #TASK 6:

    #TASK 7:

    #TASK 8:
    


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