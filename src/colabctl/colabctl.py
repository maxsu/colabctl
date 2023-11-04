import sys
import pickle
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import validators

from utils import sleep, file_to_list
from driver_queries import exists_by_text2, exists_by_xpath, exists_by_text
from driver_commands import wait_for_xpath, scroll_to_bottom

# Provide execution path to chromedriver
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

# Toggle debug mode
DEBUG = False

# Parse Arguments
fork = sys.argv[1]
timeout = int(sys.argv[2])

# Load Colab URLs
COLAB_URLS = file_to_list('notebooks.csv')
if not COLAB_URLS or not validators.url(COLAB_URLS[0]):
    raise Exception('No notebooks')
COLAB_MAIN_URL = COLAB_URLS[0]

# Setup Selenium Webdriver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
if DEBUG:
    chrome_options.add_argument("user-data-dir=profile")

wd = webdriver.Chrome('chromedriver', options=chrome_options)

wd.get(COLAB_MAIN_URL)
try:
    for cookie in pickle.load(open("gCookies.pkl", "rb")):
        wd.add_cookie(cookie)
except Exception:
    pass
wd.get(COLAB_MAIN_URL)

TOP_LEVEL_FILE_MENU = '//*[@id="file-menu-button"]/div/div/div[1]'
OK_BUTTON  = '//*[@id="ok"]'
LOGIN_DETECTION_MAGIC = '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[4]/div/div/header/div[2]'

if exists_by_text(wd, "Sign in"):
    print("No auth cookie detected. Please login to Google.")
    wd.close()
    wd.quit()
    chrome_options_gui = Options()
    chrome_options_gui.add_argument('--no-sandbox')
    if DEBUG:
        chrome_options_gui.add_argument("user-data-dir=profile")
    chrome_options_gui.add_argument('--disable-infobars')
    wd = webdriver.Chrome('chromedriver', options=chrome_options_gui)
    wd.get("https://accounts.google.com/signin")
    wait_for_xpath(wd, LOGIN_DETECTION_MAGIC)
    print("Login detected. Saving cookie & restarting connection.")
    pickle.dump(wd.get_cookies(), open("gCookies.pkl", "wb"))
    wd.close()
    wd.quit()
    wd = webdriver.Chrome('chromedriver', options=chrome_options)
while True:
    for colab_url in COLAB_URLS:
        complete = False
        wd.get(colab_url)
        print("Logged in.") # for debugging
        running = False
        wait_for_xpath(wd, TOP_LEVEL_FILE_MENU)
        print('Notebook loaded.')
        sleep(10)

        while not exists_by_text(wd, "Sign in"):
            if exists_by_text(wd, "Runtime disconnected"):
                try:
                    wd.find_element_by_xpath(OK_BUTTON).click()
                except NoSuchElementException:
                    pass
            if exists_by_text2(wd, "Notebook loading error"):
                wd.get(colab_url)
            try:
                wd.find_element_by_xpath(TOP_LEVEL_FILE_MENU)
                if not running:
                    wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.SHIFT + "q")
                    wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.SHIFT + "k")
                    exists_by_xpath(wd, OK_BUTTON, 10)
                    wd.find_element_by_xpath(OK_BUTTON).click()
                    sleep(10)
                    wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.F9)
                    running = True
            except NoSuchElementException:
                pass
            if running:
                try:
                    wd.find_element_by_css_selector('.notebook-content-background').click()
                    #actions = ActionChains(wd)
                    #actions.send_keys(Keys.SPACE).perform()
                    scroll_to_bottom(wd)
                    print("performed scroll")
                except:
                    pass
                for frame in wd.find_elements_by_tag_name('iframe'):
                    wd.switch_to.frame(frame)
                    '''
                    links = browser.find_elements_by_partial_link_text('oauth2/auth')
                    for link in links:
                        new_tab(wd, link.get_attribute("href"), 1)
                        wd.find_element_by_css_selector('li.M8HEDc:nth-child(1)>div:nth-child(1)').click()
                        wd.find_element_by_css_selector('#submit_approve_access>content:nth-child(3)>span:nth-child(1)').click()
                        auth_code = wd.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div/form/content/section/div/content/div/div/div/textarea').text
                    '''
                    for output in wd.find_elements_by_tag_name('pre'):
                        if fork in output.text:
                            running = False
                            complete = True
                            print("Completion string found. Waiting for next cycle.")
                            break
                    wd.switch_to.default_content()
                    if complete:
                        break
                if complete:
                    break
    sleep(timeout)
