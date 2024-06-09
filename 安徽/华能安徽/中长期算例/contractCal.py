import datetime
import os
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import requests
import random

from common.common import CommonClass
from 安徽.华能安徽.中长期算例.excel_handler import ExcelHeplerXlwing
from 安徽.华能安徽.中长期算例.mysqlTool import MysqlTool

yamlPath = r"D:\code\python\calCase\安徽\config\anhui_interface.yaml"
unitInfoPath = r"D:\code\python\calCase\安徽\config\unitInfo.yaml"


enumType = {
    # 交易类型
    "mltSort": [
                {
                    "name": "双边协商",
                    "id": "1"
                },
                {
                    "name": "集中竞价",
                    "id": "2"
                },
                {
                    "name": "挂牌交易",
                    "id": "3"
                },
                {
                    "name": "合同转让",
                    "id": "4"
                },
                {
                    "name": "增购交易",
                    "id": "5"
                },
                {
                    "name": "日滚动交易",
                    "id": "6"
                },

            ],

    #类型
    "contractType": [
        {
            "name": "省内",
            "id": "PROVINCIAL"
        },
        {
            "name": "省间",
            "id": "INTER_PROVINCIAL"
        }
    ],

    #交易方向
    "tradeDirection": [
        {
            "name": "买入",
            "id": "BUY"
        },
        {
            "name": "卖出",
            "id": "SELL"
        }
    ],

}

enumOrder = [
    "双边协商",
    "集中竞价",
    "挂牌交易",
    "合同转让",
    "增购交易",
    "日滚动交易",

]

