from crypt import methods
from flask import Flask, jsonify, request, abort
import time
import random
from flask_cors import CORS


class Game:
    def __init__(self) -> None:
        self.number = -1
        self.players = []
        self.mission = []
        self.readyPlayers = []
        self.locked = False
        self.identityMap = {}
        self.seenPlayersMap = {}

        self.currentLeader = 0
        self.leaderCount = 0
        self.team = []
        self.job = 0
        # stage
        # 1: form team
        # 2: vote for team
        # 3: vote for mission
        # 4: result
        self.stage = 0
        self.voteTeamMap = {}


server = Flask(__name__)
server.secret_key = "secretKey"
CORS(server)

# key: 房间号 int
# value: 游戏 Game
games = {}

# 加入房间
@server.route("/join", methods=["POST"])
def joinGame():
    if request.args.get("game") is None or request.args.get("name") is None:
        abort(400)
    name = request.args.get("name")
    room = int(request.args.get("game"))
    if room not in games:
        games[room] = Game()
    game = games[room]
    game.number = room
    if game.locked and name not in game.players:
        return abort(404)
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
    game = games[room]
    name = request.args.get("name")
    if game.locked and name not in game.players:
        return abort(404)
    if name not in game.players:
        abort(404)
    if name not in game.readyPlayers:
        game.readyPlayers.append(name)
    return jsonify(
        game=room, players=games[room].players, readyPlayers=games[room].readyPlayers
    )


def generateIdentity(game):
    identitiesMap = {
        5: ["Merlin", "Percival", "Loyal Servant of Arthur", "Morgana", "Assassin"],
        6: [
            "Merlin",
            "Percival",
            "Loyal Servant of Arthur",
            "Morgana",
            "Assassin",
            "Loyal Servant of Arthur",
        ],
        7: [
            "Merlin",
            "Percival",
            "Loyal Servant of Arthur",
            "Morgana",
            "Assassin",
            "Loyal Servant of Arthur",
            "Oberon",
        ],
        8: [
            "Merlin",
            "Percival",
            "Loyal Servant of Arthur",
            "Morgana",
            "Assassin",
            "Loyal Servant of Arthur",
            "Loyal Servant of Arthur",
            "Minion of Mordred",
        ],
        9: [
            "Merlin",
            "Percival",
            "Loyal Servant of Arthur",
            "Morgana",
            "Assassin",
            "Loyal Servant of Arthur",
            "Loyal Servant of Arthur",
            "Loyal Servant of Arthur",
            "Mordred",
        ],
        10: [
            "Merlin",
            "Percival",
            "Loyal Servant of Arthur",
            "Morgana",
            "Assassin",
            "Loyal Servant of Arthur",
            "Loyal Servant of Arthur",
            "Loyal Servant of Arthur",
            "Mordred",
            "Oberon",
        ],
    }
    identities = identitiesMap[len(game.players)]
    random.seed(time.time())
    random.shuffle(identities)
    # game.currentLeader = random.randint(0, len(game.players) - 1)
    game.currentLeader = 0  # 先改为0
    game.leaderCount = 1
    game.job = 1
    game.stage = 1
    game.voteTeamMap[1] = {}
    game.voteTeamMap[1][1] = {'agree':[],'disagree':[]}

    for player in game.players:
        game.identityMap[player] = identities[game.players.index(player)]

    for player in game.players:
        if game.identityMap[player] == "Merlin":
            game.seenPlayersMap[player] = []
            for i in game.players:
                if game.identityMap[i] in [
                    "Morgana",
                    "Assassin",
                    "Oberon",
                    "Minion of Mordred",
                ]:
                    game.seenPlayersMap[player].append(i)

        elif game.identityMap[player] == "Percival":
            game.seenPlayersMap[player] = []
            for i in game.players:
                if game.identityMap[i] in ["Merlin", "Morgana"]:
                    game.seenPlayersMap[player].append(i)

        elif game.identityMap[player] == "Morgana":
            game.seenPlayersMap[player] = []
            for i in game.players:
                if game.identityMap[i] in ["Assassin", "Mordred", "Minion of Mordred"]:
                    game.seenPlayersMap[player].append(i)

        elif game.identityMap[player] == "Assassin":
            game.seenPlayersMap[player] = []
            for i in game.players:
                if game.identityMap[i] in ["Morgana", "Mordred", "Minion of Mordred"]:
                    game.seenPlayersMap[player].append(i)

        elif game.identityMap[player] == "Mordred":
            game.seenPlayersMap[player] = []
            for i in game.players:
                if game.identityMap[i] in ["Morgana", "Assassin", "Minion of Mordred"]:
                    game.seenPlayersMap[player].append(i)

        elif game.identityMap[player] == "Minion of Mordred":
            game.seenPlayersMap[player] = []
            for i in game.players:
                if game.identityMap[i] in ["Morgana", "Assassin", "Mordred"]:
                    game.seenPlayersMap[player].append(i)
        else:
            game.seenPlayersMap[player] = []


