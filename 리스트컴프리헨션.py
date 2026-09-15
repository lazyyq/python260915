# range() 함수
for i in range(5):
    print(i)

print( list(range(10)) )

#리스트 함축 (압축)
lst = list(range(1,11))
print( [i**2 for i in lst if i>5] )

tp=("apply", "kiwi")
print( [len(i) for i in tp] )

#람다함수 활용
lst=[10,25,30]
itemL=filter(None, lst)
for i in itemL:
    print(i)

#함수 사용
def getBigger(x):
    return x>20

print("필터링 함수 활용")
itemL=filter(getBigger, lst)
for i in itemL:
    print(i)

print("람다 함수 활용")
itemL=filter(lambda x:x>20, lst)
for i in itemL:
    print(i)