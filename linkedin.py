import os
import sys
from datetime import datetime
import time
import selenium.webdriver
import selenium.webdriver.firefox.service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import random

#according to a stackoverflow answer, firefox handles this differently than chrome
def scroll_to(browser, element):
    y = element.location['y'] + 200
    browser.execute_script("javascript:window.scrollTo(0, " + str(y) + ");")

def connect_and_scrape(parent_element, browser):
    buttons = parent_element.find_elements(By.TAG_NAME, 'button')
    connect_bttns = [x for x in buttons if x.text.strip() == 'Connect']
    num_clicks = 0
    errors = 0
    limit = False
    for butt in connect_bttns:
        scroll_to(browser, butt)
        time.sleep(0.05 + random.randint(0, 40) * 0.02)
        scroll_to(browser, butt)
        try:
            butt.click()
            num_clicks += 1
        except:
            errors += 1
    time.sleep(0.05)
    current_buttons = parent_element.find_elements(By.TAG_NAME, 'button')
    remaining_connect = [x for x in buttons if x.text.strip() == 'Connect']

    if len(remaining_connect) > 0 and num_clicks > 0:
        limit = True
    links = [x.get_attribute('href') for x in parent_element.find_elements(By.TAG_NAME, 'a')]
    return (num_clicks, set([y.split('?')[0] for y in links if y.find('/in/') != -1]), limit)

def get_suggested(url, browser):
    old_window = browser.current_window_handle
    browser.switch_to.new_window('tab')
    WebDriverWait(browser, 5).until(EC.number_of_windows_to_be(2))
    browser.switch_to.window(browser.window_handles[-1])
    time.sleep(1)
    browser.get(url)
    overlay = browser.find_element(By.CLASS_NAME, 'artdeco-modal-overlay')
    modal = False
    try:
        overlay.find_element(By.CLASS_NAME, 'artdeco-tablist')
        modal = True
    except:
        pass
    if modal:
        clicks = 0
        all_profiles = set()
        prebttn = overlay.find_element(By.CLASS_NAME, 'artdeco-tablist')
        bttns = prebttn.find_elements(By.XPATH, './button')
        for x in bttns:
            scroll_to(browser, x)
            time.sleep(0.1 + random.randint(0, 15) * 0.2)
            x.click()
            info = connect_and_scrape(overlay, browser)
            clicks += info[0]
            all_profiles = all_profiles | info[1]
            if info[2]:
                break
        return (clicks, all_profiles, info[2])
    else:
        info = connect_and_scrape(overlay, browser)
    browser.close()
    browser.switch_to.window(old_window)
    return info

def get_full_element_from_anchor(anchor_name, browser):
    try:
        anc = browser.find_element(By.ID, anchor_name)
    except:
        return None
    try:
        anc = anc.find_element(By.XPATH, './..')
    except:
        return None
    try:
        link = anc.find_element(By.PARTIAL_LINK_TEXT, 'Show all').get_attribute('href')
    except:
        link = None
    return (anc, link)

def setup_new_browser(base_path, arguments):

    options = selenium.webdriver.firefox.options.Options()
    print(type(arguments), arguments)
    for arrg in arguments:
        print('adding', arrg, type(arrg))
        options.add_argument(arrg)

    # instead of hard coding arguments, since this might be used on different types of systems
    # you can set the arguments based on the system you are running the script on

    # some sample ones below
    #options.add_argument('--width=2560')
    #options.add_argument('--height=1440')
    #options.add_argument('--headless')
    #options.add_argument('--no-sandbox')

    browser = selenium.webdriver.Firefox(options=options)

    browser.get('https://www.linkedin.com/')

    read_cookies(base_path, browser)

    return browser

def read_cookies(base_path, browser):
    try:
        f = open(base_path + 'cookies.json', 'r')
        cookies = json.load(f)
        f.close()

        for cookie in cookies:
            browser.add_cookie(cookie)
    except Exception as e:
        print('error reading cookies from {0}, error {1}.\nplease sign in manually.'.format(base_path, str(e)))
        input()

def save_cookies(base_path, browser):
    f = open(base_path + 'cookies.json', 'w')
    json.dump(browser.get_cookies(), f)
    f.close()
    
def scroll_to_bottom(browser, click_button=False, repetitions=-1):
    h = browser.execute_script("return document.body.scrollHeight")
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5 + random.randint(0,5) * 0.14)
        h_new = browser.execute_script("return document.body.scrollHeight")
        if repetitions == 0:
            break
        elif repetitions < 0:
            pass
        else:
            repetitions -= 1
        if h_new == h:
            if click_button:
                button = browser.find_elements(By.CLASS_NAME, 'scaffold-finite-scroll__load-button')
                if len(button) > 0:
                    try:
                        button[0].click()
                        continue
                    except:
                        print('button click attempt failed, aborting')
                        break
            break
        h = h_new
    
def connect_all_suggested_profiles(p_url, browser):

    browser.get(p_url)

    try:
        exp = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-button--primary')) )
    except:
        print('profile not loaded in time')
        exit(1)

    scroll_to_bottom(browser)

    msg_bttn = browser.find_element(By.CLASS_NAME, 'msg-overlay-bubble-header__controls')
    msg_bttn = msg_bttn.find_element(By.XPATH, './button[2]')
    msg_bttn.click()

    suggested = []
    sug_list = ['premium_browsemap_recommendation', 'browsemap_recommendation', 'pymk_recommendation_from_school', 'pymk_recommendation_from_company', 'pymk-recommendations-from-industry', 'pymk_recommendation']

    for x in sug_list:
        suggested.append(get_full_element_from_anchor(x, browser))
    
    seen_profiles = set()
    total_clicks = 0

    for x in suggested:
        if x != None:
            if x[1] != None:
                info = get_suggested(x[1], browser)
            else:
                info = connect_and_scrape(x[0], browser)
                
            seen_profiles = seen_profiles | info[1]
            total_clicks += info[0]
            if info[2]:
                break

    time.sleep(1)   
    return (total_clicks, seen_profiles, info[2])

def scrape_current_connections(browser):
    browser.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(2 + random.randint(0, 10) * 0.2)
    scroll_to_bottom(browser, click_button=True)

    connections = []

    for lnk in browser.find_elements(By.CLASS_NAME, 'mn-connection-card__link'):
        connections.append( lnk.get_attribute("href") )

    return connections

def save_connections(base_path, connections):
    f = open(base_path + 'connections.json', 'w')
    json.dump(connections, f)
    f.close()

def get_connections(base_path):
    f = open(base_path + 'connections.json', 'r')
    conn = list(json.load(f))
    f.close()
    return conn

#assumes you have saved all your connections in oldest first order and are saving new ones
def update_connections(base_path, browser):
    
    browser.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(2 + random.randint(0, 10) * 0.2)

    old_connections = set(get_connections(base_path))
    just_saw = set()
    stop = False
    
    while not stop:
        for lnk in browser.find_elements(By.CLASS_NAME, 'mn-connection-card__link'):
            href = lnk.get_attribute("href")
            if href in just_saw:
                continue
            elif href in old_connections:
                stop = True
                break
            if not stop:
                just_saw.add(href)
        if not stop:
            scroll_to_bottom(browser, click_button = True, repetitions = 1)

    save_connections(base_path, list(old_connections | just_saw))

if __name__ == "__main__":
    base_path = sys.argv[1]
    browser = setup_new_browser(base_path)
    #print( connect_all_suggested_profiles( input('paste profile url: ').strip(), base_path ))
