from crypt import methods
from mimetypes import init
from flask import Flask, jsonify, redirect, session, request, abort


class Game:
    def __init__(self) -> None:
        self.players = []
        self.mission = []


def handleCORS(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
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
    return jsonify(game=room, players=games[room].players)


# 获取房间内所有玩家
@server.route("/players", methods=["GET"])
def getAllPlayers():
    if request.args.get("game") is None:
        abort(400)
    room = int(request.args.get("game"))
    if room not in games:
        abort(404)
    return jsonify(game=room, players=games[room].players)


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5001, debug=True)
