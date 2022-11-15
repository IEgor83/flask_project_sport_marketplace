import re
import datetime
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

products = db.select(f"SELECT * FROM products")
now = datetime.datetime.now()


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().from_db(user_id, db)


@app.route("/", methods=['GET'])
def main_page():
    products_main = products
    if request.method == 'GET' and request.args:
        products_main = []
        for product in products:
            flag = True
            for cat in request.args:
                if cat not in product['category']:
                    flag = False
                    break
            if flag:
                products_main.append(product)
    return render_template("main_page.html", products=products_main)


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('user_page'))
    error_mes = ''
    form = CreateUserForm()
    if form.validate_on_submit() or UserFormEmail().validate_on_submit() or UserFormPhone().validate_on_submit():
        email = request.form.get('email')
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


@app.route("/basket", methods=['GET', 'POST'])
def basket():
    price = 0
    products_basket = db.select(f"SELECT * FROM basket"
                                   f" INNER JOIN products ON products.number = basket.product"
                                   f" WHERE basket.user_id = {current_user.get_id()}")
    if type(products_basket) is dict:
        products_basket = [products_basket]
    for prod in products_basket:
        price += prod['product_quantity'] * prod['price']
    if request.method == 'POST':
        if request.form.get('basket_del'):
            product_for_del = request.form.get('basket_del')
            db.insert(f"DELETE FROM basket WHERE product = {product_for_del} AND user_id = {current_user.get_id()};")
        elif request.form.get('quantity_change'):
            num = request.form.get('quantity_change')
            quantity = request.form.get('tentacles')
            db.insert(f"UPDATE basket SET product_quantity = '{quantity}'"
                      f" where product = {num} AND user_id = {current_user.get_id()};")
        elif request.form.get('order'):
            if price != 0:
                max_num = db.select(f"SELECT MAX(number) FROM orders")['max']
                num = max_num + 1 if max_num else 1
                db.insert(f"INSERT into orders (number, created_at, delivery_time, order_sum, status, user_id)"
                          f" VALUES ({num}, '{now.strftime('%d-%m-%Y %H:%M')}', 3, {price}, 'wait', {current_user.get_id()});")
                for pr in products_basket:
                    db.insert(f"INSERT into orders_basket (user_id, product_number, order_number, product_quantity)"
                              f" VALUES ({current_user.get_id()}, {pr['number']}, {num}, {pr['product_quantity']});")
                db.insert("TRUNCATE basket;")
                flash('Заказ успешно оформлен!')
            else:
                flash('Добавьте товары')
        return redirect(url_for('basket'))
    return render_template("basket.html", basket=products_basket, price=price)


@app.route("/favourites", methods=['GET', 'POST'])
@login_required
def favourites():
    products_favourite = db.select(f"SELECT * FROM favourites"
        f" INNER JOIN products ON products.number = favourites.product"
        f" WHERE favourites.user_id = {current_user.get_id()}")
    if type(products_favourite) is dict:
        products_favourite = [products_favourite]
    if request.method == 'POST':
        if request.form.get('favourite'):
            del_product = request.form.get('favourite')
            db.insert(f"DELETE FROM favourites WHERE product = {del_product} AND user_id = {current_user.get_id()};")
        elif request.form.get('basket'):
            add_to_basket = request.form.get('basket')
            pr_quantity = db.select(f"SELECT product_quantity FROM basket where product = {add_to_basket}"
                                    f" and user_id = {current_user.get_id()};")
            if pr_quantity:
                db.insert(f"UPDATE basket SET product_quantity = '{pr_quantity['product_quantity'] + 1}'"
                          f" WHERE user_id = {current_user.get_id()} and product = {add_to_basket};")
            else:
                db.insert(f"INSERT into basket (user_id, product, product_quantity)"
                          f"VALUES ({current_user.get_id()}, {add_to_basket}, 1);")
        return redirect(url_for('favourites'))
    return render_template("favourites.html", favourites=products_favourite)


@app.route("/orders")
@login_required
def orders():
    orders_list = db.select(f"SELECT * FROM orders WHERE user_id = {current_user.get_id()}")
    if type(orders_list) is dict:
        orders_list = [orders_list]
    print(orders_list)
    return render_template("orders.html", orders=orders_list)


@app.route("/order/<int:number>")
@login_required
def order(number):
    order_one = db.select(f"SELECT * FROM orders INNER JOIN orders_basket "
                          f"ON orders_basket.order_number = orders.number "
                          f"INNER JOIN products ON products.number = orders_basket.product_number "
                          f"WHERE orders.user_id = {current_user.get_id()} AND orders.number = {number}")
    if type(order_one) is dict:
        order_one = [order_one]
    return render_template("order.html", order=order_one)


