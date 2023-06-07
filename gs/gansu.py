import datetime

import requests
from datetime import datetime,timedelta

from common.common import CommonClass
from excel_handler import ExcelHepler

yamlPath = r"D:\code\python\calCase\gs\config\gs_interface.yaml"




class Gansu:

    def __init__(self, session, yamlData, type):
        self.domain = None
        self.loginInfo = None
        self.yamlData = yamlData
        self.session = session
        # self.provinceId = "15"
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


    def getContractData(self , startDate,endDate):

        unitIds = [  "e4d4ed84879e91d80187b75a87210024",   # 风电#2
                     "e4d4ed84879e91d80187b75a2388001f"]   # 风电#1


        method = "GET"

        url = self.domain + "/tads/gansu/api/power/trade/mlt/position/overview/query/name"

        contractType = {
            "基数合同" : "BILATERAL_BASIC" ,
            "省间合同" : "BILATERAL_PRO_BETWEEN" ,
            "省内合同" : "BILATERAL_PRO_IN" ,
            "分时合同" : "MINUTE_HOUR_CONTRACT" ,
            "转让合同" : "BILATERAL_TRANSFER" ,
            "全部合同" : None,
        }

        finalDict = {}

        for t in contractType:

            param = [
                ["unitIds", unitIds[0]],
                ["unitIds",unitIds[1]],
                ["contractTypes",contractType[t]],
                ["startDate",startDate],
                ["endDate", endDate],
            ]

            res = CommonClass.execRequest(self.session,method="GET",params=param,url=url).json()
            nameList = []
            for d in res['data']:
                if d['complete'] == True:
                    nameList.append(d['name'])


            detailUrl = self.domain + "/tads/gansu/api/power/trade/mlt/position/overview/detail"
            spotUrl = self.domain + "/tads/gansu/api/power/trade/mlt/position/overview/spot"
            contractTypes = [contractType[t]]
            if t == "全部合同":
                contractTypes = []

            jsonData = {
                "compare": False,
                "contractNames": nameList,
                "contractTypes": contractTypes,
                "startDate": startDate,
                "endDate": endDate,
                "unitIds": unitIds
            }

            detailRes = CommonClass.execRequest(self.session, url=detailUrl, method="POST", json=jsonData).json()
            spotRes = CommonClass.execRequest(self.session, url=spotUrl, method="POST", json=jsonData).json()

            if t == "全部合同":
                print(spotRes)

            eleList = []
            priceList = []
            daAvgPriceList = []

            if detailRes['data'] != []:
                eleList = detailRes["data"]["mltUnitList"][0]["eleList"]
                priceList = detailRes["data"]["mltUnitList"][0]["priceList"]
            if spotRes['data'] != []:
                daAvgPriceList = spotRes["data"]["mltSpotDetailDTOS"][0]["daAvgPriceList"]

            finalDict[t] = []
            finalDict[t].append(eleList)
            finalDict[t].append(priceList)
            finalDict[t].append(daAvgPriceList)

        print(finalDict)
        return finalDict

    def writeReport(self,data):

        contractCol = {
            "基数合同" : [37,38,41],
            "省间合同" : [9,10,13] ,
            "省内合同" : [16,17,20],
            "分时合同" : [23,24,27] ,
            "转让合同" : [30,31,34],
            "全部合同" : [2,3,6],
        }

        reportPath = r"D:\code\python\calCase\gs\导出\报表\合同数据报表数据项.xlsx"
        sheetName = "风电调度单元-20230628"
        e = ExcelHepler(reportPath)

        for t in contractCol:

            e.writeColData(contractCol[t],data[t],[3,3,3],reportPath,sheetName)

        e.close()

if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    gs_test = Gansu(testSession, yamlData, "test")

    gs_test.login()

    startDate = "2023-06-28"
    endDate = "2023-06-28"

    data = gs_test.getContractData(startDate,endDate)
    gs_test.writeReport(data)



