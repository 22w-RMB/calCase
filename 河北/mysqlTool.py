from functools import wraps

import pymysql

class MysqlTool:

    def __init__(self,host=None,port=None,user=None,password=None,database=None,chatset=None):

        host = "127.0.0.1"
        port = 3306
        user = "root"
        password = "123456"
        database = "hebei_sql"
        charset = "utf8"

        try:
            self.db = pymysql.connect(host=host,port=port,user=user,password=password,database=database,charset=charset)
            print("连接数据库成功")
            self.db.autocommit(1)
        except:
            print("连接数据库失败")

        pass


    def cursorOperate(func):
        @wraps(func)
        def wrapper(self,*args, **kwargs):

            cursor = self.db.cursor()
            print("777")


            func(self, cursor=cursor,*args, **kwargs)

            for row in cursor.fetchall():

                pass
            cursor.close()

        return wrapper

    # @cursorOperate
    def insertContract(self,dic):

        cursor = self.db.cursor()

        sql = "insert into mlt_data_private(contract_name,buyer_name,seller_name,period_time_coding,ele,price,date,start_date,end_date,update_time,create_time,month) VALUES"

        # l = [
        #     dic["contract_name"],
        #     dic["buyer_name"],
        #     dic["seller_name"],
        #     dic["period_time_coding"],
        #     dic["ele"],
        #     dic["price"],
        #     dic["date"],
        #     dic["start_date"],
        #     dic["end_date"],
        #     dic["update_time"],
        #     dic["create_time"],
        #      ]

        l = [
            dic["contract_name"],
            dic["buyer_name"],
            dic["seller_name"],
            dic["period_time_coding"],
            dic["ele"],
            dic["price"],
            dic["date"],
            dic["start_date"],
            dic["end_date"],
            dic["update_time"],
            dic["create_time"],
            dic["month"],
             ]

        lStr = str(l).replace("[","").replace("]","")

        sql +=  "("+  lStr  +");"

        print(sql)
        cursor.execute(sql)
        cursor.close()

    def close(self):
        self.db.close()

if __name__ == '__main__':


    # db = MysqlTool()

    d = {
        "contract_name" : "dsa",
        "buyer_name" : "few",
        "seller_name" : "",
        "period_time_coding" : "",
        "ele" : "",
        "price" : "",
        "date" : "",
        "start_date" : "",
        "end_date" : "",
        "update_time" : "",
        "create_time" : "",

    }

    # db.insertContract("1",d)