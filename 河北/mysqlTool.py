from functools import wraps

import pymysql

class MysqlTool:

    def __init__(self,host="127.0.0.1",port=3306,user="root",password="123456",database="hebei_sql",charset="utf8"):

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

    def queryCalendar(self,dic):
        cursor = self.db.cursor()

        sql = "select id from mlt_calendar_data"

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

        res = cursor.fetchall()
        cursor.close()

        return [
            data[0] for data in res
        ]

    def queryTestContractData(self,dic):
        cursor = self.db.cursor()

        sql = "select id from mlt_contract"

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

        res = cursor.fetchall()
        cursor.close()

        return [
            data[0] for data in res
        ]

    def queryTestContractDetail(self,dic):
        cursor = self.db.cursor()

        sql = "select * from mlt_contract_details"

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
    def insertContract(self,dic):

        cursor = self.db.cursor()

        # sql = "insert into mlt_data_private(contract_name,buyer_name,seller_name,period_time_coding,ele,price,date,start_date,end_date,update_time,create_time,month,trading_session) VALUES"
        sql = "insert into mlt_data_private(contract_name,buyer_name,seller_name,period_time_coding,ele," \
              "price,date,start_date,end_date,update_time,create_time,month,trading_session,contract_type) " \
              "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"


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
        #     dic["month"],
        #     dic["trading_session"],
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
            dic["trading_session"],
            dic["contract_type"],
       ]
        # print(l)
        # lStr = str(l).lstrip("[").rstrip("]")
        #
        # sql +=  "("+  lStr  +");"

        print(sql)
        cursor.execute(sql,l)
        cursor.close()

        # @cursorOperate

    def queryContract(self,dic):

        cursor = self.db.cursor()

        sql = "select * from mlt_data_private"

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


    # @cursorOperate
    def insertSessionIdConfig(self,dic):

        cursor = self.db.cursor()

        sql = "replace into session_id_config(month,period_time_coding,time,haveRatio,ratio,update_time,create_time) VALUES"


        l = [
            dic["month"],
            dic["period_time_coding"],
            dic["time"],
            dic["haveRatio"],
            dic["ratio"],
            dic["update_time"],
            dic["create_time"],
             ]

        lStr = str(l).lstrip("[").rstrip("]")

        sql +=  "("+  lStr  +");"

        print(sql)
        cursor.execute(sql)
        cursor.close()

    # @cursorOperate
    def querySessionIdConfig(self):

        cursor = self.db.cursor()

        sql = "select * from session_id_config"

        cursor.execute(sql)

        header = [col[0] for col in cursor.description]

        res = cursor.fetchall()
        cursor.close()

        return [dict(zip(header,row)) for row in res]


    # @cursorOperate
    def insertPeakPinggu(self,dic):

        cursor = self.db.cursor()

        sql = "replace into peak_pinggu(month,peak_type,time,update_time,create_time) VALUES"


        l = [
            dic["month"],
            dic["peak_type"],
            dic["time"],
            dic["update_time"],
            dic["create_time"],
             ]

        lStr = str(l).lstrip("[").rstrip("]")

        sql +=  "("+  lStr  +");"

        print(sql)
        cursor.execute(sql)
        cursor.close()

    # @cursorOperate
    def queryPeakPinggu(self):

        cursor = self.db.cursor()

        sql = "select * from peak_pinggu"

        cursor.execute(sql)

        header = [col[0] for col in cursor.description]

        res = cursor.fetchall()
        cursor.close()

        return [dict(zip(header,row)) for row in res]


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