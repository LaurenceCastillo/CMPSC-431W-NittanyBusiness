import sqlite3 as sql
import bcrypt
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

#Home Page - Login
@app.route('/')
def index():
    return render_template('login.html')

#TASK 1:
#Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_email(email):
            if check_password(email, password):
                session['email'] = email
                role = get_role(email)
                if role == 'Buyer':
                    return redirect(url_for('browse_products'))
                elif role == 'Seller':
                    return redirect(url_for('seller_home'))
                elif role == 'Help Desk':
                    return redirect(url_for('helpdesk'))
                
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

#TODO: Make helpdesk page functional
@app.route('/helpdesk')
def helpdesk():
    return render_template('helpdesk.html')

#Seller Home Page
@app.route('/sellerhome')
def seller_home():
    return render_template('seller.html')

#TASK 7: User registration

#Signup
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        role = request.form['role']

        hashed_pw = hash_password(password)

        with sql.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO Users (email, hash) VALUES (?, ?)', (email, hashed_pw))

            if role == 'Buyer':
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


#TASK 3: Product Listing Management
#TODO: add the ability to remove existing products from the marketplace
#TODO: add the ability to edit existing products form the marketplace
# ADD PRODUCT
@app.route('/addproduct', methods=['POST', 'GET'])
def add_listing():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            product_title = request.form['product_title']
            product_name = request.form['product_name']
            category = request.form['category_name']
            product_description = request.form['product_description']
            quantity = request.form['quantity']
            product_price = request.form['product_price']
            status = 1

            with sql.connect('database.db') as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT MAX(listing_ID) FROM Products;')
                result = cursor.fetchone()
                new_listing_id = (result[0] + 1) if result[0] else 1

                cursor.execute('INSERT INTO Products (seller_email, listing_ID, category, product_title, product_name, product_desc, quantity, product_price, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (email, new_listing_id, category, product_title, product_name, product_description, quantity, product_price, status))
                connection.commit()

            return redirect(url_for('manage_products'))
        except Exception as e:
            print(f"[ERROR] Error inserting product: {e}")
            return f"❌ Error: {e}"
    else:
        return render_template('addproduct.html')

#Manage Products
@app.route('/manageproducts', methods=['GET'])
def manage_products():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT listing_ID, product_title, product_name, category, quantity, product_price, status FROM Products WHERE seller_email = ?', (email,))
        products = cursor.fetchall()

    return render_template('manageproducts.html', products=products)

#TASK 2: Category Heirarchy
#TODO: Implement proper search functionality from browse_products.html
#BUYER: Browse Top Categories
@app.route('/browseproducts', methods=['GET'])
def browse_products():
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT category_name FROM Categories WHERE TRIM(parent_category) = "Root";')
        categories = cursor.fetchall()

    return render_template('browseproducts.html', categories=categories, parent_category="Root")

#BUYER: Browse Inside Category (Show subcategories and products)
@app.route('/browseproducts/<category_name>', methods=['GET', 'POST'])
def browse_subcategory(category_name):
    search_query = request.form.get('search', '').strip()

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()

        cursor.execute('SELECT DISTINCT category_name FROM Categories WHERE TRIM(parent_category) = ?;', (category_name.strip(),))
        subcategories = cursor.fetchall()

        if search_query:
            cursor.execute('''
                SELECT listing_ID, product_title, product_name, product_desc, product_price
                FROM Products
                WHERE category = ? AND status = 1 AND (product_title LIKE ? OR product_name LIKE ?)
            ''', (category_name, f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute('''
                SELECT listing_ID, product_title, product_name, product_desc, product_price
                FROM Products
                WHERE category = ? AND status = 1
            ''', (category_name,))

        products = cursor.fetchall()

    return render_template('browseproducts.html', categories=subcategories, products=products, parent_category=category_name)

#TASK 4: Order Management
#TODO: Make checkout & maybe order confirmation page. Ensure that proper amount is added to the corresponding seller
#Buy Product Page
@app.route('/buyproduct/<int:listing_id>', methods=['GET', 'POST'])
def buy_product(listing_id):
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT listing_ID, product_title, product_name, product_desc, product_price
            FROM Products
            WHERE listing_ID = ? AND status = 1
        ''', (listing_id,))
        product = cursor.fetchone()

    if not product:
        return "Product not found."

    if request.method == 'POST':
        quantity = int(request.form['quantity'])

        if 'cart' not in session:
            session['cart'] = {}

        cart = session['cart']
        cart[str(listing_id)] = {
            'product_title': product[1],
            'product_name': product[2],
            'product_desc': product[3],
            'product_price': product[4],
            'quantity': quantity
        }
        session['cart'] = cart

        return redirect(url_for('view_cart'))

    return render_template('buyproduct.html', product=product)

#View Cart
@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
    if request.method == 'POST':
        cart = session.get('cart', {})
        for listing_id in list(cart.keys()):
            quantity_field = f'quantity_{listing_id}'
            if quantity_field in request.form:
                try:
                    new_quantity = int(request.form[quantity_field])
                    if new_quantity > 0:
                        session['cart'][listing_id]['quantity'] = new_quantity
                    else:
                        session['cart'].pop(listing_id)
                except ValueError:
                    pass
        session.modified = True  # Force Flask to recognize session change
        return redirect(url_for('view_cart'))

    #GET request part: Always load fresh cart data from session
    fresh_cart = session.get('cart', {})
    cart_items = []
    total_price = 0

    for listing_id, item in fresh_cart.items():
        clean_price = item['product_price'].replace('$', '').replace(',', '').strip()
        product_price = float(clean_price)
        subtotal = product_price * item['quantity']
        total_price += subtotal

        cart_items.append({
            'listing_id': listing_id,
            'product_title': item['product_title'],
            'product_name': item['product_name'],
            'product_desc': item['product_desc'],
            'product_price': product_price,
            'quantity': item['quantity'],
            'subtotal': subtotal
        })

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

#Remove From Cart
@app.route('/removefromcart/<listing_id>')
def remove_from_cart(listing_id):
    if 'cart' in session and listing_id in session['cart']:
        session['cart'].pop(listing_id)
        session.modified = True  # <== Add this to save changes!
    return redirect(url_for('view_cart'))


#check if email exists
def check_email(email):
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(1) FROM Users WHERE email = ?', (email,))
        result = cursor.fetchone()
    return result[0] > 0 if result else False

#check if password matches
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

#hash password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

#Get user role
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
        
        cursor.execute('SELECT email FROM HelpDesk WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result:
            return 'Help Desk'
    return None

#Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

#Buyer: o5mrsfw0@nittybiz.com,TbIF16hoUqGl
#Seller: ztolk7z1@nittybiz.com,ZvKy6bjCNah
#HelpDesk: u0fvl3dj@nittybiz.com,1hA1PDRKW