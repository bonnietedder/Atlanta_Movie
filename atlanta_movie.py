import re
import pymysql
import sys
from typing import *
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QDialog,
    QGroupBox,
    QComboBox,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTableView,
    QAbstractItemView,
    QLabel,
    QListView,
    QCheckBox,
)
import datetime
from pprint import pprint


class SimpleTableModel(QAbstractTableModel):
    def __init__(self, data: List[Dict[str, str]]):
        QAbstractTableModel.__init__(self, None)
        self.data = data
        self.headers = [k for k, v in data[0].items()]
        self.rows = [[v for k, v in record.items()] for record in data]

    def rowCount(self, parent):
        return len(self.rows)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if (not index.isValid()) or (role != Qt.DisplayRole):
            return QVariant()
        else:
            return QVariant(self.rows[index.row()][index.column()])

    def row(self, index):
        return self.data[index]

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        elif orientation == Qt.Vertical:
            return section + 1
        else:
            return self.headers[section]


# ================Screen 1 Login================
class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        self.setWindowTitle("Atlanta Movie Login")
        self.user = QLineEdit('cool_class4400')
        self.password = QLineEdit('333333333')
        form_group_box = QGroupBox("Login Credentials")
        layout = QFormLayout()
        layout.addRow(QLabel("Username:"), self.user)
        layout.addRow(QLabel("Password:"), self.password)

        self.login = QPushButton('Login')
        self.register = QPushButton('Register')

        self.login.pressed.connect(self.run_login)
        self.register.clicked.connect(self.run_register)
        form_group_box.setLayout(layout)
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(form_group_box)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.login)
        hbox_layout.addWidget(self.register)
        vbox_layout.addLayout(hbox_layout)
        self.setLayout(vbox_layout)

    def run_login(self):
        test1 = curs.execute(f'call user_login("{self.user.text()}", "{self.password.text()}");')
        test2 = curs.execute(f'select * from user where username = "{self.user.text()}" and status = "Approved";')
        connection.commit()
        if test1 == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid login", "Please enter a valid username and password combination.")
            w.show()
        elif test2 == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid login", "Account must be approved to log in.")
            w.show()
        else:
            curs.execute('select * from UserLogin;')
            connection.commit()
            info = curs.fetchone()
            sum = info['isCustomer'] + info['isAdmin'] + info['isManager']
            self.close()
            if sum == 1:
                if info['isAdmin'] == 1:
                    admin_only_func(self.user.text()).exec()
                elif info['isManager'] == 1:
                    manager_only_func(self.user.text()).exec()
                else:
                    customer_only_func(self.user.text()).exec()
            elif sum == 2:
                if (info['isCustomer'] + info['isAdmin']) == 2:
                    admin_customer_func(self.user.text()).exec()
                else:
                    manager_customer_func(self.user.text()).exec()
            else:
                self.close()
                user_func(self.user.text()).exec()

    def run_register(self):
        self.close()
        RegisterNav().exec()


# ================Screen 2 Register Navigation================
class RegisterNav(QDialog):
    def __init__(self):
        super(RegisterNav, self).__init__()
        self.setWindowTitle("Register Navigation")
        self.user = QPushButton('User Only')
        self.cust = QPushButton('Customer Only')
        self.man = QPushButton('Manager Only')
        self.man_cust = QPushButton('Manager-Customer')
        self.back = QPushButton('Back')

        self.user.pressed.connect(self.run_user)
        self.cust.pressed.connect(self.run_cust)
        self.man.pressed.connect(self.run_man)
        self.man_cust.pressed.connect(self.run_man_cust)
        self.back.pressed.connect(self.run_back)
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.user)
        vbox_layout.addWidget(self.cust)
        vbox_layout.addWidget(self.man)
        vbox_layout.addWidget(self.man_cust)
        vbox_layout.addWidget(self.back)
        self.setLayout(vbox_layout)

    def run_user(self):
        self.close()
        UserReg().exec()

    def run_cust(self):
        self.close()
        CustReg().exec()

    def run_man(self):
        self.close()
        ManReg().exec()

    def run_man_cust(self):
        self.close()
        ManCustReg().exec()

    def run_back(self):
        self.close()
        Login().exec()


# ================Screen 3 User Registration================
class UserReg(QDialog):
    def __init__(self):
        super(UserReg, self).__init__()
        self.setWindowTitle('User Registration')
        form_group_box = QGroupBox("User Information")
        self.firstname = QLineEdit()
        self.lastname = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.confirm_pass = QLineEdit()
        layout = QFormLayout()
        layout.addRow(QLabel("First Name:"), self.firstname)
        layout.addRow(QLabel("Last Name:"), self.lastname)
        layout.addRow(QLabel("Username:"), self.username)
        layout.addRow(QLabel("Password:"), self.password)
        layout.addRow(QLabel("Confirm Password:"), self.confirm_pass)
        form_group_box.setLayout(layout)
        self.back = QPushButton('Back')
        self.register = QPushButton('Register')
        self.back.pressed.connect(self.run_back)
        self.register.pressed.connect(self.run_register)
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(form_group_box)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.back)
        hbox_layout.addWidget(self.register)
        vbox_layout.addLayout(hbox_layout)
        self.setLayout(vbox_layout)

    def run_back(self):
        self.close()
        RegisterNav().exec()

    def run_register(self):
        if self.password.text() != self.confirm_pass.text():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Passwords do not match.")
            w.show()
        elif len(self.password.text()) < 8:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Password needs to be at least 8 characters long.")
            w.show()
        else:
            test = curs.execute(f'select * from user where username = "{self.username.text()}";')
            connection.commit()
            if test == 1:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid", "Username already exists.")
                w.show()
            else:
                curs.execute(f'call user_register("{self.username.text()}", "{self.password.text()}", '
                             f'"{self.firstname.text()}", "{self.lastname.text()}");')
                connection.commit()


# ================Screen 4 Customer-Only Registration================
class CustReg(QDialog):
    def __init__(self):
        super(CustReg, self).__init__()
        self.setWindowTitle("Customer Registration")
        form_group_box = QGroupBox("Customer Information")
        self.credit_card_list = []
        self.removed = []
        self.firstname = QLineEdit()
        self.lastname = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.confirm_pass = QLineEdit()

        self.list_view = QListView()
        self.list_model = QStandardItemModel(self.list_view)
        self.list_view.setModel(self.list_model)
        self.list_view.clicked[QModelIndex].connect(self.clicked)
        self.credit_card = QLineEdit()
        self.credit_card.textChanged.connect(self.enable_buttons)

        layout = QFormLayout()
        layout.addRow(QLabel("First Name:"), self.firstname)
        layout.addRow(QLabel("Last Name:"), self.lastname)
        layout.addRow(QLabel("Username:"), self.username)
        layout.addRow(QLabel("Password:"), self.password)
        layout.addRow(QLabel("Confirm Password:"), self.confirm_pass)
        layout.addRow(QLabel("Credit Card #:"), self.credit_card)
        form_group_box.setLayout(layout)

        self.add = QPushButton('Add')
        self.add.setEnabled(False)
        self.remove = QPushButton('Remove')
        self.remove.setEnabled(False)
        self.back = QPushButton('Back')
        self.register = QPushButton('Register')
        self.add.pressed.connect(self.run_add)
        self.remove.pressed.connect(self.run_remove)
        self.back.pressed.connect(self.run_back)
        self.register.pressed.connect(self.run_register)
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(form_group_box)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.add)
        hbox_layout.addWidget(self.remove)
        hbox_layout.addWidget(self.back)
        hbox_layout.addWidget(self.register)
        vbox_layout.addWidget(QLabel('Added Credit Cards:'))
        vbox_layout.addWidget(self.list_view)
        vbox_layout.addLayout(hbox_layout)
        self.setLayout(vbox_layout)

    def run_add(self):
        test = curs.execute(f'select * from customercreditcard where creditcardnum = "{self.credit_card.text()}";')
        connection.commit()
        if len(self.credit_card_list) >= 5:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Already 5 Credit Cards!")
            w.show()
        elif len(self.credit_card.text()) != 16:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Credit card number must be 16-digits long.")
            w.show()
        elif not self.credit_card.text().isnumeric():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Credit card number must be numeric.")
            w.show()
        elif self.credit_card.text() in self.credit_card_list:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Credit card number is already added!")
            w.show()
        elif test:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Credit card number already exists in system.")
            w.show()
        else:
            new_list_item = QStandardItem(self.credit_card.text())
            self.list_model.appendRow(new_list_item)
            self.credit_card_list.append(self.credit_card.text())
            self.credit_card.setText("")
            self.add.setEnabled(False)

    def run_remove(self):
        if self.removed[0] in self.credit_card_list:
            self.list_model.removeRow(self.removed[1])
            self.credit_card_list.remove(self.removed[0])
        else:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Please select a credit card number to remove. \n"
                                              "The selected credit card number will be highlighted blue.")
            w.show()

    def run_back(self):
        self.close()
        RegisterNav().exec()

    def run_register(self):
        if (self.firstname.text() == '' or self.lastname.text() == '' or self.username.text() == ''
                or self.password.text() == '' or self.confirm_pass == '' or len(self.credit_card_list) == 0):
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "All fields are required and you must enter "
                                              "at least one credit card number.")
            w.show()
        elif self.password.text() != self.confirm_pass.text():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Passwords do not match.")
            w.show()
        elif len(self.password.text()) < 8:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Password must be at least 8 characters long.")
            w.show()
        else:
            test = curs.execute(f'select * from user where username = "{self.username.text()}";')
            if test != 0:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid", "Username already exists")
                w.show()
            else:
                curs.execute(f'call customer_only_register("{self.username.text()}", "{self.password.text()}", '
                             f'"{self.firstname.text()}", "{self.lastname.text()}");')
                for creditcardnum in self.credit_card_list:
                    curs.execute(f'call customer_add_creditcard("{self.username.text()}", "{creditcardnum}");')
                i = QMessageBox()
                QMessageBox.information(i, "Success", "Customer registered.")
                i.show()
            connection.commit()

    def enable_buttons(self):
        if len(self.credit_card.text()) == 16:
            self.add.setEnabled(True)

    def clicked(self, index):
        self.remove.setEnabled(True)
        item = self.list_model.itemFromIndex(index)
        self.removed = [item.text(), index.row()]

