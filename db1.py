# db1.py
import sqlite3

#연결객체(일단 메모리에 저장)
con=sqlite3.connect(":memory:")
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
# for row in cur:
#     print(row)
print("---fetchone()---")
print(cur.fetchone())
print("---fetchmany(2)---")
print(cur.fetchmany(2))
print("---fetchall()---")
print(cur.fetchall())