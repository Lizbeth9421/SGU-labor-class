import random
import pytz
import requests
import json
import logging
from datetime import datetime
from dateutil import parser
import time

# 设置日志级别
file_handler = logging.FileHandler('main.log', mode='a+', encoding='utf-8')
logging.basicConfig(
    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=logging.DEBUG, handlers={
        file_handler})

# 最新的劳动课时间
gl_lastTime = datetime.fromtimestamp(int(time.time()))
logging.info(gl_lastTime)
logging.info("运行脚本")
token = ''
# 请求头
header = {
    'Connection': 'keep-alive',
    "Accept": "application/json,text/plain,*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,ko;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Content-Length": "0",
    # 下面内容自行补充
    "Host": "",
    "Origin": "",
    "Referer": "",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
}
# 用户账号密码(自行补充)
userInfos = [
    {"userNo": "", "pwd": ""}
]


def auth():
    # 登陆地址
    target_url = ''
    response = requests.get(target_url, params=random.choice(userInfos), headers=header)
    jsonText = json.loads(response.text).get('data')
    global token
    token = jsonText.get('token')
    logging.info("身份认证成功")


def initData():
    try:
        global token
        # 获取数据的url
        target_url = ''
        headerForInitData = {'Connection': 'keep-alive',
                             "Accept": "application/json,text/plain,*/*",
                             "Accept-Encoding": "gzip, deflate",
                             "Accept-Language": "zh-CN,zh;q=0.9,ko;q=0.8,en;q=0.7",
                             "Cache-Control": "no-cache",
                             "Content-Length": "0",
                             # 下面内容自行补充
                             "Host": "",
                             "Origin": "",
                             "Referer": "",
                             "Pragma": "no-cache",
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
                             "token": token
                             }
        response = requests.get(target_url, headers=headerForInitData)
        jsonText = json.loads(response.text).get('data')
        if jsonText == '':
            auth()
            return []
        msgCollection = []
        for item in jsonText:
            # 标题
            title = item.get('ktzt')
            # 老师
            teacher = item.get('skjs')
            # 总人数
            nums = item.get('pkrs')
            # 可报名人数
            remainNum = item.get('bmsyrs')
            # 地点
            location = item.get('ldkskdz')
            # 报名开始时间
            Astart = item.get('ldkxkkssj')
            # 报名结束时间
            Aend = item.get('ldkxkjssj')
            # 签到开始时间
            Qstart = item.get('ldksksj')
            # 签到结束时间
            Qend = item.get('ldkxksj')
            # 是否可以报名 0可以报 1不可用
            canSignUp = item.get('iskx')
            # 唯一标识
            uniqueFlag = item.get('jx0404id')
            global gl_lastTime
            if parser.parse(Aend) > gl_lastTime and canSignUp == "0" and int(remainNum) > 0:
                # 更新最新时间
                gl_lastTime = parser.parse(Astart)
                msgCollection.append({
                    "title": title,
                    "remainNum": remainNum,
                    "teacher": teacher,
                    "nums": nums,
                    "location": location,
                    "Astart": Astart,
                    "Aend": Aend,
                    "Qstart": Qstart,
                    "Qend": Qend,
                    "uniqueFlag": uniqueFlag
                })
        return msgCollection
    except Exception as e:
        print(e)
        logging.error("token失效")


# 构造推送的数据
def initMessage(msgCollection):
    if len(msgCollection) == 0:
        return []

    messages = []

    for item in msgCollection:
        # 标题
        title = item.get('title')
        # 老师
        teacher = item.get('teacher')
        # 总人数
        nums = item.get('nums')
        # 可报名人数
        remainNum = item.get('remainNum')
        # 地点
        location = item.get('location')
        # 报名开始时间
        Astart = item.get('Astart')
        # 报名结束时间
        Aend = item.get('Aend')
        # 签到开始时间
        Qstart = item.get('Qstart')
        # 签到结束时间
        Qend = item.get('Qend')
        # 唯一标志
        uniqueFlag = item.get('uniqueFlag')

        # 推送标题
        msgTitle = title + " 可报名人数： " + remainNum

        # 推送内容
        # msgContent = "授课老师：" + teacher + "\n" + "总人数：" + nums + "\n" \
        #              + "地点：" + location + "\n" + "报名时间:" + Astart + "-" + Aend + "\n" \
        #              + "签到时间：" + Qstart + "-" + Qend
        msgContent = "授课老师:{}\n总人数:{}\n地点:{}\n报名时间:{}-{}\n签到时间:{}-{}\n课程号={}".format(teacher, nums, location, Astart,
                                                                                     Aend,
                                                                                     Qstart, Qend, uniqueFlag)
        messages.append({"msgTitle": msgTitle, "msgContent": msgContent})
    return messages


# 去除重复
def removeRepeat(data):
    try:
        f = open("data.txt", 'a+')
        # 设置光标到最开始
        f.seek(0)
        # 已有的元素
        exit = []
        for line in f.readlines():
            line = line.strip()
            exit.append(line)
        # 剔除已经存在的元素
        for exit_item in exit:
            for data_item in data:
                if exit_item == data_item.get("uniqueFlag"):
                    data.remove(data_item)
        # 此时data全是新的元素，需要添加到文件中
        for add_item in data:
            f.write(add_item.get("uniqueFlag") + "\n")
        f.close()
        return data
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # 息知 发布订阅模式url（自行补充）
    urls = [""]
    auth()
    # 爬取数据
    data = initData()
    # 去除重复
    noRepeatData = removeRepeat(data)
    # 构建发送的消息
    messages = initMessage(noRepeatData)
    if len(messages) > 0:
        for url in urls:
            for message in messages:
                # requests.post(url, params={'title': message.get("msgTitle"), "content": message.get("msgContent")})
                time.sleep(1)
        logging.info("发送成功")
    else:
        tz = pytz.timezone('Asia/Shanghai')  # 东八区
        t = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        logging.info("暂无劳动课")
    time.sleep(2)
