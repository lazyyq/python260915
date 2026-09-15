# 함수 연습
#1)함수 정의

def times(a,b):
    return a*b

#2)함수를 호출
result=times(3,4)
print(result)

#전역변수
x=5
def func(a):
    #지역변수
    x=10
    return x+a

#호출
print(func(1))