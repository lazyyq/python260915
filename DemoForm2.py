# DemoForm2.py
# DemoForm2.ui(화면단) + DemoForm2.py(로직단)

from pathlib import Path
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic

#크롤링을 위한 선언
from bs4 import BeautifulSoup
import urllib.request

#정규표현식
import re

#실행 파일 기준 경로 설정
if getattr(sys, "frozen", False):
    executable_path = Path(sys.executable).resolve()
    app_bundle = next(
        (Path(*executable_path.parts[:index + 1])
         for index, part in enumerate(executable_path.parts)
         if part.endswith(".app")),
        None,
    )
    base_dir = app_bundle.parent if app_bundle else executable_path.parent
else:
    base_dir = Path(__file__).resolve().parent

#UI파일 로딩
ui_path = base_dir / "DemoForm2.ui"
form_class = uic.loadUiType(ui_path)[0]

#DemoForm 클래스 정의
class DemoForm(QMainWindow, form_class):
    #초기화 메서드
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText("PyQt6 처음사용")

    def firstClick(self):
        self.label.setText("첫번째 버튼 클릭")

        #파일에 저장
        f = open(base_dir / "clien.txt", "wt", encoding="utf-8")
        # f = open("todayhumor.txt", "wt", encoding="utf-8")

        hdr = {"User-Agent": "Mozilla/5.0"}

        #페이징 처리
        #클리앙은 1부터, 오늘의유머는 0부터 시작
        for i in range(0, 10):
            url = f"https://www.clien.net/service/board/sold?&od=T31&category=0&po={i}"
            # url = f"https://www.todayhumor.co.kr/board/list.php?table=bestofbest&page={i}"
            print(i)
            #요청객체
            req = urllib.request.Request(url, headers=hdr)
            data = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(data, "html.parser")

            for tag in soup.find_all("span", attrs={"data-role": "list-title-text"}):
            # for tag in soup.find_all("td", attrs={"class": "subject"}):
                title = tag.text.strip()
                title = title.replace("\n", "")
                # print(title)
                if re.search("아이패드", title):
                    print(title)
                    f.write(title + "\n")

        f.close()
        self.label.setText("중고장터 크롤링 완료")
    def secondClick(self):
        self.label.setText("두번째 버튼 클릭")
    def thirdClick(self):
        self.label.setText("세번째 버튼 클릭")

#진입점을 체크(직접 이 모듈을 실행)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DemoForm()
    demo.show()
    sys.exit(app.exec())