
import sys
import os
import subprocess
import json

retcode, output = subprocess.getstatusoutput("cd ../" + repo_name + "\n" + " ./script/check-size nrf52840")
print(output)
if retcode != 0:
    print("check-size failed")

retcode, newest_commit_id = subprocess.getstatusoutput("git rev-parse HEAD") # git 获取最近一次提交的commit id
print("newest_commit_id is: %s" % newest_commit_id)

retcode, parent_commit_id = subprocess.getstatusoutput("git rev-parse HEAD^")# git 获取parent commit id
print("parent_commit_id is: %s" % parent_commit_id)

retcode, newest_commit_timestamp = subprocess.getstatusoutput("git show -s --format=%ci HEAD")
newest_commit_timestamp = newest_commit_timestamp.split('-')[0].strip()

print("newest_commit_timestamp is: %s" % newest_commit_timestamp)
    
retcode, parent_commit_timestamp = subprocess.getstatusoutput("git show -s --format=%ci HEAD^")
parent_commit_timestamp = parent_commit_timestamp.split('-')[0].strip()
print("parent_commit_timestamp is: %s" % parent_commit_timestamp)

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

with open("./"+newest_commit_id+".json","w") as f:
    json.dump(data,f)
    print("write data into file")