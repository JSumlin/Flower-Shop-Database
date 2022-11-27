# Joseph Sumlin, Andy Kincheloe, Sahil Posa

import sqlite3
from database import Database
from schema import Schema
from flask import Flask, render_template, request, url_for, flash, redirect
import os
from util import Util

app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(24).hex())

conn = sqlite3.connect('flowershopdatabase.db', check_same_thread=False)
conn.execute("PRAGMA foreign_keys = 1")
cursor = conn.cursor()
db = Database(conn,cursor)
Schema.build(conn, cursor)
conn.commit()


def get_db_connection():
    conn = sqlite3.connect('flowershopdatabase.db', check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = 1")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    conn.close()
    return render_template('index.html')


@app.route("/about")
def about():
    conn = get_db_connection()
    cursor = conn.cursor()
    conn.close()
    return render_template('about.html')


@app.route("/customer", methods=("GET", "POST"))
def customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    db = Database(conn,cursor)
    output = conn.execute("SELECT * FROM customer").fetchall()
    if request.method == "POST":
        return Util.request_manager("customer", request, db, output)
    return render_template('customer.html', output=output)


@app.route("/employee", methods=("GET", "POST"))
def employee():
    conn = get_db_connection()
    cursor = conn.cursor()
    db = Database(conn, cursor)
    output = conn.execute("SELECT * FROM employee").fetchall()
    if request.method == "POST":
        return Util.request_manager("employee", request, db, output)
    return render_template("employee.html", output=output)


@app.route("/products", methods=("GET", "POST"))
def product():
    conn = get_db_connection()
    cursor = conn.cursor()
    db= Database(conn, cursor)
    output = conn.execute("SELECT * FROM product").fetchall()
    if request.method == "POST":
        return Util.request_manager("products", request, db, output)
    return render_template("products.html", output=output)


@app.route("/orders", methods=("GET", "POST"))
def orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    db = Database(conn, cursor)
    output = conn.execute("SELECT * FROM orders").fetchall()
    if request.method == "POST":
        return Util.request_manager("orders", request, db, output)
    return render_template("orders.html", output=output)


@app.route("/purchase", methods=("GET", "POST"))
def purchase():
    conn = get_db_connection()
    cursor = conn.cursor()
    db = Database(conn, cursor)
    output = conn.execute("SELECT * FROM purchase").fetchall()
    if request.method == "POST":
        return Util.request_manager("purchase", request, db, output)
    return render_template("purchase.html", output=output)


@app.route("/place-order", methods=("GET", "POST"))
def place_ord():
    conn = get_db_connection()
    cursor = conn.cursor()
    db = Database(conn, cursor)
    output = conn.execute("SELECT * FROM product").fetchall()
    if request.method == "POST":
        return Util.request_manager("place-order", request, db, output)
    return render_template('placeOrder.html', output=output)

    
app.run(debug=True)
conn.close()
