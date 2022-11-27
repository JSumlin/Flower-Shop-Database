import sqlite3

from flask import Flask, render_template, request, url_for, flash, redirect
from checks import Checks
from database import Database


# this class handles HTTP POST requests from the different pages
class Util:

    @staticmethod
    def request_manager(page_name: str, request, db: Database, output: list):
        match page_name:
            case "customer":
                return Util.__customer_manager(request, db, output)
            case "employee":
                return Util.__employee_manager(request, db, output)
            case "products":
                return Util.__products_manager(request, db, output)
            case "orders":
                return Util.__orders_manager(request, db, output)
            case "purchase":
                return Util.__purchase_manager(request, db, output)
            case "place-order":
                return Util.__place_ord_manager(request, db, output)

    @staticmethod
    def __purchase_manager(request, db, output):
        if request.form.get('sort') == 'sort':
            return Util.get_sort(request.form, "purchase", "purchase", db)
        elif request.form.get('add') == 'add':
            return Util.__pur_add_req(request, db, output)
        elif request.form.get('del') == 'del':
            return Util.__pur_del_req(request, db)
        return render_template("purchase.html", output=output)

    @staticmethod
    def __pur_add_req(request, db, output):
        orderID = request.form["orderID"]
        productID = request.form["productID"]
        quantity = request.form["quantity"]
        # if the orderID and productID both exist
        if (not Checks.is_order_exist(orderID, db.cursor)) and (not Checks.is_productID_exist(productID, db.cursor)):
            # and if a tuple exists in purchase with the given orderID and productID, update the tuple
            if not (Checks.is_purchase_exist(orderID, productID, db.cursor)):
                db.upd_pur(orderID, productID, quantity)
            else:
                flash("Purchase does not exist.")
        else:
            flash("Invalid order # or product ID.")
        output = db.conn.execute("SELECT * FROM purchase").fetchall()
        return render_template("purchase.html", output=output)

    @staticmethod
    def __pur_del_req(request, db):
        orderID = request.form["orderID2"]
        productID = request.form["productID2"]
        if not (Checks.is_purchase_exist(orderID, productID, db.cursor)):
            db.del_pur(orderID, productID)
        output = db.conn.execute("SELECT * FROM purchase").fetchall()
        return render_template("purchase.html", output=output)

    @staticmethod
    def __customer_manager(request, db, output):
        if request.form.get('sort') == 'sort':
            print(request.form.get('sort'))
            return Util.get_sort(request.form, "customer", "customer", db)
        elif request.form.get('add') == 'add':
            return Util.__cus_add_req(request, db, output)
        elif request.form.get('del') == 'del':
            return Util.__cus_del_req(request, db)
        return render_template('customer.html', output=output)

    @staticmethod
    def __cus_del_req(request, db):
        phone = request.form["phone2"]
        # if the phone number exists, find and delete its entry. Otherwise, tell user it doesn't exist.
        if not (Checks.is_phone_unique(phone, db.cursor)):
            customerID = db.conn.execute("SELECT customerID FROM customer where phone = " + phone).fetchall()[0][0]
            db.del_cus(customerID)
        else:
            flash("Phone number does not exist.")
        output = db.conn.execute("SELECT * FROM customer").fetchall()
        return render_template('customer.html', output=output)

    @staticmethod
    def __cus_add_req(request, db, output):
        list = [request.form["customerID"], request.form["lname"], request.form["fname"], request.form["phone"]]
        if not list[0]:  # if there is no customerID input, create a customer tuple with the other inputs
            return Util.__add_cus(list, output, db)
        # if they entered a customerID, but no such value exists in the table, instruct the user.
        elif db.cursor.execute("SELECT * FROM customer WHERE customerID=?", (list[0],)).fetchone() is None:
            flash("Customer ID does not exist. Only fill customer ID field for updating.")
            return render_template("customer.html", output=output)
        else:
            return Util.__upd_cus(list, output, db)  # if the user entered an existing customerID, update that tuple

    @staticmethod
    def __add_cus(list, output, db):
        if not list[1] or not list[2] or not list[3]:
            flash("Last, first, and phone all required for adding.")
            return render_template("customer.html", output=output)
        if not Checks.is_phone_unique(list[3], db.cursor):
            flash("Phone number already on file.")
            return render_template("customer.html", output=output)
        db.add_cus(list[2], list[1], list[3])
        output = db.conn.execute("SELECT * FROM customer").fetchall()
        return render_template("customer.html", output=output)

    @staticmethod
    def __upd_cus(list, output, db):
        Checks.not_then_none(list)
        if list[3] is not None and not Checks.is_phone_unique(list[3], db.cursor):
            flash("Phone number already on file.")
            return render_template("customer.html", output=output)
        db.upd_cus(list[0], list[2], list[1], list[3])
        output = db.conn.execute("SELECT * FROM customer").fetchall()
        return render_template("customer.html", output=output)

    @staticmethod
    def __employee_manager(request, db, output):
        if request.form.get('sort') == 'sort':
            return Util.get_sort(request.form, "employee", "employee", db)
        elif request.form.get('add') == 'add':
            return Util.__emp_add_req(request, db, output)
        elif request.form.get('del') == 'del':
            return Util.__emp_del_req(request, db)
        return render_template("employee.html", output=output)

    @staticmethod
    def __emp_del_req(request, db):
        employeeID = request.form["employeeID2"]
        if db.cursor.execute("SELECT * FROM employee WHERE employeeID=?", (employeeID,)).fetchone() is not None:
            db.del_emp(employeeID)
        else:
            flash("Employee ID does not exist.")
        output = db.conn.execute("SELECT * FROM employee").fetchall()
        return render_template("employee.html", output=output)

    @staticmethod
    def __emp_add_req(request, db, output):
        list = [request.form["employeeID"], request.form["fname"], request.form["lname"], request.form["position"],
                request.form["salary"]]
        if not list[0]:  # if there is no employeeID input, add a new employee with the other inputs
            return Util.__add_emp(list, output, db)
        elif db.cursor.execute("SELECT * FROM employee WHERE employeeID=?", (list[0],)).fetchone() is None:
            flash("Employee ID does not exist. Only fill employee ID field for updating.")
            return render_template("employee.html", output=output)
        else:
            Checks.not_then_none(list)
            db.upd_emp(list[0], list[1], list[2], list[3], list[4])
        output = db.conn.execute("SELECT * FROM employee").fetchall()
        return render_template("employee.html", output=output)

    @staticmethod
    def __add_emp(list, output, db):
        if not list[1] or not list[2] or not list[3] or not list[4]:
            flash("Last, First, Position, and Salary all required for adding.")
            return render_template("employee.html", output=output)
        db.add_emp(list[1], list[2], list[3], list[4])
        output = db.conn.execute("SELECT * FROM employee").fetchall()
        return render_template("employee.html", output=output)

    @staticmethod
    def __products_manager(request, db, output):
        if request.form.get('sort') == 'sort':
            return Util.get_sort(request.form, "product", "products", db)
        elif request.form.get('add') == 'add':
            list = [request.form["productID"], request.form["product"], request.form["price"], request.form["quantity"]]
            if not list[0]:
                if not list[1] or not list[2] or not list[3]:
                    flash("Product, price, and quantity all required for adding.")
                    return render_template("products.html", output=output)
                db.add_prod(list[1], list[2], list[3])
            elif db.cursor.execute("SELECT * FROM product WHERE productID=?", (list[0],)).fetchone() is None:
                flash("Product ID does not exist. Only fill product ID field for updating.")
                return render_template("products.html", output=output)
            else:
                Checks.not_then_none(list)
                db.upd_prod(list[0], list[1], list[2], list[3])
            output = db.conn.execute("SELECT * FROM product").fetchall()
        elif request.form.get('del') == 'del':
            productID = request.form["productID2"]
            if db.cursor.execute("SELECT * FROM product WHERE productID=?", (productID,)).fetchone() is not None:
                db.del_prod(productID)
            else:
                flash("Product ID does not exist.")
            output = db.conn.execute("SELECT * FROM product").fetchall()
        return render_template("products.html", output=output)

    @staticmethod
    def __orders_manager(request, db, output):
        if request.form.get('sort') == 'sort':
            return Util.get_sort(request.form, "orders", "orders", db)
        elif request.form.get('add') == 'add':
            orderID = request.form["orderID"]
            customerID = request.form["customerID"]
            employeeID = request.form["employeeID"]
            if not customerID:
                customerID = None
            if not employeeID:
                employeeID = None
            if not orderID:
                flash("Order # required for updates.")
                return render_template("orders.html", output=output)
            if customerID is None or not Checks.is_customerID_exist(customerID, db.cursor):
                if employeeID is None or not Checks.is_employeeID_exist(employeeID, db.cursor):
                    if not (Checks.is_order_exist(orderID, db.cursor)):
                        db.upd_ord(orderID, customerID, employeeID)
                    else:
                        flash("Order # does not exist.")
                        return render_template("orders.html", output=output)
                else:
                    flash("Employee ID does not exist.")
                    return render_template("orders.html", output=output)
            else:
                flash("Customer ID does not exist.")
                return render_template("orders.html", output=output)
            output = db.conn.execute("SELECT * FROM orders").fetchall()
        elif request.form.get('del') == 'del':
            orderID = request.form["orderID2"]
            if not (Checks.is_order_exist(orderID, db.cursor)):
                db.del_ord(int(orderID))
            output = db.conn.execute("SELECT * FROM orders").fetchall()
        return render_template("orders.html", output=output)

    @staticmethod
    def __place_ord_manager(request, db, output):
        ord_dict = dict()
        phone = Util.__pl_ord_inp(request.form['phone'])
        employeeID = Util.__pl_ord_inp(request.form['employeeID'])
        # list of productIDs to use as dictionary keys
        keys = Util.__get_keys()
        # if the user entered an employeeID, but the employeeID does not exist, an error message shows for the user
        if employeeID is not None and db.cursor.execute("SELECT * FROM employee WHERE employeeID=?",
                                                        (int(employeeID),)).fetchone() is None:
            flash("EmployeeID not found.")
            return render_template('placeOrder.html', output=output)
        # if the user entered a phone number, but the number does not exist, an error message shows for the user
        if phone is not None and db.cursor.execute("SELECT * FROM customer WHERE phone=?",
                                                   (int(phone),)).fetchone() is None:
            flash("Phone not found.")
            return render_template('placeOrder.html', output=output)
        # adds all the quantity inputs to a dictionary with the corresponding productIDs as keys
        for x in range(len(db.conn.execute("SELECT productID FROM product").fetchall())):
            ord_dict[str(keys[x][0])] = request.form[str(keys[x][0])]
        # carries out order transaction. if transaction fails, an error messages shows for the user
        if not db.ord_transaction(phone, employeeID, ord_dict):
            flash("There was an error when placing the order.")
        return redirect(url_for('index'))

    # gets list of all existing productIDs to use as dictionary keys
    @staticmethod
    def __get_keys():
        conn = sqlite3.connect('flowershopdatabase.db', check_same_thread=False)
        keys = conn.cursor().execute("SELECT productID FROM product").fetchall()
        conn.close()
        return keys

    @staticmethod
    def __pl_ord_inp(input):
        if not input:
            return None
        else:
            return int(input)

    @staticmethod
    def get_sort(request_form, table, html, db):
        output = db.conn.execute("SELECT * FROM " + table).fetchall()
        filt_attr = request_form["filt_attr"]
        op = request_form["op"]
        value = request_form["value"]
        sort_attr = request_form["sort_attr"]
        asc = request_form["asc"]
        if not Checks.sort_filt_valid(filt_attr, op, value, sort_attr, asc):
            return render_template(html + '.html', output=output)
        output = Util.get_table(table, db, filt_attr, op, value, sort_attr, asc)
        return render_template(html + '.html', output=output)

    @staticmethod
    def get_table(table_name, db, filt_attr, op, value, sort_attr, asc):
        filt_blank = Checks.is_filt_blank(filt_attr, op, value)
        sort_blank = Checks.is_sort_blank(sort_attr, asc)
        if filt_blank and sort_blank:
            return db.conn.execute("SELECT * FROM " + table_name).fetchall()
        elif not filt_blank and sort_blank:
            return db.filter_table(table_name, filt_attr, value, op)
        elif filt_blank and not sort_blank:
            return db.sort_table(table_name, sort_attr, asc)
        else:
            return db.sort_filter(table_name, sort_attr, asc, filt_attr, value, op)
