# requirements 
# https://github.com/mozilla/geckodriver/releases/tag/v0.29.0

import os
import sys
os.environ['DISPLAY']=":1"
notebookurl = sys.argv[1]

# profilePath = "/home/colab/.mozilla/firefox/ac20bfqn.default-release/"

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

options=Options()
# firefox_profile = FirefoxProfile(profilePath)
firefox_profile.set_preference("javascript.enabled", True)
options.profile = firefox_profile

import time
import requests

js = """
fetch("https://api.telegram.org/bot1003648692:AAF1JamzRqKqaNHCW3lK1uqQ6gsrSwZuTr8/sendMessage?&chat_id=628650705&text=RunningVMSetup");
document.querySelector("#cell-yThhgKBpD_dP > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > colab-run-button:nth-child(1)").click()"""
# from selenium.webdriver import Firefox

# driver = Firefox(executable_path='/content/geckodriver',service_log_path="/home/colab/geckodriver.log",options = options)

driver = webdriver.Firefox(options=options)

driver.get(notebookurl)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
element = WebDriverWait(driver,20).until(
    EC.presence_of_element_located((By.ID, "cell-yThhgKBpD_dP"))
)
driver.execute_script(js)
exit()


# assert "Python" in driver.title
# elem = driver.find_element_by_name("q")
# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
# driver.close()