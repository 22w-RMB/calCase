from functools import wraps

import pymysql

class MysqlTool:

    def __init__(self,host="192.168.1.76",port=3306,user="tads_gansu_test",password="qinghua123@",database="tads_aggre_service_gansu_test",charset="utf8"):

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


    def queryContract(self,unitId,startDate,endDate):

        cursor = self.db.cursor()

        sql = 'select tcd.* from tds_contract_detail as tcd ' \
              'left join (SELECT DISTINCT contract_name, month  FROM `tds_contract_price_setting`  ' \
              'where org_id = "e4dc743886b5910c0186cb539ae114ec") as temp on tcd.contract_name=temp.contract_name and SUBSTR(tcd.target_date,1,7)=temp.month ' \
              'where tcd.unit_id="' + unitId + '"'  \
              'and ( tcd.contract_type="MINUTE_HOUR_CONTRACT"  OR  temp.month IS NOT NULL ) ' \
              'and tcd.target_date>="' + startDate + '"'   \
              'and tcd.target_date<="' + endDate + '"'   \


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