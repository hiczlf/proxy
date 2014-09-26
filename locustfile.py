import random
from locust import HttpLocust, TaskSet, task
import MySQLdb


class StockMouser(object):

    def __init__(self):
        self.conn = MySQLdb.connect(
            host='liubei',
            user='v5v5',
            passwd='dajiayiqilai',
            charset='utf8',
            db='icbase-v5',
        )
        self.cursor = self.conn.cursor()

    def get_partnos(self):
        sql = "SELECT partno FROM icbase_stock_mouser LIMIT 5000"
        self.cursor.execute(sql)
        partnos = self.cursor.fetchall()
        return partnos


partnos = StockMouser().get_partnos()
class MyTaskSet(TaskSet):

    @task(1)
    def search(self):
        url = "/Search/Refine.aspx"
        self.client.get(url, name='search', params={'Keyword': random.choice(partnos)[0]})
        # self.client.get('/')


class MyLocust(HttpLocust):
    host = "http://cn.mouser.com/"
    task_set = MyTaskSet

if __name__ == "__main__":
    stock = StockMouser()
    partnos = stock.get_partnos()
    partno = random.choice(partnos)
    print(partno[0])
