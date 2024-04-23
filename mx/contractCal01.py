import datetime
import os
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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

# enumOrder = [
#     "双边协商",
#     "跨省跨区",
#     "省间现货",
#     "基数",
#     "集中竞价",
#     "置换增量",
#     "置换转让",
#     "挂牌交易",
# ]

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
            ele = [ random.choice([-1,1])*round(random.randint(0, round(unit["capacity"],0))/4/10/40,2) for i in range(0,96)]
            price = [ round(random.randint(10000, 100000)/100,2) for i in range(0,96)]

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

    def requestContract(self,requestData):

        url = self.domain + "/mxfire/api/mlt/contract"
        method = "POST"

        res = CommonClass.execRequest(self.session, method=method, url=url, json=requestData)
        print(res.json())

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


        # print(writeSqlList[0])
        db = MysqlTool()
        db.insertContract(writeSqlList)
        db.close()

        pass

    def queryLocalContract(self,unitName, contractType, mltSort, tradeCycle, startDate, endDate):

        contract_type = self.transformEnum("contractType",contractType)
        mlt_sort = self.transformEnum("mltSort",mltSort)
        print("=======",mlt_sort)
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


        return queryRes

    def transformEnum(self,typeName,typeList):

        ty = enumType[typeName]
        resultList = []
        if typeList == None:
            for tt in ty:
                resultList.append(tt["id"])

        else:
            for t in typeList:

                for tt in ty:
                    if tt["name"] == t:
                        resultList.append(tt["id"])
                        break

        return resultList


    #
    def calContract(self,unitNameList, contractTypeList, mltSortList, tradeCycleList, startDate, endDate):

        queryRes = self.queryLocalContract(unitNameList, contractTypeList, mltSortList, tradeCycleList, startDate, endDate)

        dayData = {

        }

        monthData = {

        }

        for res in queryRes:
            dateStr = datetime.strftime(res["date"], "%Y-%m-%d")
            monthStr = datetime.strftime(res["date"], "%Y-%m")

            if dateStr not in dayData.keys():
                dayData[dateStr] = []

            if monthStr not in monthData.keys():
                monthData[monthStr] = []

            ele = res["ele"]
            price = res["price"]
            net_loss_ratio = res["net_loss_ratio"]

            dayData[dateStr].append({
                "ele" : ele,
                "price" : price,
                "net_loss_ratio" : net_loss_ratio,
            })

            monthData[monthStr].append({
                "ele" : ele,
                "price" : price,
                "net_loss_ratio" : net_loss_ratio,
            })

        dayRes = self.calData(dayData)
        monthRes = self.calData(monthData)

        inputData = {
            "day": dayRes,
            "month": monthRes,
        }

        return inputData



    def execMain(self,unitNameList, contractTypeList, mltSortList, tradeCycleList, startDate, endDate):

        allUnitData = {

        }


        for unitName in unitNameList:
            allUnitData[unitName] = {}
            nameList = unitNameList[1:] if unitName =="all" else [unitName]
            for mltSort in mltSortList:
                sortList = mltSortList[1:] if mltSort =="all" else [mltSort]
                res = self.calContract(nameList, contractTypeList, sortList, tradeCycleList, startDate, endDate)
                allUnitData[unitName][mltSort] = res


        # print(allUnitData)
        self.outputData(allUnitData,startDate, endDate)

    # 计算合同数据
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
                # print("===========",indexData)

                for j in range(0,96):
                    if indexData["ele"][j] != None :
                        ele[j] = ele[j] + indexData["ele"][j]/(1-indexData["net_loss_ratio"]/100)
                        absEle[j] = absEle[j] + abs(indexData["ele"][j])/(1-indexData["net_loss_ratio"]/100)

                    if indexData["price"][j] == None or indexData["ele"][j] == None :
                        continue

                    fee[j] =   fee[j] + ( indexData["ele"][j]/(1-indexData["net_loss_ratio"]/100) * indexData["price"][j])
                    absFee[j] =   absFee[j] + ( abs(indexData["ele"][j])/(1-indexData["net_loss_ratio"]/100) * indexData["price"][j])

            eleSum = 0
            absEleSum = 0

            feeSum = 0
            absFeeSum = 0
            for i in range(0,96):

                eleSum += ele[i]
                absEleSum += absEle[i]
                feeSum += fee[i]
                absFeeSum += absFee[i]

                price[i] = None if ele[i] == 0 else fee[i]/ele[i]
                absPrice[i] = None if absEle[i] == 0 else absFee[i]/absEle[i]



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


    def outputData(self,inputData,startDate, endDate):



        dateData = self.outputDayDataGenertate( inputData, startDate, endDate)
        monthData = self.outputMonthDataGenertate( inputData, startDate, endDate)

        try:
            tempPath = CommonClass.mkDir("mx", "导出模板", "持仓总览模板.xlsx", isGetStr=True)
            templateE = ExcelHeplerXlwing(tempPath)
            template = templateE.getTemplateStyle("Sheet1")
        finally:
            templateE.close()

        # print(resData)

        savePath = CommonClass.mkDir("mx", "导出模板", "持仓总览结果.xlsx", isGetStr=True)
        e = ExcelHeplerXlwing()

        try:
            for date in dateData:
                e.newExcel(sheetName=date, templateStyle=template)
                e.writeData(savePath, dateData[date], date)
            e.newExcel(sheetName="月维度")
            e.writeData(savePath, monthData, "月维度",beginRow=1)
        finally:
            e.close()

        pass


    def outputDayDataGenertate(self,inputData,startDate, endDate):
        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        dateData = {}

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")

            sd += timedelta(days=1)
            dateData[dateStr] = []

            for unit in inputData:

                unitName = "汇总" if unit == "all" else unit

                for mltSort in inputData[unit].keys():

                    sortName = "中长期总体" if mltSort == "all" else mltSort

                    sortDayData = inputData[unit][mltSort]["day"]
                    if dateStr not in sortDayData.keys():
                        ele = [unitName, sortName, "电量", None]
                        ele.extend([None for i in range(0, 96)])
                        price = [unitName, sortName, "电价", None]
                        price.extend([None for i in range(0, 96)])
                        fee = [unitName, sortName, "费用", None]
                        fee.extend([None for i in range(0, 96)])
                        absEle = [unitName, sortName, "累计交易电量", None]
                        absEle.extend([None for i in range(0, 96)])
                        absPrice = [unitName, sortName, "累计交易电价", None]
                        absPrice.extend([None for i in range(0, 96)])
                        absFee = [unitName, sortName, "累计交易费用", None]
                        absFee.extend([None for i in range(0, 96)])
                        dateData[dateStr].append(ele)
                        dateData[dateStr].append(price)
                        dateData[dateStr].append(fee)
                        dateData[dateStr].append(absEle)
                        dateData[dateStr].append(absPrice)
                        dateData[dateStr].append(absFee)

                        continue

                    ele = [unitName, sortName, "电量", sortDayData[dateStr]["eleSum"]]
                    ele.extend(sortDayData[dateStr]["ele"])
                    price = [unitName, sortName, "电价", sortDayData[dateStr]["priceSum"]]
                    price.extend(sortDayData[dateStr]["price"])
                    fee = [unitName, sortName, "费用", sortDayData[dateStr]["feeSum"]]
                    fee.extend(sortDayData[dateStr]["fee"])

                    absEle = [unitName, sortName, "累计交易电量", sortDayData[dateStr]["absEleSum"]]
                    absEle.extend(sortDayData[dateStr]["absEle"])
                    absPrice = [unitName, sortName, "累计交易电价", sortDayData[dateStr]["absPriceSum"]]
                    absPrice.extend(sortDayData[dateStr]["absPrice"])
                    absFee = [unitName, sortName, "累计交易费用", sortDayData[dateStr]["absFeeSum"]]
                    absFee.extend(sortDayData[dateStr]["absFee"])

                    dateData[dateStr].append(ele)
                    dateData[dateStr].append(price)
                    dateData[dateStr].append(fee)
                    dateData[dateStr].append(absEle)
                    dateData[dateStr].append(absPrice)
                    dateData[dateStr].append(absFee)

        return dateData

    def outputMonthDataGenertate(self, inputData, startDate, endDate):
        sd = datetime.strptime(startDate[:7], "%Y-%m")
        ed = datetime.strptime(endDate[:7], "%Y-%m")

        dateData = {}
        dateData["0"] =  ["机组", "合约类型", "电量/电价", "合计/均值"]


        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m")
            dateData["0"].append(dateStr)

            sd += relativedelta(months=1)
            count = 1

            for unit in inputData:

                unitName = "汇总" if unit == "all" else unit

                for mltSort in inputData[unit].keys():

                    sortName = "中长期总体" if mltSort == "all" else mltSort

                    sortDayData = inputData[unit][mltSort]["month"]

                    if str(count) not in dateData.keys():
                        dateData[str(count)] = [unitName,sortName,"电量",sortDayData["all"]["eleSum"]]
                        dateData[str(count+1)] = [unitName,sortName,"电价",sortDayData["all"]["priceSum"]]
                        dateData[str(count+2)] = [unitName,sortName,"电费",sortDayData["all"]["feeSum"]]
                        dateData[str(count+3)] = [unitName,sortName,"累计交易电量",sortDayData["all"]["absEleSum"]]
                        dateData[str(count+4)] = [unitName,sortName,"累计交易均价",sortDayData["all"]["absPriceSum"]]
                        dateData[str(count+5)] = [unitName,sortName,"累计交易电费",sortDayData["all"]["absFeeSum"]]

                    if dateStr not in sortDayData.keys():
                        dateData[str(count)].append(None)
                        dateData[str(count + 1)].append(None)
                        dateData[str(count + 2)].append(None)
                        dateData[str(count + 3)].append(None)
                        dateData[str(count + 4)].append(None)
                        dateData[str(count + 5)].append(None)
                    else:
                        dateData[str(count)] .append(sortDayData[dateStr]["eleSum"])
                        dateData[str(count+1)] .append(sortDayData[dateStr]["priceSum"])
                        dateData[str(count+2)] .append(sortDayData[dateStr]["feeSum"])
                        dateData[str(count+3)] .append(sortDayData[dateStr]["absEleSum"])
                        dateData[str(count+4)] .append(sortDayData[dateStr]["absPriceSum"])
                        dateData[str(count+5)] .append(sortDayData[dateStr]["absFeeSum"])

                    count += 6
        dList = []
        for key in dateData.keys():
            dList.append(dateData[key])
        return dList


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    mx_test = Mengxi(testSession,yamlData,"hn")

    # mx_test.login()

    units = [
        {
            "unitId": "e4e4b4b48f08bd51018f08bfdfeb0001",
            "unitName": "火电合同#1",
            "capacity": 500,
        },
        {
            "unitId": "e4e4b4b48f08bd51018f08c0346e0003",
            "unitName": "火电合同#2",
            "capacity": 488.3,
        },
        {
            "unitId": "e4e4b4b48f08bd51018f08c006fd0002",
            "unitName": "风电合同#1",
            "capacity": 100,
        },
        {
            "unitId": "e4e4b4b48f08bd51018f08c06ac30004",
            "unitName": "水电合同#1",
            "capacity": 580,
        },
    ]

    startDate = "2024-05-01"
    endDate = "2024-06-02"

    # for unit in units:
    #     for i in range(1,2):
    #         resquestData = mx_test.generateContractRequestData(startDate,endDate,unit)
    #         mx_test.requestContract(resquestData)
    #         mx_test.writeContractIntoMysql(unit,resquestData)

    # mx_test.calContract(["bteas"],["省内合同"], ["双边协商"], ["年度"], "2024-03-30", "2024-04-01")


    mltSortList = [
        "all",
        "双边协商",
        "跨省跨区",
        "省间现货",
        "基数",
        "集中竞价",
        "置换增量",
        "置换转让",
        "挂牌交易",
    ]

    unitNameList = [
        "all",
        "火电合同#1",
        "火电合同#2",
        "水电合同#1",
        "风电合同#1",
    ]

    mx_test.execMain(unitNameList,None,mltSortList, None, "2024-05-01", "2024-06-02")