class Anhui:

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

    def generateContractRequestData(self,startDate,endDate,unit,count):

        contractDTO = {
            "ownerId": unit["unitId"],
            "mltSort": str(random.randint(1, len(enumType["mltSort"]))),
            "contractName": "随机合同" + str(count)+str(random.randint(10000, 99999)),
            "tradeDirection": random.randint(0, len(enumType["contractType"])-1),
            "type":  random.choice(["PROVINCIAL","INTER_PROVINCIAL"]),
            "oppositeSide": "购电名称"+str(random.randint(0, 10000)),
            "startDate": startDate,
            "endDate": endDate,
            "createTime": "2024-04-17",
            "ele": 1,
            "price" : 2,
        }

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")
        contractDataDTOList = []

        eleSum = 0
        feeSum = 0

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)


            eleNoneIndex = random.randint(0, 95)
            priceNoneIndex = random.randint(0, 95)
            if random.randint(0, 100) == 1:
                priceNoneIndex = eleNoneIndex

            ele = [ random.choice([-1,1])*round(random.randint(0, 500)/100,2) for i in range(0,96)]
            price = [ round(random.randint(10000, 100000)/100,2) for i in range(0,96)]

            ele[eleNoneIndex] = None
            price[priceNoneIndex] = None


            for i in range(0,96):
                if ele[i] == None or price[i]==None:
                    continue
                eleSum += ele[i]
                feeSum = feeSum + (ele[i]*price[i])



            tempDic = {
                "date": dateStr,
                "type": 3,
                "checkType": False,
                "price": price,
                "value": ele
            }
            contractDataDTOList.append(tempDic)

        contractDTO["ele"] = eleSum
        contractDTO["price"] = None if eleSum==0 else feeSum/eleSum

        # print(contractDTO)
        return {
            "contractDTO" :contractDTO,
            "contractPurchaseSaleRelated": [],
            "contractDataDTOList": contractDataDTOList
        }

    def requestContract(self,requestData):

        url = self.domain + "/ahfire/api/mlt/contract"
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
                    # date,
                    contractDataDTO["date"],
                    # mlt_sort,
                    contractDTO["mltSort"],
                    # start_date,
                    contractDTO["startDate"],
                    # end_date
                    contractDTO["endDate"],
                    # ele,
                    str(contractDataDTO["value"]),
                    # price,
                    str(contractDataDTO["price"]),
                    # unit_name,
                    unit["unitName"],
                    # opposite_side,
                    contractDTO["oppositeSide"],
                    # mlt_type,
                    contractDTO["type"],
                    # trade_direction,
                    contractDTO["tradeDirection"],
                    # contract_name,
                    contractDTO["contractName"],



                )
            )


        print(writeSqlList[0])
        db = MysqlTool()
        db.insertContract(writeSqlList)
        # db.close()

        pass

    def queryLocalContract(self,unitName, contractType, mltSort,  startDate, endDate):

        mlt_type = self.transformEnum("contractType",contractType)
        mlt_sort = self.transformEnum("mltSort",mltSort)

        d = {
            "unit_name": unitName,
            "mlt_type": mlt_type,
            "mlt_sort": mlt_sort,
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
    def calContract(self, unitNameList, contractTypeList, mltSortList, startDate, endDate):

        queryRes = self.queryLocalContract(unitNameList, contractTypeList, mltSortList,startDate,
                                           endDate)

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

            dayData[dateStr].append({
                "ele": ele,
                "price": price,
            })

            monthData[monthStr].append({
                "ele": ele,
                "price": price,
            })

        dayRes = self.calData(dayData)
        monthRes = self.calData(monthData)

        inputData = {
            "day": dayRes,
            "month": monthRes,
        }

        return inputData

    def execMain(self, unitNameList, contractTypeList, mltSortList, startDate, endDate):

        allUnitData = {

        }

        for unitName in unitNameList:
            allUnitData[unitName] = {}
            nameList = unitNameList[1:] if unitName == "all" else [unitName]
            for mltSort in mltSortList:
                sortList = mltSortList[1:] if mltSort == "all" else [mltSort]
                res = self.calContract(nameList, contractTypeList, sortList,  startDate, endDate)
                allUnitData[unitName][mltSort] = res

        # print(allUnitData)
        self.outputData(allUnitData, startDate, endDate)

    # 计算合同数据
    def calData(self, dateDict):

        resDateDict = {
            "all": {
                "eleSum": 0,
                "priceSum": 0,
                "feeSum": 0,

            }
        }

        for date in dateDict.keys():

            dateData = dateDict[date]
            ele = [0 for i in range(0, 96)]
            price = [0 for i in range(0, 96)]
            fee = [0 for i in range(0, 96)]

            for i in range(0, len(dateData)):

                indexData = dateData[i]
                # print("===========",indexData)

                for j in range(0, 96):

                    if indexData["price"][j] == None or indexData["ele"][j] == None:
                        continue

                    ele[j] = ele[j] + indexData["ele"][j]
                    fee[j] = fee[j] + (
                                indexData["ele"][j]  * indexData["price"][j])

            eleSum = 0

            feeSum = 0
            for i in range(0, 96):
                eleSum += ele[i]
                feeSum += fee[i]

                price[i] = None if ele[i] == 0 else fee[i] / ele[i]

            priceSum = None if eleSum == 0 else feeSum / eleSum

            resDateDict[date] = {
                "ele": ele,
                "price": price,
                "fee": fee,
                "eleSum": eleSum,
                "priceSum": priceSum,
                "feeSum": feeSum,

            }

        for key in resDateDict.keys():

            if key == "all":
                continue

            resDateDict["all"]["eleSum"] += resDateDict[key]["eleSum"]
            resDateDict["all"]["feeSum"] += resDateDict[key]["feeSum"]


        resDateDict["all"]["priceSum"] = None if resDateDict["all"]["eleSum"] == 0 else resDateDict["all"]["feeSum"] / \
                                                                                        resDateDict["all"]["eleSum"]


        return resDateDict

    def outputData(self, inputData, startDate, endDate):

        dateData = self.outputDayDataGenertate(inputData, startDate, endDate)
        monthData = self.outputMonthDataGenertate(inputData, startDate, endDate, dimensions="month")
        dayData = self.outputMonthDataGenertate(inputData, startDate, endDate, dimensions="day")

        try:
            tempPath = CommonClass.mkDir("安徽","华能安徽","中长期算例", "导出模板", "持仓总览模板.xlsx", isGetStr=True)
            templateE = ExcelHeplerXlwing(tempPath)
            template = templateE.getTemplateStyle("Sheet1")
        finally:
            templateE.close()

        # print(resData)

        savePath = CommonClass.mkDir("安徽","华能安徽","中长期算例", "导出模板", "持仓总览结果.xlsx", isGetStr=True)
        e = ExcelHeplerXlwing()

        try:
            for date in dateData:
                e.newExcel(sheetName=date, templateStyle=template)
                e.writeData(savePath, dateData[date], date)
            e.newExcel(sheetName="月维度")
            e.writeData(savePath, monthData, "月维度", beginRow=1)
            e.newExcel(sheetName="日维度")
            e.writeData(savePath, dayData, "日维度", beginRow=1)
        finally:
            e.close()

        pass

    def outputDayDataGenertate(self, inputData, startDate, endDate):
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

                        dateData[dateStr].append(ele)
                        dateData[dateStr].append(price)
                        dateData[dateStr].append(fee)


                        continue

                    ele = [unitName, sortName, "电量", sortDayData[dateStr]["eleSum"]]
                    ele.extend(sortDayData[dateStr]["ele"])
                    price = [unitName, sortName, "电价", sortDayData[dateStr]["priceSum"]]
                    price.extend(sortDayData[dateStr]["price"])
                    fee = [unitName, sortName, "费用", sortDayData[dateStr]["feeSum"]]
                    fee.extend(sortDayData[dateStr]["fee"])


                    dateData[dateStr].append(ele)
                    dateData[dateStr].append(price)
                    dateData[dateStr].append(fee)


        return dateData

    def outputMonthDataGenertate(self, inputData, startDate, endDate, dimensions="month"):
        sd = None
        ed = None
        if dimensions == "month":
            sd = datetime.strptime(startDate[:7], "%Y-%m")
            ed = datetime.strptime(endDate[:7], "%Y-%m")
        if dimensions == "day":
            sd = datetime.strptime(startDate, "%Y-%m-%d")
            ed = datetime.strptime(endDate, "%Y-%m-%d")
        dateData = {}
        dateData["0"] = ["机组", "合约类型", "电量/电价", "合计/均值"]

        while sd <= ed:
            dateStr = None
            if dimensions == "month":
                dateStr = datetime.strftime(sd, "%Y-%m")
                sd += relativedelta(months=1)
            if dimensions == "day":
                dateStr = datetime.strftime(sd, "%Y-%m-%d")
                sd += timedelta(days=1)

            dateData["0"].append(dateStr)

            count = 1

            for unit in inputData:

                unitName = "汇总" if unit == "all" else unit

                for mltSort in inputData[unit].keys():

                    sortName = "中长期总体" if mltSort == "all" else mltSort

                    sortDayData = inputData[unit][mltSort][dimensions]

                    if str(count) not in dateData.keys():
                        dateData[str(count)] = [unitName, sortName, "电量", sortDayData["all"]["eleSum"]]
                        dateData[str(count + 1)] = [unitName, sortName, "电价", sortDayData["all"]["priceSum"]]
                        dateData[str(count + 2)] = [unitName, sortName, "电费", sortDayData["all"]["feeSum"]]


                    if dateStr not in sortDayData.keys():
                        dateData[str(count)].append(None)
                        dateData[str(count + 1)].append(None)
                        dateData[str(count + 2)].append(None)

                    else:
                        dateData[str(count)].append(sortDayData[dateStr]["eleSum"])
                        dateData[str(count + 1)].append(sortDayData[dateStr]["priceSum"])
                        dateData[str(count + 2)].append(sortDayData[dateStr]["feeSum"])


                    count += 3
        dList = []
        for key in dateData.keys():
            dList.append(dateData[key])
        return dList



if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)
    units = CommonClass.readYaml(unitInfoPath)
    print(units)

    ah_test = Anhui(testSession,yamlData,"hn")

    ah_test.login()


    startDate = "2024-05-01"
    endDate = "2024-05-01"

    count = 0
    for unit in units:
        for i in range(1,3):
            resquestData = ah_test.generateContractRequestData(startDate,endDate,unit,count)
            print(resquestData)
            # ah_test.requestContract(resquestData)
            ah_test.writeContractIntoMysql(unit,resquestData)
            count += 1

    mltSortList = [
        "all",
        "双边协商",
        "集中竞价",
        "挂牌交易",
        "合同转让",
        "增购交易",
        "日滚动交易",
    ]

    unitNameList = [
        "all",
        "火电合同#1",
        "火电合同#2",
        "风电合同#1",
        "光伏合同#1",
    ]

    # ah_test.execMain(unitNameList,None,mltSortList, "2024-05-01", "2024-05-01")


