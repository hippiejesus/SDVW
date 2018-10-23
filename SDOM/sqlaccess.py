import os
import sys

import sqlite3

# Establish connection with the local workspace database
connection = sqlite3.connect('/home/dietpi/Database/SDOM.db')
print('Connected to SDOM.db')

# Define the cursor object for this connection
cursor = connection.cursor()

def query(target,container,conditions=None):
    if conditions != None:
        statement = "SELECT "+str(target)+" FROM "+str(container)+" "+str(conditions)
    else: 
        statement = "SELECT "+str(target)+" FROM "+str(container)
    cursor.execute(statement)
    return cursor.fetchall()

def create_table(name,columns):
    statement = "CREATE TABLE " + str(name) + " ("
    for i in columns:
        statement += str(i)
        statement += ","
    statement += ");"
    cursor.execute(statement)
    
def insert(target,substance):
    statement = "INSERT INTO " + str(target) + " VALUES ("
    for i in substance:
        statement += "'"
        statement += str(i)
        statement += "'"
        statement += ","
    statement = statement[:-1]
    statement += ")"
    cursor.execute(statement)
    
def delete(target,condition=None):
    if condition == None:
        statement = "DELETE FROM " + str(target)
    else:
        statement = "DELETE FROM " + str(target) + " WHERE " + str(condition)
    statement += ";"
    cursor.execute(statement)
    
def update(table,column,row,symbol,value):
    statement = "UPDATE " + str(table) + " SET " + str(column) + " = " + str(row) + " WHERE " + str(symbol) + " = " + str(value) + ";"

def test():
    print str(query('*','Contact','WHERE Name="Evan Dixon"')[0])[3:-3]
    
