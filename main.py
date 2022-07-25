# -*- coding: utf-8 -*-
# https://github.com/mybdye 🌟

import base64
import json
import os
import ssl
import time
from datetime import datetime

import requests
from helium import *
from selenium.webdriver.common.by import By


# EUserv 账号
try:
    EU_USER_ID = os.environ['EU_USER_ID']
except:
    # 本地调试用，在线勿填
    EU_USER_ID = ''

try:
    EU_PASS_WD = os.environ['EU_PASS_WD']
except:
    # 本地调试用，在线勿填
    EU_PASS_WD = ''

# True Captcha 账号 https://apitruecaptcha.org/
try:
    CAPTCHA_USER_ID = os.environ['CAPTCHA_USER_ID']
except:
    # 本地调试用，在线勿填
    CAPTCHA_USER_ID = ''

try:
    CAPTCHA_APIKEY = os.environ['CAPTCHA_APIKEY']
except:
    # 本地调试用，在线勿填
    CAPTCHA_APIKEY = ''

try:
    MAILPARSER = os.environ['MAILPARSER']
except:
    # 本地调试用，在线勿填
    MAILPARSER = ''

# bark push token
try:
    BARK_KEY = os.environ['BARK_KEY']
except:
    # 本地调试用，在线勿填
    BARK_KEY = ''

# tg push token
try:
    TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
except:
    # 本地调试用，在线勿填
    TG_BOT_TOKEN = ''

try:
    TG_USER_ID = os.environ['TG_USER_ID']
except:
    # 本地调试用，在线勿填
    TG_USER_ID = ''

title = 'EUserv Extend'
imgFile = '/imgCAPTCHA.png'
imgScreenShot = '/imgScreenShot.png'
urlEUserv = 'https://support.euserv.com/'
urlMJJ = 'http://mjjzp.cf/'
# 关闭证书验证
ssl._create_default_https_context = ssl._create_unverified_context

