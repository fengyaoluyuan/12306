from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import logging
from requests import ConnectionError
import random
from lxml import etree

#定义代理池
class ProxyPool(object):

    #构造函数
    def __init__(self, proxy_url):
        self.proxy_url = proxy_url
        self.logger = logging.getLogger(__name__)

    #定义代理的获取方法
    def get_proxy(self,):
        try:
            response = requests.get(self.proxy_url)
            if response.status_code == 200:
                print('obtain proxy success')
                ip = response.text
                return ip
            else:
                print('obtain proxy faild')
                return None
        except ConnectionError:
            print('ConnectionError')
            self.get_proxy()


#利用selenium模拟谷歌浏览器实现自动抢票
class BuyTickets(object):

    #构造函数
    def __init__(self, username, password, fromstation, tostation, train_date, wait_time, random_time, passenger, start_time, seat):
        self.options = webdriver.ChromeOptions()
        # self.proxy = '--proxy-server=http://%s' %proxy
        # self.options.add_argument(self.proxy)
        self.options.add_argument('–disable-images')
        self.options.add_argument("Accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'")
        self.options.add_argument("Accept-Language='zh-CN,zh;q=0.9'")
        self.options.add_argument("Connection='keep-alive'")
        #self.options.add_argument("Cookie='JSESSIONID=484F3FFAAAA561DC029A9ADFD99B7F10; ten_key=4bMeh2aAZBpOv8EUWO8iBqpZgug3/fJB; RAIL_EXPIRATION=1535473053064; RAIL_DEVICEID=AIgbJYbGo9FPzlQrQFlWtH0_Yt_QkhCStaOT0NPpm5tZMkwROnN9KkXPgUxM-32WCXsirn577qSIlYUjX35Vqil4rd8f7GoH6i7nXO7UJ28N7PSu9tSMyY4fjoKaxcktJtvR6IyXiY7A6XqDtkIPxC8eedVKax1L; ten_js_key=4bMeh2aAZBpOv8EUWO8iBqpZgug3%2FfJB; route=495c805987d0f5c8c84b14f60212447d; BIGipServerotn=4090953994.50210.0000; BIGipServerpassport=837288202.50215.0000; current_captcha_type=Z; _jc_save_fromStation=%u6210%u90FD%u4E1C%2CICW; _jc_save_toStation=%u74A7%u5C71%2CFZW; _jc_save_wfdc_flag=dc; _jc_save_toDate=2018-08-26; _jc_save_fromDate=2018-09-04; _jc_save_showIns=true")
        self.options.add_argument("User-Agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'")
        self.browser = webdriver.Chrome(chrome_options=self.options)
        self.login_url = 'https://kyfw.12306.cn/otn/login/init'
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password
        self.fromstation = fromstation
        self.tostation = tostation
        self.train_date = train_date
        self.wait_time = wait_time
        self.random_time = random_time
        self.passenger = passenger
        self.start_time = start_time
        self.seat = seat

    #验证登陆
    def filling(self):
        '''
        自动填写账户和密码，手动验证登陆
        :return: 车票预定按钮selectyuding
        '''
        try:
            print('进入登陆页面')
            self.browser.get(self.login_url)
            print('账户名')
            username = self.wait.until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            print('账户密码')
            password = self.wait.until(
                EC.presence_of_element_located((By.ID, 'password'))
            )
            # loginSub = self.wait.until(
            #     EC.element_to_be_clickable((By.ID, 'loginSub'))
            # )
            print('正在输入账户名')
            username.clear()
            username.send_keys(self.username)
            time.sleep(self.random_time)
            print('正在输入密码')
            password.clear()
            password.send_keys(self.password)
            time.sleep(self.random_time)
            print('请输入验证码……')
            while True:
                #判断是否登陆成功
                if self.landing():
                    selectyuding = self.enter_selectyuding()
                    return selectyuding
        except TimeoutError:
            print('请求超时，准备重连')
            self.filling()

    def landing(self):
        if self.browser.current_url != 'https://kyfw.12306.cn/otn/index/initMy12306':
            print('连接中,继续等待')
            time.sleep(self.wait_time)
        else:
            print('成功登陆')
            return True

    def enter_selectyuding(self):
        print('加载车票预定按钮')
        selectyuding = self.wait.until(
            EC.element_to_be_clickable((By.ID, 'selectYuding'))
        )
        print('车票预定')
        if selectyuding:
            return selectyuding

