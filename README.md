# BUPT自动申请临时出入校脚本

参考https://github.com/OhYee/bupt-scripts/blob/master/leave。由于改动比较大且对git使用不熟悉，就没有采用建立分支的方式。

## 1. 文件结构

leave.py是脚本文件，需要安装相应的包配置好python环境；cron.leave用于配置crontab，在crontab中写入“00	10	*	*	*	sh 所在路径/cron.leave”可在每天10点运行脚本；users.txt用于填写用户信息。

脚本运行后会创建log.log和error.log，用于存放日志。

## 2. users.txt

userid: "学号"
username: "姓名"
userpass: "登录密码"
phone: "手机号"
destination: "外出去向"
reason: "外出事由"
school: "校区（西土城/沙河）"

\# 辅导员（按理来说只填写工号应该就可以，但是懒得改了）

teacher_name: "辅导员姓名"
teacher_uid: 辅导员uid（不是辅导员工号，是手动填写表单时不会显示的隐藏字段，但是实际提交时不可缺少。知道的话可以直接填上然后注释掉脚本中的getUid()函数，不知道的话填好工号脚本会自动查找）
teacher_number: "辅导员工号"

\# 导师

tutor_name: "导师姓名"
tutor_uid: 导师uid
tutor_number: "导师工号"

\# 邮箱提醒，可以将脚本运行结果发送到邮箱，不需要的话注释掉脚本中邮件相关字段即可

mail_host: "邮箱服务器（比如163邮箱是smpt.163.com，默认端口465可以在脚本里改但不推荐，因为好像阿里云等云服务平台禁用了25非加密端口）"
mail_user: "发件邮箱"
mail_pass: "发件邮箱密码"
sender: "发件人（和发件邮箱一致即可）"
receivers: ["收件人，即收件邮箱"]

## 3. 脚本功能

脚本主体有三行代码

```python
randdelay()
test=leave(1,1)
test.run()
```

第一行是随机sleep1-10分钟，避免每天在同一时间点提交。

第二行创建一个leave类的实例，第一个参数表示申请日期在第几天后，第二个参数表示一次性申请几天的。例如leave(1,1)，申请运行脚本的第二天的临时出入校；leave(2,2)，申请运行脚本的第三天的连续两天。多次申请功能没有实际用过，慎用！

第三行开始运行，执行逻辑依次是：读取users.txt中的信息；登录；获取学院、身份信息；获取辅导员、导师的uid；获取校区。