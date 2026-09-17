# Chap09_중고장터검색_GUI연결.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem
)
import urllib.request
from bs4 import BeautifulSoup
import webbrowser
import re


class DemoForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        # 창 위치 및 크기
        self.setGeometry(200, 200, 800, 600)

        # 입력 텍스트
        self.lineEdit = QLineEdit("", self)
        self.lineEdit.move(20, 20)
        self.lineEdit.setText("아이폰")

        # 버튼
        self.btn = QPushButton("검색", self)
        self.btn.move(120, 20)
        self.btn.clicked.connect(self.setTableWidgetData)

        # 테이블
        self.tableWidget = QTableWidget(self)
        self.tableWidget.move(20, 70)
        self.tableWidget.resize(700, 500)
        self.tableWidget.setRowCount(100)
        self.tableWidget.setColumnCount(2)

        self.tableWidget.setColumnWidth(0, 400)
        self.tableWidget.setColumnWidth(1, 200)

        self.tableWidget.setHorizontalHeaderLabels(
            ["중고장터 매물", "URL주소"]
        )

        # 더블클릭 시 브라우저 열기
        self.tableWidget.doubleClicked.connect(self.doubleClicked)

    def setTableWidgetData(self):
        row = 0
        self.tableWidget.clearContents()

        for n in range(0, 10):
            url = (
                "https://www.clien.net/service/board/sold"
                "?&od=T31&po=" + str(n)
            )

            data = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(data, "html.parser")
            items = soup.find_all("a", attrs={"class": "list_subject"})

            with open("clien.txt", "a+", encoding="utf-8") as f:
                for item in items:
                    try:
                        title = item.text.strip()

                        if re.search(self.lineEdit.text(), title):
                            title = title.replace("\t", "")
                            title = title.replace("\n", "")

                            link = (
                                "https://www.clien.net"
                                + item["href"]
                            )

                            f.write(title + "\n")
                            f.write(link + "\n")

                            self.tableWidget.setItem(
                                row, 0,
                                QTableWidgetItem(title)
                            )
                            self.tableWidget.setItem(
                                row, 1,
                                QTableWidgetItem(link)
                            )

                            row += 1
                            print("row:", row)

                    except Exception:
                        pass

    def doubleClicked(self):
        current_row = self.tableWidget.currentRow()
        url = self.tableWidget.item(current_row, 1).text()
        webbrowser.open(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myForm = DemoForm()
    myForm.show()
    app.exec()