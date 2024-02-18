from flask import Flask,render_template, request
import mysql.connector
 
app = Flask(__name__)
 
connection = mysql.connector.connect(
   user='ISS_Project', password='veryhardpassword', host='localhost', database='issproject'
)

cursor = connection.cursor()