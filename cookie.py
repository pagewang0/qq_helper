# -*- coding: UTF-8 -*-
"""
datetime: 2017/11/16
by: pagewang
describe: qq auto login print cookie
"""
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import urllib2
import cv2
import numpy as np

driver = webdriver.Firefox()

url1 = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?appid=501038301&target=self&s_url=http://im.qq.com/loginSuccess.html'
url2 = 'http://im.qq.com/loginSuccess.html'

users = None
user = None
username = None
password = None

with open('qq帐号密码.txt') as f:
    users = f.read()

users = users.strip().replace('\r\n', '\n').split('\n')

for i in range(len(users)):
    user = users[i].split('----')
    username = user[0]
    password = user[1]
    users[i] = {'username': username, 'password': password}


def get_image_position():
    image1 = driver.find_element_by_id('slideBkg').get_attribute('src')
    image2 = driver.find_element_by_id('slideBlock').get_attribute('src')

    f = open('slide_bkg.png', 'w')
    f.write(urllib2.urlopen(image1).read())
    f.close()

    f = open('slide_block.png', 'w')
    f.write(urllib2.urlopen(image2).read())
    f.close()

    block = cv2.imread('slide_block.png', 0)
    template = cv2.imread('slide_bkg.png', 0)

    cv2.imwrite('template.jpg', template)
    cv2.imwrite('block.jpg', block)
    block = cv2.imread('block.jpg')
    block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    block = abs(255 - block)
    cv2.imwrite('block.jpg', block)

    block = cv2.imread('block.jpg')
    template = cv2.imread('template.jpg')

    result = cv2.matchTemplate(block,template,cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(),result.shape)
#    print x, y

    element = driver.find_element_by_id('tcaptcha_drag_thumb')

    ActionChains(driver).click_and_hold(on_element=element).perform()
    ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=int(y * 0.4 + 18), yoffset=0).perform()
    sleep(1)
    ActionChains(driver).release(on_element=element).perform()
    sleep(3)


def parse_cookie(cookies):
#    print cookies
    skey = None
    uin = None

    for cookie in cookies:
#        print cookie
        if cookie['name'] == 'skey':
            skey = cookie['value']
        if cookie['name'] == 'uin':
            uin = cookie['value']

    print 'skey=' + skey + '; uin=' + uin + ';'


def login(user):
    driver.get(url1)

    driver.find_element_by_id('switcher_plogin').click()
    u = driver.find_element_by_id('u')
    p = driver.find_element_by_id('p')

    if len(u.get_attribute('value')):
        u.clear()

    for s in user['username']:
        u.send_keys(s)

    for s in user['password']:
        p.send_keys(s)

    driver.find_element_by_id('login_button').click()
    driver.find_element_by_id('login_button').click()
    sleep(0.8)

    if driver.current_url == url2:
        parse_cookie(driver.get_cookies())
    else:
        while True:
            if driver.current_url == url2:
                parse_cookie(driver.get_cookies())
                return
#            print driver.find_element_by_id('err_m').text
#            print  driver.find_element_by_id('tcaptcha_drag_thumb')
            if driver.find_elements_by_css_selector('#err_m') and driver.find_element_by_id('err_m').text.encode('utf-8') == '你输入的帐号或密码不正确，请重新输入。':
                print user['username'] + ' 被告知账号或密码不正确'
                return

            if driver.find_elements_by_css_selector('#newVcodeArea'):
                driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))

            if driver.find_elements_by_css_selector('#slideBkg'):
                get_image_position()
                driver.switch_to_default_content()

            sleep(1)


for i in range(len(users)):
    login(users[i])

print 'cookie 跑完啦'
driver.close()