#选票
    #跳转到选票页面
    #单程、普通票
    #自动填写出发地、目的地、出发时间、点击查询
    #获取车票信息
    #选票
    #点击预定
    def choose_ticket(self, selectyuding):
        '''
        选择车型、出发时间段、出发车站，自动筛选购票
        :return: 车次信息
        '''
        selectyuding.click()
        while True:
            if self.browser.current_url != 'https://kyfw.12306.cn/otn/leftTicket/init':
                print('未能成功进入选票页面，继续等待')
                time.sleep(self.wait_time)
            else:
                print('成功进入选票页面')
                break
        print('起始站')
        fromStationText = self.wait.until(
                EC.presence_of_element_located((By.ID, 'fromStationText'))
            )
        print('终点站')
        toStationText = self.wait.until(
            EC.presence_of_element_located((By.ID, 'toStationText'))
        )
        print('出发时间')
        train_date = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, './/div[@id="date_range"]/ul/li/span[contains(., "{train_date}")]'.format(train_date=self.train_date)))
        )
        print('查询按钮')
        query_ticket = self.wait.until(
            EC.element_to_be_clickable((By.ID, 'query_ticket'))
        )
        print(self.train_date)
        train_date.click()
        time.sleep(self.random_time)
        print(self.fromstation)
        fromStationText.clear()
        fromStationText.send_keys(self.fromstation)
        time.sleep(self.random_time)
        fromStationText.send_keys(Keys.ENTER)
        print(self.tostation)
        toStationText.clear()
        toStationText.send_keys(self.tostation)
        time.sleep(self.random_time)
        toStationText.send_keys(Keys.ENTER)
        time.sleep(self.wait_time)
        try:
            train_info = self.get_train_info(query_ticket)
        except TimeoutError:
            print('请求超时,重新连接')
            self.get_train_info(query_ticket)
        print('车次信息')
        return train_info


    def get_train_info(self, query_ticket):
        '''
        点击查询按钮，获取车次信息
        :param query_ticket:
        :return: 车次信息
        '''
        print('点击查询')
        query_ticket.click()
        print('车次加载')
        train_info = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#query_ticket'))
        )
        if train_info:
            print('加载车次信息')
            return train_info
        else:
            print('获取车次信息失败，重新查询')
            self.get_train_info(query_ticket)

    def choose_train(self, train_info):
        '''
        选择出发时间、出发站点及座位类型，筛选车票
        :param train_info:
        :return: 返回车票信息
        '''
        if train_info:
            # print('选择车型')
            # train_type = self.browser.find_elements_by_xpath('//*[@id="_ul_station_train_code"]/li/input')
            # train_type[0].click()
            # time.sleep(self.wait_time)
            print('选择出发时间段')
            train_time = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, './/select[@id="cc_start_time"]/option[contains(., "{start_time}")]'.format(start_time=self.start_time)))
            )
            train_time.click()
            time.sleep(self.wait_time)
            print('选择出发车站')
            train_station = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="cc_from_station_{fromstation}_check"]'.format(fromstation=self.fromstation)))
            )
            train_station.click()
            time.sleep(self.wait_time)
            print('选择座位')
            train_seats = self.browser.find_elements_by_xpath('//*[@id="queryLeftTable"]/tr/td[contains(., "有") and contains(@id, "{seat}")]'.format(seat=self.seat))
            print(len(train_seats))
            if len(train_seats):
                print(train_seats[0])
                train_seats[0].click()
                time.sleep(self.wait_time)
                print('点击预定')
                book_button = train_seats[0].find_element_by_xpath('../td[last()]')
                print(book_button)
                if book_button:
                    book_button.click()
                    while True:
                        print('跳转中……')
                        time.sleep(self.wait_time)
                        if self.browser.current_url == 'https://kyfw.12306.cn/otn/confirmPassenger/initDc':
                            print('跳转成功，进入乘客信息页面')
                            return True
            else:
                print('目前无票')
                return None
