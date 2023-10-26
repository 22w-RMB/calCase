from jituance.集团小程序2.mysql_tool import MysqlTool
from jituance.集团小程序2.provicne_inner_logic import ProInLogic
from jituance.集团小程序2.provicne_between_logic import ProBeLogic
from datetime import datetime

businessTypeEnum = {
    "全能源类型" :  "energy",
    "火电" :  1,
    "水电" :  2,
    "风电" :  4,
    "光伏" :  3,
}

provinceIdEnum = {
    "天津": 12,
    "河北": 13,
    "山西": 14,
    "蒙西": 15,
    "蒙东": 150,
    "辽宁": 21,
    "吉林": 22,
    "黑龙江": 23,
    "福建": 35,
    "四川": 51,
    "西藏": 54,
    "陕西": 61,
    "甘肃": 62,
    "青海": 63,
    "宁夏": 64,
    "新疆": 65,
    "山西": 14,
    "广东": 44,
    "甘肃": 62,
    "山东": 37,
    "蒙西": 15,
    "出清": 50,
    "安徽": 34,
    "浙江": 33,
    "上海": 31,
    "全集团" :"group",
}

provinceBetIdEnum = {
    "山西": 14,
    "河北": 13,
    "天津": 12,
    "辽宁": 21,
    "吉林": 22,
    "黑龙江": 23,
    "蒙西": 15,
    "宁夏": 64,
    "蒙东": 150,
    "青海": 63,
    "陕西": 61,
    "甘肃": 62,
    "新疆": 65,
    "福建": 35,
    "四川": 51,
    "西藏": 54,
    "重庆": 50,
    "湖北": 42,
    "全集团" :"group",
}


class Applkets:

    def __init__(self):

        pass

    def getSqlData(self,dataType,startDate,endDate):
        db = MysqlTool()
        dataList = []
        try:
            if dataType == "省间私有数据":
                dataList = self.transformStringToList(db.queryProvicneBetweenPrivateData(startDate,endDate))

            if dataType == "省内私有数据":
                dataList = self.transformStringToList(db.queryProvicneInnerPrivateData(startDate,endDate))

        except Exception as e:
            db.close()

        return dataList




    # 将数据库取到的电量、电价字符串转换成python中的数据结果
    def transformStringToList(self,dataList):

        if dataList==[] or dataList==None:
            return

        for data in dataList:
            # 需要转化的字段包含的字符
            needTransformString = ["ele" , "price","run_capacity","change_cost"]

            for key in data.keys():
                for i in needTransformString:
                    if i in key and data[key] != None:
                        # null替换成None后，python才能识别转化
                        data[key] = eval( data[key].replace("null","None") )

        return dataList

    # 筛选条件
    def provicneInnerPrivateFilterCondititon(self,province,businessType,startDate,endDate):

        # sd = datetime.strptime(startDate, "%Y-%m-%d")
        # ed = datetime.strptime(endDate, "%Y-%m-%d")
        sqlDataList = self.getSqlData("省内私有数据",startDate,endDate)
        # print("数据库查询的数据",sqlDataList)

        provinceId = provinceIdEnum[province]
        businessType = businessTypeEnum[businessType]

        filterDataList = []
        for data in sqlDataList:
            if data["province_id"] ==None:
                continue
            if provinceId != "group" and int(data["province_id"]) != provinceId:
                continue
            if businessType != "energy" and int(data["business_type"]) != businessType:
                continue

            filterDataList.append(data)

        return filterDataList

    # 筛选条件
    def provicneBetweenPrivateFilterCondititon(self,province,businessType,startDate,endDate):

        # sd = datetime.strptime(startDate, "%Y-%m-%d")
        # ed = datetime.strptime(endDate, "%Y-%m-%d")
        sqlDataList = self.getSqlData("省间私有数据",startDate,endDate)
        # print("数据库查询的数据",sqlDataList)

        provinceId = provinceBetIdEnum[province]
        businessType = businessTypeEnum[businessType]

        filterDataList = []
        for data in sqlDataList:
            if data["province_id"] ==None:
                continue
            if provinceId != "group" and int(data["province_id"]) != provinceId:
                continue
            if businessType != "energy" and int(data["business_type"]) != businessType:
                continue

            filterDataList.append(data)

        return filterDataList

    # 计算省内私有数据
    def calProvicneInnerPrivateData(self,province,businessType,startDate,endDate):

        dataList = self.provicneInnerPrivateFilterCondititon(province,businessType,startDate,endDate)
        print(dataList[0])

        d = ProInLogic.execEntry(dataList,96)

        # d = ProInLogic.otherInComeProcess(dataList)
        print(d["mlt_ele_list"])
        print(d["dayAhead_ele_list"])
        print(d["realTime_ele_list"])
        print(d["mlt_price_list"])
        print(d["dayAhead_price_list"])
        print(d["realTime_price_list"])
        print(d["change_cost_price_list"])
        print(d["realTime_income_list"])
        print(d["spot_incomeIncrease_lsit"])

        pass

    # 计算间私有数据
    def calProvicneBetweenPrivateData(self,province,businessType,startDate,endDate):

        dataList = self.provicneBetweenPrivateFilterCondititon(province,businessType,startDate,endDate)
        print(dataList[0])
        ProBeLogic.execEntry(dataList,length=96)


        pass



    def executeMain(self,province,energy,startDate,endDate):




        pass

if __name__ == '__main__':

    app = Applkets()
    # app.calProvicneInnerPrivateData("山西","全能源类型","2023-10-01","2023-10-01")
    app.calProvicneBetweenPrivateData("全集团","全能源类型","2023-10-04","2023-10-10")

    pass