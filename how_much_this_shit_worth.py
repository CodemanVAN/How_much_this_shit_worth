# -*- coding: utf-8-*-
import requests
import base64
from urllib import parse
import json
import re
from PyQt5 import QtWidgets
import pyttsx3
import sys
import speech_recognition as sr
from aip import AipSpeech
import ui
import datetime
engine = pyttsx3.init()
keyword='多少钱'
def search(item_keywords):
    url = f'https://tarkov-market.com/api/items?lang=cn&search={item_keywords}&tag=&sort=change24&sort_direction=desc&trader=&skip=0&limit=20'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://tarkov-market.com/cn/',
        'sec-ch-ua': '"Microsoft Edge";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30'
    }
    resp = requests.get(url, headers=headers).json()
    if resp['result'] == 'ok':
        res = decode(resp['items'])
        return res
    else:
        print('error:', resp)
def decode(string):
    decode_string = base64.b64decode(string)
    decode_string = parse.unquote(decode_string)
    return decode_string
def show(res):
    name_reg = re.compile('"cnName":"(.*?)","cnShortName":')
    price_reg=re.compile('"avgDayPrice":(.*?),"avgWeekPrice"')
    price_trader_reg = re.compile('"traderPriceRub":(.*?),')

    name=re.findall(name_reg,res)#中文名
    price_trader=re.findall(price_trader_reg,res)#卖给商人的价格
    price=re.findall(price_reg,res)#跳蚤日均价
    for i in range(len(name)):
        details=f'查询到{name[i]},今日跳蚤价格为{price[i]},卖给商人价格为{price_trader[i]}'  
        engine.say(details)  
        engine.runAndWait()
    if len(name)==0:
        engine.say("好像没有这东西")
        engine.runAndWait()
def lisent(aip_speech):
    r = sr.Recognizer()
    m = sr.Microphone(sample_rate=16000)
    engine.say('自适应环境阈值中，阈值为{}'.format(r.energy_threshold))
    engine.runAndWait()
    while True:
        with m as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        data=audio.get_wav_data()
        ret = aip_speech.asr(data, 'wav', 16000, {'dev_pid': 1536, })
        if ret and ret['err_no'] == 0:
            result = ret['result'][0]
            with open(str(datetime.datetime.now().strftime('%Y-%m-%d'))+'_log.txt','a',encoding='utf-8') as f:
                f.write(str(datetime.datetime.now())+' : '+result)
            if keyword in result:
                search_res=search(result[:len(keyword)])
                show(search_res)
def my_authorize():
    try :
        BAIDU_APP_ID = main_wd.lineEdit.text()
        BAIDU_API_KEY = main_wd.lineEdit_2.text()
        BAIDU_SECRET_KEY = main_wd.lineEdit_3.text()
        author= main_wd.lineEdit_4.text()
        if author !='https://space.bilibili.com/36333545':
            engine.say('你改我推广,我不给你用了')
            engine.runAndWait()
            return
        aip_speech = AipSpeech(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)
        res=aip_speech._auth()
        if 'error' in res:
            engine.say('对不起，你输入的信息不对，请确认是否复制粘贴正确了')
            engine.runAndWait()
        else:
            with open('user_data.txt','w') as f:
                f.writelines(BAIDU_APP_ID+'\n')
                f.writelines(BAIDU_API_KEY+'\n')
                f.writelines(BAIDU_SECRET_KEY+'\n')
            engine.say('验证成功！正在启动')
            engine.runAndWait()
            lisent(aip_speech)
    except Exception:
        engine.say("出现未知错误，请及时联系作者，我先润了")
        engine.runAndWait()
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    main_wd=ui.Ui_main_wd()
    main_wd.setupUi(MainWindow)
    main_wd.pushButton.clicked.connect(my_authorize)
    MainWindow.show()
    sys.exit(app.exec_())