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
    
    firefox_bin = "/snap/firefox/current/usr/lib/firefox/firefox"
    
    firefoxdriver_bin = "/snap/firefox/current/usr/lib/firefox/geckodriver"
    options.binary_location = firefox_bin
    service = selenium.webdriver.firefox.service.Service(executable_path=firefoxdriver_bin, log_output='geckolog.log', service_arts=['--log', 'debug'])
    #service = selenium.webdriver.firefox.service.Service(executable_path=firefoxdriver_bin)

    print('assigning browser now')

    browser = selenium.webdriver.Firefox(options=options, service=service)

    print('getting homepage')

    browser.get('https://www.linkedin.com/')

    print('adding cookies')

    read_cookies(base_path, browser)

    print('setup new browser finished!')

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
    cookies = browser.get_cookies()
    print('cookie length:', len(cookies))
    if len(cookies) != 0:
        json.dump(cookies, f)
    f.close()

def scroll_all_heights(browser):
    h = browser.execute_script("return document.body.scrollHeight")
    for y in range(0, h, 500):
        browser.execute_script("javascript:window.scrollTo(0, " + str(y) + ");")

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

def find_recent_jobs(base_path, browser, pages):
    browser.get('https://www.linkedin.com/jobs/search/?distance=3000&f_AL=true&f_E=2&f_JT=F&f_TPR=r86400&keywords=software%20engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD')
    print('in new joblist')
    job_links = []
    y = 0
    while True:
        header = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'scaffold-layout__list-header')) )
        for job in get_all_job_links(browser):
            job_links.append(job)
        next_button = browser.find_elements(By.CLASS_NAME, 'jobs-search-pagination__button--next')
        print('at ', len(job_links), 'jobs in list')
        if len(next_button) == 0:
            break
        y += 1
        if y == pages:
            break
        next_button[0].click()
    return job_links

def get_all_job_links(browser):
    scroll_all_heights(browser)
    listofjobs = browser.find_elements(By.CLASS_NAME, 'job-card-list__title')
    return [x.get_attribute('href') for x in listofjobs]