# ================Screen 5 Manager-Only Registration================
class ManReg(QDialog):
    def __init__(self):
        super(ManReg, self).__init__()
        self.setWindowTitle("Manager-Only Registration")
        form_group_box = QGroupBox("Manager-Only Information")
        self.firstname = QLineEdit()
        self.lastname = QLineEdit()
        self.username = QLineEdit()

        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        self.com = com
        self.company = QComboBox()
        self.company.addItems(['ALL'] + self.com)

        self.password = QLineEdit()
        self.confirm_pass = QLineEdit()
        self.street_add = QLineEdit()
        self.city = QLineEdit()
        self.state = QComboBox()
        self.state.addItems(["ALL", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
               "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
               "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"])
        self.zipcode = QLineEdit()
        layout = QFormLayout()
        layout.addRow(QLabel("First Name:"), self.firstname)
        layout.addRow(QLabel("Last Name:"), self.lastname)
        layout.addRow(QLabel("Username:"), self.username)
        layout.addRow(QLabel("Company:"), self.company)
        layout.addRow(QLabel("Password:"), self.password)
        layout.addRow(QLabel("Confirm Password:"), self.confirm_pass)
        layout.addRow(QLabel("Street Address:"),self.street_add)
        layout.addRow(QLabel("City:"),self.city)
        layout.addRow(QLabel("State:"),self.state)
        layout.addRow(QLabel("Zipcode:"),self.zipcode)
        form_group_box.setLayout(layout)
        self.back = QPushButton('Back')
        self.register = QPushButton('Register')
        self.back.pressed.connect(self.run_back)
        self.register.pressed.connect(self.run_register)
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(form_group_box)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.back)
        hbox_layout.addWidget(self.register)
        vbox_layout.addLayout(hbox_layout)
        self.setLayout(vbox_layout)

    def run_back(self):
        self.close()
        RegisterNav().exec()

    def run_register(self):
        if (self.firstname.text() == '' or self.lastname.text() == '' or self.username.text() == ''
                or self.password.text() == '' or self.confirm_pass == '' or self.company.currentText() == 'ALL'
                or self.street_add.text() == '' or self.city.text() == '' or self.state.currentText() == 'ALL'
                or self.zipcode.text() == ''):
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "All fields are required and you must enter "
                                              "a specific company and state.")
            w.show()
        elif len(self.zipcode.text()) != 5 or not self.zipcode.text().isnumeric():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Zipcode must be 5 digits and must be numeric.")
            w.show()
        elif len(self.password.text()) < 8:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Password must be at least 8 characters long.")
            w.show()
        elif self.password.text() != self.confirm_pass.text():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Passwords do not match.")
            w.show()
        elif self.company.currentText() == 'ALL':
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Manager must work for a specific company")
            w.show()
        else:
            test = curs.execute(f'select * from user where username = "{self.username.text()}";')
            connection.commit()
            if test == 1:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid", "Username already exists")
                w.show()
            else:
                entered_address = self.street_add.text() + self.city.text()+self.state.currentText()+self.zipcode.text()
                curs.execute('select manStreet, manCity, manState, manZipcode from Manager;')
                all_address = curs.fetchall()
                test_address = True
                if all_address:
                    for i in all_address:
                        one_ad = i["manStreet"] + i["manCity"] + i["manState"] + i["manZipcode"]
                        if one_ad == entered_address:
                            test_address =  False
                            x = QMessageBox()
                            QMessageBox.warning(x, "Duplicate Address", "The entered address already exists in the database. Please enter another address for this manager. ")
                            break
                if test_address:
                    curs.execute(f'call manager_only_register("{self.username.text()}", "{self.password.text()}", '
                                 f'"{self.firstname.text()}", "{self.lastname.text()}", "{self.company.currentText()}", '
                                 f'"{self.street_add.text()}", "{self.city.text()}", "{self.state.currentText()}",  "{self.zipcode.text()}");')
                    w = QMessageBox()
                    QMessageBox.information(w, "Success", "Manager registered.")
                    w.show()
                    connection.commit()

# ================Screen 6 Manager-Customer Registration================
class ManCustReg(QDialog):
    def __init__(self):
        super(ManCustReg, self).__init__()
        self.setWindowTitle("Manager-Customer Registration")
        form_group_box = QGroupBox("Manager-Customer Information")
        self.credit_card_list = []
        self.removed = []
        self.firstname = QLineEdit()
        self.lastname = QLineEdit()
        self.username = QLineEdit()

        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        self.com = com
        self.company = QComboBox()
        self.company.addItems(['ALL'] + self.com)

        self.password = QLineEdit()
        self.confirm_pass = QLineEdit()
        self.street_add = QLineEdit()
        self.city = QLineEdit()
        self.state = QComboBox()
        self.state.addItems(["ALL", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
               "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
               "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"])
        self.zipcode = QLineEdit()

        self.list_view = QListView()
        self.list_model = QStandardItemModel(self.list_view)
        self.list_view.setModel(self.list_model)
        self.list_view.clicked[QModelIndex].connect(self.clicked)
        self.credit_card = QLineEdit()
        self.credit_card.textChanged.connect(self.enable_buttons)

        layout = QFormLayout()
        layout.addRow(QLabel("First Name:"), self.firstname)
        layout.addRow(QLabel("Last Name:"), self.lastname)
        layout.addRow(QLabel("Username:"), self.username)
        layout.addRow(QLabel("Company:"), self.company)
        layout.addRow(QLabel("Password:"), self.password)
        layout.addRow(QLabel("Confirm Password:"), self.confirm_pass)
        layout.addRow(QLabel("Street Address:"),self.street_add)
        layout.addRow(QLabel("City:"),self.city)
        layout.addRow(QLabel("State:"),self.state)
        layout.addRow(QLabel("Zipcode:"),self.zipcode)
        layout.addRow(QLabel("Credit Card #:"),self.credit_card)
        form_group_box.setLayout(layout)

        self.add = QPushButton('Add')
        self.add.setEnabled(False)
        self.remove = QPushButton('Remove')
        self.remove.setEnabled(False)
        self.back = QPushButton('Back')
        self.register = QPushButton('Register')
        self.add.pressed.connect(self.run_add)
        self.remove.pressed.connect(self.run_remove)
        self.back.pressed.connect(self.run_back)
        self.register.pressed.connect(self.run_register)
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(form_group_box)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.add)
        hbox_layout.addWidget(self.remove)
        hbox_layout.addWidget(self.back)
        hbox_layout.addWidget(self.register)
        vbox_layout.addWidget(QLabel('Added Credit Cards:'))
        vbox_layout.addWidget(self.list_view)
        vbox_layout.addLayout(hbox_layout)
        self.setLayout(vbox_layout)

    def run_add(self):
        test = curs.execute(f'select * from customercreditcard where creditcardnum = "{self.credit_card.text()}";')
        connection.commit()
        if len(self.credit_card_list) >= 5:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Already 5 Credit Cards!")
            w.show()
        elif len(self.credit_card.text()) != 16:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Credit card number must be 16-digits long.")
            w.show()
        elif not self.credit_card.text().isnumeric():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Credit card number must be numeric.")
            w.show()
        elif self.credit_card.text() in self.credit_card_list:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Credit card number is already added!")
            w.show()
        elif test:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Credit card number already exists in system.")
            w.show()
        else:
            new_list_item = QStandardItem(self.credit_card.text())
            self.list_model.appendRow(new_list_item)
            self.credit_card_list.append(self.credit_card.text())
            self.credit_card.setText("")
            self.add.setEnabled(False)

    def run_remove(self):
        if self.removed[0] in self.credit_card_list:
            self.list_model.removeRow(self.removed[1])
            self.credit_card_list.remove(self.removed[0])
        else:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Please select a credit card number to remove. \n"
                                              "The selected credit card number will be highlighted blue.")
            w.show()

    def run_back(self):
        self.close()
        RegisterNav().exec()

    def run_register(self):
        if (self.firstname.text() == '' or self.lastname.text() == '' or self.username.text() == ''
                or self.password.text() == '' or self.confirm_pass == '' or self.company.currentText() == 'ALL'
                or self.street_add.text() == '' or self.city.text() == '' or self.state.currentText() == 'ALL'
                or self.zipcode.text() == '' or len(self.credit_card_list) == 0):
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "All fields are required and you must enter "
                                              "at least one credit card number.\n"
                                              "You must specify a company and state.")
            w.show()
        elif self.password.text() != self.confirm_pass.text():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Passwords do not match.")
            w.show()
        elif len(self.password.text()) < 8:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Password must be at least 8 characters long.")
            w.show()
        elif len(self.zipcode.text()) != 5 or not self.zipcode.text().isnumeric():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Zipcode must be 5 digits and must be numeric.")
            w.show()
        else:
            test = curs.execute(f'select * from user where username = "{self.username.text()}";')
            if test != 0:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid", "Username already exists")
                w.show()
            else:
                entered_address = self.street_add.text() + self.city.text()+self.state.currentText()+self.zipcode.text()
                curs.execute('select manStreet, manCity, manState, manZipcode from Manager;')
                all_address = curs.fetchall()
                test_address = True
                if all_address:
                    for i in all_address:
                        one_ad = i["manStreet"] + i["manCity"] + i["manState"] + i["manZipcode"]
                        if one_ad == entered_address:
                            test_address =  False
                            x = QMessageBox()
                            QMessageBox.warning(x, "Duplicate Address", "The entered address already exists in the database. Please enter another address for this manager. ")
                            break
                if test_address:
                    curs.execute(f'call manager_customer_register("{self.username.text()}", "{self.password.text()}", '
                             f'"{self.firstname.text()}", "{self.lastname.text()}", "{self.company.currentText()}", '
                             f'"{self.street_add.text()}", "{self.city.text()}", "{self.state.currentText()}",  "{self.zipcode.text()}");')
                    for creditcardnum in self.credit_card_list:
                        curs.execute(f'call manager_customer_add_creditcard("{self.username.text()}", "{creditcardnum}");')
                    w = QMessageBox()
                    QMessageBox.information(w, "Success", " Manager-Customer registered.")
                    w.show()
                    connection.commit()

    def enable_buttons(self):
        if len(self.credit_card.text()) == 16:
            self.add.setEnabled(True)

    def clicked(self, index):
        self.remove.setEnabled(True)
        item = self.list_model.itemFromIndex(index)
        self.removed = [item.text(), index.row()]


