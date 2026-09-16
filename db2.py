# db1.py
import sqlite3

#연결객체(파일에 영구적으로 저장)
con=sqlite3.connect(r"/Users/kykint/Desktop/work/sample.db")
#커서객체 생성
cur=con.cursor()
#테이블 생성
cur.execute("create table PhoneBook (name text, phone text);")
#1건 입력
cur.execute("insert into PhoneBook (name, phone) values ('tom', '010');")
#입력 매개변수 처리
name="전우치"
phoneNum="010-222"
cur.execute(
    "insert into PhoneBook (name, phone) values (?, ?)",
    (name, phoneNum),
)
#여러건을 입력
datalist = [
    ("홍길동", "010-111"),
    ("이순신", "010-333"),
]
cur.executemany(
    "insert into PhoneBook (name, phone) values (?, ?)",
    datalist
)

#검색
cur.execute("select * from PhoneBook;")
#주석처리: ctrl + /
for row in cur:
    print(row)
#정상적 완료
con.commit()