def apply_easy_job(browser, url, excluded_companies, base_path, pause=False):
    browser.get(url)
    print('applying to', url)
    
    for y in range(10):
        time.sleep(0.1)
        post_apply = browser.find_elements(By.CLASS_NAME, 'post-apply-timeline')
        if len(post_apply) > 0:
            print('already applied')
            return True
    
    for y in range(10):
        time.sleep(0.1)
        company_card = browser.find_elements(By.CLASS_NAME, 'job-details-jobs-unified-top-card__company-name')
        if len(company_card) > 0:
            break
    company_link = company_card[0].find_element(By.TAG_NAME, 'a').get_attribute('href')
    if company_link.split('/')[4] in excluded_companies:
        print('skipping this job because', company_link, ' is an excluded company', url)
        return True

    for y in range(10):
        time.sleep(0.1)
        buttons = browser.find_elements(By.CLASS_NAME, 'jobs-apply-button')
        easy = [x for x in buttons if x.text == "Easy Apply"]
        if len(easy) == 0:
            if y == 9:
                return False
            continue
        easy[0].click()
        break

    time.sleep(1)

    last_header = ''

    #no job has 20 pages in an easy apply app
    hard_limit = 40

    while True:
        overlay = browser.find_element(By.CLASS_NAME, 'artdeco-modal-overlay')
        headers = overlay.find_elements(By.TAG_NAME, 'h3')
        heads = [x for x in headers if x.text != '']
        if len(heads) > 0:
            header = heads[0]
        else:
            print('error could not find header')
            return True
        next_button = overlay.find_element(By.CLASS_NAME, 'artdeco-button--primary')
        match next_button.text:
            case 'Submit application':
                follow_checkbox = overlay.find_elements(By.ID, 'follow-company-checkbox')
                if len(follow_checkbox) > 0:
                    follow_checkbox[0].send_keys(Keys.SPACE)
                next_button.send_keys(Keys.SPACE)
                return True
            
            case 'Next' | 'Review':
                if last_header == header.text:
                    error_list = overlay.find_elements(By.CLASS_NAME, 'artdeco-inline-feedback__message')
                    #print(len(error_list), [x.text for x in error_list])
                    if len(error_list) == 0:
                        print('header was the same but could not find any errors!')
                    else:
                        # question_answers is a json dictionary with a list of error text
                        # and keywords to match against. if all keywords are present in the question
                        # then enter the keyword in the box, click the radio button with the label
                        # or select the right drop down menu
                        # like {"Please enter a valid answer": [ {"answer": "0.0", "keywords": ["java", "experience"]}, {"answer": "4.0", "keywords": ["python", "experience"]} ] }

                        f = open(base_path + 'question_answers.json', 'r')
                        question_answers = json.load(f)
                        f.close()

                    for error in error_list:
                        entry_upper_elem = error.find_element(By.XPATH, '../../../.')
                        input_boxes = entry_upper_elem.find_elements(By.TAG_NAME, 'input')
                        select_boxes = entry_upper_elem.find_elements(By.TAG_NAME, 'select')
                        questions = entry_upper_elem.find_elements(By.TAG_NAME, 'label')


                        if len(input_boxes) == 1:
                            if input_boxes[0].get_attribute('class').find('text-input--input') != -1:
                                if error.text not in question_answers:
                                    print('unencountered error text')
                                    f = open(base_path + 'error_answers.log', 'a')
                                    output = 'error not seen before: ' + error.text + ' . question: ' + questions[0].text + ' in text box\n'
                                    f.write(output)
                                    return True

                                for qa_pair in question_answers[error.text]:
                                    keywords = qa_pair['keywords']
                                    l = 0
                                    for word in keywords:
                                        if qa_pair["case"] == "lower":
                                            if questions[0].text.lower().find(word) == -1:
                                                break
                                        else:
                                            if questions[0].text.find(word) == -1:
                                                break
                                        l += 1
                                    if l == len(keywords):
                                        #enter item
                                        print('found answer to:', questions[0].text, ' as ', qa_pair['answer'], ' in text box')
                                        input_boxes[0].send_keys(qa_pair['answer'])
                                else:
                                    print('no answer found to question:', questions[0].text, 'for error:', error.text, ' in text box')
                                    print('unencountered question text')
                                    f = open(base_path + 'error_answers.log', 'a')
                                    output = 'need answer to: ' + error.text + ' . question: ' + questions[0].text + ' in text box\n'
                                    f.write(output)
                                    return True
                            else:
                                print('non-text box input single element found', url)
                                print(input_boxes[0].get_attribute('class'))
                                return True

                        elif len(input_boxes) == 2:
                            print('job has radio button entry questions, need to debug later', url)
                            return True
                        elif len(select_boxes) == 1:
                            if error.text not in question_answers:
                                print('unencountered error text')
                                f = open(base_path + 'error_answers.log', 'a')
                                output = 'error not seen before: ' + error.text + ' . question: ' + questions[0].text + ' in dropdown\n'
                                f.write(output)
                                return True

                            for qa_pair in question_answers[error.text]:
                                keywords = qa_pair['keywords']
                                l = 0
                                for word in keywords:
                                    if qa_pair["case"] == "lower":
                                        if questions[0].text.lower().find(word) == -1 and questions:
                                            break
                                    else:
                                        if questions[0].text.find(word) == -1 and questions:
                                            break
                                    l += 1
                                if l == len(keywords):
                                    #enter item
                                    print('found answer to:', questions[0].text, ' as ', qa_pair['answer'], ' in dropdown')
                            else:
                                print('no answer found to question:', questions[0].text, 'for error:', error.text, ' in dropdown')
                                return True


                            """
                            options = select_boxes[0].find_elements(By.TAG_NAME, 'option')
                            qs = questions[0].text.lower()
                            if qs.find('vaccination') != -1 and qs.find('covid'):
                                clicked = False
                                for selection in options:
                                    if selection.text.lower().find('yes') != -1:
                                        if not selection.is_displayed():
                                            selection.location_once_scrolled_into_view
                                        selection.click()
                                        clicked = True
                                        break
                                if not clicked:
                                    print('no option marked yes', url)
                                    print('options', len(options), [x.text for x in options])
                                    return False
                            elif questions[0].text.find('OPT') != -1:
                                clicked = False
                                for selection in options:
                                    if selection.text.lower().find('no') != -1:
                                        if not selection.is_displayed():
                                            selection.location_once_scrolled_into_view
                                        selection.click()
                                        clicked = True
                                        break
                                if not clicked:
                                    print('no option marked yes', url)
                                    print('options', len(options), [x.text for x in options])
                                    return False
                            else:
                                print('unaccounted for question')
                                print('options', len(options), [x.text for x in options])
                                print('questions', len(questions), [x.text for x in questions])
                                return False
                            """
                        elif len(select_boxes) > 1:
                            print('multiple select boxes??', url)
                            return False
                        if len(select_boxes) == 0 and len(input_boxes) == 0:
                            print('error found with zero input boxes or select boxes!', url)
                            return False
                last_header = header.text
                next_button.click()

            case 'Continue applying':
                print('linkedin safety warning', url)
                return True

            case _:
                print('found different overlay', next_button.text)
                print(last_header, header.text)
                next_button.click()

        time.sleep(0.05 + random.randint(0, 40) * 0.02)
        if pause:
            print('pausing for debugging purposes')
            input()
        if hard_limit == 0:
            print('job hit page limit of 40. probably an uncaught error loop', url)
            return False
        hard_limit -= 1
