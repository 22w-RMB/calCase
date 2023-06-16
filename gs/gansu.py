import datetime
import os

import requests
from datetime import datetime,timedelta
from threading import Thread


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

        unitIds = [
            # "e4d4ed84879e91d80187b75a87210024",   # 风电#2
            # "e4d4ed84879e91d80187b75a2388001f" ,  # 风电#1
            # "e4fd338187c0cab70187d6699bb40007" ,  # 光伏1期
            "e4d4edc6878cda1301878dd384af002e" ,  # 安马
        ]


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
            finalDict[t] = []



            param = [
                ["unitIds", unitIds[0]],
                # ["unitIds",unitIds[1]],
                ["contractTypes",contractType[t]],
                ["startDate",startDate],
                ["endDate", endDate],
            ]

            res = CommonClass.execRequest(self.session,method="GET",params=param,url=url).json()
            nameList = []
            for d in res['data']:
                if d['complete'] == True:
                    nameList.append(d['name'])

            if nameList == []:
                finalDict[t].append([])
                finalDict[t].append([])
                finalDict[t].append([])
                continue
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

    def writeContractReport(self,data):

        contractCol = {
            "基数合同" : [37,38,41],
            "省间合同" : [9,10,13] ,
            "省内合同" : [16,17,20],
            "分时合同" : [23,24,27] ,
            "转让合同" : [30,31,34],
            "全部合同" : [2,3,6],
        }

        reportPath = r"D:\code\python\calCase\gs\导出\报表\场站- 合同数据报表数据项.xlsx"
        sheetName = "安马-20230303"
        e = ExcelHepler(reportPath)

        for t in contractCol:

            e.writeColData(contractCol[t],data[t],[3,3,3],reportPath,sheetName)

        e.close()

    def getarbitrageData(self , startDate):

        unitIds = [
            "e4d4ed84879e91d80187b7595596001a",   # 风电调度单元
        ]


        method = "GET"

        url = self.domain + "/tads/gansu/api/power/trade/spot/trade/analysis/arbitrage"

        paramData = [

            ["startDate" , startDate],
            ["endDate" , startDate],
            ["dispatchUnitIdList" , unitIds[0]],
            ["typeList" , "CASE_SIMULATE_SHORT_RATE_FORECAST"],
            ["typeList" , "ACTUAL_DECLARATION"],
            ["typeList" , "D1_REGION_SHORT_RATE_FORECAST"],
            ["typeList" , "D2_REGION_SHORT_RATE_FORECAST"],
            ["typeList" , "CASE_AFTER_WARDS"],

        ]

        res = CommonClass.execRequest(self.session,method="GET",url=url,params=paramData).json()

        for d in res['data']:
            pass


    def requestReport(self,i):

        url = self.domain + "/report/api/report/export"

        jsonData = {
            "startDate" :  "2022-01-01" ,
            "endDate" :  "2022-07-30" ,
            "id" :  "e4dc742a889e50f00188aaa032550014" ,
        }

        startTime = datetime.now()
        res = CommonClass.execRequest(self.session,method="POST",json=jsonData,url=url)
        print("线程【"+str(i) +"】返回结果为："+ str(res.content[:20]))
        print("线程【"+str(i) +"】状态码为："+ str(res.status_code))

        endTime = datetime.now()
        print("线程【"+str(i) +"】时间：",endTime-startTime)



    def uploadPrivateData(self):


        path = r"E:\zzw\甘肃\甘肃新版\测试数据\私有数据\新能源\风电调度单元\2022"

        url = self.domain + "/tads/gansu/api/power/trade/pri/data/import/create/multi"

        for  root,dirs,files  in os.walk(path):



            for filename in files:

                if ("202211"  in filename) or ("202212"  in filename):


                    filePath = os.path.join(root,filename)

                    formdata = {
                        "templateNameList" : [filename],
                        "provinceAreaId" : "062",
                        "sysType" : "NEWENERGY",
                    }

                    fileList = [
                        ("files",(filename, open(filePath,"rb")))
                    ]

                    res = CommonClass.execRequest(self.session,method = "post",url = url,data=formdata,files=fileList ).json()

                    print(filename,"上传情况：",res)



if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    gs_test = Gansu(testSession, yamlData, "test")

    gs_test.login()

    startDate = "2023-03-03"
    endDate = "2023-06-28"

    # data = gs_test.getContractData(startDate,startDate)
    # gs_test.writeContractReport(data)


    # gs_test.uploadPrivateData()

    threadList = []

    count = 1

    for i in range(0,count):
        t =  Thread(target=gs_test.requestReport,args=(i,))
        t.start()
        print("线程【", t , "】正在执行.....")
        threadList.append( t)

    for i in range(0, count):

        threadList[i].join()

    print("多线程结束")