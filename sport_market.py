from flask import Flask, render_template, url_for, request, redirect, flash
from db_util import Database
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreateUserForm, UserFormEmail, UserFormPhone,\
    CheckAuthorization, CheckAuthorizationEmail, CheckAuthorizationPhone
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user_login import UserLogin


app = Flask(__name__)
db = Database()
app.config['SECRET_KEY'] = 'KMBbIlF9kpd3mTQk4C6zFIsXNHOw0HAk'
login_manager = LoginManager(app)
login_manager.login_view = 'authorization'
login_manager.login_message = 'Пожалуйста авторизуйтесь'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().from_db(user_id, db)


@app.route("/")
def main_page():
    return render_template("main_page.html")


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('user_page'))
    error_mes = ''
    form = CreateUserForm()
    if form.validate_on_submit() or UserFormEmail().validate_on_submit() or UserFormPhone().validate_on_submit():
        email = request.form.get('emaфil')
        phone = request.form.get('phone')
        if email and db.select(f"SELECT COUNT(*) FROM users WHERE email='{email}'")['count'] > 0:
            error_mes = 'Пользователь с таким e-mail уже существует'
            return render_template("registration.html", form=form, error_mes=error_mes)
        if phone and db.select(f"SELECT COUNT(*) FROM users WHERE phone ='{phone}'")['count'] > 0:
            error_mes = 'Пользователь с таким телефоном уже существует'
            return render_template("registration.html", form=form, error_mes=error_mes)
        name = request.form.get('name')
        hash_pass = str(generate_password_hash(request.form.get('password')))
        role = 'user'
        max_id = db.select(f"SELECT MAX(user_id) FROM users")['max']
        if max_id is not None:
            user_id = max_id + 1
        else:
            user_id = 1
        db.insert(f"INSERT into users (user_id, role, email, phone, name, password)"
                    f"VALUES ({user_id}, '{role}', '{email}', '{phone}', '{name}', '{hash_pass}')")
        if email:
            user = db.get_user_by_email(email)
        else:
            user = db.get_user_by_phone(phone)
        userlogin = UserLogin().create(user)
        login_user(userlogin)
        return redirect(url_for('main_page'))
    return render_template("registration.html", form=form, error_mes=error_mes)


@app.route("/authorization", methods=['GET', 'POST'])
def authorization():
    if current_user.is_authenticated:
        return redirect(url_for('user_page'))
    form = CheckAuthorization()
    if form.validate_on_submit() or CheckAuthorizationPhone().validate_on_submit() or CheckAuthorizationEmail().validate_on_submit():
        with open('test.txt', 'w') as f:
            f.write(str('123456'))
        email = request.form.get('email')
        phone = request.form.get('phone')
        if email:
            user = db.get_user_by_email(email)
        elif phone:
            user = db.get_user_by_phone(phone)
        else:
            user = None
        if user:
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for('main_page'))
    return render_template("authorization.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('authorization'))


@app.route("/basket")
def basket():
    return render_template("basket.html")


@app.route("/favourites")
@login_required
def favourites():
    return render_template("favourites.html")


@app.route("/orders")
@login_required
def orders():
    return render_template("orders.html")


@app.route("/user")
@login_required
def user_page():
    return render_template("user_page.html")


if __name__ == "__main__":
    app.run(debug=True)
