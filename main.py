# -*- coding: UTF-8 -*-

'''
Author_PAPEREE                  ｜ 作者_纸片君ee
Created_2023_04_11              ｜ 日期_2023_04_11
Description_PAPEREE's_File_Bed  ｜ 描述_纸片君ee的文件小站
'''

from flask import Flask,Response,request,redirect,render_template
from flask_cors import CORS,cross_origin
from os import path,makedirs,walk,getcwd
from re import sub
from time import strftime,localtime
from codecs import open
from json import dumps,loads
from sys import exit

def pull(arg,error=None):
    return request.args.get(arg,error)

def save(filename,mode,text):
    open(f"location/{filename}",mode,"UTF-8-sig").write(text)

def load(filename):
    return open(f"location/{filename}","r","UTF-8-sig").read()

def result(state,text,arg={"help":["/","/upload","/detail","/record","/server"]}):
    return Response(dumps({"code":state,"text":text,**arg},ensure_ascii=False),mimetype="application/json")

table=str.maketrans("", "", ".-+=_/|~")
config=loads(load("config.json").replace("'", '"'))
method=["POST","GET"]

if not config["pwd"]:
    print("管理密码为空 请先修改配置文件/location/config.json中的pwd项目")
    exit(0)

app=Flask(str(id("uwu")),static_folder="/",static_url_path="/")
CORS(app,resources=r"/*")

@app.errorhandler(Exception)
def error(e):
    return render_template("4n0n4me.html"),404

@app.route("/")
@cross_origin(methods=method,headers=["Content-Type"],supports_credentials=True)
def index():
    if request.args:
        return redirect(request.base_url)

    return render_template("index.html",type="."+",.".join(config['type']),size_mb=config["size"],size_gb=round(int(config["size"])/1024,4),num=config["num"])

@app.route("/upload",methods=method)
def upload():
    files=request.files.getlist("files[]",None)
    path_list=list()

    if request.args:
        return redirect(request.base_url)

    if not files:
        return result(0,"你传了个寂寞")

    if len(files)>int(config["num"]):
        return result(0,"文件数量过多")

    ip=request.headers.get("X-Forwarded-For",request.remote_addr)
    time=strftime("%Y.%m.%d %H:%M:%S",localtime())

    for file in files:
        if file.filename.rsplit(".",1)[-1].lower() not in config["type"]:
            return result(0,"无效的文件类型")

        if int(request.content_length)>int(config["size"])*1024*1024:
            return result(0,"无效的文件大小")

        file_path="templates/"+(request.form.get("path") or "anonymous")
        new_path=sub(r"/+","/",path.join(file_path,file.filename).replace("\\","/"))

        if not new_path.rsplit(".",1)[0].translate(table).isalnum():
            return result(0,"无效的文件名/文件路径")

        makedirs(file_path,exist_ok=True)
        file.save(new_path)
        path_list.append(new_path)
        save("record.log","a+",f"{time}｜{ip}｜/{new_path}\n")

    return result(1,"文件上传成功",{"path":path_list,"time":time})

@app.route("/detail",methods=method)
def detail():
    data=list()

    for root,dirs,files in walk(f"{getcwd()}/templates"):
        for file in files:
            data.append("/"+path.join(root,file).replace("\\","/").split("/",2)[-1])

    if pull("type")=="text":
        return "<br>".join(data)

    return result(1,"文件获取成功",{"data":data})

@app.route("/record",methods=method)
def record():
    if pull("pass")!=config["pwd"]:
        return result(0,"无效的管理员密码")

    if pull("type")=="text":
        return load("record.log").replace("\n","<br>")

    return result(1,"记录获取成功",{"data":load("record.log").split("\n")[:-1]})

@app.route("/server",methods=method)
def server():
    if pull("pass")!=config["pwd"]:
        return result(0,"无效的管理员密码")

    if len(request.args)<2:
        return result(0,"你没参数有毛用啊")

    types=config["type"]

    for cmd in request.args:
        get_cmd=pull(cmd)

        if get_cmd:
            if cmd=="add" and get_cmd not in types:
                types.append(get_cmd)

            elif cmd=="rm" and get_cmd in types:
                types.pop(types.index(get_cmd))

            elif cmd in config:
                config[cmd]=get_cmd

    config["type"]=list(set(config["type"]))
    save("config.json","w",str(config))
    return result(1,"项目修改保存成功",{"data":config})

@app.route(f"/{path.basename(__file__)}")
@app.route("/location/<path:filename>")
@app.route("/undefined")
def rickroll():
    return redirect("https://1145.s3.ladydaily.com/rock.mp4")

if __name__=="__main__":
    app.run(host="127.0.0.1",port=1919,debug=True,threaded=True)