# ================Screen 7 Admin-Only Functionality================
class admin_only_func(QDialog):
    def __init__(self, username):
        super(admin_only_func, self).__init__()
        self.username = username
        self.setModal(True)
        self.setWindowTitle('Admin-Only Functionality')

        self.manage_user_button = QPushButton('Manage User')
        self.manage_user_button.clicked.connect(self.run_manage_user_button)

        self.explore_theater_button = QPushButton('Explore Theater')
        self.explore_theater_button.clicked.connect(self.run_explore_theater_button)

        self.manage_company_button = QPushButton('Manage Company')
        self.manage_company_button.clicked.connect(self.run_manage_company_button)

        self.visit_history_button = QPushButton('Visit History')
        self.visit_history_button.clicked.connect(self.run_visit_history_button)

        self.create_movie_button = QPushButton('Create Movie')
        self.create_movie_button.clicked.connect(self.run_create_movie_button)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.run_back_button)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.manage_user_button)
        vbox_layout.addWidget(self.explore_theater_button)
        vbox_layout.addWidget(self.manage_company_button)

        vbox_layout2 = QVBoxLayout()
        vbox_layout2.addWidget(self.visit_history_button)
        vbox_layout2.addWidget(self.create_movie_button)
        vbox_layout2.addWidget(self.back_button)

        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(vbox_layout)
        hbox_layout.addLayout(vbox_layout2)
        self.setLayout(hbox_layout)

    def run_manage_user_button(self):
        self.close()
        curs.execute('call admin_filter_user(null, "ALL", null, null);')
        curs.execute('select * from adfilteruser;')
        data = curs.fetchall()
        connection.commit()
        admin_manage_user(data, 7, self.username).exec()


    def run_explore_theater_button(self):
        self.close()
        curs.execute('call user_filter_th("All", "All", "", "");')
        curs.execute('select * from UserFilterTh;')
        data = curs.fetchall()
        curs.execute('select * from theater;')
        theater_names = curs.fetchall()
        theater_names = [theater_names[i]['thName'] for i in range(0, len(theater_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()

        explore_theater(data, theater_names, com, 7, self.username).exec()

    def run_manage_company_button(self):
        self.close()
        curs.execute('call admin_filter_company(null, null, null, null, null, null, null, null, null);')
        curs.execute('select * from adfiltercom;')
        data = curs.fetchall()
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()
        manage_company(data, com, 7, self.username).exec()


    def run_visit_history_button(self):
        test = curs.execute(f'select thName as Theater, concat(thStreet, ", ", thCity, ", ", thState, " ", thZipcode) '
                            f'as Address, comName as Company, visitDate as "Visit Date" from uservisittheater '
                            f'natural join theater where username = "{self.username}";')
        data = curs.fetchall()
        for i in range(len(data)):
            data[i]['Visit Date'] = str(data[i]['Visit Date'])
        connection.commit()
        if test == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "No Record", "You currently do not have any visit history.")
            w.show()
        else:
            self.close()
            visit_history(data, 7, self.username).exec()

    def run_create_movie_button(self):
        self.close()
        create_movie(self.username, 7).exec()

    def run_back_button(self):
        self.close()
        Login().exec()


# ================Screen 8 Admin-Customer Functionality================
class admin_customer_func(QDialog):
    def __init__(self, username):
        super(admin_customer_func, self).__init__()
        self.username = username
        self.setModal(True)
        self.setWindowTitle('Admin-Customer Functionality')

        self.manage_user_button = QPushButton('Manage User')
        self.manage_user_button.clicked.connect(self.run_manage_user_button)

        self.explore_movie_button = QPushButton('Explore Movie')
        self.explore_movie_button.clicked.connect(self.run_explore_movie_button)

        self.manage_company_button = QPushButton('Manage Company')
        self.manage_company_button.clicked.connect(self.run_manage_company_button)

        self.explore_theater_button = QPushButton('Explore Theater')
        self.explore_theater_button.clicked.connect(self.run_explore_theater_button)

        self.create_movie_button = QPushButton('Create Movie')
        self.create_movie_button.clicked.connect(self.run_create_movie_button)

        self.view_history_button = QPushButton('View History')
        self.view_history_button.clicked.connect(self.run_view_history_button)

        self.visit_history_button = QPushButton('Visit History')
        self.visit_history_button.clicked.connect(self.run_visit_history_button)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.run_back_button)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.manage_user_button)
        vbox_layout.addWidget(self.manage_company_button)
        vbox_layout.addWidget(self.create_movie_button)
        vbox_layout.addWidget(self.visit_history_button)

        vbox_layout2 = QVBoxLayout()
        vbox_layout2.addWidget(self.explore_movie_button)
        vbox_layout2.addWidget(self.explore_theater_button)
        vbox_layout2.addWidget(self.view_history_button)
        vbox_layout2.addWidget(self.back_button)

        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(vbox_layout)
        hbox_layout.addLayout(vbox_layout2)
        self.setLayout(hbox_layout)

    def run_manage_user_button(self):
        self.close()
        curs.execute('call admin_filter_user(null, "ALL", null, null);')
        curs.execute('select * from adfilteruser;')
        data = curs.fetchall()
        connection.commit()
        admin_manage_user(data, 8, self.username).exec()

    def run_manage_company_button(self):
        self.close()
        curs.execute('call admin_filter_company(null, null, null, null, null, null, null, null, null);')
        curs.execute('select * from adfiltercom;')
        data = curs.fetchall()
        connection.commit()
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()
        manage_company(data, com, 8, self.username).exec()

    def run_create_movie_button(self):
        self.close()
        create_movie(self.username, 8).exec()

    def run_visit_history_button(self):
        test = curs.execute(f'select thName as Theater, concat(thStreet, ", ", thCity, ", ", thState, " ", thZipcode) '
                            f'as Address, comName as Company, visitDate as "Visit Date" from uservisittheater '
                            f'natural join theater where username = "{self.username}";')
        data = curs.fetchall()
        for i in range(len(data)):
            data[i]['Visit Date'] = str(data[i]['Visit Date'])
        connection.commit()
        if test == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "No Record", "You currently do not have any visit history.")
            w.show()
        else:
            self.close()
            visit_history(data, 8, self.username).exec()

    def run_explore_movie_button(self):
        self.close()
        curs.execute('call customer_filter_mov(null, null, null, null, null, null);')
        curs.execute('select * from CosFilterMovie;')
        data = curs.fetchall()
        curs.execute('select * from movie;')
        movie_names = curs.fetchall()
        movie_names = [movie_names[i]['movName'] for i in range(0, len(movie_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        curs.execute(f'select * from customerCreditCard where username = "{self.username}";')
        credit_cards = curs.fetchall()
        credit_cards = [credit_cards[i]['creditCardNum'] for i in range(0, len(credit_cards))]
        connection.commit()

        explore_movie(data, movie_names, com, credit_cards, 8, self.username).exec()

    def run_explore_theater_button(self):

        self.close()
        curs.execute('call user_filter_th("All", "All", "", "");')
        curs.execute('select * from UserFilterTh;')
        data = curs.fetchall()
        curs.execute('select * from theater;')
        theater_names = curs.fetchall()
        theater_names = [theater_names[i]['thName'] for i in range(0, len(theater_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()

        explore_theater(data, theater_names, com, 8, self.username).exec()

    def run_view_history_button(self):
        curs.execute(f'call customer_view_history("{self.username}");')
        curs.execute("select * from CosViewHistory;")
        data = curs.fetchall()
        if (data):
            for i in data:
                i['movPlayDate'] = f"{i['movPlayDate'].year}/{i['movPlayDate'].month}/{i['movPlayDate'].day}"
            self.close()

            for i in data:
                i['view date'] = i['movPlayDate']
                del i['movPlayDate']
            view_history(data, "admin_customer", self.username).exec()
        else:
            w = QMessageBox()
            w.setIcon(QMessageBox.Critical)
            w.setText("The customer doesn't have any view history! ")
            w.setWindowTitle("Empty View History")
            w.exec_()

    def run_back_button(self):
        self.close()
        Login().exec()


# ================Screen 9 Manager-Only Functionality================
class manager_only_func(QDialog):
    def __init__(self, username):
        super(manager_only_func, self).__init__()
        self.setModal(True)
        self.setWindowTitle('Manager-Only Functionality')

        self.username = username
        self.theater_overview_button = QPushButton('Theater Overview')
        self.theater_overview_button.clicked.connect(self.run_theater_overview_button)

        self.schedule_movie_button = QPushButton('Schedule Movie')
        self.schedule_movie_button.clicked.connect(self.run_schedule_movie_button)

        self.explore_theater_button = QPushButton('Explore Theater')
        self.explore_theater_button.clicked.connect(self.run_explore_theater_button)

        self.visit_history_button = QPushButton('Visit History')
        self.visit_history_button.clicked.connect(self.run_visit_history_button)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.run_back_button)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.theater_overview_button)
        vbox_layout.addWidget(self.schedule_movie_button)

        vbox_layout2 = QVBoxLayout()
        vbox_layout2.addWidget(self.explore_theater_button)
        vbox_layout2.addWidget(self.visit_history_button)

        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(vbox_layout)
        hbox_layout.addLayout(vbox_layout2)

        vbox_layout3 = QVBoxLayout()
        vbox_layout3.addLayout(hbox_layout)
        vbox_layout3.addWidget(self.back_button)
        self.setLayout(vbox_layout3)


    def run_theater_overview_button(self):
        self.close()
        movie_query = f'call manager_filter_th("{self.username}", NULL,NULL,NULL,NULL,NULL,NULL,NULL, False);'
        curs.execute(movie_query)
        curs.execute('select * from ManFilterTh;')
        data_all = curs.fetchall()
        theater_overview(data_all, 9, self.username).exec()

    def run_schedule_movie_button(self):
        self.close()
        schedule_movie(self.username, 9).exec()

    def run_explore_theater_button(self):
        self.close()
        curs.execute('call user_filter_th("All", "All", "", "");')
        curs.execute('select * from UserFilterTh;')
        data = curs.fetchall()
        curs.execute('select * from theater;')
        theater_names = curs.fetchall()
        theater_names = [theater_names[i]['thName'] for i in range(0, len(theater_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()

        explore_theater(data, theater_names, com, 9, self.username).exec()



    def run_visit_history_button(self):
        test = curs.execute(f'select thName as Theater, concat(thStreet, ", ", thCity, ", ", thState, " ", thZipcode) '
                            f'as Address, comName as Company, visitDate as "Visit Date" from uservisittheater '
                            f'natural join theater where username = "{self.username}";')
        data = curs.fetchall()
        for i in range(len(data)):
            data[i]['Visit Date'] = str(data[i]['Visit Date'])
        connection.commit()
        if test == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "No Record", "You currently do not have any visit history.")
            w.show()
        else:
            self.close()
            visit_history(data, 9, self.username).exec()

    def run_back_button(self):
        self.close()
        Login().exec()


# ================Screen 10 Manager-Customer Functionality================
class manager_customer_func(QDialog):
    def __init__(self, username):
        super(manager_customer_func, self).__init__()
        self.username = username
        self.setModal(True)
        self.setWindowTitle('Manager-Customer Functionality')

        self.theater_overview_button = QPushButton('Theater Overview')
        self.theater_overview_button.clicked.connect(self.run_theater_overview_button)

        self.schedule_movie_button = QPushButton('Schedule Movie')
        self.schedule_movie_button.clicked.connect(self.run_schedule_movie_button)

        self.view_history_button = QPushButton('View History')
        self.view_history_button.clicked.connect(self.run_view_history_button)

        self.explore_movie_button = QPushButton('Explore Movie')
        self.explore_movie_button.clicked.connect(self.run_explore_movie_button)

        self.explore_theater_button = QPushButton('Explore Theater')
        self.explore_theater_button.clicked.connect(self.run_explore_theater_button)

        self.visit_history_button = QPushButton('Visit History')
        self.visit_history_button.clicked.connect(self.run_visit_history_button)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.run_back_button)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.theater_overview_button)
        vbox_layout.addWidget(self.schedule_movie_button)
        vbox_layout.addWidget(self.view_history_button)

        vbox_layout2 = QVBoxLayout()
        vbox_layout2.addWidget(self.explore_movie_button)
        vbox_layout2.addWidget(self.explore_theater_button)
        vbox_layout2.addWidget(self.visit_history_button)

        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(vbox_layout)
        hbox_layout.addLayout(vbox_layout2)

        vbox_layout3 = QVBoxLayout()
        vbox_layout3.addLayout(hbox_layout)
        vbox_layout3.addWidget(self.back_button)
        self.setLayout(vbox_layout3)

    def run_theater_overview_button(self):
        self.close()
        movie_query = f'call manager_filter_th("{self.username}", NULL,NULL,NULL,NULL,NULL,NULL,NULL, False);'
        curs.execute(movie_query)
        curs.execute('select * from ManFilterTh;')
        data_all = curs.fetchall()
        theater_overview(data_all, 10, self.username).exec()

    def run_schedule_movie_button(self):
        self.close()
        schedule_movie(self.username, 10).exec()

    def run_view_history_button(self):
        curs.execute(f'call customer_view_history("{self.username}");')
        curs.execute("select * from CosViewHistory;")
        data = curs.fetchall()
        if (data):
            for i in data:
                i['movPlayDate'] = f"{i['movPlayDate'].year}/{i['movPlayDate'].month}/{i['movPlayDate'].day}"
            for i in data:
                i['view date'] = i['movPlayDate']
                del i['movPlayDate']
            self.close()
            view_history(data, "manager_customer", self.username).exec()

        else:
            w = QMessageBox()
            w.setIcon(QMessageBox.Critical)
            w.setText("The customer doesn't have any view history! ")
            w.setWindowTitle("Empty View History")
            w.exec_()

    def run_explore_movie_button(self):
        self.close()
        curs.execute('call customer_filter_mov(null, null, null, null, null, null);')
        curs.execute('select * from CosFilterMovie;')
        data = curs.fetchall()
        curs.execute('select * from movie;')
        movie_names = curs.fetchall()
        movie_names = [movie_names[i]['movName'] for i in range(0, len(movie_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        curs.execute(f'select * from customerCreditCard where username = "{self.username}";')
        credit_cards = curs.fetchall()
        credit_cards = [credit_cards[i]['creditCardNum'] for i in range(0, len(credit_cards))]
        connection.commit()

        explore_movie(data, movie_names, com, credit_cards, 10, self.username).exec()

    def run_explore_theater_button(self):
        self.close()
        curs.execute('call user_filter_th("All", "All", "", "");')
        curs.execute('select * from UserFilterTh;')
        data = curs.fetchall()
        curs.execute('select * from theater;')
        theater_names = curs.fetchall()
        theater_names = [theater_names[i]['thName'] for i in range(0, len(theater_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()

        explore_theater(data, theater_names, com, 10, self.username).exec()


    def run_visit_history_button(self):
        test = curs.execute(f'select thName as Theater, concat(thStreet, ", ", thCity, ", ", thState, " ", thZipcode) '
                            f'as Address, comName as Company, visitDate as "Visit Date" from uservisittheater '
                            f'natural join theater where username = "{self.username}";')
        data = curs.fetchall()
        for i in range(len(data)):
            data[i]['Visit Date'] = str(data[i]['Visit Date'])
        connection.commit()
        if test == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "No Record", "You currently do not have any visit history.")
            w.show()
        else:
            self.close()
            visit_history(data, 10, self.username).exec()

    def run_back_button(self):
        self.close()
        Login().exec()


# ================Screen 11 Customer Functionality================
class customer_only_func(QDialog):
    def __init__(self, username):
        super(customer_only_func, self).__init__()
        self.username = username
        self.setModal(True)
        self.setWindowTitle('Customer Functionality')

        self.explore_movie_button = QPushButton('Explore Movie')
        self.explore_movie_button.clicked.connect(self.run_explore_movie_button)

        self.explore_theater_button = QPushButton('Explore Theater')
        self.explore_theater_button.clicked.connect(self.run_explore_theater_button)

        self.view_history_button = QPushButton('View History')
        self.view_history_button.clicked.connect(self.run_view_history_button)

        self.visit_history_button = QPushButton('Visit History')
        self.visit_history_button.clicked.connect(self.run_visit_history_button)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.run_back_button)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.explore_movie_button)
        vbox_layout.addWidget(self.explore_theater_button)

        vbox_layout2 = QVBoxLayout()
        vbox_layout2.addWidget(self.view_history_button)
        vbox_layout2.addWidget(self.visit_history_button)

        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(vbox_layout)
        hbox_layout.addLayout(vbox_layout2)

        vbox_layout3 = QVBoxLayout()
        vbox_layout3.addLayout(hbox_layout)
        vbox_layout3.addWidget(self.back_button)
        self.setLayout(vbox_layout3)

    def run_view_history_button(self):
        curs.execute(f'call customer_view_history("{self.username}");')
        curs.execute("select * from CosViewHistory;")
        data = curs.fetchall()
        if (data):
            for i in data:
                i['movPlayDate'] = f"{i['movPlayDate'].year}/{i['movPlayDate'].month}/{i['movPlayDate'].day}"
            self.close()
            for i in data:
                i['view date'] = i['movPlayDate']
                del i['movPlayDate']
            view_history(data, "customer_only", self.username).exec()
        else:
            w = QMessageBox()
            w.setIcon(QMessageBox.Critical)
            w.setText("The customer doesn't have any view history! ")
            w.setWindowTitle("Empty View History")
            w.exec_()

    def run_explore_movie_button(self):
        self.close()
        curs.execute('call customer_filter_mov(null, null, null, null, null, null);')
        curs.execute('select * from CosFilterMovie;')
        data = curs.fetchall()
        curs.execute('select * from movie;')
        movie_names = curs.fetchall()
        movie_names = [movie_names[i]['movName'] for i in range(0, len(movie_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        curs.execute(f'select * from customerCreditCard where username = "{self.username}";')
        credit_cards = curs.fetchall()
        credit_cards = [credit_cards[i]['creditCardNum'] for i in range(0, len(credit_cards))]
        connection.commit()

        explore_movie(data, movie_names, com, credit_cards, 11, self.username).exec()

    def run_explore_theater_button(self):
        self.close()
        curs.execute('call user_filter_th("All", "All", "", "");')
        curs.execute('select * from UserFilterTh;')
        data = curs.fetchall()
        curs.execute('select * from theater;')
        theater_names = curs.fetchall()
        theater_names = [theater_names[i]['thName'] for i in range(0, len(theater_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()

        explore_theater(data, theater_names, com, 11, self.username).exec()

    def run_visit_history_button(self):
        test = curs.execute(f'select thName as Theater, concat(thStreet, ", ", thCity, ", ", thState, " ", thZipcode) '
                            f'as Address, comName as Company, visitDate as "Visit Date" from uservisittheater '
                            f'natural join theater where username = "{self.username}";')
        data = curs.fetchall()
        for i in range(len(data)):
            data[i]['Visit Date'] = str(data[i]['Visit Date'])
        connection.commit()
        if test == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "No Record", "You currently do not have any visit history.")
            w.show()
        else:
            self.close()
            visit_history(data, 11, self.username).exec()

    def run_back_button(self):
        self.close()
        Login().exec()


# ================Screen 12 User Functionality================
class user_func(QDialog):
    def __init__(self, username):
        super(user_func, self).__init__()
        self.username = username
        self.setModal(True)
        self.setWindowTitle('User Functionality')

        self.explore_theater_button = QPushButton('Explore Theater')
        self.explore_theater_button.clicked.connect(self.run_explore_theater_button)

        self.visit_history_button = QPushButton('Visit History')
        self.visit_history_button.clicked.connect(self.run_visit_history_button)

        self.back_button = QPushButton('Back')
        self.back_button.clicked.connect(self.run_back_button)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.explore_theater_button)
        vbox_layout.addWidget(self.visit_history_button)
        vbox_layout.addWidget(self.back_button)

        self.setLayout(vbox_layout)

    def run_explore_theater_button(self):
        self.close()
        curs.execute('call user_filter_th("All", "All", "", "");')
        curs.execute('select * from UserFilterTh;')
        data = curs.fetchall()
        curs.execute('select * from theater;')
        theater_names = curs.fetchall()
        theater_names = [theater_names[i]['thName'] for i in range(0, len(theater_names))]
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()

        explore_theater(data, theater_names, com, 12, self.username).exec()

    def run_visit_history_button(self):
        test = curs.execute(f'select thName as Theater, concat(thStreet, ", ", thCity, ", ", thState, " ", thZipcode) '
                            f'as Address, comName as Company, visitDate as "Visit Date" from uservisittheater '
                            f'natural join theater where username = "{self.username}";')
        data = curs.fetchall()
        for i in range(len(data)):
            data[i]['Visit Date'] = str(data[i]['Visit Date'])
        connection.commit()
        if test == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "No Record", "You currently do not have any visit history.")
            w.show()
        else:
            self.close()
            visit_history(data, 12, self.username).exec()

    def run_back_button(self):
        self.close()
        Login().exec()


# ================Screen 13 Admin Manage User================
class admin_manage_user(QDialog):
    def __init__(self, data, screen, username):
        super(admin_manage_user, self).__init__()
        self.screen = screen
        self.username = username
        self.setWindowTitle("Manage User")
        self.username_input = QLineEdit()
        self.status = QComboBox()
        self.status.addItems(['ALL', 'Pending', 'Declined', 'Approved'])
        self.sortby = QComboBox()
        self.sortby.addItems(['Username', 'Credit Card Count', 'User Type', 'Status'])
        self.sortdirection = QComboBox()
        self.sortdirection.addItems(['DESC', 'ASC'])
        self.filter = QPushButton('Filter')
        self.approve = QPushButton('Approve')
        self.decline = QPushButton('Decline')
        self.back = QPushButton('Back')
        self.filter.pressed.connect(self.run_filter)
        self.approve.pressed.connect(self.run_approve)
        self.decline.pressed.connect(self.run_decline)
        self.back.pressed.connect(self.run_back)
        self.table_model = SimpleTableModel(data)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)

        hbox_layout1 = QHBoxLayout()
        hbox_layout1.addWidget(QLabel('Username:'))
        hbox_layout1.addWidget(self.username_input)
        hbox_layout2 = QHBoxLayout()
        hbox_layout2.addWidget(QLabel('Status:'))
        hbox_layout2.addWidget(self.status)
        hbox_layout3 = QHBoxLayout()
        hbox_layout3.addWidget(QLabel('Sort By:'))
        hbox_layout3.addWidget(self.sortby)
        hbox_layout4 = QHBoxLayout()
        hbox_layout4.addWidget(QLabel('Sort Direction:'))
        hbox_layout4.addWidget(self.sortdirection)
        hbox_layout5 = QHBoxLayout()
        hbox_layout5.addWidget(self.approve)
        hbox_layout5.addWidget(self.decline)
        vbox_layout1 = QVBoxLayout()
        vbox_layout1.addLayout(hbox_layout1)
        vbox_layout1.addLayout(hbox_layout3)
        vbox_layout2 = QVBoxLayout()
        vbox_layout2.addLayout(hbox_layout2)
        vbox_layout2.addLayout(hbox_layout4)
        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(vbox_layout1)
        hbox_layout.addLayout(vbox_layout2)
        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addWidget(self.filter)
        vbox_layout.addWidget(self.table_view)
        vbox_layout.addLayout(hbox_layout5)
        vbox_layout.addWidget(self.back)
        self.setLayout(vbox_layout)

    def run_filter(self):
        curs.execute(f'call admin_filter_user("{self.username_input.text()}", "{self.status.currentText()}", '
                     f'"{self.sortby.currentText().replace(" ","")}", "{self.sortdirection.currentText()}");')
        test = curs.execute('select * from adfilteruser;')
        if test == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "Empty Filter Result", "No data matches the entered requirements.")
            w.show()
        else:
            self.close()
            data = curs.fetchall()
            connection.commit()
            admin_manage_user(data, self.screen, self.username).exec()

    def run_approve(self):
        current_index = self.table_view.currentIndex().row()
        selected_item = self.table_model.row(current_index)
        test = curs.execute(f'call admin_approve_user("{selected_item["username"]}");')
        if test == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "User is already approved")
            w.show()
        else:
            self.close()
            curs.execute('call admin_filter_user(null, "ALL", null, null);')
            curs.execute('select * from adfilteruser;')
            data = curs.fetchall()
            connection.commit()
            admin_manage_user(data, self.screen, self.username ).exec()

    def run_decline(self):
        current_index = self.table_view.currentIndex().row()
        selected_item = self.table_model.row(current_index)
        test = curs.execute(f'call admin_decline_user("{selected_item["username"]}");')
        if test == 0:
            if selected_item['status'] == 'Declined':
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid", "User is already declined")
                w.show()
            elif selected_item['status'] == 'Approved':
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid", "Cannot decline an approved user")
                w.show()
        else:
            self.close()
            curs.execute('call admin_filter_user(null, "ALL", null, null);')
            curs.execute('select * from adfilteruser;')
            data = curs.fetchall()
            connection.commit()
            admin_manage_user(data, self.screen, self.username ).exec()

    def run_back(self):
        self.close()
        if self.screen == 7:
            admin_only_func(self.username).exec()
        else:
            admin_customer_func(self.username).exec()


# ================Screen 14 Admin Manage Company================
class manage_company(QDialog):
    def __init__(self, data, com, screen, username):
        super(manage_company, self).__init__()
        self.setWindowTitle("Manage Company")
        self.setMaximumWidth(300)
        self.username = username
        self.com = com
        self.screen = screen
        self.name = QComboBox()
        self.name.addItems(['ALL'] + self.com)
        self.mincity = QLineEdit()
        self.maxcity = QLineEdit()
        self.mintheater = QLineEdit()
        self.maxtheater = QLineEdit()
        self.minemployee = QLineEdit()
        self.maxemployee = QLineEdit()
        self.sortby = QComboBox()
        self.sortby.addItems(['Com Name', 'Num City Cover', 'Num Theater', 'Num Employee'])
        self.sortdirection = QComboBox()
        self.sortdirection.addItems(['DESC', 'ASC'])
        self.filter = QPushButton('Filter')
        self.create_theater = QPushButton('Create Theater')
        self.detail = QPushButton('Detail')
        self.back = QPushButton('Back')
        self.filter.pressed.connect(self.run_filter)
        self.create_theater.pressed.connect(self.run_create_theater)
        self.detail.pressed.connect(self.run_detail)
        self.back.pressed.connect(self.run_back)
        self.table_model = SimpleTableModel(data)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)

        hbox_layout1 = QHBoxLayout()
        hbox_layout1.addWidget(QLabel('Name:'))
        hbox_layout1.addWidget(self.name)
        hbox_layout2 = QHBoxLayout()
        hbox_layout2.addWidget(QLabel('# City Covered:'))
        hbox_layout2.addWidget(self.mincity)
        hbox_layout2.addWidget(QLabel('-'))
        hbox_layout2.addWidget(self.maxcity)
        hbox_layout3 = QHBoxLayout()
        hbox_layout3.addWidget(QLabel('# Theaters:'))
        hbox_layout3.addWidget(self.mintheater)
        hbox_layout3.addWidget(QLabel('-'))
        hbox_layout3.addWidget(self.maxtheater)
        hbox_layout4 = QHBoxLayout()
        hbox_layout4.addWidget(QLabel('# Employees:'))
        hbox_layout4.addWidget(self.minemployee)
        hbox_layout4.addWidget(QLabel('-'))
        hbox_layout4.addWidget(self.maxemployee)
        hbox_layout5 = QHBoxLayout()
        hbox_layout5.addWidget(QLabel('Sort By:'))
        hbox_layout5.addWidget(self.sortby)
        hbox_layout6 = QHBoxLayout()
        hbox_layout6.addWidget(QLabel('Sort Direction:'))
        hbox_layout6.addWidget(self.sortdirection)
        hbox_layout7 = QHBoxLayout()
        hbox_layout7.addWidget(self.filter)
        hbox_layout7.addWidget(self.detail)
        vbox_layout1 = QVBoxLayout()
        vbox_layout1.addLayout(hbox_layout1)
        vbox_layout1.addLayout(hbox_layout3)
        vbox_layout1.addLayout(hbox_layout5)
        vbox_layout2 = QVBoxLayout()
        vbox_layout2.addLayout(hbox_layout2)
        vbox_layout2.addLayout(hbox_layout4)
        vbox_layout2.addLayout(hbox_layout6)
        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(vbox_layout1)
        hbox_layout.addLayout(vbox_layout2)
        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addWidget(self.table_view)
        vbox_layout.addLayout(hbox_layout7)
        vbox_layout.addWidget(self.create_theater)
        vbox_layout.addWidget(self.back)
        self.setLayout(vbox_layout)

    def run_filter(self):
        test = self.mincity.text() + self.maxcity.text() + self.mintheater.text()\
               + self.maxtheater.text() + self.minemployee.text() + self.maxemployee.text()
        if not test.isnumeric() and test != '':
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", 'Fields for "# City Covered", "# Theaters", and "# Employees" '
                                              'must be numeric')
            w.show()
        else:
            nums = [self.mincity.text(), self.maxcity.text(), self.mintheater.text(), self.maxtheater.text(),
                    self.minemployee.text(), self.maxemployee.text()]
            nums = ['null' if i == '' else i for i in nums]
            curs.execute(f'call admin_filter_company("{self.name.currentText()}", {nums[0]}, {nums[1]}, {nums[2]}, '
                         f'{nums[3]}, {nums[4]}, {nums[5]}, "{self.sortby.currentText().replace(" ", "")}", '
                         f'"{self.sortdirection.currentText()}");')
            test1 = curs.execute('select * from adfiltercom;')
            if test1 == 0:
                w = QMessageBox()
                QMessageBox.warning(w, "Empty Filter Result", "No data matches the entered requirements.")
                w.show()
            else:
                self.close()
                data = curs.fetchall()
                connection.commit()
                manage_company(data, self.com, self.screen, self.username).exec()

    def run_create_theater(self):
        self.close()
        CreateTheater(self.screen, self.username).exec()

    def run_detail(self):
        self.close()
        current_index = self.table_view.currentIndex().row()
        selected_item = self.table_model.row(current_index)
        CompanyDetail(selected_item['comName'], self.screen, self.username).exec()

    def run_back(self):
        self.close()
        if self.screen == 7:
            admin_only_func(self.username).exec()
        else:
            admin_customer_func(self.username).exec()


# ================Screen 15 Admin Create Theater================
class CreateTheater(QDialog):
    def __init__(self, screen, username):
        super(CreateTheater, self).__init__()
        self.setWindowTitle("Create Theater")
        self.screen = screen
        self.username = username
        state_List = ["ALL", "WA", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
                      "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
                      "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WV", "WI", "WY"]
        state_List.sort()
        self.thName = QLineEdit()
        self.comName = QComboBox()
        curs.execute("SELECT comName FROM company")
        comName_List = curs.fetchall()
        connection.commit()
        self.comName.addItems(["ALL"] + [com['comName'] for com in comName_List])
        self.thStreet = QLineEdit()
        self.thCity = QLineEdit()
        self.thState = QComboBox()
        self.thState.addItems(state_List)
        self.thZipcode = QLineEdit()
        self.capcity = QLineEdit()
        self.manUsername = QComboBox()
        curs.execute("select username from manager where username not in (select manusername from theater);")
        manUsername_List = curs.fetchall()
        connection.commit()
        self.manUsername.addItems([man['username'] for man in manUsername_List])

        hbox_layout1 = QHBoxLayout()
        hbox_layout1.addWidget(QLabel("Name:"))
        hbox_layout1.addWidget(self.thName)
        hbox_layout1.addWidget(QLabel("Company:"))
        hbox_layout1.addWidget(self.comName)

        hbox_layout3 = QHBoxLayout()
        hbox_layout3.addWidget(QLabel("Street Address:"))
        hbox_layout3.addWidget(self.thStreet)

        hbox_layout4 = QHBoxLayout()
        hbox_layout4.addWidget(QLabel("City:"))
        hbox_layout4.addWidget(self.thCity)
        hbox_layout4.addWidget(QLabel("State:"))
        hbox_layout4.addWidget(self.thState)
        hbox_layout4.addWidget(QLabel("Zipcode:"))
        hbox_layout4.addWidget(self.thZipcode)

        hbox_layout7 = QHBoxLayout()
        hbox_layout7.addWidget(QLabel("Capcity:"))
        hbox_layout7.addWidget(self.capcity)
        hbox_layout7.addWidget(QLabel("Manager:"))
        hbox_layout7.addWidget(self.manUsername)

        self.back = QPushButton("Back")
        self.create = QPushButton("Create")
        self.back.clicked.connect(self.run_back)
        self.create.clicked.connect(self.create_Theater)

        hbox_layout9 = QHBoxLayout()
        hbox_layout9.addWidget(self.back)
        hbox_layout9.addWidget(self.create)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout1)
        vbox_layout.addLayout(hbox_layout3)
        vbox_layout.addLayout(hbox_layout4)
        vbox_layout.addLayout(hbox_layout7)
        vbox_layout.addLayout(hbox_layout9)
        self.setLayout(vbox_layout)

    def run_back(self):
        self.close()
        curs.execute('call admin_filter_company(null, null, null, null, null, null, null, null, null);')
        curs.execute('select * from adfiltercom;')
        data = curs.fetchall()
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()
        manage_company(data, com, self.screen, self.username).exec()

    def create_Theater(self):
        thName_duplicate_count = curs.execute(f'SELECT * FROM theater WHERE thName = "{self.thName.text()}" and '
                                              f'comName = "{self.comName.currentText()}";')
        man_company = curs.execute(f'select * from manager where comname = "{self.comName.currentText()}" and '
                                   f'username = "{self.manUsername.currentText()}";')
        connection.commit()
        if self.capcity.text():
            try:
                int(self.capcity.text())
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Capacity", "Capacity must be an integer value.")
                w.show()
        if self.manUsername.currentText() == "":
            w = QMessageBox()
            QMessageBox.warning(w, "No Manager Available", "Please add more managers to the system.")
            w.show()
        elif (self.thName.text() == "" or self.thStreet.text() == "" or self.thCity.text() == ""
              or self.thZipcode.text() == "" or self.capcity.text() == ""):
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "All fields are required.")
            w.show()
        elif thName_duplicate_count != 0:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Duplicate theater name for selected company.")
            w.show()
        elif self.comName.currentText() == 'ALL':
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Theater must belong to a specific company")
            w.show()
        elif len(self.thZipcode.text()) != 5 or not self.thZipcode.text().isnumeric():
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Zipcode must be 5 digits and must be numeric.")
            w.show()
        elif man_company == 0:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Selected manager does not work at the company you selected.")
            w.show()
        else:
            curs.execute(f'call admin_create_theater("{self.thName.text()}", "{self.comName.currentText()}", '
                         f'"{self.thStreet.text()}", "{self.thCity.text()}", "{self.thState.currentText()}", '
                         f'"{self.thZipcode.text()}", {self.capcity.text()}, "{self.manUsername.currentText()}");')
            connection.commit()
            i = QMessageBox()
            QMessageBox.information(i, "Success", "Theater created successfully.")
            i.show()
            self.close()
            CreateTheater(self.screen, self.username).exec()


# ================Screen 16 Admin Company Detail================
class CompanyDetail(QDialog):
    def __init__(self, company_Name, screen, username):
        # data, com, screen, username needed from screen 14
        super(CompanyDetail, self).__init__()
        self.comName = company_Name
        self.screen = screen
        self.username = username
        self.setWindowTitle("Company Detail")

        curs.execute(f'call admin_view_comDetail_emp("{self.comName}");')
        curs.execute('select * from adcomdetailemp;')
        self.empdata = curs.fetchall()
        self.empdata = [(name['empFirstname'] + ' ' + name['empLastname']) for name in self.empdata]

        curs.execute(f'SELECT theater.thName as Name, concat(user.firstname, " ", user.lastname) AS Manager, '
                     f'theater.thCity as City, theater.thState as State, theater.capacity AS Capacity '
                     f'FROM theater JOIN manager ON theater.manUsername = manager.username '
                     f'JOIN user ON manager.username = user.username WHERE theater.comName = "{self.comName}";')
        self.thdata = curs.fetchall()

        self.table_model = SimpleTableModel(self.thdata)
        self.Theater_List = QTableView()
        self.Theater_List.setModel(self.table_model)
        self.Theater_List.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)

        self.back = QPushButton("Back")
        self.back.pressed.connect(self.run_back)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(QLabel(f"Name: {self.comName}"))
        vbox_layout.addWidget(QLabel('Employees: ' + ', '.join(self.empdata)))
        vbox_layout.addWidget(self.Theater_List)
        vbox_layout.addWidget(self.back)
        self.setLayout(vbox_layout)

    def run_back(self):
        self.close()
        curs.execute('call admin_filter_company(null, null, null, null, null, null, null, null, null);')
        curs.execute('select * from adfiltercom;')
        data = curs.fetchall()
        curs.execute('select * from company;')
        com = curs.fetchall()
        com = [com[i]['comName'] for i in range(0, len(com))]
        connection.commit()
        manage_company(data, com, self.screen, self.username).exec()


# ================Screen 17 Admin Create Movie================
class create_movie(QDialog):
    def __init__(self, username, screen):
        super(create_movie, self).__init__()
        self.setWindowTitle("Create Movie")
        self.username = username
        self.screen = screen
        self.movName = QLineEdit()
        self.duration = QLineEdit()
        self.movReleaseDate = QLineEdit()

        hbox_layout1 = QHBoxLayout()
        hbox_layout1.addWidget(QLabel("Name: "))
        hbox_layout1.addWidget(self.movName)

        hbox_layout2 = QHBoxLayout()
        hbox_layout2.addWidget(QLabel("Duration: "))
        hbox_layout2.addWidget(self.duration)

        hbox_layout12 = QHBoxLayout()
        hbox_layout12.addLayout(hbox_layout1)
        hbox_layout12.addLayout(hbox_layout2)

        hbox_layout3 = QHBoxLayout()
        hbox_layout3.addWidget(QLabel("Release Date (YYYY/MM/DD): "))
        hbox_layout3.addWidget(self.movReleaseDate)

        self.back = QPushButton("Back")
        self.create = QPushButton("Create")
        self.back.clicked.connect(self.run_back)
        self.create.clicked.connect(self.create_Movie)

        hbox_layout4 = QHBoxLayout()
        hbox_layout4.addWidget(self.back)
        hbox_layout4.addWidget(self.create)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout12)
        vbox_layout.addLayout(hbox_layout3)
        vbox_layout.addLayout(hbox_layout4)
        self.setLayout(vbox_layout)

    def run_back(self):
        self.close()
        if self.screen == 7:
            admin_only_func(self.username).exec()
        else:
            admin_customer_func(self.username).exec()

    def create_Movie(self):
        x = re.search('\d{4}/\d{2}/\d{2}', self.movReleaseDate.text())
        if self.movName.text() == '' or self.duration.text() == '' or self.movReleaseDate.text() == '':
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "All fields are required.")
            w.show()
        elif len(self.movReleaseDate.text()) != 10 or x == None:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid", "Incorrect format for date. \nMust follow YYYY/MM/DD convention.")
            w.show()
        else:
            try:
                int(self.duration.text())
                releasedtime = self.movReleaseDate.text().replace("/", "-")
                movie_duplicate_count = curs.execute(f'SELECT * FROM movie WHERE movName = "{self.movName.text()}" AND movReleaseDate = "{releasedtime}";')
                if (movie_duplicate_count != 0):
                    w = QMessageBox()
                    QMessageBox.warning(w, "Invalid", "Duplicate Movie Error")
                    w.show()
                else:
                    curs.execute(f'call admin_create_mov("{self.movName.text()}", "{self.duration.text()}", "{releasedtime}");')
                    connection.commit()
                    i = QMessageBox()
                    QMessageBox.information(i, 'Success', 'Movie created successfully.')
                    i.show()
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid", "Duration must be a number. ")
                w.show()




