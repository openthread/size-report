from flask import request
from flask import jsonify
from flask import current_app
from backend.db import *

app = current_app

@app.route("/getcommit", methods=("POST",))
def retrieve_commit_data():
    db = get_db()

    if request.method == "POST":
        content_type = request.headers["Content-type"]
        charset = request.headers["charset"]

        if content_type != "application/json":
            return
        
        commit = request.get_json()["commits"][0]
        parent_commit = request.get_json["commits"][1]
        db.execute("insert into commitinfo value({},{},{})".format(commit["commit_id"], commit["timestamp"], parent_commit["parent_commit_id"]))

        for item in commit["code_size"]:
            db.execute("insert into filechange value({}, {},{},{},{},{})",
                        commit["commit_id"], 
                        item.key(), 
                        int(item.value()["text"]), 
                        int(item.value()["data"]),
                        int(item.value()["bss"]),
                        int(item.value()["total"]))

        # 若此条commit的上一条commit不在数据库中，插入这一条commit的记录。
        if db.execute("select * from commitinfo where id = ?", (parent_commit["parent_commit_id"],), ).fetchall() is None:
            db.execute("insert into commit info value({},{})".format(parent_commit["parent_commit_id"], parent_commit["parent_timestamp"]))

            for item in parent_commit["parent_code_size"]:
                db.execute("insert into filechange value({}, {},{},{},{},{})",
                        parent_commit["parent_commit_id"], 
                        item.key(), 
                        int(item.value()["text"]), 
                        int(item.value()["data"]),
                        int(item.value()["bss"]),
                        int(item.value()["total"]))


@app.route("/latestcommit", methods=("GET",))
def latest_commit_id():
    db = get_db()

    return db.execute("select id from commitinfo"
                      "order by timestamp desc").fetchone()["id"]

# 返回最新的n条记录（暂定post的内容有n这一条，里面存了记录的数目
# 返回格式是json（数组）
@app.route("/ncommmitinfo", methods=("POST",))
def get_n_commits():
    db = get_db()

    if request.method == "POST":
        content_type = request.headers["Content-type"]
        charset = request.headers["charset"]

        if content_type != "application/json":
            return
        
        n = request.get_json()["n"]

        if int(db.execute("select count(*) from commitinfo;").fetchall()[0][0]) < n:
            basic_info = db.execute("select * from commitinfo order by create_at desc").fetchall()

            return_value = []
            
            for it in basic_info:
                commitid = it[0]
                filesinfo = db.execute("select * from filechange where commit_id = ?", (commitid,),).fetchall()

                files = dict()
                
                for item in filesinfo:
                    files[item["file_name"]] = {"text": item["textsize"], 
                                                "data": item["datasize"], 
                                                "bss": item["bsssize"], 
                                                "total": item["totalsize"]}

                commit_info = {"commit_id": commitid, "parent_id": it[2], "created_time": it[1], "code": files}
                return_value.append(commit_info)

            return jsonify(return_value)

        else:
            basic_info = db.execute("select * from commitinfo order by create_at desc").fetchall()[:n]

            return_value = []
            
            for it in basic_info:
                commitid = it[0]
                filesinfo = db.execute("select * from filechange where commit_id = ?", (commitid,),).fetchall()

                files = dict()
                
                for item in filesinfo:
                    files[item["file_name"]] = {"text": item["textsize"], 
                                                "data": item["datasize"], 
                                                "bss": item["bsssize"], 
                                                "total": item["totalsize"]}

                commit_info = {"commit_id": commitid, "parent_id": it[2], "created_time": it[1], "code": files}
                return_value.append(commit_info)

            return jsonify(return_value)



# 找到指定id对应的commit信息。暂定前端post返回json，有commit_id一项
@app.route("/commitinfo", methods=("GET", "POST"))
def get_commit_info():
    db = get_db()

    if request.method == "POST":
        content_type = request.headers["Content-type"]
        charset = request.headers["charset"]

        if content_type != "application/json":
            return
        
        commit_id = request.get_json()["commit_id"]

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

