from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import threading

url = "https://tixcraft.com/"
date_select = '2023/05/06'
area_stack1 = "1000"
area_stack2 = "1800"
area_stack3 = "2200"
area_stack4 = "2000"

options = webdriver.ChromeOptions()
options.binary_location = "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

def format_keyword_string(keyword):
    if not keyword is None:
        if len(keyword) > 0:
            keyword = keyword.replace('／','/')
            keyword = keyword.replace('　','')
            keyword = keyword.replace(',','')
            keyword = keyword.replace('，','')
            keyword = keyword.replace('$','')
            keyword = keyword.replace(' ','').lower()
    return keyword

def launchBrowser():
    global url
    driver.get(url)
    driver.implicitly_wait(1)

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
    table = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#gameList > table > tbody'))
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

def select_area():
    is_success = False
    area_stack_list = [area_stack1, area_stack2, area_stack3, area_stack4]   
    try:
        table = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.zone'))
        )
        area_list = table.find_elements(By.TAG_NAME, 'a')
        
        for row in area_list:
            row_text = row.text.strip()
            row_text = format_keyword_string(row_text)           
            if any(area_stack in row_text for area_stack in area_stack_list):
                print("area stack: ", row_text)
                row.click()
                is_success = True
                break           
        if not is_success:
            print("No area found, refreshing page...")
            driver.refresh()           
    except TimeoutException:
        print("Timed out waiting for table to load, refreshing page...")
        driver.refresh()      
    return is_success

def thread1():
    global url
    while True:
        if '/activity/detail/' in url:
            is_redirected = redirect(driver, url)
            if is_redirected:
                url = driver.current_url
        else:
            url = driver.current_url

def thread2():
    global url
    while True:
        if '/activity/game/' in url:
            is_find = date()        
            if is_find == True:
                break

def thread3():
    global url  
    while True:
        if '/ticket/area/' in url:
            success = select_area()
            if success:
                break            

t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=thread2)
t3 = threading.Thread(target=thread3)

launchBrowser()

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()

driver.quit()
""" 
def select_area():
    is_need_refresh = False
    is_success = False
    area_list = None
    area_list_count = 0
    table = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.zone'))
    )
    el = driver.find_element(By.CSS_SELECTOR, '.zone')   
    if el is not None:
        area_list = el.find_elements(By.TAG_NAME, 'a')
        if area_list is not None:
            area_list_count = len(area_list)
            if area_list_count == 0:
                print("area list is empty, do refresh!")
                is_need_refresh = True
        else:
            is_need_refresh = True
    if area_list_count > 0:
        area_stack_list = [area_stack1, area_stack2, area_stack3, area_stack4]
        for i in range(0,4):
            for row in area_list:
                row_is_enabled=False
                row_is_enabled = row.is_enabled()
                row_text = ""        
                if row_is_enabled:
                    row_text = row.text
                if row_text is None:
                    row_text = ""
                if len(row_text) > 0:
                    row_text = format_keyword_string(row_text)        
                    if area_stack_list[i] in row_text:
                        print("area stack: ", i+1)
                        row.click()
                        is_success = True
                        break
                    if is_success:
                        break

        if not is_success:
            print("none area")
            is_need_refresh = True
                    
    if is_need_refresh:
        driver.refresh()
    return is_success
"""
