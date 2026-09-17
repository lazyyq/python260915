import sqlite3
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


def get_database_path():
    if getattr(sys, "frozen", False):
        executable_path = Path(sys.executable).resolve()
        for parent in executable_path.parents:
            if parent.suffix == ".app":
                return parent.parent / "MyProduct2.db"
        return executable_path.parent / "MyProduct2.db"

    return Path(__file__).resolve().with_name("MyProduct2.db")


DB_PATH = get_database_path()


class ProductWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connection = sqlite3.connect(DB_PATH)
        self.create_table()
        self.setup_ui()
        self.load_products()

    def create_table(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS MyProduct (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL
            )
            """
        )
        self.connection.commit()

    def setup_ui(self):
        self.setWindowTitle("자전거용품 관리")
        self.resize(760, 560)

        self.id_input = QLineEdit()
        self.id_input.setReadOnly(True)
        self.id_input.setPlaceholderText("자동 생성")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예: 자전거 헬멧")

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("숫자만 입력")

        form_layout = QFormLayout()
        form_layout.addRow("ID", self.id_input)
        form_layout.addRow("제품명", self.name_input)
        form_layout.addRow("가격", self.price_input)

        self.add_button = QPushButton("입력")
        self.update_button = QPushButton("수정")
        self.delete_button = QPushButton("삭제")
        self.search_button = QPushButton("검색")
        self.clear_button = QPushButton("전체보기")

        self.add_button.setObjectName("addButton")
        self.update_button.setObjectName("updateButton")
        self.delete_button.setObjectName("deleteButton")
        self.search_button.setObjectName("searchButton")
        self.clear_button.setObjectName("clearButton")

        self.add_button.clicked.connect(self.add_product)
        self.update_button.clicked.connect(self.update_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.search_button.clicked.connect(self.search_products)
        self.clear_button.clicked.connect(self.load_products)
        self.name_input.returnPressed.connect(self.search_products)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "제품명", "가격"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 300)
        self.table.cellDoubleClicked.connect(self.select_product)

        button_layout = QHBoxLayout()
        for button in (
            self.add_button,
            self.update_button,
            self.delete_button,
            self.search_button,
            self.clear_button,
        ):
            button_layout.addWidget(button)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 28)
        main_layout.setSpacing(18)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #102a43;
            }
            QWidget {
                color: #edf6f9;
                font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
                font-size: 14px;
            }
            QFormLayout QLabel {
                color: #b8f2e6;
                font-size: 15px;
                font-weight: 700;
                padding-right: 12px;
            }
            QLineEdit {
                min-height: 38px;
                padding: 0 12px;
                color: #102a43;
                background-color: #f4fbf9;
                border: 2px solid #4ecdc4;
                border-radius: 10px;
                selection-background-color: #ff6b6b;
            }
            QLineEdit:focus {
                border: 2px solid #ffd166;
                background-color: #ffffff;
            }
            QLineEdit:read-only {
                color: #5b7083;
                background-color: #dce8ed;
            }
            QPushButton {
                min-height: 40px;
                padding: 0 18px;
                border: none;
                border-radius: 10px;
                color: #102a43;
                font-size: 14px;
                font-weight: 800;
            }
            QPushButton:hover {
                border: 2px solid #ffffff;
            }
            QPushButton:pressed {
                padding-top: 3px;
            }
            #addButton { background-color: #4ecdc4; }
            #addButton:hover { background-color: #78e0d8; }
            #updateButton { background-color: #ffd166; }
            #updateButton:hover { background-color: #ffe39a; }
            #deleteButton { background-color: #ff6b6b; }
            #deleteButton:hover { background-color: #ff9292; }
            #searchButton { background-color: #f7aef8; }
            #searchButton:hover { background-color: #facbfa; }
            #clearButton { background-color: #90dbf4; }
            #clearButton:hover { background-color: #b6eafa; }
            QTableWidget {
                color: #183b56;
                background-color: #f7fbfc;
                alternate-background-color: #e8f5f2;
                border: 3px solid #4ecdc4;
                border-radius: 12px;
                gridline-color: #b8d8d8;
                selection-background-color: #ff6b6b;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                color: #ffffff;
                background-color: #147d92;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: 800;
            }
            QTableCornerButton::section {
                background-color: #147d92;
                border: none;
            }
            QScrollBar:vertical {
                width: 12px;
                background-color: #dce8ed;
                margin: 2px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                min-height: 30px;
                background-color: #4ecdc4;
                border-radius: 6px;
            }
            """
        )

    def read_product_input(self, require_id=False):
        product_id = self.id_input.text().strip()
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip().replace(",", "")

        if require_id and not product_id.isdigit():
            QMessageBox.warning(self, "입력 오류", "수정 또는 삭제할 제품을 먼저 선택하세요.")
            return None
        if not name:
            QMessageBox.warning(self, "입력 오류", "제품명을 입력하세요.")
            return None
        if not price_text.isdigit():
            QMessageBox.warning(self, "입력 오류", "가격은 0 이상의 정수로 입력하세요.")
            return None

        return int(product_id) if product_id else None, name, int(price_text)

    def add_product(self):
        product = self.read_product_input()
        if product is None:
            return

        _, name, price = product
        self.connection.execute(
            "INSERT INTO MyProduct (name, price) VALUES (?, ?)",
            (name, price),
        )
        self.connection.commit()
        self.load_products()
        self.clear_inputs()

    def update_product(self):
        product = self.read_product_input(require_id=True)
        if product is None:
            return

        product_id, name, price = product
        cursor = self.connection.execute(
            "UPDATE MyProduct SET name = ?, price = ? WHERE id = ?",
            (name, price, product_id),
        )
        self.connection.commit()
        if cursor.rowcount == 0:
            QMessageBox.information(self, "수정 결과", "해당 제품을 찾을 수 없습니다.")
            return

        self.load_products()
        self.clear_inputs()

    def delete_product(self):
        product_id = self.id_input.text().strip()
        if not product_id.isdigit():
            QMessageBox.warning(self, "입력 오류", "삭제할 제품을 먼저 선택하세요.")
            return

        answer = QMessageBox.question(
            self,
            "삭제 확인",
            f"제품 ID {product_id}를 삭제할까요?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.connection.execute("DELETE FROM MyProduct WHERE id = ?", (int(product_id),))
        self.connection.commit()
        self.load_products()
        self.clear_inputs()

    def search_products(self):
        keyword = self.name_input.text().strip()
        if keyword.isdigit():
            rows = self.connection.execute(
                "SELECT id, name, price FROM MyProduct WHERE id = ? ORDER BY id",
                (int(keyword),),
            ).fetchall()
        elif keyword:
            rows = self.connection.execute(
                "SELECT id, name, price FROM MyProduct "
                "WHERE name LIKE ? ORDER BY id",
                (f"%{keyword}%",),
            ).fetchall()
        else:
            rows = self.get_all_products()

        self.fill_table(rows)

    def load_products(self):
        self.fill_table(self.get_all_products())

    def get_all_products(self):
        return self.connection.execute(
            "SELECT id, name, price FROM MyProduct ORDER BY id"
        ).fetchall()

    def fill_table(self, rows):
        self.table.setRowCount(0)
        for row_index, (product_id, name, price) in enumerate(rows):
            self.table.insertRow(row_index)
            values = (str(product_id), name, f"{price:,}")
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column_index in (0, 2):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_index, column_index, item)

    def select_product(self, row, _column):
        id_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        price_item = self.table.item(row, 2)
        if id_item is None or name_item is None or price_item is None:
            return

        self.id_input.setText(id_item.text())
        self.name_input.setText(name_item.text())
        self.price_input.setText(price_item.text().replace(",", ""))

    def clear_inputs(self):
        self.id_input.clear()
        self.name_input.clear()
        self.price_input.clear()

    def closeEvent(self, event):
        self.connection.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductWindow()
    window.show()
    sys.exit(app.exec())
