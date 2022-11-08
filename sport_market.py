from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def main_page():
    return '''HELLO'''


@app.route("/registration")
def registration():
    return '''Регистрация'''


@app.route("/authorization")
def authorization():
    return '''Авторизация'''


@app.route("/basket")
def basket():
    return '''Корзина'''


@app.route("/favourites")
def favourites():
    return '''Избранное'''


@app.route("/orders")
def orders():
    return '''Заказы'''


@app.route("/user")
def user_page():
    return '''Личная страница'''


if __name__ == "__main__":
    app.run(debug=True)