# ================Screen 18 Manager Theater Overview================
class theater_overview(QDialog):
    def __init__(self, data, screen, username):
        super(theater_overview, self).__init__()
        self.setWindowTitle("Theater Overview")
        form_group_box = QGroupBox("Theater Overview")
        self.username = username
        self.screen = screen
        self.only_include_not_played = ''

        self.filter = QPushButton("Filter")
        self.filter.clicked.connect(self.run_filter)
        self.filter.setEnabled(True)

        self.back = QPushButton("Back")
        self.back.clicked.connect(self.run_back)
        self.back.setEnabled(True)

        self.movie_name = QLabel("Movie Name (Include)")
        self.movie_name_entry = QLineEdit()
        self.movie_duration = QLabel("Movie Duration")
        self.movie_duration_start = QLineEdit()
        self.separate = QLabel("--")
        self.movie_duration_end = QLineEdit()

        self.movie_release = QLabel("Movie Release Date")
        self.separate2 = QLabel("--")
        self.movie_release_start = QLineEdit()
        self.movie_release_end = QLineEdit()

        self.movie_playdate = QLabel("Movie Play Date")
        self.movie_playdate_start = QLineEdit()
        self.separate3 = QLabel("--")
        self.movie_playdate_end = QLineEdit()
        self.not_played = QCheckBox("Only Include Not Played Movies")

        self.data = data
        self.data = [{'Movie Name':i['movName'], 'Duration':i['movDuration'], 'Release Date':f"{i['movReleaseDate'].year}/{i['movReleaseDate'].month}/{i['movReleaseDate'].day}" if i['movReleaseDate'] else '', 'Play Date':f"{i['movPlayDate'].year}/{i['movPlayDate'].month}/{i['movPlayDate'].day}" if i['movPlayDate'] else ''} for i in data]
        self.table_model = SimpleTableModel(self.data)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)

        hbox_layout1 = QHBoxLayout()
        hbox_layout1.addWidget(self.movie_name)
        hbox_layout1.addWidget(self.movie_name_entry)
        hbox_layout1.addWidget(self.movie_duration)
        hbox_layout1.addWidget(self.movie_duration_start)
        hbox_layout1.addWidget(self.separate)
        hbox_layout1.addWidget(self.movie_duration_end)

        hbox_layout2 = QHBoxLayout()
        hbox_layout2.addWidget(self.movie_release)
        hbox_layout2.addWidget(self.movie_release_start)
        hbox_layout2.addWidget(self.separate2)
        hbox_layout2.addWidget(self.movie_release_end)

        hbox_layout3 = QHBoxLayout()
        hbox_layout3.addWidget(self.movie_playdate)
        hbox_layout3.addWidget(self.movie_playdate_start)
        hbox_layout3.addWidget(self.separate3)
        hbox_layout3.addWidget(self.movie_playdate_end)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout1)
        vbox_layout.addLayout(hbox_layout2)
        vbox_layout.addLayout(hbox_layout3)
        vbox_layout.addWidget(self.not_played)
        vbox_layout.addWidget(self.filter)
        vbox_layout.addWidget(self.table_view)
        vbox_layout.addWidget(self.back)

        self.setLayout(vbox_layout)

    def run_filter(self):
        entry = [self.movie_duration_start.text(), self.movie_duration_end.text(), (self.movie_release_start.text()).replace('/', '-'), (self.movie_release_end.text()).replace('/', '-'), (self.movie_playdate_start.text()).replace('/', '-'), (self.movie_playdate_end.text()).replace('/', '-'), self.movie_name_entry.text()]
        count = 0
        if entry[0]:
            try:
                start_duration = int(entry[0])
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Duration", "Please make sure the start duration is valid")
                w.show()
        else:
            count += 1

        if entry[1]:
            try:
                end_duration = int(entry[1])
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Duration", "Please make sure the end duration is valid")
                w.show()
        else:
            count += 1

        if entry[0] and entry[1] and (int(entry[0]) > int(entry[1])):
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid Duration", "Please make sure the start duration is less than the end duration")
            w.show()
        else:
            count += 1

        if entry[2]:
            try:
                min_date = entry[2].split('-')
                newDate = datetime.datetime(int(min_date[0]), int(min_date[1]), int(min_date[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the minimum release date is valid")
                w.show()
        else:
            count += 1

        if entry[3]:
            try:
                max_date = entry[3].split('-')
                newDate = datetime.datetime(int(max_date[0]), int(max_date[1]), int(max_date[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the maximum release date is valid")
                w.show()
        else:
            count += 1

        if entry[2] and entry[3] and entry[2] > entry[3]:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid Date", "Please make sure the minimum release date is less than the maximum release date.")
            w.show()
        else:
            count += 1

        if entry[4]:
            try:
                min_playdate = entry[4].split('-')
                newDate = datetime.datetime(int(min_playdate[0]), int(min_playdate[1]), int(min_playdate[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the minimum play date is valid")
                w.show()
        else:
            count += 1

        if entry[5]:
            try:
                max_playdate = entry[5].split('-')
                newDate = datetime.datetime(int(max_playdate[0]), int(max_playdate[1]), int(max_playdate[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the maximum play date is valid")
                w.show()
        else:
            count += 1

        if entry[4] and entry[5] and entry[4] > entry[5]:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid Date", "Please make sure the minimum play date is less than the maximum play date.")
            w.show()
        else:
            count += 1

        if count == 9:
            if entry[6] == '':
                entry[6] = 'NULL'
            if entry[0] == '':
                entry[0] = 'NULL'
            else:
                entry[0] = int(entry[0])
            if entry[1] == '':
                entry[1] = 'NULL'
            else:
                entry[1] = int(entry[1])
            if entry[2] == '':
                entry[2] = 'NULL'
            if entry[3] == '':
                entry[3] = 'NULL'
            if entry[4] == '':
                entry[4] = 'NULL'
            if entry[5] == '':
                entry[5] = 'NULL'

            if self.not_played.isChecked():
                self.only_include_not_played = True
            else:
                self.only_include_not_played = False

            filter_query = f'call manager_filter_th ("{self.username}", "{entry[6]}", {entry[0]}, {entry[1]}, "{entry[2]}", "{entry[3]}", "{entry[4]}", "{entry[5]}", {self.only_include_not_played});'
            filter_query = filter_query.replace('"NULL"', 'NULL')
            curs.execute(filter_query)
            curs.execute('SELECT * FROM ManFilterTh;')
            data = curs.fetchall()
            connection.commit()
            if data:
                self.close()
                theater_overview(data, self.screen, self.username).exec()
            else:
                w = QMessageBox()
                QMessageBox.information(w, "Empty Filter Result", "The filter result based on your inputs is empty.")
                w.show()

    def run_back(self):
        self.close()
        if self.screen == 9:
            manager_only_func(self.username).exec()
        else:
            manager_customer_func(self.username).exec()


# ================Screen 19 Manager Schedule Movie================
class schedule_movie(QDialog):
    def __init__(self, username, screen):
        super(schedule_movie, self).__init__()
        self.setWindowTitle("Schedule Movie")
        self.username = username
        self.screen = screen

        self.name_label = QLabel("Name:")
        self.name = QComboBox()

        curs.execute('SELECT movName FROM movie;')
        data = curs.fetchall()
        connection.commit()
        movie_list = [movie['movName'] for movie in data]
        self.name.addItems(movie_list)

        self.release_label = QLabel("Release Date:")
        self.release_date = QLineEdit()

        self.play_label = QLabel("Play Date:")
        self.play_date = QLineEdit()

        self.back = QPushButton("Back")
        self.back.clicked.connect(self.run_back)
        self.add = QPushButton("Add")
        self.add.clicked.connect(self.run_add)

        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.name_label)
        hbox_layout.addWidget(self.name)

        hbox_layout1 = QHBoxLayout()
        hbox_layout1.addWidget(self.release_label)
        hbox_layout1.addWidget(self.release_date)

        hbox_layout2 = QHBoxLayout()
        hbox_layout2.addWidget(self.play_label)
        hbox_layout2.addWidget(self.play_date)

        hbox_layout3 = QHBoxLayout()
        hbox_layout3.addWidget(self.back)
        hbox_layout3.addWidget(self.add)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addLayout(hbox_layout1)
        vbox_layout.addLayout(hbox_layout2)
        vbox_layout.addLayout(hbox_layout3)
        self.setLayout(vbox_layout)

    def run_back(self):
        self.close()
        if self.screen == 9:
            manager_only_func(self.username).exec()
        else:
            manager_customer_func(self.username).exec()

    def run_add(self):
        entry = [self.username, (self.release_date.text()).replace('/', '-'), (self.play_date.text()).replace('/', '-')]
        count = 0
        if entry[1]:
            try:
                releaseDate = entry[1].split('-')
                newReleaseDate = datetime.datetime(int(releaseDate[0]), int(releaseDate[1]), int(releaseDate[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the release date is valid.")
                w.show()
        else:
            w = QMessageBox()
            QMessageBox.warning(w, "Release Date Empty", "Please enter release date.")
            w.show()

        if entry[2]:
            try:
                playDate = entry[2].split('-')
                newPlayDate = datetime.datetime(int(playDate[0]), int(playDate[1]), int(playDate[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the play date is valid.")
                w.show()
        else:
            w = QMessageBox()
            QMessageBox.warning(w, 'Play Date Empty',"Please enter play date.")
            w.show()

        if entry[1] and entry[2] and (entry[1] > entry[2]):
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid Entry", "Play date cannot be before release date.")
            w.show()
        else:
            count += 1


        if count == 3:
            test1 = curs.execute(f'select * from movie where movName = "{self.name.currentText()}" and movReleaseDate = "{entry[1]}";')
            connection.commit()
            if test1 == 0:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Input", f'No movie titled "{self.name.currentText()}" and released on {entry[1]}.')
                w.show()
            else:
                try:
                    test2 = curs.execute(f'call manager_schedule_mov("{entry[0]}", "{self.name.currentText()}","{entry[1]}", "{entry[2]}");')

                    if test2 == 0:
                        w = QMessageBox()
                        QMessageBox.warning(w, "Access Denied", "You are currently not authorized to schedule movies.")
                        w.show()
                    else:
                        w = QMessageBox()
                        QMessageBox.information(w, "Success","Movie has been scheduled!")
                        w.show()
                except:
                    w = QMessageBox()
                    QMessageBox.warning(w, "Duplicate Entry Error", f'You have already scheduled "{self.name.currentText()}" released on {entry[1]} with the same theater, company, and play date entry. Please pick a different play date. ')
                    w.show()


# ================Screen 20 Customer Explore Movie================
class explore_movie(QDialog):
    def __init__(self, data, movie_names, com, credit_card, screen, username):
        super(explore_movie, self).__init__()
        self.screen = screen
        self.username = username
        self.setWindowTitle("Explore Movie")
        self.data = data
        self.movie_names = movie_names
        self.com = com
        self.credit_card = credit_card
        #drop down lists
        self.mov_name = QComboBox()
        self.mov_name.addItems(['ALL'] + self.movie_names)

        self.com_name = QComboBox()
        self.com_name.addItems(['ALL'] + self.com)

        self.state = QComboBox()
        self.state.addItems(["ALL", "WA", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
                            "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
                            "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WV", "WI", "WY"])

        self.credit_card_list = QComboBox()
        self.credit_card_list.addItems(self.credit_card)
        #line edits
        self.min_play_date = QLineEdit()
        self.max_play_date = QLineEdit()
        self.city = QLineEdit()
        #buttons
        self.filter = QPushButton('Filter')
        self.filter.clicked.connect(self.run_filter)
        self.view = QPushButton('View')
        self.view.clicked.connect(self.run_view)
        self.view.setEnabled(False)

        self.back = QPushButton('Back')
        self.back.clicked.connect(self.run_back)
        #table
        self.data = [{'Movie':i['movName'], 'Theater':i['thName'], 'Address':i['thStreet'] +", "+ i['thCity'] + ", "+ i['thState'] +", "+ i['thZipcode'], 'Company':i['comName'], 'Play Date':f"{i['movPlayDate'].year}/{i['movPlayDate'].month}/{i['movPlayDate'].day}"} for i in self.data]
        self.table_model = SimpleTableModel(self.data)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.clicked.connect(self.enable_view_button)

        hbox_layout1 = QHBoxLayout()
        hbox_layout1.addWidget(QLabel('Movie Name:'))
        hbox_layout1.addWidget(self.mov_name)

        hbox_layout2 = QHBoxLayout()
        hbox_layout2.addWidget(QLabel('Company Name:'))
        hbox_layout2.addWidget(self.com_name)

        hbox_layout12 = QHBoxLayout()
        hbox_layout12.addLayout(hbox_layout1)
        hbox_layout12.addLayout(hbox_layout2)

        hbox_layout3 = QHBoxLayout()
        hbox_layout3.addWidget(QLabel('City:'))
        hbox_layout3.addWidget(self.city)

        hbox_layout4 = QHBoxLayout()
        hbox_layout4.addWidget(QLabel('State:'))
        hbox_layout4.addWidget(self.state)

        hbox_layout34 = QHBoxLayout()
        hbox_layout34.addLayout(hbox_layout3)
        hbox_layout34.addLayout(hbox_layout4)

        hbox_layout5 = QHBoxLayout()
        hbox_layout5.addWidget(QLabel('Movie Play Date:'))
        hbox_layout5.addWidget(self.min_play_date)
        hbox_layout5.addWidget(QLabel('-'))
        hbox_layout5.addWidget(self.max_play_date)

        hbox_layout6 = QHBoxLayout()
        hbox_layout6.addWidget(self.back)
        hbox_layout6.addWidget(QLabel('Card Number'))
        hbox_layout6.addWidget(self.credit_card_list)
        hbox_layout6.addWidget(self.view)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout12)
        vbox_layout.addLayout(hbox_layout34)
        vbox_layout.addLayout(hbox_layout5)
        vbox_layout.addWidget(self.filter)
        vbox_layout.addWidget(self.table_view)
        vbox_layout.addLayout(hbox_layout6)

        self.setLayout(vbox_layout)

    def enable_view_button(self):
        if (self.table_view.currentIndex() == -1) or (self.credit_card_list.currentText() == ''):
            self.view.setEnabled(False)
        else:
            self.view.setEnabled(True)

    def run_filter(self):
        entry = [self.mov_name.currentText(), self.com_name.currentText(),self.city.text(),self.state.currentText(), (self.min_play_date.text()).replace('/','-'), (self.max_play_date.text()).replace('/','-')]
        count = 0

        if entry[4]:
            try:
                min_date = entry[4].split('-')
                newDate = datetime.datetime(int(min_date[0]), int(min_date[1]), int(min_date[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the minimum play date is valid. ")
                w.show()
        else:
            count += 1
        if entry[5]:
            try:
                max_date = entry[5].split('-')
                newDate = datetime.datetime(int(max_date[0]), int(max_date[1]), int(max_date[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the maximum play date is valid. ")
                w.show()
        else:
            count += 1
        if entry[4] and entry[5] and entry[4] > entry[5]:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid Date", "Please make sure the minimum play date is less than the maximum play date. ")
            w.show()
        else:
            count += 1
        if count == 3:
            if entry[0] == 'ALL':
                entry[0] = 'NULL'
            if entry[1] == 'ALL':
                entry[1] = 'NULL'
            if entry[2] == '':
                entry[2] = 'NULL'
            if entry[3] == 'ALL':
                entry[3] = 'NULL'
            if entry[4] == '':
                entry[4] = 'NULL'
            if entry[5] == '':
                entry[5] = 'NULL'
            query = f'call customer_filter_mov("{entry[0]}", "{entry[1]}", "{entry[2]}", "{entry[3]}","{entry[4]}","{entry[5]}");'
            query = query.replace('"NULL"', 'NULL')
            curs.execute(query)
            curs.execute('select * from CosFilterMovie;')
            data1 = curs.fetchall()
            connection.commit()
            if data1:
                self.close()
                explore_movie(data1, self.movie_names, self.com,self.credit_card, self.screen, self.username).exec()

            else:
                w = QMessageBox()
                QMessageBox.information(w, "Empty Filter Result", "The filter result based on your inputs is empty.")
                w.show()

    def run_back(self):
        self.close()
        if self.screen == 11:
            customer_only_func(self.username).exec()
        elif self.screen == 8:
            admin_customer_func(self.username).exec()
        else:
            manager_customer_func(self.username).exec()

    def run_view(self):
        current_index = self.table_view.currentIndex().row()
        selected_item = self.table_model.row(current_index)
        used_credit_card = self.credit_card_list.currentText()
        mov_name = selected_item['Movie']
        curs.execute(f'select movReleaseDate from movie where movName = "{mov_name}";')
        mov_released_date = curs.fetchall()[0]['movReleaseDate']
        mov_released_date = f'{mov_released_date.year}-{mov_released_date.month}-{mov_released_date.day}'
        th_name = selected_item['Theater']
        com_name = selected_item['Company']
        mov_play_date = selected_item['Play Date'].replace('/','-')
        query = f'call customer_view_mov("{used_credit_card}","{mov_name}", "{mov_released_date}","{th_name}", "{com_name}", "{mov_play_date}");'

        #3 movies a day???
        try:
            curs.execute(f'call customer_view_history("{self.username}");')
            curs.execute('select * from CosViewHistory;')
            result = curs.fetchall()
            playdates = [i['movPlayDate'] for i in result]
            playdates = [f'{i.year}-{i.month}-{i.day}' for i in playdates]
            if playdates.count(mov_play_date) >= 3:
                w = QMessageBox()
                QMessageBox.warning(w, "Daily View Maximum Error", "You have already viewed 3 movies on this date. Please choose another date.")
            else:
                curs.execute(query) #insert
                connection.commit()
                x = QMessageBox()
                QMessageBox().information(x, "Success", "You have successfully viewed the movie! ")

        except:
            w = QMessageBox()
            QMessageBox.warning(w, "Duplicate View Movie Error", "You have alraedy viewed this movie at this theater using this credit card. Please choose a new movie.")
            w.show()


# ================Screen 21 Customer View History================
class view_history(QDialog):
    def __init__(self, data, screen, username):
        super(view_history, self).__init__()
        self.screen = screen
        self.username = username
        self.setWindowTitle("View History")
        self.table_model= SimpleTableModel(data)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionMode(QAbstractItemView.SelectRows | QAbstractItemView.SingleSelection)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.run_back_button)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.table_view)
        vbox_layout.addWidget(self.back_button)
        self.setLayout(vbox_layout)

    def run_back_button(self):
        self.close()
        if self.screen == 'manager_customer':
            manager_customer_func(self.username).exec()
        elif self.screen == 'customer_only':
            customer_only_func(self.username).exec()
        else:
            admin_customer_func(self.username).exec()


# ================Screen 22 User Explore Theater================
class explore_theater(QDialog):
    def __init__(self,data,theater_names,com,screen,username):
        super(explore_theater, self).__init__()
        self.screen = screen
        self.username = username
        self.setWindowTitle("Explore Theater")

        self.data = data
        self.theater_names = theater_names
        self.com = com

        #drop down lists
        self.thea_name = QComboBox()
        self.thea_name.addItems(['ALL'] + self.theater_names)
        self.com_name = QComboBox()
        self.com_name.addItems(['ALL'] + self.com)
        self.state = QComboBox()
        self.state.addItems(["ALL","WA", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS",
                            "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
                            "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WV", "WI", "WY"])
        #line edits
        self.city = QLineEdit()
        self.visitdate = QLineEdit()
        self.visitdate.textChanged.connect(self.enable_visit_button)
        #buttons
        self.filter = QPushButton('Filter')
        self.filter.clicked.connect(self.run_filter)

        self.back = QPushButton('Back')
        self.back.clicked.connect(self.run_back)

        self.logvisit = QPushButton('Log Visit')
        self.logvisit.clicked.connect(self.run_logvisit)
        self.logvisit.setEnabled(False)
        #table
        self.data = [{'Theater':i['thName'], 'Address':i['thStreet'] +", "+ i['thCity'] + ", "+ i['thState'] +", "+ i['thZipcode'], 'Company':i['comName']}for i in self.data]

        self.table_model = SimpleTableModel(self.data)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.clicked.connect(self.enable_visit_button)

        #layout
        hbox_layout1 = QHBoxLayout()
        hbox_layout1.addWidget(QLabel('Theater Name:'))
        hbox_layout1.addWidget(self.thea_name)

        hbox_layout2 = QHBoxLayout()
        hbox_layout2.addWidget(QLabel('Company Name:'))
        hbox_layout2.addWidget(self.com_name)

        hbox_layout12 = QHBoxLayout()
        hbox_layout12.addLayout(hbox_layout1)
        hbox_layout12.addLayout(hbox_layout2)

        hbox_layout3 = QHBoxLayout()
        hbox_layout3.addWidget(QLabel('City:'))
        hbox_layout3.addWidget(self.city)

        hbox_layout4 = QHBoxLayout()
        hbox_layout4.addWidget(QLabel('State:'))
        hbox_layout4.addWidget(self.state)

        hbox_layout34 = QHBoxLayout()
        hbox_layout34.addLayout(hbox_layout3)
        hbox_layout34.addLayout(hbox_layout4)

        hbox_layout5 = QHBoxLayout()
        hbox_layout5.addWidget(self.back)
        hbox_layout5.addWidget(QLabel('Visit Date:'))
        hbox_layout5.addWidget(self.visitdate)
        hbox_layout5.addWidget(self.logvisit)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout12)
        vbox_layout.addLayout(hbox_layout34)
        vbox_layout.addWidget(self.filter)
        vbox_layout.addWidget(self.table_view)
        vbox_layout.addLayout(hbox_layout5)

        self.setLayout(vbox_layout)

    def enable_visit_button(self):
        if (self.table_view.currentIndex() != -1) and (self.visitdate.text() != ''):
            self.logvisit.setEnabled(True)
        else:
            self.logvisit.setEnabled(False)

    def run_filter(self):
        curs.execute(f'call user_filter_th("{self.thea_name.currentText()}", "{self.com_name.currentText()}","{self.city.text()}","{self.state.currentText()}");')
        query = f'call user_filter_th("{self.thea_name.currentText()}", "{self.com_name.currentText()}","{self.city.text()}","{self.state.currentText()}");'
        curs.execute(f'select * from UserFilterTh;')
        data = curs.fetchall()
        connection.commit()
        if (data):
            self.close()
            explore_theater(data, self.theater_names, self.com, self.screen, self.username).exec()
        else:
            w = QMessageBox()
            QMessageBox.information(w, "Empty Filter Result", "The filter result based on your inputs is empty.")
            w.show()
    def run_back(self):
        self.close()
        if self.screen == 7:
            admin_only_func(self.username).exec()
        elif self.screen == 8:
            admin_customer_func(self.username).exec()
        elif self.screen == 9:
            manager_only_func(self.username).exec()
        elif self.screen == 10:
            manager_customer_func(self.username).exec()
        elif self.screen == 11:
            customer_only_func(self.username).exec()
        elif self.screen == 12:
            user_func(self.username).exec()

    def run_logvisit(self):
        current_index = self.table_view.currentIndex().row()
        selected_item = self.table_model.row(current_index)
        used_visitdate = self.visitdate.text().replace('/','-')

        th_name = selected_item['Theater']
        com_name = selected_item['Company']
        query = f'call user_visit_th("{th_name}", "{com_name}", "{used_visitdate}","{self.username}");'

        try:
            used_visitdate = used_visitdate.split('-')
            newDate = datetime.datetime(int(used_visitdate[0]), int(used_visitdate[1]), int(used_visitdate[2]))

            curs.execute(query) #insert
            connection.commit()

            w = QMessageBox()
            QMessageBox.information(w, "Success", "You have successfully visited this theater! ")
            w.show()

        except:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid Date", "Please make sure the visit date is valid. ")
            w.show()


# ================Screen 23 User Visit History================
class visit_history(QDialog):
    def __init__(self, data, screen, username):
        super(visit_history, self).__init__()
        self.setWindowTitle("Visit History")
        self.username = username
        self.screen = screen

        self.name_label = QLabel("Company Name:")
        self.name = QComboBox()
        curs.execute('SELECT comName FROM company;')
        data1 = curs.fetchall()
        comName_list = [com['comName'] for com in data1]
        self.name.addItems(['ALL'] + comName_list)

        self.table_model = SimpleTableModel(data)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)

        self.visit_date_start_label = QLabel("Visit Date:")
        self.visit_date_start = QLineEdit()
        self.separate = QLabel("-")
        self.visit_date_end = QLineEdit()

        self.filter = QPushButton("Filter")
        self.filter.clicked.connect(self.run_filter)
        self.back = QPushButton("Back")
        self.back.clicked.connect(self.run_back)

        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.name_label)
        hbox_layout.addWidget(self.name)
        hbox_layout.addWidget(self.visit_date_start_label)
        hbox_layout.addWidget(self.visit_date_start)
        hbox_layout.addWidget(self.separate)
        hbox_layout.addWidget(self.visit_date_end)

        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addWidget(self.filter)
        vbox_layout.addWidget(self.table_view)
        vbox_layout.addWidget(self.back)

        self.setLayout(vbox_layout)

    def run_filter(self):
        entry = [self.username, (self.visit_date_start.text()).replace('/','-'), (self.visit_date_end.text()).replace('/', '-')]
        count = 0
        if entry[1]:
            try:
                min_date = entry[1].split('-')
                newDate = datetime.datetime(int(min_date[0]), int(min_date[1]), int(min_date[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the minimum visit date is valid.")
                w.show()
        else:
            count += 1

        if entry[2]:
            try:
                max_date = entry[2].split('-')
                newDate = datetime.datetime(int(max_date[0]), int(max_date[1]), int(max_date[2]))
                count += 1
            except:
                w = QMessageBox()
                QMessageBox.warning(w, "Invalid Date", "Please make sure the maximum visit date is valid.")
                w.show()
        else:
            count += 1

        if entry[1] and entry[2] and entry[1] > entry[2]:
            w = QMessageBox()
            QMessageBox.warning(w, "Invalid Date", "Please make sure the minimum visit date is less than the maximum visit date.")
            w.show()
        else:
            count += 1

        if count == 3:
            if entry[1] == '':
                entry[1] = 'NULL'
            if entry[2] == '':
                entry[2] = 'NULL'
            filter_query = f'SELECT thName as Theater, concat(thStreet, ", ", thCity, ", ", thState, " ", thZipcode) ' \
                f'as Address, comName as Company, visitDate as "Visit Date" FROM UserVisitTheater NATURAL JOIN Theater ' \
                f'WHERE username = "{self.username}" AND ("{entry[1]}" IS NULL OR visitDate >= "{entry[1]}") ' \
                f'AND ("{entry[2]}" IS NULL OR visitDate <= "{entry[2]}") AND ' \
                f'("{self.name.currentText()}" = "ALL" OR comName = "{self.name.currentText()}");'
            filter_query = filter_query.replace('"NULL"', 'NULL')
            curs.execute(filter_query)
            data = curs.fetchall()
            for i in range(len(data)):
                data[i]['Visit Date'] = str(data[i]['Visit Date'])
            connection.commit()
            if data:
                self.close()
                visit_history(data, self.screen, self.username).exec()
            else:
                w = QMessageBox()
                QMessageBox.information(w, "Empty Filter Result", "The filter result based on your inputs is empty.")
                w.show()

    def run_back(self):
        self.close()
        if self.screen == 7:
            admin_only_func(self.username).exec()
        elif self.screen == 8:
            admin_customer_func(self.username).exec()
        elif self.screen == 9:
            manager_only_func(self.username).exec()
        elif self.screen == 10:
            manager_customer_func(self.username).exec()
        elif self.screen == 11:
            customer_only_func(self.username).exec()
        elif self.screen == 12:
            user_func(self.username).exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    connection = pymysql.connect(host="localhost", user="root", password="",
                                 db="Team8", charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    curs = connection.cursor()
    main = Login()
    main.show()
    sys.exit(app.exec_())
