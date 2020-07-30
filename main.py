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

last_commit_id = ""

retcode, output = subprocess.getstatusoutput("cd .. \n" + "git clone " + clone_url)
print("git clone retcode is: %s" % retcode);#0表示执行成功,否则表示失败
print(output)

if retcode != 0:
    retcode, output = subprocess.getstatusoutput("cd ../"+repo_name+ "\n" + "git pull origin master")
    print(output)
    if retcode != 0:
        sys.exit("git pull failed") 
    else:
        last_commit_id, output = subprocess.getstatusoutput("git rev-parse HEAD") # git 获取最近一次提交的commit id
        print(output)
        print("last_commit_id is: %s" % last_commit_id)

# SIZE_REPORT_URL =http://localhost:3000/  
# compile : make -f examples/Makefile-nrf52840 "
# run  ./script/code-size nrf52840  : already install arm-none-eabi-gcc
# arm-none-eabi-readelf -S /tmp/ot-size-report/b/output/nrf52840/bin/ot-cli-ftd
retcode, output = subprocess.getstatusoutput("cd ../" + repo_name + "\n" + " ./script/check-size nrf52840")
print(output)
if retcode != 0:
    sys.exit("check-size failed")


with open('/tmp/size_report') as f:
    lines = f.readlines()
    filename = ""
    for line in lines:
        splitted = line.split('|')
        if (lines.index(line) - 2 ) % 3 == 0:
            filename = splitted[1]
        # if (lines.index(line) - 3 ) % 3 == 0:
        commit_id = splitted[2]
        text = splitted[3]
        data = splitted[4]
        bss = splitted[5]
        total = splitted[6]

        filechange = {"commit_id":commit_id,"code_size":{filename:{"text":text , "data" :data ,"bss":bss, "total":total }}}
        print(file_change) 



#test cmd : python3 main.py https://github.com/chris98122/openthread.git 1 openthread
