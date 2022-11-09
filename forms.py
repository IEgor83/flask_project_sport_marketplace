from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, InputRequired, EqualTo, Length, Regexp


class CreateUserForm(FlaskForm):
    username = StringField(label=('Логин: '),
        validators=[InputRequired(message='Заполните это поле'),
        Length(min=6, max=16, message='Логин должен содержать от %(min)d до %(max)d символов'),
        Regexp(regex="^[a-zA-Z0-9]+$",
            message='Только латинские буквы и цифры')])
    password = PasswordField(label=('Пароль: '),
        validators=[InputRequired(message='Заполните это поле'),
        Length(min=8, message='Пароль должен содержать минимум %(min)d символов')])
    confirm_password = PasswordField(
        label=('Подтверждение пароля: '),
        validators=[InputRequired(message='Заполните это поле'),
        EqualTo('password', message='Пароли должны совпадать')])
    contacts = StringField(label=('Телефон или e-mail: '),
        validators=[InputRequired(message='Заполните это поле'),
            Regexp(regex="\+[0-9]{1,4}[0-9]{1,10}|(.*)@(.*)\.[a-z]{2,5}",
                message='Введите корректный e-mail или телефон')])
    submit = SubmitField(label=('Отправить'))
