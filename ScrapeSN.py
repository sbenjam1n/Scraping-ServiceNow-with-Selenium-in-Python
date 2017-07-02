import json
import pdb
import sh
import requests
import time
from collections import deque
from selenium import webdriver
from selenium.webdriver.support.ui import Select # for <SELECT> HTML form
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

query = webdriver.Firefox(executable_path='/home/user/mech_pr/geckodriver')

#query = webdriver.PhantomJS(executable_path='/home/user/mech_pr/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')

get_login = query.get("https://wgu.service-now.com")

get_query = query.get("https://wgu.service-now.com/nav_to.do?uri=%2Fproblem_list.do%3Fsysparm_query%3DstateANYTHING%255Esys_class_name%253Dproblem%255Esys_created_onRELATIVEGE%2540month%2540ago%25403%26sysparm_first_row%3D1%26sysparm_view%3D")

WGU_owl = """https://pbs.twimg.com/profile_images/628666536295731200/Pn9ghXNM.jpg"""

get_login

query.implicitly_wait(120)

login_username = query.find_element_by_id('login-username')

login_password = query.find_element_by_id('login-password')

login_button = query.find_element_by_class_name('btn')

problemPage = EC.title_contains('Problems | ServiceNow Service Management')

username = "username"
password = "password"

if login_username.is_displayed():
   print "Attempting to login..."
   login_username.send_keys(username)
   login_password.send_keys(password)
   login_button.click()
   #query.get_screenshot_as_file('/home/user/mech_pr/login_screenshot.png')
   #WebDriverWait(query, 120).until(problemPage)
   print "Logged in!"

   PRtable = []

def get_all_row_data(table):
    #PRtable = query.find_elements_by_xpath('//*[@id="problem_table"]/tbody/tr')
    for row in table:
        yield row.text

def get_pr_data(n):
    PRs = []
    i=1
    def get_pr_row(i):
        pr = """//*[@id="problem_table"]/tbody/tr[%s]/td[3]/a""" % i
        pr_description = """//*[@id="problem_table"]/tbody/tr[%s]/td[4]""" % i
        pr_bs = """//*[@id="problem_table"]/tbody/tr[%s]/td[12]/a""" % i
        pr_status = """//*[@id="problem_table"]/tbody/tr[%s]/td[7]""" % i
        pr_dateCreated = """//*[@id="problem_table"]/tbody/tr[%s]/td[11]/div[2]""" % i
        pr_row = query.find_element_by_xpath(pr).text, query.find_element_by_xpath(pr_description).text, query.find_element_by_xpath(pr_bs).text, query.find_element_by_xpath(pr_status).text, query.find_element_by_xpath(pr_dateCreated).get_attribute("innerHTML"), query.find_element_by_xpath(pr).get_attribute('href')
        return pr_row

    while i <= n:
        PRs.append(get_pr_row(i))
        i += 1
    return PRs

empty_message_card = {
  "themeColor": "0078D7",
  "sections": [],
  "potentialAction": []
}

openURI_potentialAction = {
  "@type": "OpenUri",
  "name": "",
  "targets": [{"os": "default", "uri": ""}]
}

#def send_pr_data_message_card(webhook):
def send_pr_data_message_card(n, q):
    try:
    	iframe = query.find_element_by_id('gsft_main')#[0]
    	query.switch_to_frame(iframe)
    	q
    	pr = get_pr_data(n)

    	i = 0
    	def create_pr_section(l):
        	pr_section = {
        	"activityTitle": "",
        	"activitySubtitle": " ",
        	"activityImage": WGU_owl,
        	"activityText": ""
        	 }
        	pr_section['activityTitle'] = """[%s](%s)""" % (pr[l][0], pr[l][5])#PR Name and href
        	pr_section['activityText'] = pr[l][1]#PR Description
        	pr_section['activitySubtitle'] = pr[l][4]#PR dateCreated
        	return pr_section

    	while i < n:
        	empty_message_card['sections'].append(create_pr_section(i))
        	i += 1
    	json_pr_section = json.dumps(empty_message_card, indent=4, sort_keys=False)
    	print json_pr_section
    	#print dictionaryToJson
    	#post = """-H "Content-Type: application/json" -d %s http://localhost""" % json_pr_section
    	#url     = 'http://localhost'
    	#payload = { 'key' : 'val' }
    	#headers = {"Content-Type: application/json"}
    	##res = requests.post(url, json=json_pr_section)
    	#sh.curl(post)
    except:
        pass

send_pr_data_message_card(5, get_query)

def check_new():
   t = time.time()
   while 1:
       if problemPage:
           if time.time()-t>1:
              send_pr_data_message_card(1, get_query_new)
              t = time.time()
              yield
              continue
           else:
              yield
              continue
   else:
       print "Probably logged out."
       query.close()

def check_current():
   t = time.time()
   while 1:
       if problemPage:
           if time.time()-t>5:
              send_pr_data_message_card(5, get_query)
              t = time.time()
              yield
              continue
           else:
              yield
              continue
   else:
       print "Probably logged out."
       query.close()

class QueryScheduler(object):
    _task_queue = deque()
    def _init_(self):
       object.__init__(self)
       self._task_queue = deque()

    def new_task(self, task):
        self._task_queue.append(task)

    def run(self):
        while self._task_queue:
            task = self._task_queue.popleft()
            try:
                next(task)
                self._task_queue.append(task)
            except StopIteration:
                pass

send_pr_data_message_card(5, get_query)
sched = QueryScheduler()
sched.new_task(check_new())
sched.new_task(check_current())
sched.run()
