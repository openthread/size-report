# !/usr/bin/python
# -*- coding:utf8 -*-

#test cmd : python3 main.py https://github.com/chris98122/openthread.git 1 openthread

import sys
import requests
import os
import subprocess
import json
print (sys.argv[0])
clone_url = sys.argv[1]
#https://github.com/chris98122/openthread.git
compare_url = sys.argv[2]
repo_name = sys.argv[3]
#openthread

newest_commit_id = ""
parent_commit_id = ""
newest_commit_timestamp = ""
parent_commit_timestamp = ""

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

        retcode, newest_commit_timestamp = subprocess.getstatusoutput("git show -s --format=%ci HEAD")
        newest_commit_timestamp = newest_commit_timestamp.split('+')[0].strip()
        print(output)
        print("newest_commit_timestamp is: %s" % newest_commit_timestamp)
            
        retcode, parent_commit_timestamp = subprocess.getstatusoutput("git show -s --format=%ci HEAD^")
        parent_commit_timestamp = parent_commit_timestamp.split('+')[0].strip()
        print(output)
        print("parent_commit_timestamp is: %s" % parent_commit_timestamp)

# SIZE_REPORT_URL =http://localhost:3000/  
# compile : make -f examples/Makefile-nrf52840 "
# run  ./script/code-size nrf52840  : already install arm-none-eabi-gcc
# arm-none-eabi-readelf -S /tmp/ot-size-report/b/output/nrf52840/bin/ot-cli-ftd
retcode, output = subprocess.getstatusoutput("cd ../" + repo_name + "\n" + " ./script/check-size nrf52840")
print(output)
if retcode != 0:
    print("check-size failed")


parent_code_size =[]
code_size = []
with open('/tmp/size_report') as f:
    lines = f.readlines()
    filename = ""
    for line in lines:
        splitted = line.split('|')
        try:
            text = int(splitted[3].strip())
            data = int(splitted[4].strip())
            bss = int(splitted[5].strip())
            total = int(splitted[6].strip())
        except Exception as ex:
            continue

        if (lines.index(line) - 2 ) % 3 == 0:
            filename = splitted[1].strip()
            parent_code_size.append({filename:{"text":text , "data" :data ,"bss":bss, "total":total }})
            
        if (lines.index(line) - 3 ) % 3 == 0 and lines.index(line) != 0:
            code_size.append({filename:{"text":text , "data" :data ,"bss":bss, "total":total }})
            
        

parent_filechange = {"parent_commit_id":parent_commit_id, "'parent_timestamp'":parent_commit_timestamp,"'parent_code_size'":parent_code_size}
print(parent_filechange) 

filechange = {"commit_id":newest_commit_id, "timestamp":newest_commit_timestamp,"code_size":code_size }
print(filechange) 
commits=[]
commits.append(filechange)
commits.append(parent_filechange)
data ={"commits":commits}

# send request
base_url = "https://summer20-sps-50.df.r.appspot.com"
url = base_url+"/commits"

r = requests.post(url,
                  data=json.dump(data),
                  headers={'Content-type': 'application/json; charset=utf-8'})
print(r.json())