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

    @cursorOperate
    def contract(self,cursor):

        sql = "select * from mlt_data_private"
        cursor.execute(sql)
        print("6666")


        print("你牛")
        pass

    def close(self):
        self.db.close()

if __name__ == '__main__':


    db = MysqlTool()

    db.contract()