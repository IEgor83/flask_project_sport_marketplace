from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template("main_page.html")


@app.route("/registration")
def registration():
    return render_template("registration.html")


@app.route("/authorization")
def authorization():
    return render_template("authorization.html")


@app.route("/basket")
def basket():
    return render_template("basket.html")


@app.route("/favourites")
def favourites():
    return render_template("favourites.html")


@app.route("/orders")
def orders():
    return render_template("orders.html")


@app.route("/user")
def user_page():
    return render_template("user_page.html")


if __name__ == "__main__":
    app.run(debug=True)
