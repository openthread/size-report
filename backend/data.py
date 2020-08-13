from flask import request
from flask import jsonify
from flask import current_app
from backend.db import *
from flask import render_template
from flask import Blueprint

app = Blueprint("data", __name__)

@app.route('/')
def index():
    return render_template("index.html")
    # return "Hello world"

@app.route("/getcommit", methods=("POST",))
def retrieve_commit_data():
    # print("getting commit data")
    db = get_db()

    if request.method == "POST":
        content_type = request.headers["Content-type"]
        # charset = request.headers["charset"]

        if content_type != "application/json":
            return

        json = request.get_json()

        commit = json["commits"][0]
        parent_commit = json["commits"][1]

        # print(commit, parent_commit)
        # print(commit["commit_id"], commit["timestamp"])

        if db.execute("select * from commitinfo where id = ?", (commit["commit_id"],)).fetchall() != None:
            return jsonify({"status": "OK"})

        db.execute("insert into commitinfo values('{}','{}','{}');".format(commit["commit_id"], commit["timestamp"], parent_commit["parent_commit_id"]))
        db.commit()
        # print("insert commit info successfully ", db.execute("select * from commitinfo").fetchall()[0][0], db.execute("select * from commitinfo").fetchall()[0][1], db.execute("select * from commitinfo").fetchall()[0][2])

        # print(commit["code_size"])

        for item in commit["code_size"]:
            # print(list(item.keys()))
            # print(dict(list(item.values())[0]))
            db.execute("insert into filechange values('{}','{}',{},{},{},{});".format
                        (commit["commit_id"], 
                        list(item.keys())[0], 
                        int(dict(list(item.values())[0])["text"]), 
                        int(dict(list(item.values())[0])["data"]),
                        int(dict(list(item.values())[0])["bss"]),
                        int(dict(list(item.values())[0])["total"])))
            db.commit()

        # print("insert file info into filechange successfully ", db.execute("select * from filechange").fetchall()[0])

        # 若此条commit的上一条commit不在数据库中，插入这一条commit的记录。
        if db.execute("select * from commitinfo where id = ?", (parent_commit["parent_commit_id"],), ).fetchall() is None:
            db.execute("insert into commit info values('{}',{});".format(parent_commit["parent_commit_id"], parent_commit["parent_timestamp"]))
            db.commit()

            for item in parent_commit["parent_code_size"]:
                db.execute("insert into filechange values('{}', '{}',{},{},{},{});".format
                        (parent_commit["parent_commit_id"], 
                        list(item.keys())[0], 
                        int(dict(list(item.values())[0])["text"]), 
                        int(dict(list(item.values())[0])["data"]),
                        int(dict(list(item.values())[0])["bss"]),
                        int(dict(list(item.values())[0])["total"])))
                db.commit()

        # test
        # print(list(db.execute("select * from commitinfo").fetchall()))
        return jsonify({"status": "OK"})


@app.route("/latestcommit", methods=("GET",))
def latest_commit_id():
    db = get_db()

    return jsonify(db.execute("select id from commitinfo order by created_at desc").fetchone()[0])

# 返回最新的n条记录（暂定post的内容有n_commit_info这一条，里面存了记录的数目
# 返回格式是json（数组）
@app.route("/ncommitinfo", methods=("POST",))
def get_n_commits():
    db = get_db()

    if request.method == "POST":
        content_type = request.headers["Content-type"]
        # charset = request.headers["charset"]

        if content_type != "application/json":
            return

        json = request.get_json()
        
        n = json["n_commit_info"]

        if int(db.execute("select count(*) from commitinfo;").fetchall()[0][0]) < int(n):
            test_info = db.execute("select * from commitinfo").fetchall()
            print(list(test_info))
            basic_info = db.execute("select * from commitinfo order by created_at desc").fetchall()
            print(list(basic_info))

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
        # charset = request.headers["charset"]

        if content_type != "application/json":
            return

        json = request.get_json()
        # print(json)
        
        commit_id = json["commit_id"]
        print(commit_id)

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
            commit_id=basic_info["id"],
            parent_id=basic_info["parent_id"],
            created_time=basic_info["created_at"],
            code=files
        )

