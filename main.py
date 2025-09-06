from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)


if __name__ == "__main__":
    app.run(debug=True)
