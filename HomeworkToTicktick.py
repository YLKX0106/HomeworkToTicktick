import configparser
from datetime import datetime
import requests
from fake_useragent import UserAgent
from lxml import etree

import ticktickCreate

ua = UserAgent()
config = configparser.ConfigParser()
config.read("/root/python/chaoxing/config.ini")

global currClass
currClass = 0


def setConf(section: str, option: str, value: str):
    '''在指定section中添加变量和变量值'''
    try:
        config.add_section(section)
    except configparser.DuplicateSectionError:
        sss = ("Section already exists")
        # print(sss)
    config.set(section, option, value)
    config.write(open("/root/python/chaoxing/config.ini", "w"))


def login(username, password):
    url = "https://passport2-api.chaoxing.com/v11/loginregister?code=" + password + "&cx_xxt_passport=json&uname=" + username + "&loginType=1&roleSelect=true"
    headers = {
        'User-Agent': ua.chrome,
        'Referer': r'http://passport2.chaoxing.com/login?fid=&newversion=true&refer=http%3A%2F%2Fi.chaoxing.com'
    }
    global session
    session = requests.session()
    a = session.post(url, headers=headers)
    if a.json()['mes'] == '验证通过':
        print('登陆成功')
    else:
        print(a.json()['mes'])
        exit()


def getClass():
    url = 'http://mooc1-2.chaoxing.com/visit/courses'
    headers = {
        'User-Agent': ua.chrome,
        'Referer': r'http://i.chaoxing.com/'
    }
    res = session.get(url, headers=headers)

    if res.status_code == 200:
        class_HTML = etree.HTML(res.text)
        i = 0
        global course_dict
        course_dict = {}

        for class_item in class_HTML.xpath("/html/body/div/div[2]/div[3]/ul/li[@class='courseItem curFile']"):
            try:
                class_item_name = class_item.xpath("./div[2]/h3/a/@title")[0]
                if (class_item.xpath("./div[2]/p/@style")[0] != 'color:#0099ff'):
                    i += 1
                    course_dict[i] = [class_item_name, "https://mooc1-1.chaoxing.com{}".format(
                        class_item.xpath("./div[1]/a[1]/@href")[0]) + '&ismooc2=1']
            except:
                pass
    else:
        print("error:课程处理失败")


def getWork(url: str, name: str):
    global zy_onid
    headers = {
        'User-Agent': ua.chrome,
        'Referer': 'http://mooc1-1.chaoxing.com/'
    }
    course_url = session.get(url, headers=headers, stream=True).url
    course_data = session.get(course_url, headers=headers)
    # 获取 work enc
    course_html = etree.HTML(course_data.text)
    enc = (course_html.xpath(
        "//*[@id='workEnc']/@value")[0])
    # 获取 work url
    list_url = course_url.replace('https://mooc2-ans.chaoxing.com/mycourse/stu?',
                                  'https://mooc1.chaoxing.com/mooc2/work/list?').replace('courseid',
                                                                                         'courseId').replace('clazzid',
                                                                                                             'classId')
    list_url = list_url.split("enc=")[0] + 'enc=' + enc
    work_data = session.get(list_url, headers=headers)
    work_html = etree.HTML(work_data.text)
    workDetail = work_html.xpath('//p[contains(text(),\'未交\')]')
    # 检测是否有作业未完成
    if workDetail:
        for i in workDetail:
            zy_url = i.xpath('./../../@data')[0]
            zy_res = session.get(url=zy_url, headers=headers)
            zy_html = etree.HTML(zy_res.text)
            # 作业ID
            zy_title = zy_html.xpath('//h2[@class=\'mark_title\']/text()')[0]  # 作业标题
            zy_time_s = zy_html.xpath('//div[@class=\'infoHead\']/p/em[1]//text()')[0]  # 开始时间
            zy_time_e = zy_html.xpath('//div[@class=\'infoHead\']/p/em[2]//text()')  # 结束时间
            if not zy_time_e:
                time_e = '0'
            else:
                time_e = zy_time_e[0]
            # 标识为 课程名+作业标题+开始时间+结束时间
            zy_id = name + zy_title + zy_time_s + time_e
            if zy_id in zy_onid:
                continue
            # 作业内容
            con = []
            zy_div = zy_html.xpath('//div[contains(@class,"mark_table")]/descendant::div[@class="whiteDiv"]')
            for z_div in zy_div:
                z_title = z_div.xpath("./h2[@class='type_tit']/text()")
                con += z_title
                z_con = z_div.xpath('./div/h3[contains(@class,"mark_name")]')
                for xx in z_con:
                    con.append(''.join(xx.xpath("./text()")))
            con.append("\n#### 作业连接:")
            con.append(zy_url)

            title = '{}-{}'.format(zy_title, name)
            # 时间处理
            if not zy_time_e:
                end_time = datetime(2022, 7, 30, 12, 00, 00)
            else:
                zy_time_str = zy_time_e[0]
                end_time = datetime(2022, int(zy_time_str[0:2]), int(zy_time_str[3:5]), int(zy_time_str[6:8]),
                                    int(zy_time_str[9:11]))

            ticktickCreate.send(title, '\n'.join(con), end_time)
            zy_onid.append(zy_id)


def get():
    work_id = ticktickCreate.get("作业ID")
    return work_id['content'].splitlines()


def id_update(b):
    ticktickCreate.update(title="作业ID", content='\n'.join(b))


if __name__ == '__main__':
    # 账号
    username = ''
    # 密码
    password = ''
    zy_onid = get()

    login(username, password)
    getClass()

    try:
        for currClass in course_dict:
            getWork(course_dict[currClass][1], course_dict[currClass][0])
    except:
        print(currClass, "错误")

    id_update(zy_onid)
