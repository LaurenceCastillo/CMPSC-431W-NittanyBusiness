# CMPSC431W Web Programming Exercise

Simple overview of use/purpose.

## Description

* This is the code for the NittanyBusiness prototype.
* // TODO


## Features
* `User login` The user can log in using an existing account and password. 
  * If the email is recorded as either a buyer or seller, you will be taken to the respective home page.
  * If the entered password is incorrect, the webpage will display an error message.

* `Account registration:=` When registering account, the user can select whether to register as a buyer or seller.
  * During account registration, the system asks for the user's business and credit card information.
  * The selected role will decide which database the newly registered email gets stored to.
  * All entered information will be stored to their corresponding databases.

* `Buyer features`
* Upon successful login, the user will be taken to the seller portal, containing a list of product subcategories
  * Upon clicking one of them, a table of products or subcategories further down the heirarchy will be displayed
  * The title, description, and price are displayed for each product
    * Buy -- the page will display a dialogue window to enter the quantity for the corresponding product
    * After that, you can add the product to your cart
      * After clicking it, you will be taken to your shopping cart, with a table of all of the products currently in cart
      * You can remove any product within the shopping cart
      * You can update the quantity for each product by changing the number in each product box and click the "Update" button
      * Continue Shopping -- here you will be prompted to enter your credit card information
        * Upon successful verification, your account balance will be deducted and then taken to a review page
  * Using the product search box on the top of the landing page, with a subcategory selected you can filter products to view
    * The webpage will return a table that only contain the products matching the search keyword
  * You can log out from the main page and every subpage. Shopping cart info will not be saved

* `Seller features`
* Upon successful login, the user will be taken to the seller portal
  * You are able to either add a new product, manage the products you are selling, or view sales for your product listings
    * Add New Product -- enter the details of the product you want to sell:
      * Product title, name, category, description, quantity, price ($)
      * After adding product, you will be taken to the Manage Products page
  * Manage Products -- see the table of all listings of this account
  * Information for each listing is displayed:
    * Listing ID, Product name, title, category, quantity, price, status (Active/Inactive)
    * For each listing, you are able to edit listing information, delete listing, or mark its status as Sold Out or In Stock
      * Mark Sold Out - set the status to Inactive, and buyers are unable to see the listing regardless of its quantity
      * Mark In Stock - make the listing visible to buyers
  * View Sales -- show how much products under the current account is sold
    * The page will display a table of each purchase of listed products, with the corresponding details:
      * Order ID, Buyer Email, Product title + name + quantity, buyer payment, transaction date, buyer rating and review

* `HelpDesk features`
* Upon successful login, the user will be taken to a helpdesk portal
  * Manage Users -- HelpDesk staff can update email and password of Seller or Buyer accounts
    * Changes will be reflected in database
  * User requests -- HelpDesk can view requests from users and update the status for each request
    * Status can be updated to Pending or Resolved
  * My Account -- HelpDesk staff can view their account information
    * They are able to change their own role (i.e. IT Support Specialist)
    * HelpDesk users cannot change their own account email address or password, only backend developers can do

* `General features`
* Return to home page (Seller/Buyer/helpdesk dashboard), Log Out
* Account Settings -- view and set your current account, business, and credit card information
  * Save Changes - update your account information, which will be reflected in the database
  * Contacting HelpDesk is required for updating your account email
* Request Help -- User (Seller/Buyer) can send a request to helpdesk with a title and message

## Organization
* This project is organized with many separate, smaller files.
  * `app.py` Functions handling all database queries, and backend features (i.e. responding to buttons)
  * `load_data.py` Python script for populating the database
  * `database.db` Where the data for all of the system is stored
  * `schema.txt` Where the table creation commands are stored

  * `/templates` Folder containing every .html page
    * `login.html` User login page
    * `signup.html` User registration page
    * `accountsettings.html` User change account settings page
    * `requesthelp.html` User can send a message to HelpDesk staff to request help

    * `SellerPage.html` Seller dashboard (login landing page)
    * `addproduct.html` Seller page for adding products to their catalogs
    * `manageproducts.html` Seller page for managing their product listings
    * `viewsales.html` Seller page for displaying sales history
    * `editproduct.html` Seller page for editing a previously added product listing.

    * `browseproducts.html` Buyers can browse the product catalog and select subcategories (login landing page)
    * `cart.html` Buyer can view a product and add a certain quantity to cart
    * `cart.html` Buyer page for viewing and editing their shopping carts
    * `checkout.html` Buyer page for entering payment information to make an order
    * `checkoutsuccess.html` Confirmation page when buyer check out success

    * `HelpDeskPage.html` HelpDesk staff dashboard (login landing page)
    * `edituser.html` HelpDesk can edit Seller/Buyer account information
    * `helpdesk_acccount.html` HelpDesk staff can view their own account info and update their position
    * `virequests.html` HelpDesk staff can view user requests and update request status


## Getting Started

### Dependencies

* PyCharm Professional, Python 3.9, virtualenv (Programming)
* Flask, Bootstrap 4.4.1, Popper.js (UI design)
* SQLite3, jQuery 3.4.1 (database query)
* bcrypt (encryption)

### Installing

* To run the test webpage in the browser using a local domain, virtualenv must be installed.
* Run the following to install. (using Homebrew installed)
```aiignore
brew install virtualenv
```
* After downloading and extracting the .zip containing the project files, place the entire project folder into the folder where PyCharm projects are located.
* After opening Pycharm Professional, select Open project.
* Locate the project folder to open the program.

### Executing program

* After dependencies are installed, press the green "play button" on the top of the PyCharm window.
* If the program is running properly, it will display `Running on http://127.0.0.1:5000` in the terminal.
* Click the http link to where the test website will be displayed, using a local domain.
* Be sure to select a venv (virtual environment) for the interpreter, or the Terminal will not show the desired results.

### Troubleshooting
* For Mac users, a common issue may be the following warning: `Address already in use Port 5000 is in use by another program. `
* A common solution would be to turn off AirPlay receiver within the System Settings.
  * (Settings -> AirDrop & Handoff -> AirPlay Receiver)
* This issue can be resolved by typing the follow in the Terminal:
```aiignore
 % kill -9 $(lsof -t -i:"5000")  
```
* The process using Port 5000 will be killed.
