import psycopg2
from decouple import config


class Database:
    def __init__(self):
        self.con = psycopg2.connect(
            dbname="sportshop",
            user="postgres",
            password=config('password', default=''),
            host="localhost",
            port=5432
        )
        self.cur = self.con.cursor()

    def select(self, query):
        self.cur.execute(query)
        data = self.prepare_data(self.cur.fetchall())
        if len(data) == 1:
            data = data[0]

        return data

    def insert(self, query):
        self.cur.execute(query)
        self.con.commit()

    def prepare_data(self, data):
        mas = []
        if len(data):
            column_names = [desc[0] for desc in self.cur.description]
            for row in data:
                mas += [{c_name: row[key] for key, c_name in enumerate(column_names)}]

        return mas

    def get_user_by_id(self, user_id):
        res = self.select(f"SELECT * FROM users WHERE user_id = {user_id} LIMIT 1")
        if not res:
            return False
        return res

    def get_user_by_email(self, email):
        res = self.select(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
        if not res:
            return False
        return res

    def get_user_by_phone(self, phone):
        res = self.select(f"SELECT * FROM users WHERE phone = '{phone}' LIMIT 1")
        if not res:
            return False
        return res