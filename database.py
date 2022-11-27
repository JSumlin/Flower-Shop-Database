from checks import Checks
from flask import flash
import sqlite3


class Database:
    #constructor
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    #insert function for employee table
    def add_emp(self, fname, lname, position, salary):
        if not Checks.is_pos_num(salary, "float", "Salary"):
            return
        if fname is None or lname is None or salary is None:
            print("Invalid input. First name, last name, and salary all require inputs.")
            return
        self.cursor.execute("""INSERT INTO employee (fname, lname, position, salary)
            VALUES (?, ?, ?, ?)""", (fname, lname, position, float(salary)))
        self.conn.commit()

    #insert function for customer table
    def add_cus(self, fname, lname, phone):
        if not Checks.is_phone(phone):
            print("Invalid input. Phone number must be a 10 digit number formatted 1234567890.")
            return
        if not Checks.is_phone_unique(phone, self.cursor):
            print("Invalid input. Phone number already exists.")
            return
        if fname is None or lname is None:
            print("Invalid input. First and last name required.")
            return
        self.cursor.execute("INSERT INTO customer (fname, lname, phone) VALUES (?, ?,?)", (fname, lname, int(phone)))
        self.conn.commit()

    #insert function for product table
    def add_prod(self, p_desc, price, stock):
        if not Checks.is_pos_num(price, "float", "Price"):
            return
        if not Checks.is_pos_num(stock, "int", "Stock"):
            return
        if p_desc is None:
            print("Invalid input. Product description required.")
            return
        self.cursor.execute("INSERT INTO product (p_desc, price, stock) VALUES (?, ?, ?)",
                       (p_desc, float(price), int(stock)))
        self.conn.commit()

    #insert function for orders table
    def add_ord(self, customerID, employeeID, total):
        if not Checks.is_pos_int([customerID, employeeID]) or not Checks.is_pos_float([total]):
            return
        customerID = int(customerID)
        employeeID = int(employeeID)
        self.cursor.execute("SELECT customerID FROM customer WHERE customerID=?", (customerID,))
        if self.cursor.fetchone() is None:
            print("CustomerID does not exist. Setting to NULL.")
            customerID = None
        self.cursor.execute("SELECT employeeID FROM employee WHERE employeeID=?", (employeeID,))
        if self.cursor.fetchone() is None:
            print("EmployeeID does not exist. Setting to NULL.")
            employeeID = None
        self.cursor.execute("INSERT INTO orders (customerID, employeeID, total) VALUES (?, ?, ?)",
                       (customerID, employeeID, float(total)))
        self.conn.commit()

    def add_pur(self,orderID,productID,quantity):
        if not Checks.is_pos_int([orderID, productID, quantity]):
            return
        self.cursor.execute("INSERT INTO purchase (orderID, productID, quantity) VALUES (?, ?, ?)",
                       (orderID, productID, quantity))
        self.conn.commit()

    #update function for customer table
    def upd_cus(self, customerID, fname, lname, phone):
        var_list = [fname, lname, phone]
        name_list = ["customerID", "fname", "lname", "phone"]
        if not Checks.is_pos_num(customerID, "int", "customerID"):
            return
        Checks.none_update(var_list, name_list, "customer", customerID, self.cursor)
        if not Checks.is_phone(var_list[2]):
            flash("Invalid input. Phone number must be a 10 digit number formatted 1234567890.")
            return
        self.cursor.execute("UPDATE CUSTOMER SET FNAME = ?, LNAME = ?, PHONE = ? WHERE CUSTOMERID = ?",
                            (var_list[0], var_list[1], var_list[2], customerID))
        self.conn.commit()

    #update function for employee table
    def upd_emp(self,employeeID, fname, lname, position, salary):
        var_list = [fname, lname, position, salary]
        name_list = ["employeeID", "fname", "lname", "position", "salary"]
        Checks.none_update(var_list, name_list, "employee", employeeID, self.cursor)
        if not Checks.is_pos_int([employeeID]) or not Checks.is_pos_float([var_list[3]]):
            return
        self.cursor.execute("UPDATE EMPLOYEE SET FNAME = ?, LNAME = ?, POSITION = ?,SALARY=? WHERE EMPLOYEEID = ?",
                            (var_list[0], var_list[1], var_list[2], var_list[3], employeeID))
        self.conn.commit()

    #update function for product table
    def upd_prod(self,productID, p_desc, price, stock):
        var_list = [p_desc, price, stock]
        name_list = ["productID", "p_desc", "price", "stock"]
        Checks.none_update(var_list, name_list, "product", productID, self.cursor)
        if not Checks.is_pos_int([var_list[2], productID]) or not Checks.is_pos_float([var_list[1]]):
            return
        self.cursor.execute("UPDATE PRODUCT SET P_DESC = ?, PRICE = ?, STOCK = ? WHERE PRODUCTID = ?",
                                (var_list[0], float(var_list[1]), int(var_list[2]),int(productID)))
        self.conn.commit()

    #update function for orders table
    def upd_ord(self,orderID, customerID, employeeID):
        if customerID is not None and not Checks.is_pos_num(customerID, "int", "customerID"):
            return
        if employeeID is not None and not Checks.is_pos_num(employeeID, "int", "employeeID"):
            return
        if not Checks.is_pos_num(orderID, "int", "orderID"):
            return
        if customerID is not None and employeeID is not None:
            self.cursor.execute("UPDATE ORDERS SET CUSTOMERID = ?, EMPLOYEEID = ? WHERE ORDERID = ?",
                                (int(customerID), int(employeeID), int(orderID)))
        elif employeeID is None and customerID is not None:
            self.cursor.execute("UPDATE ORDERS SET CUSTOMERID = ? WHERE ORDERID = ?",
                                (int(customerID), int(orderID)))
        elif customerID is None and employeeID is not None:
            self.cursor.execute("UPDATE ORDERS SET EMPLOYEEID = ? WHERE ORDERID = ?",
                                (int(employeeID), int(orderID)))
        else:
            flash("Must enter customer ID and/or employee ID to update.")
        self.conn.commit()

    def upd_pur(self,orderID,productID,quantity):
        if not Checks.is_pos_int([orderID, productID, quantity]):
            return
        with self.conn:
            self.cursor.execute("BEGIN")
            try:
                quan_diff = int(quantity) - self.cursor.execute("""SELECT quantity FROM purchase 
                WHERE orderID=? and productID = ?""", (orderID, productID)).fetchone()[0]
                stock = self.cursor.execute("""SELECT stock FROM product WHERE productID = ?""",
                                                   (productID,)).fetchone()[0]
                if quan_diff > stock:
                    flash("Not enough stock for the increase in quantity.")
                    return
                elif quan_diff > 0:
                    self.cursor.execute("UPDATE product SET stock=? WHERE productID=?", (stock-quan_diff,productID))
                price = self.cursor.execute("SELECT price FROM product WHERE productID = ?",
                                               (productID,)).fetchone()[0]
                total= self.cursor.execute("SELECT total FROM orders WHERE orderID=?", (orderID,)).fetchone()[0]
                self.cursor.execute("UPDATE orders SET total = ? WHERE orderID=?", (total+price*quan_diff, orderID))
                self.cursor.execute("UPDATE Purchase SET quantity = ? WHERE orderID = ? and PRODUCTID = ?",
                                    (int(quantity), int(orderID), int(productID)))
                self.conn.commit()
            except sqlite3.Error:
                print("transaction failed")
                self.cursor.execute("ROLLBACK")
        self.conn.commit()

    #delete function for customer table
    def del_cus(self,customerID):
        if not Checks.is_pos_num(customerID, "int", "customerID"):
            return
        self.cursor.execute("DELETE FROM CUSTOMER WHERE CUSTOMERID = "+str(customerID))
        self.conn.commit()

    #delete function for employee table
    def del_emp(self,employeeID):
        if not Checks.is_pos_num(employeeID, "int", "employeeID"):
            return
        self.cursor.execute("DELETE FROM EMPLOYEE WHERE EMPLOYEEID = "+str(employeeID))
        self.conn.commit()

    #delete function for product table
    def del_prod(self,productID):
        if not Checks.is_pos_num(productID, "int", "productID"):
            return
        self.cursor.execute("DELETE FROM PRODUCT WHERE PRODUCTID = "+str(productID))
        self.conn.commit()

    #delete function for orders table
    def del_ord(self,orderID):
        if not Checks.is_pos_num(orderID, "int", "orderID"):
            return
        self.cursor.execute("DELETE FROM ORDERS WHERE ORDERID = "+str(orderID))
        self.conn.commit()

    #delete function for purchasetable
    def del_pur(self,orderID,productID):
        if not Checks.is_pos_int([orderID, productID]):
            return
        with self.conn:
            self.cursor.execute("BEGIN")
            try:
                quantity = self.cursor.execute("SELECT quantity FROM purchase WHERE orderID=? and productID = ?",
                                               (orderID, productID)).fetchone()[0]
                price = self.cursor.execute("SELECT price FROM product WHERE productID = ?",
                                               (productID,)).fetchone()[0]
                total = self.cursor.execute("SELECT total FROM orders WHERE orderID=?", (orderID,)).fetchone()[0]
                self.cursor.execute("UPDATE orders SET total = ? WHERE orderID=?", (total-price*quantity, orderID))
                self.cursor.execute("DELETE FROM purchase WHERE orderID=? and PRODUCTID = ?", (orderID, productID))
                self.conn.commit()
            except sqlite3.Error:
                print("transaction failed")
                self.cursor.execute("ROLLBACK")

    #sorted select functions
    def sort_table(self,table,order,asc):
        return self.conn.execute(f"SELECT * FROM {table} ORDER BY {order} {asc}").fetchall()

    #Filters results
    def filter_table(self,table,target,value,op):
        return self.conn.execute(f"SELECT * FROM {table} WHERE {target} {op} \"{value}\"").fetchall()

    #sorts and filters
    def sort_filter(self,table,order,asc,target,value,op):
        return self.conn.execute(f"SELECT * FROM {table} WHERE {target} {op} \"{value}\" ORDER BY {order} {asc}").fetchall()

    # returns the customerID linked to a phone number. If the phone number is None, it returns None.
    def get_customerID(self, phone):
        if phone is not None:
            return int(self.cursor.execute("SELECT customerID FROM customer WHERE phone=?",
                                           (phone,)).fetchone()[0])
        else:
            return None

    # creates a new order with a total of 0 so that the orderID can be used in ord_transaction
    def __get_new_orderID(self, customerID, employeeID):
        self.cursor.execute("INSERT INTO orders (customerID, employeeID, total) VALUES (?, ?, ?)",
                            (customerID, employeeID, 0))
        return self.cursor.execute("SELECT MAX(orderID) from orders").fetchone()[0]

    # Uses the order dictionary, and the orderID made in __get_new_orderID to add the products purchased and their
    # quantity to the purchase table. It also tallies to total for the orders table and updates the stock on the
    # product table.
    def __ord_trans_util(self, ord_dict, orderID):
        keys = list(ord_dict.keys())  # a list of all productIDs that exist in the database
        for x in range(len(ord_dict)):
            if int(ord_dict[keys[x]]) > 0:  # if the quantity for the productID is greater than 0
                self.cursor.execute("INSERT INTO purchase (orderID, productID, quantity) VALUES (?, ?, ?)",
                                    (orderID, keys[x], int(ord_dict[keys[x]])))
                price = self.cursor.execute("SELECT price FROM product WHERE productID=?",
                                            (keys[x],)).fetchone()[0]
                # tallies total. Updates total to current total + quantity * price
                self.cursor.execute("UPDATE orders SET total=? WHERE orderID=?",
                                    (round(self.cursor.execute("SELECT total FROM orders WHERE orderID=?",
                                                               (orderID,)).fetchone()[0] + int(ord_dict[keys[x]]) *
                                           price, 2), orderID))
                # Updates stock. Subtracts quantity purchased from current stock.
                self.cursor.execute("UPDATE product SET stock=? WHERE productID=?",
                                    ((self.cursor.execute("SELECT stock FROM product WHERE productID=?",
                                                          (keys[x],)).fetchone()[0] - int(ord_dict[keys[x]])), keys[x]))

    #handles transactions for placing orders
    def ord_transaction(self, phone, employeeID, ord_dict: dict):
        with self.conn:
            self.cursor.execute("BEGIN")
            try:
                orderID = self.__get_new_orderID(self.get_customerID(phone), employeeID)
                self.__ord_trans_util(ord_dict, orderID)
                self.conn.commit()
            except sqlite3.Error:
                print("transaction failed")
                self.cursor.execute("ROLLBACK")
                return False
            return True
