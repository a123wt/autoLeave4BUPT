# coding=utf-8

from urllib import parse
import requests
import datetime
import re
import yaml
import os

import smtplib
from email.mime.text import MIMEText
from email.header import Header

import time
import random


class leave():
    loginInfo={
        'userid',
        'userpass'
    }
    form_main={
        'phone':'',
        'destination':'',
        'reason':'',
        'school':''
    }
    form_teacher={
        'uid':0,
        'name':'',
        'number':''
    }
    form_tutor={
        'uid':0,
        'name':'',
        'number':''
    }
    form_time={
        'date':'',
        'begin':'',
        'end':''
    }
    form_college=''
    form_name=''
    form_school=''
    form_status=''

    mail={
        'mail_host':'',
        'mail_user':'',
        'mail_pass':'',
        'sender':'',
        'receivers':['']
    }
    conf={
        'start_day':1,
        'days_num':1
    }
    session = requests.Session()
    FormData=''


    def __init__(self):
        self.conf['start_day']=1
        self.conf['days_num']=1

    def __init__(self,start,num):
        self.conf['start_day']=start
        self.conf['days_num']=num
    
    def getTime(self,start):
        theday = datetime.datetime.now() + datetime.timedelta(days=start)
        date = theday.replace(
            hour=0, minute=0, second=0,
            microsecond=0
        ).isoformat(timespec="microseconds")[:-7] + "+08:00"

        beginTime = theday.replace(
            hour=7, minute=0, second=0, microsecond=0
        ).astimezone(
            tz=datetime.timezone.utc
        ).isoformat(timespec="microseconds").replace("000+00:00", "Z")

        endTime = theday.replace(
            hour=23, minute=30, second=0, microsecond=0
        ).astimezone(
            tz=datetime.timezone.utc
        ).isoformat(timespec="microseconds").replace("000+00:00", "Z")

        self.form_time={
            'date':date,
            'begin':beginTime,
            'end':endTime
        }
        return 0
        
    def readFile(self):
        with open(os.path.join(os.path.dirname(__file__), "users.txt"),'rb') as f:
            confs = yaml.load_all(f, Loader=yaml.FullLoader)
            for c in confs:
                self.form_name=c['username']
                self.loginInfo={
                    'userid':c['userid'],
                    'userpass':c['userpass']
                }
                self.form_main={
                    'phone':c['phone'],
                    'destination':c['destination'],
                    'reason':c['reason'],
                    'school':c['school'],
                }
                self.form_teacher={
                    'uid':c['teacher_uid'],
                    'name':c['teacher_name'],
                    'number':c['teacher_number']
                }
                self.form_tutor={
                    'uid':c['tutor_uid'],
                    'name':c['tutor_name'],
                    'number':c['tutor_number']
                }

                self.mail={
                    'mail_host':c['mail_host'],
                    'mail_user':c['mail_user'],
                    'mail_pass':c['mail_pass'],
                    'sender':c['sender'],
                    'receivers':c['receivers']
                }
        return 0

    def getCollegeAndStatus(self):
        resp = self.session.get("https://service.bupt.edu.cn/site/user/get-name")

        self.form_status=resp.json()["d"]["identity_id"]
        self.form_college=resp.json()["d"]["college"]
        return 0

    def getSchool(self):
        schools = {
            "沙河": {"name": "沙河校区", "value": "1", "default": 0, "imgdata": ""},
            "西土城": {"name": "西土城校区", "value": "2", "default": 0, "imgdata": ""},
        }

        self.form_school=schools[self.form_main['school']]
        return 0

    def getUid(self):
        # 由于未知原因，需要先执行self.session.get("https://service.bupt.edu.cn/site/user/get-name")，才能进行教师信息查询

        postdata={
            "param": '{"keyword":"'+self.form_teacher['number']+'","search_field":["name","number"],"depart_id":[],"job_id":[],"tag_id":[200076,195971,195969],"uids":[],"relation":[]}',
            "agent_uid":"", 
            "starter_depart_id": 181787,
            "test_uid": 0
        }

        resp = self.session.post(
        "https://service.bupt.edu.cn/site/user/form-search-user",
        data=postdata,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",    # 只要有这个就能查，其他的不重要
            # "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38",
            # "refer": "https://service.bupt.edu.cn/v2/matter/start?id=578",
            # "x-requested-with": "XMLHttpRequest",
            # "origin": "https://service.bupt.edu.cn",
            # "accept": "application/json, text/plain, */*",+
        })
        self.form_teacher['uid']=resp.json()["d"]["data"][0]["id"]

        postdata={
            "param": '{"keyword":"'+self.form_tutor['number']+'","search_field":["name","number"],"depart_id":[],"job_id":[],"tag_id":[200076,195971,195969],"uids":[],"relation":[]}',
            "agent_uid":"", 
            "starter_depart_id": 181787,
            "test_uid": 0
        }

        resp = self.session.post(
        "https://service.bupt.edu.cn/site/user/form-search-user",
        data=postdata,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",    # 只要有这个就能查，其他的不重要
            # "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38",
            # "refer": "https://service.bupt.edu.cn/v2/matter/start?id=578",
            # "x-requested-with": "XMLHttpRequest",
            # "origin": "https://service.bupt.edu.cn",
            # "accept": "application/json, text/plain, */*",+
        })
        self.form_tutor['uid']=resp.json()["d"]["data"][0]["id"]

        return 0

    def login(self):
        # login and get name.

        self.session.cookies.clear()
        resp = self.session.get("https://auth.bupt.edu.cn/authserver/login")
        match_execution = re.findall(
            r'<input name="execution" value="(.*)"/><input name="_eventId" value="submit"/>', resp.text)
        if len(match_execution)==0:
            print("CSRF错误")
            print("登录失败")
            return -1
        



        resp=self.session.post(
            "https://auth.bupt.edu.cn/authserver/login",
            data={
                "username": self.loginInfo['userid'],
                "password": self.loginInfo['userpass'],
                "submit": "登录",
                "type": "username_password",
                "execution": match_execution, 
                "_eventId": "submit",
                "rmShown": 1,
            })
        if resp.text.find("<!DOCTYPE html><html lang=en><head><meta charset=utf-8>")>=0 :
            print("登录成功")
            return 0
        print("登录失败")
        return -1



    def complete_FormData(self):
        self.FormData = {
            "data": {
                "app_id": "578",
                "node_id": "",
                "form_data": {
                    "1716": {
                        "Alert_67": "",
                        # "Count_74": {"type": 0, "value": 1},  # unused
                        # "Valudate_66": "",  # unused
                        "User_5": self.form_name,
                        "User_7": self.loginInfo['userid'],
                        "User_9": self.form_college,
                        "User_11": self.form_main['phone'],
                        "Input_28": self.form_main['destination'],
                        "User_75": self.form_status,
                        "Radio_52": {
                            "value": "1",
                            "name": "本人已阅读并承诺",
                        },
                        # "Radio_73": {         # unuse
                        #     "value": "1",
                        #     "name": "是",
                        # },
                        "Calendar_47": self.form_time['end'],
                        "Calendar_50": self.form_time['begin'],
                        "Calendar_62": self.form_time['date'],
                        # "Calendar_69": date,  # unused
                        "SelectV2_58": [self.form_school],
                        "MultiInput_30": self.form_main['reason'],
                        "UserSearch_60": self.form_teacher,
                        "Input_81": self.form_teacher['number'],  # 第二个辅导员选项

                        "UserSearch_84": self.form_tutor,  # 查找导师
                        "Input_80": self.form_tutor['number'],  # 导师工号

                        "Validate_63": "",
                        "Alert_65": "",
                        "Validate_66": "",
                        # "Variate_74": "否",  # unused
                        # "DataSource_75": ""  # unused
                    }
                },
                "userview": 1,
                "special_approver": [
                    {
                        "node_key": "UserTask_100lwr4",
                        "uids": [
                            self.form_teacher['uid']
                        ],
                        "subprocessIndex": ""
                    }
                ]
            }
        }
        return 0

    def post_FormData(self):
        resp = self.session.post(
            "https://service.bupt.edu.cn/site/apps/launch",
            data="data=" + parse.quote(str(self.FormData["data"]).replace(
                "'", '"').replace(" ", "")),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                # "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38",
                # "refer": "https://service.bupt.edu.cn/v2/matter/start?id=578",
                # "x-requested-with": "XMLHttpRequest",
                # "accept": "application/json, text/plain, */*",
            }
        )
        resp.encoding = "utf-8"
        return resp.text

    def sendmail(self,sub,text):

        message = MIMEText(text, 'plain', 'utf-8')
        message['From'] = Header(self.mail['sender'], 'utf-8')
        message['To'] =  Header(self.mail['receivers'][0], 'utf-8')
        
        subject = sub
        message['Subject'] = Header(subject, 'utf-8')

        
        try:
            smtpObj = smtplib.SMTP_SSL(self.mail['mail_host'])
            # smtpObj.set_debuglevel(1)     #用于测试
            smtpObj.connect(self.mail['mail_host'], 465)    # 数字 为 SMTP 端口号
            smtpObj.login(self.mail['mail_user'],self.mail['mail_pass'])  
            smtpObj.sendmail(self.mail['sender'], self.mail['receivers'][0], message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")
    
    def run(self):
        try:
            self.readFile()
            self.login()
            self.getCollegeAndStatus()
            
            self.getUid()      ### 不知道UID的话用这个函数，知道的话可以直接写在txt里。因为未知原因，需要在getCollegeAndStatus()之后运行
            self.getSchool()

            i=0
            while(i<self.conf['days_num']):
                self.getTime(i+self.conf['start_day'])
                i+=1
                self.complete_FormData()
                print(test.FormData)
                sub='脚本'
                text=self.post_FormData()
                self.sendmail(sub,text)
        except Exception as e:
            sub='【错误】'
            if e.print_exc():
                text=e.print_exc()
                self.sendmail(sub, text)
            else:
                text='未知错误'
                self.sendmail(sub,text)

def delay(mins):
    time.sleep(mins*60)
def randdelay():
    # delay 1-10 min at random
    mins=random.randint(1,10)
    delay(mins)

# 随机延时函数，如果不需要可以注释掉
randdelay()

test=leave(1,1)
test.run()




