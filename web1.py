# web1.py
from bs4 import BeautifulSoup

#웹페이지를 로딩(rt-read text, wt-write text)
page = open("chap09_test.html", "rt", encoding="utf-8").read()
#검색이 용이한 스프 객체
soup = BeautifulSoup(page, "html.parser")
#전체 페이지를 출력
# print(soup.prettify())
#<p> 태그를 몽땅 검색
# print(soup.find_all("p"))
#첫번째 <p>태그만 검색
# print(soup.find("p"))
#조건검색: <p class='outer-text'>만 검색
# print(soup.find_all("p", class_="outer-text"))
#attrs를 사용
# print(soup.find_all("p", attrs={"class": "outer-text"}))
#id를 사용한 검색: <p id='inner-text'>만 검색
# print(soup.find("p", id="first"))
#태그 내부에 문자열만 가져오기: .text 속성
for tag in soup.find_all("p"):
    title=tag.text.strip()
    title=title.replace("\n", "")
    print(title)

#문자열 메서드
#정규표현식
#파일에 쓰고, 읽기
f=open("demo.txt", "wt", encoding="utf-8")
f.write("첫번째\n두번째\n")
f.close()

f=open("demo.txt", "rt", encoding="utf-8")
result=f.read()
print(result)
f.close()

#문자열 처리
data="<<< 햄버거 피자 치킨 >>>"
result=data.strip("<> ")
print(result)
result2=result.replace("햄버거", "치폴레")
print(result2)
#리스트로 변경
lst=result2.split()
print(lst)
#하나의 문자열로 조립
result3=" ".join(lst)
print(result3)

#정규표현식
import re

result=re.search("[0-9]*th", "35th")
print(result)
print(result.group())

result=re.search("\d{4}", "올해는 2026년입니다.")
print(result)
print(result.group())

result=re.search("apple", "this is apple")
print(result)
print(result.group())