from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, InputRequired, EqualTo, Length, Regexp


class CreateUserForm(FlaskForm):
    email = StringField(label=('e-mail: '),
        validators=[InputRequired(message='Заполните это поле'),
        Regexp(regex="/^[A-Z0-9._%+-]+@[A-Z0-9-]+.+.[A-Z]{2,4}$/i",
            message='Введите корректный e-mail')])
    phone = StringField(label=('Телефон: '),
        validators=[InputRequired(message='Заполните это поле'),
        Regexp(regex="^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$",
            message='Введите корректный номер телефона')])
    password = PasswordField(label=('Пароль: '),
        validators=[InputRequired(message='Заполните это поле'),
        Length(min=8, message='Пароль должен содержать минимум %(min)d символов')])
    confirm_password = PasswordField(
        label=('Подтверждение пароля: '),
        validators=[InputRequired(message='Заполните это поле'),
        EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField(label=('Отправить'))
