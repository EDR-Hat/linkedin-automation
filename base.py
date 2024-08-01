import logging
import selenium.webdriver
import selenium.webdriver.firefox.service


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

firefox_bin = "/snap/firefox/current/usr/lib/firefox/firefox"
firefoxdriver_bin = "/snap/firefox/current/usr/lib/firefox/geckodriver"

options = selenium.webdriver.firefox.options.Options()
options.binary_location = firefox_bin
options.add_argument('--headless')
options.add_argument('--no-sandbox')

service = selenium.webdriver.firefox.service.Service(executable_path=firefoxdriver_bin)

browser = selenium.webdriver.Firefox(service=service, options=options)
browser.get("http://example.com/")
