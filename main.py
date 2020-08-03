# !/usr/bin/python
# -*- coding:utf8 -*-
import sys
import requests
import os
import subprocess
print (sys.argv[0])
clone_url = sys.argv[1]
#https://github.com/chris98122/openthread.git
compare_url = sys.argv[2]
repo_name = sys.argv[3]
#openthread

newest_commit_id = ""
parent_commit_id = ""

retcode, output = subprocess.getstatusoutput("cd .. \n" + "git clone " + clone_url)
print("git clone retcode is: %s" % retcode);#0表示执行成功,否则表示失败
print(output)

if retcode != 0:
    retcode, output = subprocess.getstatusoutput("cd ../"+repo_name+ "\n" + "git pull origin master")
    print(output)
    if retcode != 0:
        sys.exit("git pull failed") 
    else:
        retcode, newest_commit_id = subprocess.getstatusoutput("git rev-parse HEAD") # git 获取最近一次提交的commit id
        print(output)
        print("newest_commit_id is: %s" % newest_commit_id)

        retcode, parent_commit_id = subprocess.getstatusoutput("git rev-parse HEAD^")# git 获取parent commit id
        print(output)
        print("parent_commit_id is: %s" % parent_commit_id)

# SIZE_REPORT_URL =http://localhost:3000/  
# compile : make -f examples/Makefile-nrf52840 "
# run  ./script/code-size nrf52840  : already install arm-none-eabi-gcc
# arm-none-eabi-readelf -S /tmp/ot-size-report/b/output/nrf52840/bin/ot-cli-ftd
retcode, output = subprocess.getstatusoutput("cd ../" + repo_name + "\n" + " ./script/check-size nrf52840")
print(output)
if retcode != 0:
    print("check-size failed")

with open('/tmp/size_report') as f:
    lines = f.readlines()
    filename = ""
    for line in lines:
        splitted = line.split('|')
        text = int(splitted[3].strip())
        data = int(splitted[4].strip())
        bss = int(splitted[5].strip())
        total = int(splitted[6].strip())

        if (lines.index(line) - 2 ) % 3 == 0:
            filename = splitted[1].strip()
            parent_filechange = {"commit_id":parent_commit_id,"code_size":{filename:{"text":text , "data" :data ,"bss":bss, "total":total }}}
            print(parent_filechange) 

        if (lines.index(line) - 3 ) % 3 == 0 and lines.index(line) !=0 :
            filechange = {"commit_id":newest_commit_id,"code_size":{filename:{"text":text , "data" :data ,"bss":bss, "total":total }}}
            print(filechange) 
        
#test cmd : python3 main.py https://github.com/chris98122/openthread.git 1 openthread
