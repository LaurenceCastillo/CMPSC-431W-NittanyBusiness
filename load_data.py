import csv
import os
import bcrypt
import sqlite3 as sql

# This file is to be used for loading csv data into database.db
#some attributes must be transformed to fit the schema in database.db


with sql.connect('database.db') as connection:
    cursor = connection.cursor()

    for path in os.listdir("NittanyBusinessDataset_v3"):

        with open("NittanyBusinessDataset_v3/" + path, 'r') as file:
            reader = csv.reader(file)
            next(reader)

            table = path[:-4] #remove .csv extension 
            for row in reader:
                if table == 'Address':
                    cursor.execute('INSERT OR IGNORE INTO Address VALUES (?, ?, ?, ?)', row) #OR IGNORE prevents an exception from being raised if primary key already exists (cancells insertion of row)
                    
                elif table == 'Buyers':
                    cursor.execute('INSERT OR IGNORE INTO Buyer VALUES (?, ?, ?)', row)
                    
                elif table == 'Categories':
                    cursor.execute('INSERT OR IGNORE INTO Categories VALUES (?, ?)', row)
                    
                elif table == 'Credit_Card': #TO DO: remove '-' from credit card numbers
                    cursor.execute('INSERT OR IGNORE INTO Credit_Cards VALUES (?, ?, ?, ?, ?, ?)', row) 

                elif table == 'Helpdesk': #
                    cursor.execute('INSERT OR IGNORE INTO HelpDesk VALUES (?, ?)', row)
                    
                elif table == 'Orders':
                    cursor.execute('INSERT OR IGNORE INTO Orders VALUES (?, ?, ?, ?, ?, ?, ?)', row)
                    
                elif table == 'Product_Listings': #TO DO: Remove '$' from Product_Price column
                    cursor.execute('INTO OR IGNORE INTO Products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', row)
                    
                elif table == 'Requests':
                    cursor.execute('INSERT OR IGNORE INTO Requests VALUES (?, ?, ?)', row)

                elif table == 'Reviews':
                    cursor.execute('INSERT OR IGNORE INTO Reviews VALUES (?, ?, ?)', row)
                    
                elif table == 'Sellers': #TO DO: remove '-' from bank_account_number
                    cursor.execute('INSERT OR IGNORE INTO Seller VALUES (?, ?, ?, ?, ?, ?)')

                #elif table == 'Users': #Users were already hashed and inserted during the progress check, make sure to hash if using this line again
                #    cursor.execute('INSERT OR IGNORE INTO Users VALUES (?, ?)', row)

                elif table == 'Zipcode_Info':
                    cursor.execute('INSERT OR IGNORE INTO Zipcode VALUES (?, ?, ?)', row)