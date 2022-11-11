from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, EqualTo, Regexp


class Required:
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if field.data:
            return

        if self.message is not None:
            message = self.message
        else:
            message = 'Заполните это поле'

        raise ValidationError(message)


class Length:
    def __init__(self, message=None, min=0, max=None):
        self.message = message
        self.min = min
        self.max = max

    def __call__(self, form, field):
        min_str = self.min
        max_str = self.max
        length = len(field.data) if field.data else 0
        if max_str is None:
            message = f"Длина поля должна иметь хотя бы {min_str} символов"
            if length >= min_str:
                return
        else:
            message = f"Длина поля должна иметь от {min_str} до {max_str} символов"
            if min_str <= length <= max_str:
                return

        if self.message is not None:
            message = self.message
        else:
            message = message

        raise ValidationError(message % dict(min=self.min, max=self.max, length=length))


class CreateUserForm(FlaskForm):
    email = StringField(label=('e-mail: '),
        validators=[Required(message='Заполните это поле'),
        Regexp(regex="^[-a-z0-9!#$%&'*+/=?^_`{|}~]+(?:\.[-a-z0-9!#$%&'*+/=?^_`{|}~]+)*@"\
            "(?:[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?\.)*(?:aero|arpa|asia|biz|cat|"\
                "com|coop|edu|gov|info|int|jobs|mil|mobi|museum|name|net|org|pro|tel|travel|[a-z][a-z])$",
            message='Введите корректный e-mail')])
    phone = StringField(label=('Телефон: '),
        validators=[Required(message='Заполните это поле'),
        Regexp(regex="^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$",
            message='Введите корректный номер телефона')])
    name = StringField(label=('Имя пользователя: '),
        validators=[Required(message='Заполните это поле'),
        Length(min=1, message='Имя пользователя должно содержать минимум %(min)d символ'),
        Regexp(regex="^[а-яА-ЯёЁa-zA-Z0-9]+$",
            message='Допускается латиница, кириллица и цифры')])
    password = PasswordField(label=('Пароль: '),
        validators=[Required(message='Заполните это поле'),
        Length(min=6, message='Пароль должен содержать минимум %(min)d символов')])
    confirm_password = PasswordField(
        label=('Подтверждение пароля: '),
        validators=[Required(message='Заполните это поле'),
        EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField(label=('Отправить'))


class UserFormEmail(CreateUserForm):
    phone = None


class UserFormPhone(CreateUserForm):
    email = None

