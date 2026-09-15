# 튜플과세트형식.py

tp = (100,200,300)
print(len(tp))
print(tp.count(300))
print(tp.index(200))

#한방에 입력
print("id: %s, name: %s" % ("kim", "김유신"))
print("id: {0}, name: {1}, id: {0}".format("kim", "김유신"))

#여러개를 리턴
def times(a,b):
    return a+b, a*b

#호출
result=times(3,4)
print(result)

#형식변환
a=list((1,2,3))
a.append(4)
print(a)
b=set(a)
print(b)

#Set형식
s1={1,2,3,3}
s2={3,4,4,5}
print(s1.union(s2), s1|s2)
print(s1.intersection(s2), s1&s2)
print(s1.difference(s2), s1-s2)

#Dict형식(사전식)
fruits = {"apple":10, "kiwi":20}
#입력
fruits["banana"]=50
print(fruits)
#수정
fruits["apple"]=15
#삭제
del fruits["kiwi"]
print(fruits)

for item in fruits.items():
    print(item)