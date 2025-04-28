import sqlite3 as sql
import bcrypt
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

#Navigate to login
@app.route('/')
def index():
    return render_template('login.html')

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
                    return render_template('SellerPage.html')
                elif role == 'HelpDesk':
                    return redirect(url_for('helpdesk_dashboard'))
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

#Seller Home Page
@app.route('/sellerhome')
def seller_home():
    return render_template('SellerPage.html')

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

            #Check if email already exists
            cursor.execute('SELECT email FROM Users WHERE email = ?', (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                print("[DEBUG] Email already exists:", email)
                return render_template('signup.html', error='Email already registered. Please login.')

            #If email not exists, insert new user
            cursor.execute('INSERT INTO Users (email, hash) VALUES (?, ?)', (email, hashed_pw))
            print("[DEBUG] Inserted new user into Users:", email)

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
                print("[DEBUG] Inserted new Buyer profile:", email)

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
                print("[DEBUG] Inserted new Seller profile:", email)

            connection.commit()

        return redirect(url_for('index'))

    else:
        return render_template('signup.html')

#Add Product
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

#Edit Product
@app.route('/editproduct/<int:listing_id>', methods=['GET', 'POST'])
def edit_product(listing_id):
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()

        if request.method == 'POST':
            #Form Data
            new_title = request.form['product_title']
            new_name = request.form['product_name']
            new_category = request.form['category_name']
            new_description = request.form['product_description']
            new_quantity = int(request.form['quantity'])
            new_price = request.form['product_price']

            #Update table
            cursor.execute('''
                UPDATE Products
                SET product_title = ?, product_name = ?, category = ?, product_desc = ?, quantity = ?, product_price = ?
                WHERE listing_ID = ? AND seller_email = ?
            ''', (new_title, new_name, new_category, new_description, new_quantity, new_price, listing_id, email))

            connection.commit()
            return redirect(url_for('manage_products'))

        # Show the product info to edit
        cursor.execute('SELECT product_title, product_name, category, product_desc, quantity, product_price FROM Products WHERE listing_ID = ? AND seller_email = ?', (listing_id, email))
        product = cursor.fetchone()

    if not product:
        return "Product not found."

    return render_template('editproduct.html', product=product, listing_id=listing_id)

# DELETE PRODUCT
@app.route('/deleteproduct/<int:listing_id>')
def delete_product(listing_id):
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Products WHERE listing_ID = ? AND seller_email = ?', (listing_id, email))
        connection.commit()

    return redirect(url_for('manage_products'))

# MARK PRODUCT AS SOLD OUT (Soft delete)
@app.route('/soldoutproduct/<int:listing_id>')
def soldout_product(listing_id):
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE Products SET status = 2 WHERE listing_ID = ? AND seller_email = ?', (listing_id, email))
        connection.commit()

    return redirect(url_for('manage_products'))

#Mark product as in stock
@app.route('/markinstock/<int:listing_id>')
def mark_in_stock(listing_id):
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE Products SET status = 1 WHERE listing_ID = ? AND seller_email = ?', (listing_id, email))
        connection.commit()

    return redirect(url_for('manage_products'))

#SELLER - View Sales
@app.route('/viewsales')
def view_sales():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT o.order_ID, o.buyer_email, p.product_title, p.product_name, o.quantity, o.payment, o.date,
                   r.rate, r.review_desc
            FROM Orders o
            JOIN Products p ON o.listing_ID = p.listing_ID
            LEFT JOIN Reviews r ON o.order_ID = r.order_ID
            WHERE o.seller_email = ?
            ORDER BY o.date DESC
        ''', (email,))
        sales = cursor.fetchall()

    return render_template('viewsales.html', sales=sales)



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

#BUYER: Buy Product Page
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
        session.modified = True  #Force Flask to recognize session change
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
        session.modified = True  #Add this to save changes!
    return redirect(url_for('view_cart'))

#Checkout
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return "Your cart is empty!", 400

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()

        for listing_id, item in cart.items():
            quantity_purchased = item['quantity']

            #Get current product info
            cursor.execute('SELECT quantity, seller_email, product_price FROM Products WHERE listing_ID = ?', (listing_id,))
            product = cursor.fetchone()

            if not product:
                continue

            current_quantity, seller_email, product_price = product

            clean_price = str(product_price).replace('$', '').replace(',', '').strip()
            product_price = float(clean_price)

            #Check stock
            if quantity_purchased > current_quantity:
                return f"Not enough stock for {item['product_name']}.", 400

            #Update stock
            new_quantity = current_quantity - quantity_purchased
            new_status = 2 if new_quantity == 0 else 1

            cursor.execute('''
                UPDATE Products
                SET quantity = ?, status = ?
                WHERE listing_ID = ?
            ''', (new_quantity, new_status, listing_id))

            #Update seller balance
            subtotal = product_price * quantity_purchased
            cursor.execute('''
                UPDATE Seller
                SET balance = balance + ?
                WHERE seller_email = ?
            ''', (subtotal, seller_email))

            #Insert into Orders table
            cursor.execute('''
                INSERT INTO Orders (seller_email, listing_ID, buyer_email, date, quantity, payment)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            ''', (seller_email, listing_id, session['email'], quantity_purchased, subtotal))

        connection.commit()

    #Clear cart after successful checkout
    session['cart'] = {}

    return render_template('checkoutsuccess.html')

#BUYERS: My orders
@app.route('/myorders')
def my_orders():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT o.order_ID, p.product_title, p.product_name, o.quantity, o.payment, o.date,
                (SELECT COUNT(1) FROM Reviews r WHERE r.order_ID = o.order_ID) AS reviewed
            FROM Orders o
            JOIN Products p ON o.listing_ID = p.listing_ID
            WHERE o.buyer_email = ?
            ORDER BY o.date DESC
        ''', (email,))
        orders = cursor.fetchall()

    return render_template('myorders.html', orders=orders)

#BUYERS: Review
@app.route('/submit_review/<int:order_id>', methods=['POST'])
def submit_review(order_id):
    rate = request.form.get('rate')
    review_desc = request.form.get('review_desc')

    if not rate or not review_desc:
        return "Rating and review are required.", 400

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()

        #Insert review
        cursor.execute('''
            INSERT INTO Reviews (order_ID, rate, review_desc)
            VALUES (?, ?, ?)
        ''', (order_id, rate, review_desc))

        connection.commit()

    return redirect(url_for('my_orders'))

#check email
def check_email(email):
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(1) FROM Users WHERE email = ?', (email,))
        result = cursor.fetchone()
    return result[0] > 0 if result else False

#check password
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

#Account Settings
@app.route('/accountsettings', methods=['GET', 'POST'])
def account_settings():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()

        #Determine role: Buyer or Seller
        role = get_role(email)

        if request.method == 'POST':
            if role == 'Buyer':
                buyer_bname = request.form['buyer_bname']
                street_num = request.form['street_num']
                street_name = request.form['street_name']
                zipcode = request.form['zipcode']
                credit_card_num = request.form['credit_card_num']
                card_type = request.form['card_type']
                expire_month = request.form['expire_month']
                expire_year = request.form['expire_year']
                security_code = request.form['security_code']

                #Update buyer info
                cursor.execute('UPDATE Buyer SET buyer_bname = ? WHERE buyer_email = ?', (buyer_bname, email))
                cursor.execute('UPDATE Address SET street_num = ?, street_name = ?, zipcode = ? WHERE addr_ID = (SELECT buyer_addr_ID FROM Buyer WHERE buyer_email = ?)', (street_num, street_name, zipcode, email))
                cursor.execute('UPDATE Credit_Cards SET credit_card_num = ?, card_type = ?, expire_month = ?, expire_year = ?, security_code = ? WHERE owner_email = ?', (credit_card_num, card_type, expire_month, expire_year, security_code, email))

            elif role == 'Seller':
                seller_bname = request.form['seller_bname']
                street_num = request.form['street_num']
                street_name = request.form['street_name']
                zipcode = request.form['zipcode']
                bank_rno = request.form['bank_rno']
                bank_accno = request.form['bank_accno']

                #Update seller information
                cursor.execute('UPDATE Seller SET seller_bname = ?, bank_rno = ?, bank_accno = ? WHERE seller_email = ?', (seller_bname, bank_rno, bank_accno, email))
                cursor.execute('UPDATE Address SET street_num = ?, street_name = ?, zipcode = ? WHERE addr_ID = (SELECT seller_addr_ID FROM Seller WHERE seller_email = ?)', (street_num, street_name, zipcode, email))

            connection.commit()
            return redirect(url_for('account_settings'))

        user_data = {}

        if role == 'Buyer':
            cursor.execute('''
                SELECT B.buyer_bname, A.street_num, A.street_name, A.zipcode, C.credit_card_num, C.card_type, C.expire_month, C.expire_year, C.security_code
                FROM Buyer B
                JOIN Address A ON B.buyer_addr_ID = A.addr_ID
                JOIN Credit_Cards C ON B.buyer_email = C.owner_email
                WHERE B.buyer_email = ?
            ''', (email,))
            user_data = cursor.fetchone()

        elif role == 'Seller':
            cursor.execute('''
                SELECT S.seller_bname, A.street_num, A.street_name, A.zipcode, S.bank_rno, S.bank_accno
                FROM Seller S
                JOIN Address A ON S.seller_addr_ID = A.addr_ID
                WHERE S.seller_email = ?
            ''', (email,))
            user_data = cursor.fetchone()

    return render_template('accountsettings.html', user_data=user_data, role=role, email=email)


# HELP DESK - ACCOUNT SETTINGS
@app.route('/helpdesk/account', methods=['GET', 'POST'])
def helpdesk_account_settings():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()

        if request.method == 'POST':
            position = request.form.get('position')
            cursor.execute('UPDATE HelpDesk SET position = ? WHERE email = ?', (position, email))
            connection.commit()
            return redirect(url_for('helpdesk_account_settings'))

        # GET: Load profile
        cursor.execute('SELECT email, position FROM HelpDesk WHERE email = ?', (email,))
        profile = cursor.fetchone()

    return render_template('helpdesk_account.html', profile=profile)


# Helpdesk

# HELP DESK DASHBOARD
@app.route('/helpdesk')
def helpdesk_dashboard():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    # Check if this user is a HelpDesk Staff
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT email FROM HelpDesk WHERE email = ?', (email,))
        result = cursor.fetchone()

    if result:
        return render_template('HelpDeskPage.html')
    else:
        return "Unauthorized Access", 403

# HELP DESK - MANAGE USERS
@app.route('/helpdesk/manageusers')
def helpdesk_manage_users():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    # Confirm HelpDesk staff
    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT email FROM HelpDesk WHERE email = ?', (email,))
        result = cursor.fetchone()

        if not result:
            return "Unauthorized Access", 403

        # Fetch all buyers and sellers
        cursor.execute('''
            SELECT email, "Buyer" as role FROM Users
            WHERE email IN (SELECT buyer_email FROM Buyer)
            UNION ALL
            SELECT email, "Seller" as role FROM Users
            WHERE email IN (SELECT seller_email FROM Seller)
        ''')
        users = cursor.fetchall()

    return render_template('manageusers.html', users=users)

# REQUEST HELP (for Buyers and Sellers)
@app.route('/requesthelp', methods=['GET', 'POST'])
def request_help():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    if request.method == 'POST':
        request_type = request.form.get('request_type')
        request_desc = request.form.get('request_desc')

        with sql.connect('database.db') as connection:
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO Requests (sender_email, request_type, request_desc, request_status)
                VALUES (?, ?, ?, ?)
            ''', (email, request_type, request_desc, 'Pending'))

            connection.commit()

        return redirect(url_for('browse_products'))

    return render_template('requesthelp.html')


#HELP DESK - VIEW REQUESTS
@app.route('/helpdesk/requests', methods=['GET', 'POST'])
def helpdesk_view_requests():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT email FROM HelpDesk WHERE email = ?', (email,))
        result = cursor.fetchone()

        if not result:
            return "Unauthorized Access", 403

        if request.method == 'POST':
            request_id = request.form.get('request_id')
            new_status = request.form.get('new_status')

            cursor.execute('UPDATE Requests SET request_status = ? WHERE request_ID = ?', (new_status, request_id))
            connection.commit()

            return redirect(url_for('helpdesk_view_requests'))

        cursor.execute('''
            SELECT request_ID, sender_email, request_desc, request_status
            FROM Requests
            ORDER BY request_ID DESC
        ''')
        requests = cursor.fetchall()

    return render_template('viewrequests.html', requests=requests)

# HELP DESK - EDIT USER (email & password)
@app.route('/helpdesk/edituser/<string:user_email>', methods=['GET', 'POST'])
def helpdesk_edit_user(user_email):
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    with sql.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT email FROM HelpDesk WHERE email = ?', (email,))
        result = cursor.fetchone()

        if not result:
            return "Unauthorized Access", 403

        if request.method == 'POST':
            new_email = request.form['new_email']
            new_password = request.form['new_password']
            hashed_pw = hash_password(new_password)

            cursor.execute('UPDATE Users SET email = ?, hash = ? WHERE email = ?', (new_email, hashed_pw, user_email))
            cursor.execute('UPDATE Buyer SET buyer_email = ? WHERE buyer_email = ?', (new_email, user_email))
            cursor.execute('UPDATE Seller SET seller_email = ? WHERE seller_email = ?', (new_email, user_email))
            cursor.execute('UPDATE HelpDesk SET email = ? WHERE email = ?', (new_email, user_email))

            connection.commit()
            return redirect(url_for('helpdesk_manage_users'))

        return render_template('edituser.html', user_email=user_email)


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
        cursor.execute('SELECT email FROM HelpDesk WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result:
            return 'HelpDesk'        
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