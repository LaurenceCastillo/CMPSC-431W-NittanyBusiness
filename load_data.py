import csv
import os
import bcrypt
import sqlite3 as sql

# This file is to be used for loading csv data into database.db
#some attributes must be transformed to fit the schema in database.db

for path in os.listdir("NittanyBusinessDataset_v3"):
    with open(path, newline = '') as file:
        pass
    pass