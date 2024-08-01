# Why Automate Linkedin?
Getting a larger network is one way to potentially get into an industry you want. Knowing people through the business social media can be important, and as a job seeker or as a hiring manager is part of getting a more robust network of people.
Also clicking the buttons and searching people up is tedious and your time could be better spent messaging your existing contacts.

The idea here is to use LinkedIn's existing recommendation algorithms to send connection requests to users who are already likely to accept your connections. My script does this by leveraging your existing connections and send out some, but not too many requests.

To get started you'll want to run ``connection_saver.py``, it will pause and ask to to log in and will save your cookies. Then you can run ``crawl_connections.py``. You can alternateively run these scripts to update the connections list once you get to the end of the last saved list.

It does not currently use the seen profiles that it was unable to click on yet, but that is something I plan on making in the future. So if you only have say 5 or so connections, this script won't do very much for you at the start. Of course you could easily change that.

# setting these on a schedule

I set up a home server that runs these on a schedule on Ubuntu server. I have the cronjob of just crawl_connections.py set up like this to run early every weekday:
``python3 /path/to/crawl_connections.py /path/to/browser/cookies 50 --headless --no-sandbox 2>&1 | logger -t 'linkedin'``
if you don't know, that stuff at the end pipes standard error in and the logger command puts the output piped in into ``/var/log/syslog`` so that any error messages get stored.

You might want to run the connections updater on a schedule or you could leave it to be done manually.

# Avoiding being flagged as a Bot
One thing that can often happen when using Selenium is that your script will act in superhuman or obvious ways and can easily be detected as a bot. The first thing this script does to protect against auto flagging is to utilize cookies so that you look more like a regular user and we get to skip the part where we navigate through the login page. The other strategy is making the script wait at random intervals. I also advise to not use this script too much


## making Selenium work in Ubuntu
In newer installations of Ubuntu (at least 24.0+), the Firefox package has moved away from deb packages and is new avalible on snap. For me at least these did not work straight out of the box. A long term release version of Firefox is apparently availble through apt, and it is still currently possilbe to make that install over the snap version, but eventually Mozilla will pull the plug on the .deb version.

Try running the following most basic Python script:

```
from selenium import webdriver

browser = webdriver.Firefox()
browser.get("http://www.example.com")
```

If it doesn't fail, then you are all good and do not have to edit the linkedin.py script!

I eventually found a solution that jn-chrn posted in the github issue tracker (https://github.com/SeleniumHQ/selenium/issues/13252#issuecomment-1845021270)[https://github.com/SeleniumHQ/selenium/issues/13252#issuecomment-1845021270] and got it to work.

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
You'll want to edit the function ``setup_new_browser`` function in linkedin.py

