import time

def wait_for_xpath(driver, x):
    while True:
        try:
            driver.find_element_by_xpath(x)
            return True
        except:
            time.sleep(0.1)
            pass


def scroll_to_bottom(driver):
    SCROLL_PAUSE_TIME = 0.5
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def switch_to_tab(driver, tab_index):
    print("Switching to tab " + str(tab_index))
    try:
        driver.switch_to.window(driver.window_handles[tab_index])
    except:
        print("Error switching tabs.")
        return False


def new_tab(driver, url, tab_index):
    print("Opening new tab to " + str(url))
    try:
        driver.execute_script("window.open('" + str(url) + "')")
    except:
        print("Error opening new tab.")
        return False
    switch_to_tab(driver, tab_index)
    return True

def kill_driver(driver):
    driver.close()
    driver.quit()

