from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def main_page():
    return '''HELLO'''


if __name__ == "__main__":
    app.run(debug=True)