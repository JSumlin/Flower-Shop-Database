from flask import flash


class Checks:

    @staticmethod
    def is_num(testInput, type):
        if testInput is None:
            return False
        try:
            if type == "float":
                testFloat = float(testInput)
            elif type == "int":
                testInt = int(testInput)
            else:
                raise Exception("Invalid type.")
            return True
        except ValueError:
            return False

    @staticmethod
    def is_pos(testInput, type):
        if type == "float" and float(testInput) < 0:
            return False
        if type == "int" and int(testInput) < 0:
            return False
        return True

    @staticmethod
    def is_pos_num(testInput, type, varName):
        if not Checks.is_num(testInput, type) or not Checks.is_pos(testInput, type):
            print("Invalid input. " + varName + " must be a positive number.")
            return False
        return True

    @staticmethod
    def is_phone(phone):
        if phone is None:
            return False
        try:
            testInt = int(phone)
        except ValueError:
            return False
        if len(str(phone)) != 10:
            return False
        return True

    @staticmethod
    def is_phone_unique(phone, cursor):
        cursor.execute("SELECT * FROM customer WHERE phone=?", (phone,))
        if cursor.fetchone() is None:
            return True
        return False

    @staticmethod
    def is_sort_valid(attribute, asc):
        if (attribute == "") != (asc == ""):
            return False
        return True

    @staticmethod
    def is_filt_valid(attribute, op, value):
        if (attribute == "") != (op == ""):
            return False
        if attribute+op == "" and value:
            return False
        if attribute+op != "" and not value:
            return False
        return True

    @staticmethod
    def is_sort_blank(attribute, asc):
        if attribute+asc == "":
            return True
        return False

    @staticmethod
    def is_filt_blank(attribute, op, value):
        if attribute+op == "" and not value:
            return True
        return False

    @staticmethod
    def sort_filt_valid(filt_attr, op, value, sort_attr, asc):
        if not Checks.is_filt_valid(filt_attr, op, value):
            flash("Must fill all filter options or none.")
            return False
        if not Checks.is_sort_valid(sort_attr, asc):
            flash("Must choose both sort options or neither.")
            return False
        return True

    @staticmethod
    def is_employee_exist(fname,lname,cursor):
        cursor.execute("SELECT * FROM employee WHERE fname=? and lname=?", (fname,lname))
        if cursor.fetchone() is None:
            return True
        return False

    @staticmethod
    def is_employeeID_exist(employeeID,cursor):
        cursor.execute("SELECT * FROM employee WHERE employeeID=?", (employeeID,))
        if cursor.fetchone() is None:
            return True
        return False

    @staticmethod
    def is_customerID_exist(customerID,cursor):
        cursor.execute("SELECT * FROM customer WHERE customerID=?", (customerID,))
        if cursor.fetchone() is None:
            return True
        return False

    @staticmethod
    def is_product_exist(product, cursor):
        cursor.execute("SELECT * FROM product WHERE p_desc=?", (product,))
        if cursor.fetchone() is None:
            return True
        return False

    @staticmethod
    def is_productID_exist(productID, cursor):
        cursor.execute("SELECT * FROM product WHERE productID=?", (int(productID),))
        if cursor.fetchone() is None:
            return True
        return False

    @staticmethod
    def is_order_exist(orderID,cursor):
        cursor.execute("SELECT * FROM orders WHERE orderID=?", (orderID,))
        if cursor.fetchone() is None:
            return True
        return False

    @staticmethod
    def is_purchase_exist(orderID,productID,cursor):
        cursor.execute("SELECT * FROM purchase WHERE orderID=? and productID=?", (orderID,productID))
        if cursor.fetchone() is None:
            return True
        return False

    @staticmethod
    def none_update(var_list, name_list, table, ID, cursor):
        for x in range(len(var_list)):
            if var_list[x] is None:
                var_list[x] = cursor.execute("SELECT "+name_list[x+1]+" FROM "+table+" WHERE "+name_list[0]+"=?",
                                             (ID,)).fetchone()[0]

    @staticmethod
    def is_pos_int(test_list):
        for x in test_list:
            if not Checks.is_pos_num(x, "int", "Variable"):
                return False
        return True

    @staticmethod
    def is_pos_float(test_list):
        for x in test_list:
            if not Checks.is_pos_num(x, "float", "Variable"):
                return False
        return True

    @staticmethod
    def not_then_none(list):
        for x in range(len(list)-1):
            if not list[x+1]:
                list[x+1] = None
