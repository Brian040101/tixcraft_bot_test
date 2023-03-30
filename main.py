import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import threading

url = "https://tixcraft.com/"
date_select = '2023/03/31'

options = webdriver.ChromeOptions()
options.binary_location = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

def launchBrowser():
    global url
    driver.get(url)

def redirect(driver, url):
    ret = False
    url_split = url.split("/")

    if len(url_split) >= 6:
        game_name = url_split[5]

    if "/activity/detail/%s" % (game_name,) in url:        
        entry_url = url.replace("/activity/detail/","/activity/game/")
        print("redirect to new url:", entry_url)
        driver.get(entry_url)
        ret = True 
    return ret
def date():
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#gameList > table > tbody"))
    )
    area_list = driver.find_elements(By.CSS_SELECTOR, '#gameList > table > tbody > tr')
    matched_rows = []
    is_find = False
    if area_list is not None:
        area_list_count = len(area_list)
        for i in range(1, area_list_count+1):
            date_scan = f'#gameList > table > tbody > tr:nth-child({i}) > td:nth-child(1)'
            rows = driver.find_elements(By.CSS_SELECTOR, date_scan)
            row_content = []
            for row in rows:
                row_content.append(row.text)
            row_str = "".join(row_content)
            if date_select in row_str:
                matched_rows.append(row_content)
                button_scan = f'#gameList > table > tbody > tr:nth-child({i}) > td:nth-child(4)'
                button_available = driver.find_element(By.CSS_SELECTOR, button_scan)             
                button_html = button_available.get_attribute('outerHTML')
                if 'button' in button_html:
                    button_url_start_index = button_html.find('data-href="') + len('data-href="')
                    button_url_end_index = button_html.find('"', button_url_start_index)
                    button_url = button_html[button_url_start_index:button_url_end_index]
                    is_find = True
                    print(button_url)
                    driver.get(button_url)
                else:
                    driver.refresh()

    return is_find
def thread1():
    global url
    while True:
        if "/activity/detail/" in url:
            is_redirected = redirect(driver, url)
            if is_redirected:
                url = driver.current_url
        else:
            url = driver.current_url

def thread2():
    while True:
        is_find = date()
        if is_find == True:
            break

t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=thread2)

launchBrowser()

t1.start()
t2.start()

t1.join()
t2.join()

driver.quit()
