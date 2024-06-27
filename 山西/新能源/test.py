import datetime
import os
import statistics
import time
from datetime import datetime, timedelta
from 山西.新能源.excel_handler import ExcelHeplerXlwing

import requests

from common.common import CommonClass


yamlPath = r"D:\code\python\calCase\山西\新能源\config\shanxi_interface.yaml"



class Shanxi:

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


    def getPublicDailyRoll(self,startDate,endDate):

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")


        url = self.domain +"/sxAdss/api/mlt/trade/info/roll/trade/daily"

        resultDataDic = {

        }

        while sd <= ed:

            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            resultDataDic[dateStr] = {

            }
            resultDataDic[dateStr]["dayAheadPirce"] = self.getPublicDayAheadPrice(dateStr)

            for i in range(0,11):
                temS = "汇总"
                if i > 0 :
                    temS = "D-" + str(i)
                resultDataDic[dateStr][temS] = {
                    "price": [None for i in range(0,24)],
                    "minPrice": [None for i in range(0,24)],
                    "medianPrice": [None for i in range(0,24)],
                    "maxPrice": [None for i in range(0,24)],
                    "ele": [None for i in range(0,24)],
                }


            tempD = sd + timedelta(days=-10)
            tempDateStr = datetime.strftime(tempD, "%Y-%m-%d")

            sd += timedelta(days=1)

            paramData = {
                "startDate" :  tempDateStr,
                "endDate" : dateStr ,
                "provinceAreaId" :  "014",
            }

            resJson = CommonClass.execRequest(self.session,url=url,method="GET",params=paramData).json()
            print(resJson)

            for resData in resJson["data"]["tradeData"]:


                tradeDateStr = resData["tradeDate"][:10]
                targetEndDateStr = resData["targetEndDate"][:10]

                if targetEndDateStr != dateStr :
                    continue

                tradeD = datetime.strptime(tradeDateStr, "%Y-%m-%d")
                targetD = datetime.strptime(targetEndDateStr, "%Y-%m-%d")
                intervalDay = targetD-tradeD

                intervalDayStr = "D-" + str(intervalDay.days)
                print(intervalDayStr)

                resultDataDic[dateStr][intervalDayStr]["price"] = resData["price"]
                resultDataDic[dateStr][intervalDayStr]["minPrice"] = resData["minPrice"]
                resultDataDic[dateStr][intervalDayStr]["medianPrice"] = resData["medianPrice"]
                resultDataDic[dateStr][intervalDayStr]["maxPrice"] = resData["maxPrice"]
                resultDataDic[dateStr][intervalDayStr]["ele"] = resData["ele"]
                # resultDataDic[dateStr][intervalDayStr] = {
                #     "price" : resData["price"],
                #     "minPrice" : resData["minPrice"],
                #     "medianPrice" : resData["medianPrice"],
                #     "maxPrice" : resData["maxPrice"],
                #     "ele" : resData["ele"],
                # }



        print(resultDataDic)
        return resultDataDic


        pass


    def calAllDate(self,startDate,endDate,filter=[]):

        publicDailyRoll = self.getPublicDailyRoll(startDate,endDate)

        allDateDic = {}

        totalItem = ["汇总"]
        for i in range(1,11):
            totalItem.append("D-"+str(i))

        # headerList = ["标的日期" ,"时段","日前出清价格"]
        # itemList =  [ "成交电量","成交均价","价差(总成交均价-日前价格)","成交最高均价",
        #               "价差(成交最高均价-日前价格)","成交最低均价","价差(成交最低均价-日前价格)",
        #               "成交中位数均价","价差(成交中位数均价-日前价格)"]



        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:

            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)

            allDateDic[dateStr] = {

            }

            dateDic = publicDailyRoll[dateStr]
            dayAheadPirce = dateDic["dayAheadPirce"]
            allDateDic[dateStr]["日前出清价格"] = dayAheadPirce
            allDateDic[dateStr]["总成交电量"] = None
            allDateDic[dateStr]["总成交均价"] = None
            allDateDic[dateStr]["总成交费用"] = None
            allDateDic[dateStr]["总价差(总成交均价-日前价格)"] = None
            allDateDic[dateStr]["总成交最高均价"] = None
            allDateDic[dateStr]["总价差(成交最高均价-日前价格)"] = None
            allDateDic[dateStr]["总成交最低均价"] = None
            allDateDic[dateStr]["总价差(成交最低均价-日前价格)"] = None
            allDateDic[dateStr]["总成交中位数均价"] = None
            allDateDic[dateStr]["总价差(成交中位数均价-日前价格)"] = None


            sumEleList = []
            sumFeeList = []
            sumPriceList = []

            for key in dateDic.keys():
                if key == "汇总" or key=="dayAheadPirce":
                    continue


                tempDic = dateDic[key]


                allDateDic[dateStr][key+"成交电量"] = tempDic["ele"]
                allDateDic[dateStr][key+"成交均价"] = tempDic["price"]
                allDateDic[dateStr][key+"成交费用"] = self.multiData(tempDic["ele"],tempDic["price"])
                allDateDic[dateStr][key+"价差(总成交均价-日前价格)"] = self.subData(tempDic["price"],dayAheadPirce)
                allDateDic[dateStr][key+"成交最高均价"] = tempDic["maxPrice"]
                allDateDic[dateStr][key+"价差(成交最高均价-日前价格)"] = self.subData(tempDic["maxPrice"],dayAheadPirce)
                allDateDic[dateStr][key+"成交最低均价"] = tempDic["minPrice"]
                allDateDic[dateStr][key+"价差(成交最低均价-日前价格)"] = self.subData(tempDic["minPrice"],dayAheadPirce)
                allDateDic[dateStr][key+"成交中位数均价"] = tempDic["medianPrice"]
                allDateDic[dateStr][key+"价差(成交中位数均价-日前价格)"] = self.subData(tempDic["medianPrice"],dayAheadPirce)


                if filter == [] or key in filter:
                    sumEleList.append(tempDic["ele"])
                    sumPriceList.append(tempDic["price"])
                    sumFeeList.append(self.multiData(tempDic["ele"],tempDic["price"]))


            allDateDic[dateStr]["总成交电量"] = self.otherData(sumEleList)["add"]
            allDateDic[dateStr]["总成交费用"] = self.otherData(sumFeeList)["add"]
            allDateDic[dateStr]["总成交均价"] = self.divData(allDateDic[dateStr]["总成交费用"],allDateDic[dateStr]["总成交电量"])
            allDateDic[dateStr]["总价差(总成交均价-日前价格)"] = self.subData( allDateDic[dateStr]["总成交均价"],allDateDic[dateStr]["日前出清价格"]  )
            allDateDic[dateStr]["总成交最高均价"] = self.otherData(sumPriceList)["max"]
            allDateDic[dateStr]["总价差(成交最高均价-日前价格)"] = self.subData( allDateDic[dateStr]["总成交最高均价"],allDateDic[dateStr]["日前出清价格"]  )
            allDateDic[dateStr]["总成交最低均价"] = self.otherData(sumPriceList)["min"]
            allDateDic[dateStr]["总价差(成交最低均价-日前价格)"] = self.subData( allDateDic[dateStr]["总成交最低均价"],allDateDic[dateStr]["日前出清价格"]  )
            allDateDic[dateStr]["总成交中位数均价"] = self.otherData(sumPriceList)["median"]
            allDateDic[dateStr]["总价差(成交中位数均价-日前价格)"] = self.subData( allDateDic[dateStr]["总成交中位数均价"],allDateDic[dateStr]["日前出清价格"]  )


        # print(allDateDic)

        return allDateDic

    def calTotal(self,allDateData):

        totalDic = {}
        # itemList =  [ "成交电量","成交均价","价差(总成交均价-日前价格)","成交最高均价",
        #               "价差(成交最高均价-日前价格)","成交最低均价","价差(成交最低均价-日前价格)",
        #               "成交中位数均价","价差(成交中位数均价-日前价格)"]

        typeList = ["总"]
        for i in range(1,11):
            typeList.append("D-"+str(i))

        dayAheadPriceList = []

        for i in typeList:

            sumEleList = []
            sumFeeList = []
            sumPriceList = []

            for dateStr in allDateData:
                dDic = allDateData[dateStr]

                sumEleList.append( dDic[ i +"成交电量"]  )
                sumFeeList.append(dDic[i +"成交费用"] )
                sumPriceList.append(dDic[i +"成交均价"] )

                if i == "总":
                    dayAheadPriceList.append(dDic["日前出清价格"])

            if i == "总":
                totalDic["日前出清价格"] = self.otherData(dayAheadPriceList)["avg"]

            totalDic[i + "成交电量"] = self.otherData(sumEleList)["add"]
            totalDic[i + "成交费用"] = self.otherData(sumFeeList)["add"]
            totalDic[i + "成交均价"] = self.divData(totalDic[i + "成交费用"],totalDic[i + "成交电量"])
            totalDic[i + "价差(总成交均价-日前价格)"] = self.subData( totalDic[i + "成交均价"],totalDic["日前出清价格"]  )
            totalDic[i + "成交最高均价"] = self.otherData(sumPriceList)["max"]
            totalDic[i + "价差(成交最高均价-日前价格)"] = self.subData( totalDic[i + "成交最高均价"],totalDic["日前出清价格"]  )
            totalDic[i + "成交最低均价"] = self.otherData(sumPriceList)["min"]
            totalDic[i + "价差(成交最低均价-日前价格)"] = self.subData( totalDic[i + "成交最低均价"],totalDic["日前出清价格"]  )
            totalDic[i + "成交中位数均价"] = self.otherData(sumPriceList)["median"]
            totalDic[i + "价差(成交中位数均价-日前价格)"] = self.subData( totalDic[i + "成交中位数均价"],totalDic["日前出清价格"]  )


        return totalDic



    def multiData(self,list1,list2):

        resList = []
        for i in range(0,len(list1)):
            if list1[i] == None or list2[i] ==None:
                resList.append(None)
            else:
                resList.append(list1[i]*list2[i])

        return resList

    def subData(self, list1, list2):

        resList = []
        for i in range(0, len(list1)):
            if list1[i] == None or list2[i] == None:
                resList.append(None)
            else:
                resList.append(list1[i] - list2[i])

        return resList

    def divData(self, list1, list2):

        resList = []
        for i in range(0, len(list1)):
            if list1[i] == None or list2[i] == None or list2[i] == 0:
                resList.append(None)
            else:
                resList.append(list1[i] / list2[i])

        return resList


    def otherData(self, dataLists):

        resDic = {
            "add" : [None for i in range(0,24)],
            "max" : [None for i in range(0,24)],
            "min" : [None for i in range(0,24)],
            "median" : [None for i in range(0,24)],
            "avg" : [None for i in range(0,24)],
        }

        for i in range(0,24):
            temp = None
            tempList = []
            for l in dataLists:
                tempList.append(l[i])
                if l[i] == None:
                    continue
                temp = (0 if temp==None else temp) + l[i]

            tempList = [x for x in tempList if x is not None]

            if len(tempList) > 0:
                resDic["add"][i] = (temp)
                resDic["max"][i] = max(tempList)
                resDic["min"][i] = min(tempList)
                resDic["median"][i] = statistics.median(tempList)
                resDic["avg"][i] = sum(tempList)/len(tempList)

        return resDic

    def addData(self, dataLists):

        resList = []

        for i in range(0,24):
            temp = None
            for l in dataLists:
                if l[i] == None:
                    continue
                temp = (0 if temp==None else temp) + l[i]

            resList.append(temp)

        return resList


    def getPublicDayAheadPrice(self,startDate):

        price = [None for i in range(0,24)]

        url = self.domain +"/PublicDataManage/014/api/spot/market/clearingPrice/regulated/query/latest"


        jsonData = {
            "dateMerge": {
                "aggregateType": "AVG",
                "mergeType": "NONE"
            },
            "dateRanges": [{
                "start": startDate,
                "end": startDate
            }],
            "marketType": None,
            "provinceAreaId": "014",
            "timeSegment": {
                "aggregateType": None,
                "filterPoints": None,
                "segmentType": "SEG_24"
            },
            "statistics": {
                "groupType": "RANGE"
            }
        }

        resJson = CommonClass.execRequest(self.session,url=url,method="POST",json=jsonData).json()

        print(resJson["data"]["dataList"])

        for d in resJson["data"]["dataList"]:

            if d["marketType"] == "DAY_AHEAD":

                price = d["price"]

        print(price)
        return price


    def outputData(self, dateData,totalData):




        try:
            tempPath = CommonClass.mkDir("山西","新能源","导出", "模板.xlsx", isGetStr=True)
            templateE = ExcelHeplerXlwing(tempPath)
            template = templateE.getTemplateStyle("Sheet1")
        finally:
            templateE.close()

        # print(resData)

        savePath = CommonClass.mkDir("山西","新能源","导出", "结果.xlsx", isGetStr=True)
        e = ExcelHeplerXlwing()

        try:
            for date in dateData.keys():
                res = self.transData(dateData[date])
                e.newExcel(sheetName=date, templateStyle=template)
                e.writeData(savePath, res, date,beginRow=1,beginCol=1)

            e.newExcel(sheetName="汇总", templateStyle=template)
            total = self.transData(totalData)
            e.writeData(savePath, total, "汇总",beginRow=1,beginCol=1)

        finally:
            e.close()


    def transData(self,dicData):
        # print(dicData)
        returnList = [ [] for i in range(0,25) ]
        returnList[0].append("时刻")
        for key in dicData.keys():
            if "费" in key:
                continue
            returnList[0].append(key)

        for i in range(0,24):
            returnList[i + 1].append(i+1)
            for key in dicData.keys():
                if "费" in key:
                    continue
                returnList[i+1].append( dicData[key][i] )

        # print(returnList)
        return returnList
    pass


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    sx_test = Shanxi(testSession,yamlData,"test")

    sx_test.login()


    startDate = "2024-05-01"
    endDate = "2024-05-01"

    # sx_test.getPublicDailyRoll(startDate,endDate)
    dateData = sx_test.calAllDate(startDate,endDate,filter=[])
    print(dateData)
    totalData = sx_test.calTotal(dateData)
    sx_test.outputData(dateData,totalData)