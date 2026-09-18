import base64
import mimetypes
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PyQt6.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


load_dotenv(Path(__file__).with_name(".env"))


class DescriptionWorker(QObject):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path

    def run(self):
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    ".env 파일에 OPENAI_API_KEY가 설정되어 있지 않습니다."
                )

            mime_type = mimetypes.guess_type(self.image_path)[0] or "image/jpeg"
            with open(self.image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "이미지를 보고 주요 인물, 사물, 장소와 상황을 "
                                    "한국어로 이해하기 쉽게 설명해줘."
                                ),
                            },
                            {
                                "type": "input_image",
                                "image_url": (
                                    f"data:{mime_type};base64,{encoded_image}"
                                ),
                            },
                        ],
                    }
                ],
                max_output_tokens=400,
            )
            self.finished.emit(response.output_text)
        except Exception as error:
            self.failed.emit(str(error))


class ImageDescriptionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_pixmap = QPixmap()
        self.analysis_thread = None
        self.analysis_worker = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("AI 사진 설명기")
        self.resize(620, 720)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(12)

        self.image_label = QLabel("분석할 사진을 선택하세요")
        self.image_label.setMinimumSize(560, 400)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(
            "QLabel { background: #f2f4f7; border: 1px dashed #98a2b3; "
            "border-radius: 8px; color: #667085; }"
        )
        layout.addWidget(self.image_label)

        self.upload_button = QPushButton("사진 업로드 및 설명하기")
        self.upload_button.clicked.connect(self.select_image)
        layout.addWidget(self.upload_button)

        self.status_label = QLabel(".env의 OPENAI_API_KEY를 사용합니다.")
        layout.addWidget(self.status_label)

        self.description_edit = QTextEdit()
        self.description_edit.setReadOnly(True)
        self.description_edit.setPlaceholderText("사진 설명이 여기에 표시됩니다.")
        layout.addWidget(self.description_edit)

        self.setCentralWidget(central_widget)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "사진 선택",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "사진 오류", "이미지를 읽을 수 없습니다.")
            return

        self.current_pixmap = pixmap
        self.update_preview()
        self.description_edit.clear()
        self.start_analysis(file_path)

    def update_preview(self):
        if not self.current_pixmap.isNull():
            self.image_label.setPixmap(
                self.current_pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()

    def start_analysis(self, file_path: str):
        self.upload_button.setEnabled(False)
        self.status_label.setText("사진을 분석하는 중입니다...")

        self.analysis_thread = QThread(self)
        self.analysis_worker = DescriptionWorker(file_path)
        self.analysis_worker.moveToThread(self.analysis_thread)
        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_worker.finished.connect(self.show_description)
        self.analysis_worker.failed.connect(self.show_error)
        self.analysis_worker.finished.connect(self.finish_analysis)
        self.analysis_worker.failed.connect(self.finish_analysis)
        self.analysis_thread.start()

    def show_description(self, description: str):
        self.description_edit.setPlainText(description)
        self.status_label.setText("분석이 완료되었습니다.")

    def show_error(self, message: str):
        self.description_edit.setPlainText(f"분석 중 오류가 발생했습니다.\n\n{message}")
        self.status_label.setText("분석에 실패했습니다.")

    def finish_analysis(self, *_):
        self.upload_button.setEnabled(True)
        if self.analysis_thread is not None:
            self.analysis_thread.quit()
            self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)
        if self.analysis_worker is not None:
            self.analysis_worker.deleteLater()
        self.analysis_thread = None
        self.analysis_worker = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDescriptionApp()
    window.show()
    sys.exit(app.exec())