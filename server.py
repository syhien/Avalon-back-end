from crypt import methods
from mimetypes import init
from flask import Flask, jsonify, redirect, session, request, abort


class Game:
    def __init__(self) -> None:
        self.players = []
        self.mission = []
        self.readyPlayers = []
        self.job = 0
        # stage
        # 0: wait everyone to ready
        # 1: form team
        # 2: vote for team
        # 3: vote for mission
        # 4: result
        self.stage = 0


def handleCORS(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "X-Requested-With,content-type"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


server = Flask(__name__)
server.secret_key = "secretKey"
server.after_request(handleCORS)

# key: 房间号 int
# value: 游戏 Game
games = {}

# 加入房间
@server.route("/join", methods=["POST"])
def joinGame():
    if request.args.get("game") is None or request.args.get("name") is None:
        abort(400)
    room = int(request.args.get("game"))
    if room not in games:
        games[room] = Game()
    game = games[room]
    name = request.args.get("name")
    if name not in game.players:
        game.players.append(name)
    server.logger.debug(games[room].players)
    return jsonify(
        game=room, players=games[room].players, readyPlayers=games[room].readyPlayers
    )

# 玩家准备，可以开始游戏
@server.route("/readyGame", methods=["POST"])
def readyGame():
    if request.args.get("game") is None or request.args.get("name") is None:
        abort(400)
    room = int(request.args.get("game"))
    if room not in games:
        games[room] = Game()
    game = games[room]
    name = request.args.get("name")
    if name not in game.players:
        abort(404)
    if name not in game.readyPlayers:
        game.readyPlayers.append(name)
    return jsonify(
        game=room, players=games[room].players, readyPlayers=games[room].readyPlayers
    )

# 获取房间内所有玩家
@server.route("/players", methods=["GET"])
def getAllPlayers():
    if request.args.get("game") is None:
        abort(400)
    room = int(request.args.get("game"))
    if room not in games:
        abort(404)
    return jsonify(
        game=room, players=games[room].players, readyPlayers=games[room].readyPlayers
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5001, debug=True)
