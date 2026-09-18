import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTextEdit, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from openai import OpenAI
import base64

class ImageDescriptionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_pixmap = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle('컴퓨터비전으로 이미지 분석하는 앱')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        self.image_label = QLabel('이미지 분석에 필요한 사진을 업로드하세요.')
        self.image_label.setFixedSize(400, 400)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.upload_button = QPushButton('이미지 업로드')
        self.upload_button.clicked.connect(self.upload_image)
        self.layout.addWidget(self.upload_button)

        self.description_edit = QTextEdit()
        self.layout.addWidget(self.description_edit)

        self.central_widget.setLayout(self.layout)

    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File', '', 'Images (*.png *.xpm *.jpg)')
        if file_name:
            self.display_image(file_name)
            self.get_image_description(file_name)

    def display_image(self, file_name):
        pixmap = QPixmap(file_name)
        self.current_pixmap = pixmap
        self.update_image_preview()

    def update_image_preview(self):
        if not self.current_pixmap:
            return

        scaled = self.current_pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image_preview()

    # Function to encode the image
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
  
    def get_image_description(self, file_name):
        base64_image = self.encode_image(file_name)
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            self.description_edit.setPlainText("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            return

        try:
            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "이 이미지에 무엇이 있는지 한글로 설명해줘?"},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        ],
                    }
                ],
                max_output_tokens=300,
            )
            self.description_edit.setPlainText(response.output_text)
        except Exception as e:
            self.description_edit.setPlainText(f"이미지 분석 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageDescriptionApp()
    ex.show()
    sys.exit(app.exec())
