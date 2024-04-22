import datetime
import os
import time
from datetime import datetime, timedelta

import requests
import random

from common.common import CommonClass
from mx.mysqlTool import MysqlTool

yamlPath = r"D:\code\python\calCase\mx\config\mx_interface.yaml"


enumType = {
    # 交易类型
    "mltSort": [
                {
                    "name": "双边协商",
                    "id": "1"
                },
                {
                    "name": "跨省跨区",
                    "id": "2"
                },
                {
                    "name": "省间现货",
                    "id": "3"
                },
                {
                    "name": "基数",
                    "id": "4"
                },
                {
                    "name": "集中竞价",
                    "id": "5"
                },
                {
                    "name": "置换增量",
                    "id": "6"
                },
                {
                    "name": "置换转让",
                    "id": "7"
                },
                {
                    "name": "挂牌交易",
                    "id": "8"
                }
            ],

    #合同区域
    "mltArea": [
        {
            "name": "全网统一出清",
            "id": "1"
        },
        {
            "name": "东区",
            "id": "2"
        },
        {
            "name": "西区",
            "id": "3"
        }
    ],
    "contractTradeCycle": [
        {
            "name": "年度",
            "id": "1"
        },
        {
            "name": "多月",
            "id": "2"
        },
        {
            "name": "月度",
            "id": "3"
        },
        {
            "name": "月内",
            "id": "4"
        }
    ],
    "contractType": [
        {
            "name": "省内合同",
            "id": "1"
        },
        {
            "name": "省间合同",
            "id": "2"
        }
    ],
}


