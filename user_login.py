from flask_login import UserMixin


class UserLogin(UserMixin):
    def from_db(self, user_id, db):
        self.__user = db.get_user_by_id(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['user_id'])

    def get_user(self):
        return self.__user
