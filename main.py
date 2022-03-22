"""
셀레니움을 이용한 간단한 자동화 수강 프로그램
마지막 업데이트 2022-03-16
"""


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import datetime

userID = input("ID입력 : ")
userPassword = input("PW입력 : ")

# 크롬브라우저 열기
chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 학교홈페이지로 이동
driver.get('https://plato.pusan.ac.kr/')

# 로그인
login = driver.find_element(By.ID, "input-username")
login.send_keys(userID)
login = driver.find_element(By.ID, "input-password")
login.send_keys(userPassword)
driver.find_element(By.NAME, "loginbutton").click()
time.sleep(3)

# 강의 목록 가져오기
lec_list = driver.find_elements(By.CSS_SELECTOR, '.course-title')
lec_count = len(lec_list)
print("수강중인 강의 수: ", lec_count)

# 팝업창 끄기
closeBtn_list = driver.find_elements(By.CSS_SELECTOR, '.close_notice')
for i in range(len(closeBtn_list)-1, -1, -1):
    closeBtn_list[i].click()

sequence = 0
# 수강중인 강좌수만큼 반복
for lec_num in range(lec_count):
    # 강의실 입장
    lec_list = driver.find_elements(By.CSS_SELECTOR, '.course-title')
    print("강좌명: ", lec_list[lec_num].find_element(By.CSS_SELECTOR, 'h3').text)
    lec_list[lec_num].click()
    time.sleep(1)

    # 들어야할 강의 확인
    # 온라인 출석부 입장
    checkBtn = driver.find_elements(By.CSS_SELECTOR, '.submenu-item')[2].find_element(By.CSS_SELECTOR, 'a')
    checkBtn.click()
    time.sleep(1)

    # 들어야할 강의 목록 생성
    check_list = []
    time_list = []
    for i in range(1, 1000):
        try:
            check = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/table/tbody/tr[' + str(i) + ']/td[4]')
            if check.text == 'O':
                pass
            elif check.text == 'X':
                check_list.append(driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/table/tbody/tr[' + str(i) + ']/td[1]').text)
                time_list.append(driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/table/tbody/tr[' + str(i) + ']/td[2]').text)
            else:
                check = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/table/tbody/tr[' + str(i) + ']/td[5]')
                if check.text == 'X':
                    check_list.append(driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/table/tbody/tr[' + str(i) + ']/td[2]').text)
                    time_list.append(driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/table/tbody/tr[' + str(i) + ']/td[3]').text)
        except:
            break
    len_check_list = len(check_list)
    print("이 강좌에서 수강하지 않은 강의 수: ", len_check_list)
    if len_check_list:
        print("---강의 목록---")
        for check in check_list:
            print(check)
            print(time_list[sequence])
            sequence += 1

    driver.back()
    time.sleep(1)

    # 강의 듣기
    sequence = 0
    video_list = driver.find_elements(By.CSS_SELECTOR, '.instancename')  # 강의목록 가져오기
    for check in check_list:
        for video in video_list:
            if (check in video.text) and ('동영상' in video.text):  # 수강해야할 강의인지 확인
                video.click()
                time.sleep(2)

                # 주의: alert 처리 미구현
                driver.switch_to.window(driver.window_handles[1])
                driver.find_element(By.CSS_SELECTOR, '.vjs-big-play-button').click()  # 강의 재생 버튼
                time.sleep(1)
                driver.find_element(By.CSS_SELECTOR, '.vjs-mute-control').click()  # 강의 소리 끄기

                # 강의 시간동안 기다리기 (출석 인정시간 * 1.12)
                try:
                    lec_time = time.strptime(time_list[sequence], "%H:%M:%S")
                except:
                    lec_time = time.strptime(time_list[sequence], "%M:%S")
                time.sleep(datetime.timedelta(hours=lec_time.tm_hour,
                                            minutes=lec_time.tm_min,
                                            seconds=lec_time.tm_sec).total_seconds()*1.12)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                sequence += 1
                break  # 다음 check 로 넘어가기

    # 강의실 퇴장
    driver.back()
    time.sleep(1)
    print("\n")

driver.close()
print("수강 완료!")
