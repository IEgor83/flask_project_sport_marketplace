from flask import Flask, render_template, url_for, request
from db_util import Database
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
db = Database()
app.config['SECRET_KEY'] = 'KMBbIlF9kpd3mTQk4C6zFIsXNHOw0HAk'


@app.route("/")
def main_page():
    return render_template("main_page.html")


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        if request.form.get('password') == request.form.get('confirm'):
            login = request.form.get('login')
            hash_pass = str(generate_password_hash(request.form.get('password')))
            contact = request.form.get('contacts')
            role = 'user'
            max_id = db.select(f"SELECT MAX(user_id) FROM users")['max']
            if max_id is not None:
                user_id = max_id + 1
            else:
                user_id = 1
            db.insert(f"INSERT into users (user_id, role, login, password, contacts) VALUES ({user_id}, '{role}', '{login}', '{hash_pass}', '{contact}')")
    return render_template("registration.html")


@app.route("/authorization", methods=['GET', 'POST'])
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
