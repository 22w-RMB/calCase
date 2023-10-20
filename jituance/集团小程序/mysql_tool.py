from functools import wraps

import pymysql

class MysqlTool:

    def __init__(self,host="127.0.0.1",port=3306,user="root",password="123456",database="hn_group",charset="utf8"):

        host = host
        port = port
        user = user
        password = password
        database = database
        charset = charset

        try:
            self.db = pymysql.connect(host=host,port=port,user=user,password=password,database=database,charset=charset)
            print("连接数据库成功")
            self.db.autocommit(1)
        except:
            print("连接数据库失败")

        pass



    def queryProvicneBetweenPrivateData(self):
        cursor = self.db.cursor()

        sql = "select * from data_province_clearing_result dpcr left join unit u on dpcr.unit_id=u.id where u.enable=1"


        print(sql)
        cursor.execute(sql)

        header = [col[0] for col in cursor.description]

        res = cursor.fetchall()
        cursor.close()

        return [dict(zip(header, row)) for row in res]

    def queryProvicneInnerPrivateData(self):
        cursor = self.db.cursor()

        sql = "select * from group_spot_period_data gppd left join unit u on gppd.owmer_id=u.id where u.enable=1"


        print(sql)
        cursor.execute(sql)

        header = [col[0] for col in cursor.description]

        res = cursor.fetchall()
        cursor.close()

        return [dict(zip(header, row)) for row in res]


    def close(self):
        self.db.close()

if __name__ == '__main__':


    db = MysqlTool()
    print(db.queryProvicneBetweenPrivateData()[0])