# 返回验证码文本
def solve(f):
    with open(f, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    # print(encoded_string)
    url = 'https://api.apitruecaptcha.org/one/gettext'

    data = {
            'userid': CAPTCHA_USER_ID,
            'apikey': CAPTCHA_APIKEY,
            'case': 'mixed',
            'data': str(encoded_string)[2:-1]
            }
    r = requests.post(url=url, json=data)
    j = json.loads(r.text)
    return (j)

# 返回验证码运算结果
def calculate(text):
    if text[1] == 'X' or text[1] == 'x':
        resultCAPTCHA = int(text[0]) * int(text[2])
    elif text[1] == '+':
        resultCAPTCHA = int(text[0]) + int(text[2])
    elif text[1] == '-':
        resultCAPTCHA = int(text[0]) - int(text[2])
    return resultCAPTCHA

# 验证码
def captcha():
    Image('CAPTCHA Image').web_element.screenshot(os.getcwd() + imgFile)
    print('- imgCAPTCHA screenshot finished')
    try:
        text = solve(os.getcwd() + imgFile)['result']
        if len(text) == 3:
            resultCAPTCHA = calculate(text)
            print('text:', resultCAPTCHA)
        else:
            resultCAPTCHA = text
            print('text:', resultCAPTCHA)
        write(resultCAPTCHA, into=S('@captcha_code'))
        time.sleep(3)
        print('- click button [Login]')
        click('Login')
        time.sleep(3)
        switch_to('EUserv')

    except:
        text = solve(os.getcwd() + imgFile)['error']
        print('text:', text)

# 续期
def renew():
    time.sleep(3)
    wait_until(Text('vServer').exists)
    print('- click button [vServer]')
    click(S('#kc2_order_customer_orders_tab_1'))
    time.sleep(3)
    try:
        wait_until(Text('Extend contract').exists)
        print('- click button [Extend contract]')
        click('Extend contract')
        time.sleep(3)
        wait_until(Text('Keep existing contract').exists)
        print('- click button [Extend]')
        click(S('.kc2_customer_contract_details_change_plan_item_action_button'))
        time.sleep(5)
        wait_until(Text('Security check').exists)
        print('- Security check')
        time.sleep(10)
        try:
            pin = get_pin()
        except Exception as e:
            print(e)
            print('- Send new PIN')
            click(S('.btn btn-primary btn-sm'))
            wait_until(Text('Thank you! An email with the PIN was send to').exists)
            time.sleep(10)
            pin = get_pin()
        time.sleep(2)
        print('- fill pin')
        write(pin, into=S('@password'))
        click('Continue')
        wait_until(Text('Contract Extension Confirmation').exists)
        click('Confirm')
        if Text('Thank you! The contract has been extended.').exists():
            push('🎉 Thank you! The contract has been extended.')

    except Exception as e:
        print(e)
        text_list = find_all(S('.kc2_order_extend_contract_term_container'))
        text = [key.web_element.text for key in text_list][0]
        print('status of vps:', text)
        date_delta = date_delta_caculate(text.split(' ')[-1])
        if date_delta > 0:
            print('*** No Need To Renew ***\n %d Days Left!' % date_delta)
            body = text + '\n*** No Need To Renew ***\n' + str(date_delta) + ' Days Left!'
            push(body)

# 日期计算
def date_delta_caculate(date_allow):
    date_allow = datetime.strptime(date_allow, '%Y-%m-%d')
    date_now = time.strftime('%Y-%m-%d')
    date_now = datetime.strptime(date_now, '%Y-%m-%d')

    second_allow = time.mktime(date_allow.timetuple())
    second_now = time.mktime(date_now.timetuple())

    second_delta = int(second_allow) - int(second_now)
    date_delta = int(second_delta / 60 / 60 / 24)
    return date_delta

# 推送
def push(body):
    print('- waiting for push result')
    # bark push
    if BARK_KEY == '':
        print('*** No BARK_KEY ***\nfinish!')
    else:
        barkurl = 'https://api.day.app/' + BARK_KEY
        rq = requests.get(url=f'{barkurl}/{title}/{body}?isArchive=1')
        if rq.status_code == 200:
            print('- bark push Done!\nfinish!')

    # tg push
    if TG_BOT_TOKEN == '' or TG_USER_ID == '':
        print('*** No TG_BOT_TOKEN or TG_USER_ID ***\nfinish!')
    else:
        body = title + '\n\n' + body
        server = 'https://api.telegram.org'
        tgurl = server + '/bot' + TG_BOT_TOKEN + '/sendMessage'
        rq_tg = requests.post(tgurl, data={'chat_id': TG_USER_ID, 'text': body}, headers={
            'Content-Type': 'application/x-www-form-urlencoded'})
        if rq_tg.status_code == 200:
            print('- tg push Done!\nfinish!')
        else:
            print(rq_tg.content.decode('utf-8'))

# 登陆
def login_euserv():
    print('- login_euserv')
    time.sleep(2)
    if Text('Login').exists() is False:
        go_to(urlEUserv)
        login_euserv()
    else:
        if Text('Too many login failures').exists():
            print('*** Too many login failures ***\n'
                  'wait for 5 minutes...')
            time.sleep(300)
            print('- refresh')
            refresh()
        print('- fill user id')
        if EU_USER_ID == '':
            print('*** user id is empty ***')
            kill_browser()
        else:
            write(EU_USER_ID, into=S('@email'))
        print('- fill password')
        if EU_PASS_WD == '':
            print('*** password is empty ***')
            kill_browser()
        else:
            write(EU_PASS_WD, into=S('@password'))

    time.sleep(2)
    print('- click button [Login]')
    click('Login')
    time.sleep(10)
    if Text('Login failed.').exists():
        print('*** Login failed. ***\n'
              'Please check email address/customer ID and password.')
        kill_browser()
    if Image('CAPTCHA Image').exists():
        print('- CAPTCHA Found')
        captcha()
        while Text('The captcha solution is not correct.').exists:
            print('*** The captcha solution is not correct. ***')
            captcha()
            if not Text('The captcha solution is not correct.').exists():
                print('- captcha done')
                break
    if Text('Confirm or change your customer data here.').exists():
        print('- login success, customer data need to be check')
        scroll_down(800)
        print('- click button [Save]')
        time.sleep(1)
        click('Save')
        print('- renew')
        time.sleep(1)
        renew()
    elif Text('To finish the login process enter the PIN that you receive via email.').exists():
        print('*** To finish the login process enter the PIN that you receive via email. ***')
        pin = get_pin()
        time.sleep(2)
        print('- fill pin')
        #write(pin, into=S('@auth'))
        write(pin, into=S('@password'))
        print('- click button [Confirm]')
        time.sleep(1)
        click('Confirm')
        print('- renew')
        time.sleep(1)
        renew()
    elif Text('Hello').exists():
        print('- login success')
        print('- renew')
        time.sleep(1)
        renew()
    else:
        # debug
        screenshot()
        # print('*** re-login ***')
        # login_euserv()

# 返回 PIN
def get_pin():
    print('- get pin')
    response = requests.get(url=MAILPARSER)
    pin = response.json()[0]['pin']
    print('- pin:', pin)
    return pin

# 截图(debug)
def screenshot():  # debug
    driver = get_driver()
    driver.get_screenshot_as_file(os.getcwd() + imgScreenShot)
    print('- screenshot done')
    #driver.tab_new(urlMJJ)
    driver.execute_script('''window.open('http://mjjzp.cf/',"_blank")''')
    driver.switch_to.window(driver.window_handles[1])
    # switch_to('白嫖图床')
    time.sleep(2)
    driver.find_element(By.ID, 'image').send_keys(os.getcwd() + imgScreenShot)
    time.sleep(4)
    click('上传')
    wait_until(Text('完成').exists)
    print('- upload done')
    # textList = find_all(S('#code-url'))
    # result = [key.web_element.text for key in textList][0]
    result = S('#code-url').web_element.text
    print('*** 📷 capture src:', result)
    driver.close()
    # driver.switch_to.window(driver.window_handles[0])

# 程序开始
print('- loading...')

try:
    start_chrome(urlEUserv)
except Exception as e:
    print(e)
    try:
        print('*** Chrome may crashed ,retry ...***')
        kill_browser()
        start_chrome(urlEUserv)
    except Exception as e:
        print(e)
        start_chrome(urlEUserv)

print('- title:', Window().title)
login_euserv()
