import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6 import uic
import sqlite3
import os.path

# DB파일이 없으면 만들고 있다면 접속
if os.path.exists("ProductList.db"):
    con = sqlite3.connect("ProductList.db")
    cur = con.cursor()
else:
    con = sqlite3.connect("ProductList.db")
    cur = con.cursor()
    cur.execute("""
        create table Products (
            id integer primary key autoincrement,
            Name text,
            Price integer
        );
    """)

# 디자인 파일 로딩
form_class = uic.loadUiType("Chap10_ProductList.ui")[0]


class DemoForm(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 초기값 셋팅
        self.id = 0
        self.name = ""
        self.price = 0

        # QTableWidget 컬럼폭 설정
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 100)

        # 헤더 설정
        self.tableWidget.setHorizontalHeaderLabels(["제품ID", "제품명", "가격"])

        # 탭키 네비게이션 금지
        self.tableWidget.setTabKeyNavigation(False)

        # 엔터키 → 다음 컨트롤 이동
        self.prodID.returnPressed.connect(lambda: self.focusNextChild())
        self.prodName.returnPressed.connect(lambda: self.focusNextChild())
        self.prodPrice.returnPressed.connect(lambda: self.focusNextChild())

        # 더블클릭 시그널
        self.tableWidget.doubleClicked.connect(self.doubleClick)

    def addProduct(self):
        self.name = self.prodName.text()
        self.price = self.prodPrice.text()

        cur.execute(
            "insert into Products (Name, Price) values(?,?);",
            (self.name, self.price)
        )

        self.getProduct()
        con.commit()

    def updateProduct(self):
        self.id = self.prodID.text()
        self.name = self.prodName.text()
        self.price = self.prodPrice.text()

        cur.execute(
            "update Products set name=?, price=? where id=?;",
            (self.name, self.price, self.id)
        )

        self.getProduct()
        con.commit()

    def removeProduct(self):
        self.id = self.prodID.text()

        cur.execute("delete from Products where id=?;", (self.id,))

        self.getProduct()
        con.commit()

    def getProduct(self):
        self.tableWidget.clearContents()

        cur.execute("select * from Products;")

        row = 0
        for item in cur:
            int_as_strID = "{:10}".format(item[0])
            int_as_strPrice = "{:10}".format(item[2])

            # ID
            itemID = QTableWidgetItem(int_as_strID)
            itemID.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tableWidget.setItem(row, 0, itemID)

            # Name
            self.tableWidget.setItem(row, 1, QTableWidgetItem(item[1]))

            # Price
            itemPrice = QTableWidgetItem(int_as_strPrice)
            itemPrice.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.tableWidget.setItem(row, 2, itemPrice)

            row += 1
            print("row:", row)

    def doubleClick(self):
        current_row = self.tableWidget.currentRow()

        self.prodID.setText(self.tableWidget.item(current_row, 0).text())
        self.prodName.setText(self.tableWidget.item(current_row, 1).text())
        self.prodPrice.setText(self.tableWidget.item(current_row, 2).text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demoForm = DemoForm()
    demoForm.show()
    app.exec()