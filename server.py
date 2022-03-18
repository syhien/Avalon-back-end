from flask import Flask, jsonify, redirect, session, request
import sqlite3

def handleCORS(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

server = Flask(__name__)
server.secret_key = "secretKey"
server.after_request(handleCORS)


@server.route("/", methods=["GET"])
def defaultPage():
    if (
        session.get("name") is None
        or session.get("qq") is None
        or session.get("seat") is None
    ):
        return redirect("/info")


# 注册一个用户
@server.route("/info", methods=["POST"])
def newInfo():
    if request.args.get("name") is None:
        return "Missing name"
    name = request.args.get("name")
    if request.args.get("seat") is None:
        return "Missing seat"
    seat = int(request.args.get("seat"))
    qq = -1
    if request.args.get("qq") is not None:
        qq = int(request.args.get("qq"))
    session["name"] = name
    session["qq"] = qq
    session["seat"] = seat
    return "success"


# 获取信息
@server.route("/info", methods=["GET"])
def getInfo():
    if (
        session.get("name") is None
        or session.get("qq") is None
        or session.get("seat") is None
    ):
        return "Please Register first"
    json = {
        "name": session.get("name"),
        "qq": int(session.get("qq")),
        "seat": int(session.get("seat")),
    }
    return jsonify(json)


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5001, debug=True)
