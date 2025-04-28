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

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)