import datetime
import os
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import requests
import random

from common.common import CommonClass
from gs.合同.excel_handler import ExcelHeplerXlwing
from gs.合同.mysqlTool import MysqlTool

yamlPath = r"D:\code\python\calCase\gs\config\gs_interface.yaml"


class Gansu:

    def __init__(self, session, yamlData, type):
        self.domain = None
        self.loginInfo = None
        self.session = session
        self.provinceId = "15"
        if type == "test":
            self.domain = yamlData['url_domain']['test_domain']
            self.loginInfo = yamlData['logininfo']['test_info']
        elif type == "tcloud":
            self.domain = yamlData['url_domain']['tcloud_domain']
            self.loginInfo = yamlData['logininfo']['tcloud_info']
        elif type == "hn":
            self.domain = yamlData['url_domain']['hn_domain']
            self.loginInfo = yamlData['logininfo']['hn_info']

    def login(self):
        CommonClass.login(self.session, self.domain, self.loginInfo)

    # 判断dic中是否存在对应key
    def judgeDictt(self, k , d ):

        if k not in d.keys():
            return  [None for i in range(0,96)]



    # 获取日前统一结算点电价
    def getDayAheadUnifiedSettlementPoint(self,startDate,endDate):

        url = self.domain + "/PublicDataManage/062/api/spot/area/clearingPrice/query/latest"
        method = "POST"

        requestBody = {
            "dateMerge": {
                "aggregateType": "AVG",
                "mergeType": "NONE"
            },
            "dateRanges": [{
                "start": startDate,
                "end": endDate
            }],
            "marketType": None,
            "provinceAreaId": "062",
            "timeSegment": {
                "aggregateType": None,
                "filterPoints": None,
                "segmentType": "SEG_96"
            },
            "areas": ["河西", "河东", "统一结算点"]
        }

        res = CommonClass.execRequest(self.session, method=method, url=url, json=requestBody).json()


        resDataList = res["data"]["dataList"]
        returnData = {

        }

        for i in range(0,len(resDataList)):
            if resDataList[i]["area"] == "统一结算点" and  resDataList[i]["marketType"] == "DAY_AHEAD" :
                dateStr = resDataList[i]["date"][:10]
                returnData[dateStr] = resDataList[i]["price"]


        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)
            if dateStr not in returnData.keys():
                returnData[dateStr] = [None for i in range(0,96)]

        print(res)
        print(returnData)


    # 获取私有数据
    def getPrivateData(self,unitsList,startDate,endDate):

        # 初始化
        returnData = {}
        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")
        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)
            returnData[dateStr] = {}
            for unit in unitsList:
                returnData[dateStr][unit["unitName"]] = {}

        url = self.domain + "/tads/gansu/api/power/trade/trading/curve"
        method = "GET"


        for unit in unitsList:

            unitName = unit["unitName"]

            requestBody = {
                "curveTypes": "SHORT_TERM_FORECAST,MLT_SETTLE_CURVE,BILATERAL_CLEARING,ON_LINE_SCADA_POWER,CLEARING_PRICE,PROVINCE_CLEARING_POWER,PROVINCE_CLEARING_PRICE,SELF_PLAN,REAL_TIME_PLAN,ULTRA_SHORT_TERM_FORECAST,TRANS_PROVINCIAL_SPOT_CLEARING_POWER,REAL_TIME_CLEARING_BASIS",
                "startDate": startDate,
                "endDate": endDate,
                "unitIds": unit["unitId"],
                "unitSubtypes": "DISPATCH_UNIT"
            }


            res = CommonClass.execRequest(self.session, method=method, url=url, params=requestBody).json()

            resDataList = res["data"]

            for i in range(0,len(resDataList)):
                if resDataList[i]["curveType"] == "CLEARING_PRICE" and  resDataList[i]["tradingMarketType"] == "DAY_AHEAD" :
                    dateStr = resDataList[i]["date"]
                    returnData[dateStr][unitName]["省内日前出清电价"] = resDataList[i]["dataList"]
                if resDataList[i]["curveType"] == "BILATERAL_CLEARING" and  resDataList[i]["tradingMarketType"] == "IN_TRADE_DAY" :
                    dateStr = resDataList[i]["date"]
                    returnData[dateStr][unitName]["省内日前出清电力"] = resDataList[i]["dataList"]
                if resDataList[i]["curveType"] == "PROVINCE_CLEARING_POWER" and  resDataList[i]["tradingMarketType"] == "DAY_AHEAD" :
                    dateStr = resDataList[i]["date"]
                    returnData[dateStr][unitName]["省间日前出清电力"] = resDataList[i]["dataList"]
                if resDataList[i]["curveType"] == "ON_LINE_SCADA_POWER" and  resDataList[i]["tradingMarketType"] == "IN_TRADE_DAY" :
                    dateStr = resDataList[i]["date"]
                    returnData[dateStr][unitName]["实时上网scada电力"] = resDataList[i]["dataList"]

        print(returnData)

    def getContractDetail(self,unitsList,startDate,endDate):

        # 初始化
        returnData = {}
        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")
        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)
            returnData[dateStr] = {}
            for unit in unitsList:
                returnData[dateStr][unit["unitName"]] = {}

        db = MysqlTool()
        for unit in unitsList:
            queryRes = db.queryContract(unit["unitId"],startDate,endDate)

        db.close()

        for r in queryRes:
            r["energy"] = eval(r["energy"].replace("null", "None"))
            r["price"] = eval(r["price"].replace("null", "None"))

        print(queryRes)
        return queryRes

        pass

if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    gs_test = Gansu(testSession, yamlData, "test")

    gs_test.login()

    # gs_test.getDayAheadUnifiedSettlementPoint("2024-06-01","2024-06-02")


    unitsList = [
        {
            "unitId": "e4d4ed84879e91d80187b75a2388001f",
            "unitName": "风电1期",
        },

    ]

    startDate = "2024-06-01"
    endDate = "2024-06-02"

    gs_test.getContractDetail(unitsList,startDate,endDate)


