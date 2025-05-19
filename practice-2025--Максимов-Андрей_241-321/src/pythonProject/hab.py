from flask import Flask, jsonify


hab = Flask(__name__)

@hab.route("/")
def osn():
    return jsonify({"status": "server is started on lacalserver"})


@hab.route("/commits")
def listCom():
    commits = []
    return jsonify(commits)

if __name__ == '__main__':
    hab.run(debug=True, port=8080)# dsasdsa