#买票
    #选择乘客
        #搜索
        #勾选
        #确认
    #提交订单
        #选择位置
        #点击确定
    def buy_tickets(self):
        '''
        填写乘客信息，提交订单
        :return:
        '''
        print('乘客')
        passenger_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'quickQueryPassenger_id'))
            )
        passenger_input.clear()
        print(self.passenger)
        passenger_input.send_keys(self.passenger)
        time.sleep(self.wait_time)
        print('选中乘客')
        passenger_button = self.browser.find_element_by_id('normalPassenger_0')
        passenger_button.click()
        time.sleep(self.wait_time)
        if self.wait.until(
            EC.text_to_be_present_in_element_value((By.ID, 'passenger_name_1'), self.passenger)
        ):
            print('确认乘客信息')
            submit_button = self.browser.find_element_by_id('submitOrder_id')
            submit_button.click()
            # print('选择座位')
            # finally_seat = self.wait.until(
            #     EC.element_to_be_clickable((By.XPATH, '//*[@id="1F"]'))
            # )
            # finally_seat.click()
            # time.sleep(self.wait_time)
            print('确认订单')
            confirm_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'qr_submit_id'))
            )
            print('点击提交', confirm_button)
            confirm_button.click()
            while True:
                if self.browser.current_url == 'https://kyfw.12306.cn/otn/confirmPassenger/initDc':
                    print('等待中')
                    time.sleep(self.wait_time)
                else:
                    print('预定成功')
                    break

#通知
    #利用邮件通知购票人
    def send_email(self):
        msg_from = 'fromuser@qq.com'  # 发送方邮箱
        passwd = ''  # 填入发送方邮箱的授权码
        msg_to = 'touer@qq.com'  # 收件人邮箱
        mail_host = "smtp.qq.com"  # 发送人邮件的stmp服务器
        port = 465  # 端口号
        # 邮件
        subject = "12306"  # 主题
        content = "订票成功"  # 正文
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = msg_from
        msg['To'] = msg_to
        # 创建连接对象并连接到服务器
        s = smtplib.SMTP_SSL(mail_host, port)  # 邮件服务器及端口号，SMTP_SSL默认使用465端口号，端口号可省略
        # 登录服务器
        s.login(msg_from, passwd)
        try:
            s.sendmail(msg_from, msg_to, msg.as_string())
            print("发送成功")
            return True
        except s.SMTPException as e:
            print(e)
            print("发送失败")
        finally:
            s.quit()

def main():
    # proxy_url = 'http://localhost:5555/random'
    # proxypool = ProxyPool(proxy_url)
    # PROXY = proxypool.get_proxy()
    USERNAME = ''
    PASSWORD = ''
    FROMSTATION = '成都东'
    TOSTATION = '重庆北'
    TRAIN_DATE = '09-04'
    # TRAIN_DATE = './/div[@id="date_range"]/ul/li/span[contains(., "{train_date}")]'.format(train_date=self.train_date)
    WAIT_TIME = 1
    RANDOM_TIME = random.randint(3, 5)
    PASSENGER = ''
    #时间段
    START_TIME = '12:00--18:00'
    #座位类型
    SEAT = 'ZE_'
    tickets = BuyTickets(USERNAME, PASSWORD, FROMSTATION, TOSTATION, TRAIN_DATE, WAIT_TIME, RANDOM_TIME, PASSENGER, START_TIME, SEAT)
    selectyuding = tickets.filling()
    while True:
        train_info = tickets.choose_ticket(selectyuding)
        train = tickets.choose_train(train_info)
        if train:
            tickets.buy_tickets()
            while True:
                result = tickets.send_email()
                if result:
                    break
            break
        else:
            time.sleep(10 * 60)


if __name__ == '__main__':
    main()
