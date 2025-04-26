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
                if table == 'Address': #remember to clear tables if there is an error in running this file DELETE * FROM table_name
                    cursor.execute('INSERT INTO Address VALUES (?, ?, ?, ?)', row) #put OR IGNORE after done testing.
                    
                elif table == 'Buyers':
                    cursor.execute('INSERT INTO Buyer VALUES (?, ?, ?)', row)
                    
                elif table == 'Categories':
                    cursor.execute('INSERT INTO Categories VALUES (?, ?)', row)
                    
                elif table == 'Credit_Cards': #TO DO: remove '-' from credit card numbers

                    row[0] = int(row[0].replace('-','')) #int matches schema and is faster to process
                    cursor.execute('INSERT INTO Credit_Cards VALUES (?, ?, ?, ?, ?, ?)', row) 

                elif table == 'Helpdesk': #
                    cursor.execute('INSERT INTO HelpDesk VALUES (?, ?)', row)
                    
                elif table == 'Orders':
                    cursor.execute('INSERT INTO Orders VALUES (?, ?, ?, ?, ?, ?, ?)', row)
                    
                elif table == 'Product_Listings': #TO DO: Remove '$' from Product_Price column

                    #row[8] = int(row[8].replace('$','')) #SCHEMA HAS PRICE AS VARCHAR: WILL RAISE ERROR. CONSIDER CHANGING SCHEMA OR OMITT THIS LINE
                    row[8] = row[8].replace('$','') #remember to turn to int if doing any operations with product price
                    cursor.execute('INSERT INTO Products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', row)
                    
                elif table == 'Requests':
                    cursor.execute('INSERT INTO Requests VALUES (?, ?, ?, ?, ?, ?)', row)

                elif table == 'Reviews':
                    cursor.execute('INSERT INTO Reviews VALUES (?, ?, ?)', row)
                    
                elif table == 'Sellers': #DISCUSS IF WE WANT TO KEEP ROUTING NUMBER AS A VARCHAR OR CHANGE TO INT
                    cursor.execute('INSERT INTO Seller VALUES (?, ?, ?, ?, ?, ?)', row)

                #elif table == 'Users': #Users were already hashed and inserted during the progress check, make sure to hash if using this line again
                #    cursor.execute('INSERT OR IGNORE INTO Users VALUES (?, ?)', row)

                elif table == 'Zipcode_Info':
                    cursor.execute('INSERT INTO Zipcode VALUES (?, ?, ?)', row)
        
connection.commit()

# how to merge main (the real deal) and master (stuff on my end)