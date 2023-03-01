#!/usr/bin/python
# -*- coding:utf8 -*-
import os, time,re,smtplib,subprocess
from email.mime.text import MIMEText
from email.utils import formataddr

# 获取CPU负载信息
def get_cpu():
    last_worktime = 0
    last_idletime = 0
    f = open("/proc/stat", "r")
    line = ""
    while not "cpu " in line: line = f.readline()
    f.close()
    spl = line.split(" ")
    worktime = int(spl[2]) + int(spl[3]) + int(spl[4])
    idletime = int(spl[5])
    dworktime = (worktime - last_worktime)
    didletime = (idletime - last_idletime)
    rate = float(dworktime) / (didletime + dworktime)
    last_worktime = worktime
    last_idletime = idletime
    if (last_worktime == 0): return 0
    return rate
# 获取内存负载信息
def get_mem_usage_percent():
    try:
        f = open('/proc/meminfo', 'r')
        for line in f:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1])
            elif line.startswith('MemFree:'):
                mem_free = int(line.split()[1])
            elif line.startswith('Buffers:'):
                mem_buffer = int(line.split()[1])
            elif line.startswith('Cached:'):
                mem_cache = int(line.split()[1])
            elif line.startswith('SwapTotal:'):
                vmem_total = int(line.split()[1])
            elif line.startswith('SwapFree:'):
                vmem_free = int(line.split()[1])
            else:
                continue
        f.close()
    except:
        return None
    physical_percent = usage_percent(mem_total - (mem_free + mem_buffer + mem_cache), mem_total)
    virtual_percent = 0
    if vmem_total > 0:
        virtual_percent = usage_percent((vmem_total - vmem_free), vmem_total)
    return physical_percent, virtual_percent

def usage_percent(use, total):
    try:
        ret = (float(use) / total) * 100
    except ZeroDivisionError:
        raise Exception("ERROR - zero division error")
    return ret
# 获取磁盘根目录占用信息
def disk_info():
    statvfs = os.statvfs('/') #根目录信息 可根据情况修改
    total_disk_space = statvfs.f_frsize * statvfs.f_blocks
    free_disk_space = statvfs.f_frsize * statvfs.f_bfree
    disk_usage = (total_disk_space - free_disk_space) * 100.0 / total_disk_space
    disk_usage = int(disk_usage)
    disk_tip = "硬盘空间使用率（最大100%）：" + str(disk_usage) + "%"
    return disk_tip
# 获取内存占用信息
def mem_info():
    mem_usage = get_mem_usage_percent()
    mem_usage = int(mem_usage[0])
    mem_tip = "物理内存使用率（最大100%）：" + str(mem_usage) + "%"
    return mem_tip
# 获取CPU占用信息
def cpu_info():
    cpu_usage = int(get_cpu() * 100)
    cpu_tip = "CPU使用率（最大100%）：" + str(cpu_usage) + "%"
    return cpu_tip
# 获取系统占用信息
def sys_info():
    load_average = os.getloadavg()
    load_tip = "系统负载（三个数值中有一个超过3就是高）：" + str(load_average)
    return load_tip
# 获取计算机当前时间
def time_info():
    now_time = time.strftime('%Y-%m-%d %H:%M:%S')
    return "主机的当前时间：%s" %now_time
# 获取计算机主机名称
def hostname_info():
    hostnames = os.popen("hostname").read().strip()
    return "你的主机名是: %s"%hostnames
# 获取IP地址信息
def ip_info():
    ipadd = os.popen("ip a| grep eth0 | grep inet | awk '{print $2}'").read().strip()
    return ipadd
# 获取根的占用信息
def disk_info_root():
    child = subprocess.Popen(["df", "-h"], stdout=subprocess.PIPE)
    out = child.stdout.readlines()

    for item in out:
        line = item.strip().split()
        # 我这里只查看centos的根
        if '/dev/sda1' in line:
            title = [u'-文件系统-',u'--容量-', u'-已用-', u'-可用-', u'-已用-', u'-挂载点--']
            content = "\t".join(title)
            if eval(line[4][0:-1]) > 60:
                line[0] = 'centos-root'
                content += '\r\n' + '\t'.join(line)
                return content
# 将系统信息发送到指定邮箱
def send_mail(info):
    my_sender = 'xxxxxx@163.com'  # 发件人邮箱账号
    my_pass = 'xxxxxx'  # 发件人邮箱密码
    my_user = 'xxxxxx@qq.com'  # 收件人邮箱账号
    ret = True
    try:
        msg = MIMEText(info, 'plain', 'utf-8')
        msg['From'] = formataddr(["发送者", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["接收者", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号 昵称无法显示
        msg['Subject'] = "【警告！！】服务器资源占用统计"+time.strftime('%Y-%m-%d %H:%M:%S')  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP_SSL("smtp.163.com", 994)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret
# 测试程序
if __name__ == "__main__":
    flag = 0
    disk_information = disk_info()
    disk_usage = [int(s) for s in re.findall(r'\b\d+\b', disk_information)]
    infomation = [hostname_info(),time_info()]

    memory_information = mem_info()
    mem_usage = [int(s) for s in re.findall(r'\b\d+\b', memory_information)]
    infomation = [hostname_info(),time_info()]

    cpu_information = cpu_info()
    cpu_usage = [int(s) for s in re.findall(r'\b\d+\b', cpu_information)]
    infomation = [hostname_info(),time_info()]

    # 如果磁盘占用高于90%就发邮件告警
    if disk_usage[0]>=90:
        infomation.append(disk_information)
        flag = 1
    
    

    # 如果内存占用高于90%就发邮件告警
    if mem_usage[0]>=90:
        infomation.append(memory_information)
        flag = 1
    


    # 如果cpu占用高于90%就发邮件告警
    if cpu_usage[0]>=90:
        infomation.append(cpu_information)
        flag = 1
    
    if flag:
        send_mail('\r\n'.join(infomation))
   
    print(hostname_info())
    print(time_info())
    print(ip_info())
    print(sys_info())
    print(cpu_info())
    print(mem_info())
    print(disk_info())
    
   


