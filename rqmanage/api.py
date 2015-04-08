from flask import Flask

app = Flask(__name__)

@app.route("/version")
def get_version():
    return "v0.1.0"

if __name__ == "__main__":
    app.run(debug=True)
