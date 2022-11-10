from flask import Flask, render_template, url_for, request, redirect
from db_util import Database
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreateUserForm

app = Flask(__name__)
db = Database()
app.config['SECRET_KEY'] = 'KMBbIlF9kpd3mTQk4C6zFIsXNHOw0HAk'


@app.route("/")
def main_page():
    return render_template("main_page.html")


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    error_mes = ''
    form = CreateUserForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        phone = request.form.get('phone')
        if email and db.select(f"SELECT COUNT(*) FROM users WHERE email='{email}'")['count'] > 0:
            error_mes = 'Пользователь с таким e-mail уже существует'
            return render_template("registration.html", form=form, error_mes=error_mes)
        if phone and db.select(f"SELECT COUNT(*) FROM users WHERE phone ='{phone}'")['count'] > 0:
            error_mes = 'Пользователь с таким телефоном уже существует'
            return render_template("registration.html", form=form, error_mes=error_mes)
        hash_pass = str(generate_password_hash(request.form.get('password')))
        role = 'user'
        max_id = db.select(f"SELECT MAX(user_id) FROM users")['max']
        if max_id is not None:
            user_id = max_id + 1
        else:
            user_id = 1
        db.insert(f"INSERT into users (user_id, role, email, phone, password, ) VALUES ({user_id}, '{role}', '{email}', '{phone}', '{hash_pass}')")
        return redirect(url_for('main_page'))
    return render_template("registration.html", form=form, error_mes=error_mes)


@app.route("/authorization", methods=['GET', 'POST'])
def authorization():
    error = ''
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        if email:
            user_pas = db.select(f"SELECT password FROM users WHERE email='{email}'")
            error = 'Неверный e-mail'
        elif phone:
            user_pas = db.select(f"SELECT password FROM users WHERE phone='{phone}'")
            error = 'Неверный номер телефона'
        else:
            user_pas = None
            error = 'Заполните поля'
        if user_pas:
            if check_password_hash(user_pas['password'], str(password)):
                return redirect(url_for('main_page'))
    return render_template("authorization.html", error=error)


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
