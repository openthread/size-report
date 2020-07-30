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
 
