# DemoForm.py
# DemoForm.ui(화면단) + DemoForm.py(로직단)

import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6 import uic

#UI파일 로딩
form_class = uic.loadUiType("DemoForm.ui")[0]

#DemoForm 클래스 정의
class DemoForm(QDialog, form_class):
    #초기화 메서드
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText("PyQt6 처음사용")

#진입점을 체크(직접 이 모듈을 실행)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DemoForm()
    demo.show()
    sys.exit(app.exec())