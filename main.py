from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import UnexpectedAlertPresentException
import threading
import base64
import ddddocr
import time

url = "https://tixcraft.com/"
date_select = '2023/05/14'
area_stack1 = "none"
area_stack2 = "none"
area_stack3 = "none"
area_stack4 = "看台區"
quantity = "1"
SID = ""

options = webdriver.ChromeOptions()
options.binary_location = "C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('ignore-certificate-errors')
driver = webdriver.Chrome(options=options)

ocr = ddddocr.DdddOcr()

session = 0

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
    if len(SID) > 1:
        driver.delete_cookie("SID")
        driver.add_cookie({"name":"SID", "value": SID, "path" : "/", "secure":True})
        driver.refresh()
        time.sleep(1)

def redirect(driver, url):
    ret = False
    url_split = url.split("/")
    if len(url_split) >= 6:
        game_name = url_split[5]
    if "/activity/detail/%s" % (game_name,) in url:        
        entry_url = url.replace("/activity/detail/","/activity/game/")
        driver.get(entry_url)
        ret = True 
    return ret

def date():
    table = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#gameList > table > tbody'))
    )
    area_list = table.find_elements(By.CSS_SELECTOR, 'tr')
    is_find = False
    if area_list is not None:
        area_list_count = len(area_list)
        for i in range(1, area_list_count+1):
            date_scan = f'tr:nth-child({i}) > td:nth-child(1)'
            rows = table.find_elements(By.CSS_SELECTOR, date_scan)
            row_content = []
            for row in rows:
                row_content.append(row.text)
            row_str = "".join(row_content)
            if date_select in row_str:
                button_scan = f'tr:nth-child({i}) > td:nth-child(4) > button'
                button_available = table.find_element(By.CSS_SELECTOR, button_scan)  
                driver.execute_script("arguments[0].click();", button_available)
                time.sleep(0.1)
                is_find = True
                """     
                button_html = button_available.get_attribute('outerHTML')
                if 'button' in button_html:
                    button_url_start_index = button_html.find('data-href="') + len('data-href="')
                    button_url_end_index = button_html.find('"', button_url_start_index)
                    button_url = button_html[button_url_start_index:button_url_end_index]
                    is_find = True
                    print(button_url)
                    driver.get(button_url)
                    break
                """
            if is_find:
                break
    return is_find

def select_area():
    is_success = False
    area_list = None
    area_list_count = 0
    table = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.zone'))
    )
    el = driver.find_element(By.CSS_SELECTOR, '.zone')   
    if el is not None:
        area_list = el.find_elements(By.TAG_NAME, 'a')
        if area_list is not None:
            area_list_count = len(area_list)
            if area_list_count == 0:
                is_success = False
        else:
            is_success = False
    if area_list_count > 0:
        area_stack_list = [area_stack1, area_stack2, area_stack3, area_stack4]
        for i in range(0,4):
            for row in area_list:
                row_is_enabled = False
                row_is_enabled = row.is_enabled()
                row_text = ""        
                if row_is_enabled:
                    row_text = row.text
                if row_text is None:
                    row_text = ""
                if len(row_text) > 0:
                    row_text = format_keyword_string(row_text)        
                    if area_stack_list[i] in row_text:
                        driver.execute_script("arguments[0].click();", row)
                        is_success = True
                        break
            if is_success:
                break
    return is_success

def ocr_answer():
    ocr_answer = None
    image_id = 'TicketForm_verifyCode-image'
    form_verifyCode_base64 = driver.execute_async_script("""
        var canvas = document.createElement('canvas');
        var context = canvas.getContext('2d');
        var img = document.getElementById('%s');
        canvas.height = img.naturalHeight;
        canvas.width = img.naturalWidth;
        context.drawImage(img, 0, 0);
        callback = arguments[arguments.length - 1];
        callback(canvas.toDataURL());
        """ % (image_id))
    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
    if not img_base64 is None:
        try:
            ocr_answer = ocr.classification(img_base64)
        except Exception as exc:
            pass      
    return ocr_answer

def check_ocr(answer):
    is_wrong = False    
    if not len(answer) == 4:
        image = driver.find_element(By.ID,'TicketForm_verifyCode-image')
        driver.execute_script("arguments[0].click();", image)
        #time.sleep(0.1)
        is_wrong = True
    return is_wrong

def check_and_quantity():
    form_select = None
    is_ticket_number_assigned = False    
    table = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#form-ticket-ticket'))
    )
    form_select = driver.find_element(By.CSS_SELECTOR, '.mobile-select')
    form_checkbox = driver.find_element(By.CSS_SELECTOR, '#TicketForm_agree')
    is_finish_checkbox_click = False
    select_obj = None
    if form_select is not None:
        select_obj = Select(form_select)
    if not select_obj is None:
        select_obj.select_by_visible_text(quantity)
        is_ticket_number_assigned = True
    if form_checkbox is not None:
        if form_checkbox.is_enabled():
            if not form_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", form_checkbox)
            is_finish_checkbox_click = True
    return is_ticket_number_assigned,is_finish_checkbox_click

def fillin_ocr(answer):
    form_verifyCode = None
    is_form_sumbited = False
    form_verifyCode = driver.find_element(By.ID, 'TicketForm_verifyCode')
    if form_verifyCode is not None:
        form_verifyCode.clear()
        form_verifyCode.send_keys(answer)
        is_form_sumbited = True
    if is_form_sumbited:
        form_verifyCode.send_keys(Keys.ENTER)

def thread1():
    global url
    while True:
        match(session):            
            case(1):
                while True:
                    if '/activity/detail/' in url:
                        try:
                            is_redirected = redirect(driver, url)
                        except Exception as exc:
                            pass
                        if is_redirected or session != 1:             
                            break
            case(2):                    
                while True:
                    if '/activity/game/' in url:
                        try:
                            is_find = date()
                        except Exception as exc:
                            pass                                                 
                        if is_find == True or session != 2:               
                            break
                        else:
                            driver.refresh()   
            case(3):        
                while True:
                    suc = False
                    if '/ticket/area/' in url:                        
                        try:
                            suc = select_area()
                        except Exception as exc:
                            pass
                        if suc == True or session != 3:
                                                                     
                            break
            case(4):        
                while True:
                    if '/ticket/ticket/' in url:
                        while True:
                            try:
                                quan_ok,check_ok = check_and_quantity()
                            except Exception as exc:
                                pass
                            if quan_ok and check_ok:
                                break   
                        for redo_ocr in range(999):
                            try:
                                code = ocr_answer()
                            except Exception as exc:
                                pass
                            if code is not None:
                                try:
                                    wrong = check_ocr(code)
                                except Exception as exc:
                                    pass
                            if not wrong:                    
                                break
                        try:                                                         
                            fillin_ocr(code)
                        except Exception as exc:
                            pass
                        time.sleep(0.1)
                        if session == 4:
                            continue
                        else: 
                            break
            
def thread2():
    global url
    global session
    while True:
        try:
            url = driver.current_url
            if '/activity/detail/' in url:
                session = 1
            elif '/activity/game/' in url:
                session = 2
            elif '/ticket/area/' in url:
                session = 3
            elif '/ticket/ticket/' in url:
                session = 4
            else:
                session = 0
        except UnexpectedAlertPresentException:            
            pass
                                      
t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=thread2)
launchBrowser()
t1.start()
t2.start()
t1.join()
t2.join()
driver.quit()
