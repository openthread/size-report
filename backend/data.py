from flask import request
from flask import jsonify
from flask import current_app
from backend.db import *

app = current_app

@app.route("/getcommit", methods=("GET","POST"))
def retrieve_commit_data():
    db = get_db()

    if request.method == "POST":
        content_type = request.headers["Content-type"]
        charset = request.headers["charset"]

        if content_type != "application/json":
            return
        
        data = request.get_json()
        db.execute("insert into commitinfo value({},{},{})".format(data["commit_id"], data["timestamp"], data["parent_id"]))

        for item in data["code_size"]:
            db.execute("insert into filechange value({}, {},{},{},{},{})",
                        data["commit_id"], 
                        item.key(), 
                        int(item.value()["text"]), 
                        int(item.value()["data"]),
                        int(item.value()["bss"]),
                        int(item.value()["total"]))

# 假定一秒内只有一条commit。可能后续需要修改
@app.route("/latestcommit", methods=("GET"))
def latest_commit_id():
    db = get_db()

    return db.execute("select id from commitinfo"
                      "order by timestamp desc").fetchone()["id"]


# 找到指定id对应的commit信息
@app.route("/commitinfo", methods=("GET", "POST"))
def get_parent_commit_info(commit_id):
    db = get_db()

    basic_info = db.execute("select * from "
                            "commitinfo where id = ?",
                            (commit_id,),).fetchone()

    fileinfo = db.execute("select * from "
                          "filechange where commit_id = ?",
                          (commit_id,),).fetchall()
    
    files = dict()

    for item in fileinfo:
        files[item["file_name"]] = {"text": item["textsize"], 
                                    "data": item["datasize"], 
                                    "bss": item["bsssize"], 
                                    "total": item["totalsize"]}

    return jsonify(
        commit_id=basic_info["commit_id"],
        parent_id=basic_info["parent_id"],
        created_time=basic_info["created_at"],
        code=files
    )