class Mengxi:

    def __init__(self,session, yamlData, type):
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

    def createUnit(self,unitsInfo):

        url = self.domain + "/mxfire/api/unit/basic"
        method = "POST"
        for unit in unitsInfo:
            data = {
               "businessType": unit['businessType'],
               "isNew":   True,
               "edit": True,
               "unitName": unit['unitName'],
               "acNodeIds" : ["e4dbf97d8200200d0182007fbd0b0002"],
            }
            print(data)
            res = CommonClass.execRequest(self.session,method=method,url=url,json=data)
            print(res)
        pass

    def getFireUnit(self):
        url = self.domain + "/mxfire/api/unit/list"
        method = "GET"
        res = CommonClass.execRequest(self.session, method=method, url=url).json()['data']
        unitsInfo = []

        for r in res:
            unitsInfo.append(
                {
                    "unitId" : r['id'],
                    "unitName" : r['unitName'],
                    "businessType" : r['businessType'],
                }
            )
        return unitsInfo

    def deleteUnit(self,filterUnits=[]):

        unitsInfo = self.getFireUnit()

        method = "DELETE"
        for unit in unitsInfo:

            if unit['unitName'] in filterUnits:
                continue

            url = self.domain + "/mxfire/api/ex/unit/basic/" +  unit['unitId']

            res = CommonClass.execRequest(self.session, method=method, url=url).json()
            print(res)

        pass

    def generateContractRequestData(self,startDate,endDate,unit):

        contractDTO = {
            "ownerId": unit["unitId"],
            "mltSort": str(random.randint(1, 8)),
            "contractName": "随机合同",
            "area": random.randint(1, 3),
            "tradeCycle": str(random.randint(1, 4)),
            "contractType": str(random.randint(1, 2)),
            "netLossRatio": random.randint(0, 10000)/100,
            "oppositeSide": "对方名称",
            "startDate": startDate,
            "endDate": endDate,
            "createTime": "2024-04-17"
        }

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")
        contractDataDTOList = []

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)
            ele = [ round(random.randint(0, unit["capacity"])/4/10/40,2) for _ in range(96)]
            price = [ round(random.randint(10000, 100000)/100,2) for _ in range(96)]

            tempDic = {
                "date": dateStr,
                "type": 3,
                "checkType": False,
                "price": price,
                "value": ele
            }
            contractDataDTOList.append(tempDic)


        # print(contractDTO)
        return {
            "contractDTO" :contractDTO,
            "contractPurchaseSaleRelated": [],
            "contractDataDTOList": contractDataDTOList
        }


    # def requesetContract(self):
    #
    #     requesetData = {
    #         "contractDTO": {
    #             "ownerId": unitId,
    #             "mltSort": "1",
    #             "contractName": "光伏 双边协商合同",
    #             "area": "1",
    #             "netLossRatio": 0,
    #             "oppositeSide": "1",
    #             "startDate": "2024-05-01",
    #             "endDate": "2024-05-02",
    #             "createTime": "2024-04-17"
    #         },
    #         "contractPurchaseSaleRelated": [],
    #         "contractDataDTOList": [{
    #             "date": "2024-05-01",
    #             "type": 3,
    #             "checkType": False,
    #             "price": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "value": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #         }, {
    #             "date": "2024-05-02",
    #             "type": 3,
    #             "checkType": False,
    #             "price": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             "value": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #         }]
    #     }
    #
    #     pass

    def writeContractIntoMysql(self,unit,requestData):

        contractDTO = requestData["contractDTO"]
        contractDataDTOList = requestData["contractDataDTOList"]

        writeSqlList = []
        # print(requestData)

        for contractDataDTO in contractDataDTOList:

            writeSqlList.append(
                (
                    # unit_id,
                    unit["unitId"],
                    # unit_name,
                    unit["unitName"],
                    # contract_name,
                    contractDTO["contractName"],
                    # date,
                    contractDataDTO["date"],
                    # opposite_side,
                    contractDTO["oppositeSide"],
                    # contract_type,
                    contractDTO["contractType"],
                    # mlt_sort,
                    contractDTO["mltSort"],
                    # trade_cycle,
                    contractDTO["tradeCycle"],
                    # net_loss_ratio,
                    contractDTO["netLossRatio"],
                    # ele,
                    str(contractDataDTO["value"]),
                    # price,
                    str(contractDataDTO["price"]),
                    # start_date,
                    contractDTO["startDate"],
                    # end_date
                    contractDTO["endDate"],
                )
            )


        print(writeSqlList[0])
        db = MysqlTool()
        db.insertContract(writeSqlList)
        db.close()

        pass

    def queryLocalContract(self,unitName, contractType, mltSort, tradeCycle, startDate, endDate):

        contract_type = self.transformEnum("contractType",contractType)
        mlt_sort = self.transformEnum("mltSort",mltSort)
        trade_cycle = self.transformEnum("contractTradeCycle",tradeCycle)

        d = {
            "unit_name": unitName,
            "contract_type": contract_type,
            "mlt_sort": mlt_sort,
            "trade_cycle": trade_cycle,
            "start_date": startDate,
            "end_date": endDate,
        }


        db = MysqlTool()

        queryRes = db.queryContract(d)

        db.close()

        for r in queryRes:
            r["ele"] = eval(r["ele"].replace("null", "None"))
            r["price"] = eval(r["price"].replace("null", "None"))

        print(queryRes)

        return queryRes

    def transformEnum(self,typeName,typeList):

        ty = enumType[typeName]
        resultList = []

        for t in typeList:

            for tt in ty:
                if tt["name"] == t:
                    resultList.append(tt["id"])
                    break


        pass


    def calContract(self,unitName, contractType, mltSort, tradeCycle, startDate, endDate):

        queryRes = self.queryLocalContract(unitName, contractType, mltSort, tradeCycle, startDate, endDate)


        time96List = {

        }

        dayData = {

        }

        monthData = {

        }

        for res in queryRes:
            dateStr = datetime.strftime(res["date"], "%Y-%m-%d")
            monthStr = datetime.strftime(res["date"], "%Y-%m")

            if dateStr not in dayData.keys():
                dayData[dateStr] = {
                    "ele" : [None for i in range(0,96)],
                    "price" : [None for i in range(0,96)],
                    "fee" : [None for i in range(0,96)],
                    "eleSum": [None for i in range(0, 96)],
                    "priceSum": [None for i in range(0, 96)],
                    "feeSum": [None for i in range(0, 96)],
                }

            if dateStr not in dayData.keys():
                monthData[monthStr] = {
                    "ele": [None for i in range(0, 96)],
                    "price": [None for i in range(0, 96)],
                    "fee": [None for i in range(0, 96)],
                    "eleSum": [None for i in range(0, 96)],
                    "priceSum": [None for i in range(0, 96)],
                    "feeSum": [None for i in range(0, 96)],
                }



        pass

    def calData(self):

        pass

if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    mx_test = Mengxi(testSession,yamlData,"hn")

    # mx_test.login()

    unit = {
        "unitId": "23",
        "unitName": "bteas",
        "capacity": 580,
    }

    startDate = "2024-04-01"
    endDate = "2024-04-02"

    # for i in range(1,10):
    #     resquestData = mx_test.generateContractRequestData(startDate,endDate,unit)
    #     mx_test.writeContractIntoMysql(unit,resquestData)

    mx_test.queryLocalContract(["bteas"],["省内合同"], ["双边协商"], ["年度"], "2024-04-01", "2024-04-01")

