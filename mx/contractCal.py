import datetime
import os
import time
from datetime import datetime, timedelta

import requests
import random

from common.common import CommonClass
from mx.excel_handler import ExcelHeplerXlwing
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




        dayData = {

        }

        monthData = {

        }

        for res in queryRes:
            dateStr = datetime.strftime(res["date"], "%Y-%m-%d")
            monthStr = datetime.strftime(res["date"], "%Y-%m")

            if dateStr not in dayData.keys():
                dayData[dateStr] = []

            if monthStr not in dayData.keys():
                monthData[monthStr] = []

            ele = res["ele"]
            price = res["price"]

            dayData[dateStr].append({
                "ele" : ele,
                "price" : price,
            })

            monthData[monthStr].append({
                "ele" : ele,
                "price" : price,
            })



        dayRes = self.calData(dayData)
        monthRes = self.calData(monthData)

        print(dayRes)
        print(monthRes)

        inputData = {
            "day": dayRes,
            "month": monthRes,
        }
        self.outputData(inputData)


    def calData(self,dateDict):

        resDateDict = {
            "all" : {
                "eleSum" : 0,
                "priceSum" : 0,
                "feeSum" : 0,
                "absEleSum": 0,
                "absPriceSum": 0,
                "absFeeSum": 0,
            }
        }

        for date in dateDict.keys():

            dateData = dateDict[date]
            ele = [0 for i in range(0,96)]
            absEle = [0 for i in range(0,96)]
            price = [0 for i in range(0,96)]
            absPrice = [0 for i in range(0,96)]
            fee = [0 for i in range(0,96)]
            absFee = [0 for i in range(0,96)]


            for i in range(0,len(dateData)):

                indexData = dateData[i]

                for j in range(0,96):
                    if indexData["ele"][j] != None :
                        ele[j] += indexData["ele"][j]
                        absEle[j] += abs(indexData["ele"][j])

                    if indexData["price"][j] == None or indexData["ele"][j] == None :
                        continue

                    fee[j] =   fee[j] + ( indexData["ele"][j] * indexData["price"][j])
                    absFee[j] =   fee[j] + ( abs(indexData["ele"][j]) * indexData["price"][j])

            eleSum = 0
            absEleSum = 0

            feeSum = 0
            absFeeSum = 0
            for i in range(0,96):
                price[i] = None if ele[i] == 0 else fee[i]/ele[i]
                absPrice[i] = None if absEle[i] == 0 else absFee[i]/absEle[i]

                eleSum += ele[i]
                absEleSum += absEle[i]
                feeSum += fee[i]
                absFeeSum += absFee[i]

            priceSum = None if eleSum == 0 else feeSum/eleSum
            absPriceSum = None if eleSum == 0 else absFeeSum/absEleSum

            resDateDict[date] = {
                "ele" : ele,
                "price" : price,
                "fee" : fee,
                "absEle" : absEle,
                "absPrice" : absPrice,
                "absFee" : absFee,
                "eleSum" : eleSum,
                "priceSum" : priceSum,
                "feeSum" : feeSum,
                "absEleSum" : absEleSum,
                "absPriceSum" : absPriceSum,
                "absFeeSum" : absFeeSum,
            }

        for key in resDateDict.keys():

            if key == "all":

                continue

            resDateDict["all"]["eleSum"] += resDateDict[key]["eleSum"]
            resDateDict["all"]["feeSum"] += resDateDict[key]["feeSum"]
            resDateDict["all"]["absEleSum"] += resDateDict[key]["absEleSum"]
            resDateDict["all"]["absFeeSum"] += resDateDict[key]["absFeeSum"]

        resDateDict["all"]["priceSum"] = None if resDateDict["all"]["eleSum"] == 0 else resDateDict["all"]["feeSum"] / resDateDict["all"]["eleSum"]
        resDateDict["all"]["absPriceSum"] = None if resDateDict["all"]["absEleSum"] == 0 else resDateDict["all"]["absFeeSum"] / resDateDict["all"]["absEleSum"]

        return resDateDict

    # 输出到excel
    def outputData(self,inputData):

        # sd = datetime.strptime(startDate, "%Y-%m-%d")
        # ed = datetime.strptime(endDate, "%Y-%m-%d")

        resData = {}
        dayData = inputData["day"]
        monthData = inputData["month"]

        print(dayData)
        print(monthData)

        for date in dayData.keys():
            if date=="all":
                continue

            dateResData = []
            # dateResData.append(
            #     # ["日期","机组", "合约类型", "电量/电价", "合计/均值"],
            # )

            ele = [date,"全厂", "中长期总体", "电量" ,dayData[date]["eleSum"]]
            ele.extend(dayData[date]["ele"])
            price = [date,"全厂", "中长期总体", "电价" ,dayData[date]["priceSum"]]
            price.extend(dayData[date]["price"])
            fee = [date,"全厂", "中长期总体", "电费" ,dayData[date]["feeSum"]]
            fee.extend(dayData[date]["fee"])

            absEle = [date,"全厂", "中长期总体", "累计交易电量" ,dayData[date]["absEleSum"]]
            absEle.extend(dayData[date]["absEle"])
            absPrice = [date,"全厂", "中长期总体", "累计交易电价" ,dayData[date]["absPriceSum"]]
            absPrice.extend(dayData[date]["absPrice"])
            absFee = [date,"全厂", "中长期总体", "累计交易电费" ,dayData[date]["absFeeSum"]]
            absFee.extend(dayData[date]["absFee"])

            dateResData.append(ele)
            dateResData.append(price)
            dateResData.append(fee)
            dateResData.append(absEle)
            dateResData.append(absPrice)
            dateResData.append(absFee)
            resData[date] = dateResData




        monthResData = []
        monthSheetHeader = ["机组", "合约类型", "电量/电价", "合计/均值"]
        monthSheetHeader.extend(monthData.keys())

        monthele = ["全厂", "中长期总体", "电量", monthData["all"]["eleSum"]]
        monthprice = ["全厂", "中长期总体", "电价", monthData["all"]["priceSum"]]
        monthfee = ["全厂", "中长期总体", "电费", monthData["all"]["feeSum"]]
        monthabsEle = ["全厂", "中长期总体", "累计交易电量", monthData["all"]["absEleSum"]]
        monthabsPrice = ["全厂", "中长期总体", "累计交易电价", monthData["all"]["absPriceSum"]]
        monthabsFee = ["全厂", "中长期总体", "累计交易电费", monthData["all"]["absFeeSum"]]

        monthResData.append(monthSheetHeader)
        monthResData.append(monthele)
        monthResData.append(monthprice)
        monthResData.append(monthfee)
        monthResData.append(monthabsEle)
        monthResData.append(monthabsPrice)
        monthResData.append(monthabsFee)

        for month in monthData.keys():


            monthele.append(monthData[month]["eleSum"])
            monthprice.append(monthData[month]["priceSum"])
            monthfee.append(monthData[month]["feeSum"])

            monthabsEle.append(monthData[month]["absEleSum"])
            monthabsPrice.append(monthData[month]["absPriceSum"])
            monthabsFee.append(monthData[month]["absFeeSum"])




        # while sd <= ed:
        #     dateStr = datetime.strftime(sd, "%Y-%m-%d")
        #     dateResData[0].append(dateStr)
        #
        #
        #     # 日期 +1
        #     sd += timedelta(days=1)
        #
        # for date in resData:
        #
        #     if len(dateResData) - 1 < len(resData[date]):
        #         for data in resData[date]:
        #             dateResData.append(data[0:4])
        #         continue
        #
        #     for i in range(0, len(resData[date])):
        #         dateResData[i + 1].append(resData[date][i][3])

        tempPath = CommonClass.mkDir("mx", "导出模板", "持仓总览模板.xlsx", isGetStr=True)
        templateE = ExcelHeplerXlwing(tempPath)
        template = templateE.getTemplateStyle("Sheet1")
        templateE.close()

        # print(resData)

        savePath = CommonClass.mkDir("mx", "导出模板", "持仓总览结果.xlsx", isGetStr=True)
        e = ExcelHeplerXlwing()

        print(resData)
        print(monthResData)
        try:
            for date in resData:
                e.newExcel(sheetName=date, templateStyle=template)
                e.writeData(savePath, resData[date], date)

            e.newExcel(sheetName="月维度")
            e.writeData(savePath, monthResData, "月维度", beginRow=1)
        finally:
            e.close()

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

    startDate = "2024-03-31"
    endDate = "2024-04-02"

    for i in range(1,10):
        resquestData = mx_test.generateContractRequestData(startDate,endDate,unit)
        mx_test.writeContractIntoMysql(unit,resquestData)

    mx_test.calContract(["bteas"],["省内合同"], ["双边协商"], ["年度"], "2024-03-30", "2024-04-01")

