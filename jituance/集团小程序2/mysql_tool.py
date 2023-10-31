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


        host = "192.168.1.76"
        port = port
        user = "huaneng_group_test"
        password = "qinghua123@"
        database = "huaneng_group_test"



        try:
            self.db = pymysql.connect(host=host,port=port,user=user,password=password,database=database,charset=charset)
            print("连接数据库成功")
        except:
            print("连接数据库失败")

        pass



    def queryProvicneBetweenPrivateData(self,provinceIdList,businessTypeList,startDate=None,endDate=None):
        cursor = self.db.cursor()

        sql = "select * from data_province_clearing_result dpcr join unit u on dpcr.unit_id=u.id where u.enable=1 "
        if startDate !=None and endDate!=None:
            dateSql = ' and dpcr.date>="' + startDate + '" and dpcr.date<="' + endDate+ '"'
            sql = sql + dateSql

        provinceIdSql = ' and u.province_id in ( ' + (",".join(provinceIdList)) + ')'
        sql = sql + provinceIdSql

        businessTypeSql = ' and u.business_type in ( ' + (",".join( businessTypeList ) ) +  ')'
        sql = sql + businessTypeSql

        print(sql)
        cursor.execute(sql)

        header = [col[0] for col in cursor.description]

        res = cursor.fetchall()
        cursor.close()

        return [dict(zip(header, row)) for row in res]

    def queryProvicneInnerPrivateData(self,provinceIdList,businessTypeList,startDate=None,endDate=None):
        cursor = self.db.cursor()

        sql = 'select gppd.*,u.business_type,gpd.clearing_price from group_spot_period_data gppd  join unit u on gppd.owner_id=u.id  '

        mxSql = sql + "join group_public_data gpd on gppd.province_id=gpd.province_id and gpd.type=1 and gppd.date = gpd.date "
        otherSql  = sql + "left join group_public_data gpd on gppd.province_id=gpd.province_id and gpd.type=1 and gppd.date = gpd.date "
        whereSql = "where 1 "
        mxSql = mxSql + whereSql
        otherSql = otherSql + whereSql

        if startDate !=None and endDate!=None:
            dateSql = ' and gppd.date>="' + startDate + '" and gppd.date<="' + endDate+ '"'
            mxSql = mxSql + dateSql
            otherSql = otherSql + dateSql

        businessTypeSql = ' and u.business_type in ( ' + (",".join(businessTypeList)) + ')'
        mxSql = mxSql + businessTypeSql
        otherSql = otherSql + businessTypeSql


        mxIdList = ["15"]
        otherIdList = []
        for i in provinceIdList:
            if i != "15":
                otherIdList.append(i)

        mxSqlRes = []
        otherSqlRes = []
        sqlRes = []

        if "15" in provinceIdList:
            provinceIdSql = ' and gppd.province_id in ( ' + (",".join(mxIdList)) + ')'
            mxSql = mxSql + provinceIdSql
            print(mxSql)
            cursor.execute(mxSql)
            res = cursor.fetchall()
            header = [col[0] for col in cursor.description]
            mxSqlRes = [dict(zip(header, row)) for row in res]

        if len(otherIdList)>0:
            provinceIdSql = ' and gppd.province_id in ( ' + (",".join(otherIdList)) + ')'
            otherSql = otherSql + provinceIdSql
            print(otherSql)
            cursor.execute(otherSql)
            res = cursor.fetchall()
            header = [col[0] for col in cursor.description]
            otherSqlRes = [dict(zip(header, row)) for row in res]

        sqlRes.extend(mxSqlRes)
        sqlRes.extend(otherSqlRes)

        cursor.close()

        return sqlRes


    def close(self):
        self.db.close()

if __name__ == '__main__':


    # db = MysqlTool()
    # print(db.queryProvicneBetweenPrivateData(startDate="2023-01-01",endDate="2023-01-02")[0])
    print(",".join([1, 2, 3]))
