# 셀리니움_웹드라이버_네이버로그인.py

# 잘 안 됨 ㅠㅠ

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import clipboard
import time

#selenium 4.6이상은 웹드라이버 설치 없이 사용 
driver = webdriver.Chrome()
driver.get('https://nid.naver.com/nidlogin.login')

# 로그인 창에 아이디/비밀번호 입력
loginID = "..."
clipboard.copy(loginID)
#mac은 COMMAND, window는 CONTROL
driver.find_element(By.XPATH,'//*[@id="id"]').send_keys(
    Keys.COMMAND, 'v')
time.sleep(1)

loginPW = "..."
clipboard.copy(loginPW)
driver.find_element(By.XPATH,'//*[@id="pw"]').send_keys(
    Keys.COMMAND, 'v')
time.sleep(1)

# 로그인 버튼 클릭
driver.find_element(By.XPATH,'//*[@id="loginBtn_row"]').click()
time.sleep(1)

# 비번 다시 입력
loginPW = "..."
clipboard.copy(loginPW)
driver.find_element(By.XPATH,'//*[@id="pw"]').send_keys(
    Keys.COMMAND, 'v')
time.sleep(1)

# 로그인 버튼 다시 클릭
driver.find_element(By.XPATH,'//*[@id="loginBtn_row"]').click()
time.sleep(1)

while True:
    pass 