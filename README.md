# linkedinAutomation
Automate linkedin connection requests with selenium

The idea is to search key terms, specific business urls, or just go through your network. Then it will send out templated messages, that are at least somewhat tailored to the person using information on their profile if possible.

There are some files that you will run in a specific order to get started.

## making sure Selenium works
In newer installations of Ubuntu (at least 24.0+), the Firefox package has moved away from deb packages and is new avalible on snap. A long term release version of Firefox is apparently availble through apt, and it is still currently possilbe to make that install over the snap version, but eventually Mozilla will pull the plug on that.

Try running the following most basic python script:

```
from selenium import webdriver

browser = webdriver.Firefox()
browser.get("http://www.example.com")
```

It will most likely fail to find the webdriver or for other reasons not function.

I finally found a solution that jn-chrn posted in the github issue tracker (https://github.com/SeleniumHQ/selenium/issues/13252#issuecomment-1845021270)[https://github.com/SeleniumHQ/selenium/issues/13252#issuecomment-1845021270] and got it to work!

His example script is reproduced below
```
import logging
import selenium.webdriver
import selenium.webdriver.firefox.service


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

firefox_bin = "/snap/firefox/current/usr/lib/firefox/firefox"
firefoxdriver_bin = "/snap/firefox/current/usr/lib/firefox/geckodriver"

options = selenium.webdriver.firefox.options.Options()
options.add_argument('--headless')
options.binary_location = firefox_bin

service = selenium.webdriver.firefox.service.Service(executable_path=firefoxdriver_bin)

browser = selenium.webdriver.Firefox(service=service, options=options)
```

his example includes logging and other options turned on so that the person running this could provide more information in case this didn't function. A paired down most basic script would be:
```
import selenium.webdriver
import selenium.webdriver.firefox.service


firefox_bin = "/snap/firefox/current/usr/lib/firefox/firefox"
firefoxdriver_bin = "/snap/firefox/current/usr/lib/firefox/geckodriver"

options = selenium.webdriver.firefox.options.Options()
#options.add_argument('--headless')  #headless comment toggle
options.binary_location = firefox_bin

service = selenium.webdriver.firefox.service.Service(executable_path=firefoxdriver_bin)

browser = selenium.webdriver.Firefox(service=service, options=options)
```

# Avoiding being flagged as a Bot
One thing that can often happen when using Selenium is that your script will act in superhuman or obvious ways and can easily be detected as a bot. The first thing this script does to protect against this is to utilize cookies so that you look more like a regular user and we get to skip the part where we navigate through the login page.

One other strategy is making the script wait at random intervals.

