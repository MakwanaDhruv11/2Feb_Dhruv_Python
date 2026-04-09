import tkinter as tk
from tkinter import messagebox
import pymysql

def getdata():
 return pymysql.connector.connect(host ="localhost",user = "root",password = "",database="tkinter_app",)
db = getdata()
print("Data connected")
cr = db.cursor()

create_table = "create table myinfo(ID INTEGER PRIMERY KEY AUTO_INCREMENT,name text,email text,mobile text)"
try:
    cr.execute(create_table)
    print("Table Created!")
except Exception as e:
    print(e)

def submit_data():
    name = name_entry.get()
    email = email_entry.get()
    mobile = mobile_entry.get()