@app.route("/user", methods=['GET', 'POST'])
@login_required
def user_page():
    param = None
    if request.method == 'POST':
        if 'change_birthday' in request.form:
            param = 'change_birthday'
            new_birthday = request.form.get('change_birthday')
            db.insert(f"UPDATE users SET birthday = '{new_birthday}' WHERE user_id = {current_user.get_id()};")
            return redirect(url_for('user_page'))
        elif 'change_phone' in request.form:
            param = 'change_phone'
            new_phone = request.form.get('change_phone')
            if new_phone is not None:
                tpl = "^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"
                if re.match(tpl, new_phone) is not None:
                    db.insert(f"UPDATE users SET phone = '{new_phone}' WHERE user_id = {current_user.get_id()};")
                    return redirect(url_for('user_page'))
                else:
                    flash('Введите корректный номер телефона', 'change_error')
            else:
                flash('Заполните поле', 'change_error')
        elif 'change_email' in request.form:
            param = 'change_email'
            new_email = request.form.get('change_email')
            if new_email is not None:
                tpl = "^[-a-z0-9!#$%&'*+/=?^_`{|}~]+(?:\.[-a-z0-9!#$%&'*+/=?^_`{|}~]+)*@" \
                      "(?:[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?\.)*(?:aero|arpa|asia|biz|cat|" \
                      "com|coop|edu|gov|info|int|jobs|mil|mobi|museum|name|net|org|pro|tel|travel|[a-z][a-z])$"
                if re.match(tpl, new_email) is not None:
                    db.insert(f"UPDATE users SET email = '{new_email}' WHERE user_id = {current_user.get_id()};")
                    return redirect(url_for('user_page'))
                else:
                    flash('Введите корректный e-mail', 'change_error')
            else:
                flash('Заполните поле', 'change_error')
        elif 'change_name' in request.form:
            param = 'change_name'
            new_name = request.form.get('change_name')
            if new_name is not None:
                if len(new_name) > 0:
                    tpl = "^[а-яА-ЯёЁa-zA-Z0-9]+$"
                    if re.match(tpl, new_name) is not None:
                        db.insert(f"UPDATE users SET name = '{new_name}' WHERE user_id = {current_user.get_id()};")
                        return redirect(url_for('user_page'))
                    else:
                        flash('Допускается латиница, кириллица и цифры', 'change_error')
                else:
                    flash('Минимум 1 символ', 'change_error')
            else:
                flash('Заполните поле', 'change_error')
    return render_template("user_page.html", param=param)


@app.route("/product/<int:number>", methods=['GET', 'POST'])
def product(number):
    if current_user.is_authenticated:
        favourite = db.select(f"SELECT product FROM favourites"
        f" WHERE user_id = {current_user.get_id()}")
        if type(favourite) is dict:
            favourite = [favourite]
    else:
        favourite = []
    favourite_products = set()
    for pr in favourite:
        favourite_products.add(pr['product'])
    product_inf = db.select(f"SELECT * FROM products WHERE number = {number}")
    if request.method == 'POST':
        if request.form.get('basket'):
            pr_quantity = db.select(f"SELECT product_quantity FROM basket where product = {product_inf['number']}"
                                    f" and user_id = {current_user.get_id()};")
            if pr_quantity:
                db.insert(f"UPDATE basket SET product_quantity = '{pr_quantity['product_quantity'] + 1}'"
                          f" WHERE user_id = {current_user.get_id()} and product = {product_inf['number']};")
            else:
                db.insert(f"INSERT into basket (user_id, product, product_quantity)"
                          f"VALUES ({current_user.get_id()}, {product_inf['number']}, 1);")
            return redirect(url_for('product', number=product_inf['number']))
        elif request.form.get('favourite'):
            db.insert(f"INSERT into favourites (user_id, product)"
                f"VALUES ({current_user.get_id()}, {product_inf['number']});")
            return redirect(url_for('product', number=product_inf['number']))
        elif request.form.get('favourite_del'):
            db.insert(f"DELETE FROM favourites WHERE product = {product_inf['number']} AND user_id = {current_user.get_id()};")
            return redirect(url_for('product', number=product_inf['number']))
    return render_template("product.html", product=product_inf, favourite=favourite_products)


if __name__ == "__main__":
    app.run(debug=True)
