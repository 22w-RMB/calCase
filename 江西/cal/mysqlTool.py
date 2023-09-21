from functools import wraps

import pymysql

class MysqlTool:

    def __init__(self,host="127.0.0.1",port=3306,user="root",password="123456",database="jiangxi_sql",charset="utf8"):

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


    def insertContract(self,datalist):

        cursor = self.db.cursor()

        # sql = "insert into mlt_data_private(contract_name,buyer_name,seller_name,period_time_coding,ele,price,date,start_date,end_date,update_time,create_time,month,trading_session) VALUES"
        sql = "insert into mlt_data_private(contract_name,unit,buyer_name,seller_name,ele,price,date,contract_type1,contract_type2,dataType) " \
              "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"


        print("开始执行插入语句")
        cursor.executemany(sql,datalist)
        self.db.commit()
        cursor.close()
        print("插入语句执行成功")
        # @cursorOperate

    def queryContract(self,dic):

        cursor = self.db.cursor()

        sql = "select * from mlt_data_private"

        l = []

        for key in dic.keys():

            if dic[key] != None:
                if key == "start_date":
                    l.append("date" + ">=" + '"' + dic[key] + '"')
                    continue

                if key == "end_date":
                    l.append("date" + "<=" + '"' + dic[key] + '"')
                    continue
                ll = []
                for k in dic[key]:
                    ll.append(key + "=" + '"' + k + '"')

                l.append(
                    "(" + (" or ".join(ll)) + ")"
                )

        if l != []:
            if len(l) == 1:
                sql = sql + (" where ") + l[0]
            else:
                sql = sql + (" where ") + (" and ".join(l))

        print(sql)
        cursor.execute(sql)

        header = [col[0] for col in cursor.description]

        res = cursor.fetchall()
        cursor.close()

        return [dict(zip(header, row)) for row in res]

    def deleteContract(self,dic):

        cursor = self.db.cursor()

        sql = "delete from mlt_data_private"

        l = []

        for key in dic.keys():

            if dic[key] != None:

                ll = []
                for k in dic[key]:
                    ll.append( key + "=" + '"'+k+'"' )

                l.append(
                    "("+ (" or ".join(ll)) +")"
                )

        if l != []:
            if len(l) == 1:
                sql = sql + (" where ") + l[0]
            else:
                sql = sql + (" where ") + (" and ".join(l))

        print(sql)
        cursor.execute(sql)

        cursor.close()

    def queryRemoteContractData(self,dic):
        cursor = self.db.cursor()

        sql = "select ci.type as contract_type,ces.type as data_type,ces.date,ces.value as ele,ces.price , ci.name ,u.unit_name " \
              "from contract_electricity_split ces " \
              "left join contract_info ci on ces.contract_id = ci.id " \
              "left join unit u on ci.org_id = u.id "

        l = []

        for key in dic.keys():
            ll = []
            for k in dic[key]:
                ll.append(key + "=" + '"' + k + '"')

            l.append(
                "(" + (" or ".join(ll)) + ")"
            )

        if l != []:
            if len(l) == 1:
                sql = sql + (" where ") + l[0]
            else:
                sql = sql + (" where ") + (" and ".join(l))

        print(sql)
        cursor.execute(sql)

        header = [col[0] for col in cursor.description]

        res = cursor.fetchall()
        cursor.close()

        return [dict(zip(header, row)) for row in res]

    # @cursorOperate
    def insertClearingData(self,dic):

        cursor = self.db.cursor()

        sql = "replace into clearing_data(date,unit,ele,power,price,clearing_type,update_time,create_time) VALUES"


        l = [
            dic["date"],
            dic["unit"],
            dic["ele"],
            dic["power"],
            dic["price"],
            dic["dataType"],
            dic["update_time"],
            dic["create_time"],
             ]

        lStr = str(l).lstrip("[").rstrip("]")

        sql +=  "("+  lStr  +");"

        print(sql)
        cursor.execute(sql)
        cursor.close()

    def queryClearingData(self,dic):

        cursor = self.db.cursor()

        sql = "select * from clearing_data"

        l = []

        for key in dic.keys():

            if dic[key] != None:
                if key == "start_date":
                    l.append("date" + ">=" + '"'+dic[key]+'"')
                    continue

                if key == "end_date":
                    l.append("date" + "<=" + '"'+dic[key]+'"')
                    continue
                ll = []
                for k in dic[key]:
                    ll.append( key + "=" + '"'+k+'"' )

                l.append(
                    "("+ (" or ".join(ll)) +")"
                )

        if l != []:
            if len(l) == 1:
                sql = sql + (" where ") + l[0]
            else:
                sql = sql + (" where ") + (" and ".join(l))

        print(sql)
        cursor.execute(sql)

        header = [col[0] for col in cursor.description]

        res = cursor.fetchall()
        cursor.close()

        return [dict(zip(header, row)) for row in res]


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