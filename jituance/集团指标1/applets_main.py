import json

import requests

from jituance.集团指标1.mysql_tool import MysqlTool
from jituance.集团指标1.provicne_inner_logic import ProInLogic
from jituance.集团指标1.provicne_between_logic import ProBeLogic
from datetime import datetime

businessTypeEnum = {
    "火电" :  1,
    "水电" :  2,
    "风电" :  4,
    "光伏" :  3,
}

provinceInIdEnum = {
    "山西": 14,
    "广东": 44,
    "甘肃": 62,
    "山东": 37,
    "蒙西": 15,
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
}


class Applkets:

    def __init__(self):

        pass

    def sqlQueryData(self, privateDataType,  provinceName ,businessTypeName,startDate,endDate):

        provinceIdList = []
        businessTypeList = []
        provinceEnum = []

        if privateDataType == "省间私有":
            provinceEnum = provinceBetIdEnum
        elif privateDataType == "省内私有":
            provinceEnum = provinceInIdEnum

        if provinceName == "全集团":
            for p in provinceEnum:
                provinceIdList.append(str(provinceEnum[p]))
        else:
            provinceIdList.append(str(provinceEnum[provinceName]))


        if businessTypeName == "全能源类型":
            for b in businessTypeEnum:
                businessTypeList.append(str(businessTypeEnum[b]))
        else:
            businessTypeList.append(str(businessTypeEnum[businessTypeName]))

        db = MysqlTool()
        dataList = []
        try:
            if privateDataType == "省间私有":
                dataList = self.transformStringToList(
                    db.queryProvicneBetweenPrivateData(provinceIdList,businessTypeList,startDate,endDate)
                )

            if privateDataType == "省内私有":
                dataList = self.transformStringToList(
                    db.queryProvicneInnerPrivateData(provinceIdList,businessTypeList,startDate,endDate)
                )

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


    # 计算省内私有数据
    def calProvicneInnerPrivateData(self,provinceName,businessTypeName,startDate,endDate):

        dataList = self.sqlQueryData( "省内私有",  provinceName ,businessTypeName,startDate,endDate)



        ProInLogic.execEntry(dataList,96)


        pass

    # 计算间私有数据
    def calProvicneBetweenPrivateData(self,provinceName,businessTypeName,startDate,endDate):

        dataList = self.sqlQueryData( "省间私有",  provinceName ,businessTypeName,startDate,endDate)

        ProBeLogic.execEntry(dataList,length=96)

        pass



    def calRunCapacity(self,startDate,endDate):
        proInAllTypeDataList = self.sqlQueryData("省内私有", "全集团","全能源类型", startDate, endDate)
        proBetwAllTypeDataList = self.sqlQueryData("省间私有", "全集团","全能源类型", startDate, endDate)

        proInAllType = ProInLogic.getFrontPageRunCapacity(proInAllTypeDataList)
        proBetwAllType = ProBeLogic.getFrontPageRunCapacity(proBetwAllTypeDataList)
        finalAllType = proInAllType + proBetwAllType

        finalData = {
            "全集团" : finalAllType,
        }
        proInData = {
            "全集团": proInAllType,
        }
        proBetwData = {
            "全集团": proBetwAllType,
        }

        for businessType in businessTypeEnum:
            proInTypeDataList = self.sqlQueryData("省内私有", "全集团", businessType, startDate, endDate)
            proBetwTypeDataList = self.sqlQueryData("省间私有", "全集团", businessType, startDate, endDate)

            proInType = ProInLogic.getFrontPageRunCapacity(proInTypeDataList)
            proBetwType = ProBeLogic.getFrontPageRunCapacity(proBetwTypeDataList)
            finalType = proInType + proBetwType
            finalData[businessType] = finalType
            proInData[businessType] = proInType
            proBetwData[businessType] = proBetwType

        print("省内+省间：",finalData)
        print("省内：",proInData)
        print("省间：",proBetwData)





    def executeMain(self,province,energy,startDate,endDate):




        pass

    def requestInterface(self):
        loginurl = "http://ihntest.gzdevops3.tsintergy.com/adsswxapp/api/wx/loginController/bind"

        loginparam = {"code": "wangming", "state": "STATE"}

        s = requests.Session()
        s.post(loginurl, json=loginparam)

        url = "http://ihntest.gzdevops3.tsintergy.com/adsswxapp/api/group/routing/trade/overview"
        param = {
            "date": "2020-04-28",
        }

        res = s.get(url, params=param).json()
        print(json.dumps(res,indent=4))

if __name__ == '__main__':

    app = Applkets()
    app.calProvicneInnerPrivateData("全集团","全能源类型","2023-09-01","2023-09-01")
    # app.calProvicneBetweenPrivateData("全集团","全能源类型","2023-10-26","2023-10-28")
    # app.calRunCapacity("2023-10-28","2023-10-28")
    # app.requestInterface()

    pass