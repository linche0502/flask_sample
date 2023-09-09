from flask import Blueprint, render_template, redirect, request
from .model import *
import json



app= Blueprint("main", __name__)


# 首頁
@app.route("/")
def home():
    return render_template("home.html", title="Hello Flask 首頁")


# 註冊頁面
@app.route("/signup")
def signup():
    errorMsg= request.args.get('errorMsg','')
    return render_template("signup.html", title="註冊", errorMsg=errorMsg)


# 註冊連結到資料庫insert
@app.route("/signup/insert", methods=["POST"])
def signupInsert():
    if request.form.get('name') and request.files.get("imageFile").filename:
        user_id= insertData("user", {"name":request.form.get("name")})
        newFile(user_id, request.files.get("imageFile"))
        return redirect("/")
    else:
        return redirect("/signup?errorMsg=請填寫完整")


# 登入頁面
@app.route("/login")
def login():
    return render_template("login.html", title="登入")


# 登入時的人臉辨識配對結果
@app.route("/login/compare", methods=["POST"])
def loginCompare():
    if request.form.get("imageData"):
        # 網頁傳回來的是"data:image/jpeg;base64,/9j/4A....."之類的編碼，但是解碼時不需要","前面的type說明部分
        result= compareFace(request.form.get("imageData").split(',')[-1])
    return json.dumps({"result":result})


# chatGPT聊天室頁面
@app.route("/chat/<int:user_id>")
def chat(user_id):
    dialogue= getData("chat", f"SELECT msg,type FROM chat WHERE user_id={user_id};")
    user_name= getData("user", f"SELECT name FROM user WHERE id={user_id};")[0][0]
    # 將dialogue dump成JSON格式的字串，但是要先新\字符到\n,\t,'之類的字符之前，以讓輸出到html上的javascript能夠正確解讀此字串
    dialogue= json.dumps(dialogue).replace("\\","\\\\").replace("'","\\'")
    return render_template("chat.html", title="聊天室", user_id=user_id, user_name=user_name, dialogue=dialogue)


# 向chatGPT發訊息
@app.route("/chat/send/<int:user_id>", methods=["POST"])
def chatSend(user_id):
    if request.form.get("msg"):
        return json.dumps({"response": getChatGPTResponse(user_id, request.form.get("msg"))})
    return json.dumps({"response": None})

