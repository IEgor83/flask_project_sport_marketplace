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
