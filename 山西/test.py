import datetime
import os
import time
from datetime import datetime, timedelta

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


    pass


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    sx_test = Shanxi(testSession,yamlData,"test")

    sx_test.login()


    startDate = "2024-05-01"
    endDate = "2024-05-01"

    # sx_test.getPublicDailyRoll(startDate,endDate)
    sx_test.getPublicDayAheadPrice(startDate)
