# 형식연습.py

#배열 형식

lst = [10,20,30]
print(len(lst))
print(type(lst))

for i in lst:
    print(i)


#다중라인 문자열
strC = """첫번째 문장은
두번째 문장은
세번째 문장은
"""

print(strC)
strA="python"
print(strA[0])
print(strA[1])
print(strA[0:3])
print(strA[:3])
print(strA[-3:])

#배열(리스트형식)
colors=["red","green","blue"]
print(len(colors))
colors.append("white")
colors.insert(1, "pink")
print(colors)
colors.remove("blue")
print(colors)