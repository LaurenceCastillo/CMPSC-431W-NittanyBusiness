# CMPSC-431W-NittanyBusiness

## Description
The following files are for the Phase 2 Progress Review for CMPSC 431W. It provides the user a login page for which the user can enter an email and password before pressing the "Log In" button, which then then checks whether the username and password exist in the local database. 

## Organization
app.py:
This file contains functions that handle all database actions and routing to other pages. It is in this file where the validity of the email and password is checked.

login.html: 
This is the login page for which the user must enter an email and password before submitting. These fields must not be empty when submitting the form. Additionally, if the email is incorrect, a message will display and ask to enter a valid email. Similarly, wrong passwords will display a message to enter the correct password. The form itself commuicates with app.py using the 'POST' method. 

filler.html: 
This is a dummy page that is navigated to to demonstrate that the login was successful.

database.db:
This contains the Users table which has the columns "email" and "hash". Ths table was populated by reading Users.csv and then hashing the values that existed under the "password" column. These hashed passwords were then inserted into Users with email as the primary key.


## Dependencies
Pycharm Professional, Python 3.9
Libraries: Flask, sqlite3, bcrypt

## Executing program
Method 1: Using terminal/command prompt, type "python app.py". After this, copy and paste "http://127.0.0.1:5000/" into the browser of your choice. From here you are free to interact with the site as you wish.

Method 2: If the user is using PyCharm, press the green "play button" on the top of the PyCharm window. If the program is running properly, it will display 'Running on http://127.0.0.1:5000/' in the terminal. Click the http link to where the test website will be displayed, using local domain.