# 开始游戏，发放身份
@server.route("/identity", methods=["GET"])
def getIdentity():
    if request.args.get("game") is None or request.args.get("name") is None:
        abort(404)
    room = int(request.args.get("game"))
    game = games[room]
    name = request.args.get("name")
    if name not in game.players:
        abort(404)
    if len(game.players) != len(game.readyPlayers):
        abort(404)
    if game.locked is False:
        game.locked = True
        generateIdentity(game)
        print(game.identityMap)
        print(game.seenPlayersMap)
    return jsonify(
        game=room,
        players=games[room].players,
        identity=game.identityMap[name],
        seenPlayers=game.seenPlayersMap[name],
    )


@server.route("/voteTeam", methods=["GET"])
def allVoteTeam():
    if request.args.get("game") is None or request.args.get("name") is None:
        abort(404)
    room = int(request.args.get("game"))
    game = games[room]
    name = request.args.get("name")
    if name not in game.players:
        abort(404)
    return jsonify(
        game=room,
        players=games[room].players,
        leader=game.currentLeader,
        leaderCount=game.leaderCount,
        team=game.team,
        voteResult=game.voteMap[game.job][game.leaderCount],
    )


@server.route("/formTeam", methods=["POST"])
def formTeam():
    if request.args.get("game") is None or request.args.get("name") is None:
        abort(404)
    room = int(request.args.get("game"))
    game = games[room]
    name = request.args.get("name")
    if name != game.players[game.currentLeader]:
        abort(400)
    if request.args.get("team") is None:
        abort(404)
    team = request.args.get("team")
    # if len(team) <= len(game.players):
    #     abort(400)
    game.team = team
    return jsonify(
        game=room,
        players=games[room].players,
        leader=game.currentLeader,
        leaderCount=game.leaderCount,
        team=game.team,
    )

# 所有玩家投票是否同意当前的队伍
@server.route("/voteTeam", methods=["POST"])
def voteTeam():
    if request.args.get("game") is None or request.args.get("name") is None:
        abort(404)
    room = int(request.args.get("game"))
    game = games[room]
    name = request.args.get("name")
    if name not in game.players:
        abort(404)
    if request.args.get("vote") is None:
        abort(404)
    vote = request.args.get("vote")
    if vote not in ["agree", "disagree"]:
        abort(404)
    game.voteTeamMap[game.job][game.leaderCount][vote].append(name)
    return jsonify(
        game=room,
        players=games[room].players,
        leader=game.currentLeader,
        leaderCount=game.leaderCount,
        team=game.team,
        voteResult=game.voteMap[game.job][game.leaderCount],
    )

# 获取当前游戏阶段
@server.route("/status", methods=["GET"])
def getGameStatus():
    if request.args.get("game") is None:
        abort(404)
    room = int(request.args.get("game"))
    game = games[room]
    return jsonify(
        game=room,
        players=games[room].players,
        leader=game.currentLeader,
        leaderCount=game.leaderCount,
        job=game.job,
        stage=game.stage,
        team=game.team,
        identityMap=game.identityMap,
        seenPlayersMap=game.seenPlayersMap,
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
