# !/usr/bin/python
# -*- coding:utf8 -*-
import sys
import requests
import os

print (sys.argv[0])
clone_url = sys.argv[1]
compare_url = sys.argv[2]
repo_name = sys.argv[3]

retcode =  os.system("cd .. \n" + "git clone " + clone_url)
print("retcode is: %s" % retcode);#0表示执行成功,否则表示失败

