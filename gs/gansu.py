import datetime
import json
import os
import random

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

    # def getPriceVersionData(self,startDate,endDate):
    #
    #     getVersionUrl = self.domain + "/tads/gansu/api/public/data/version/info"
    #     getVersionMethod = "GET"
    #     getVersionParam = {
    #         "date" : "2023-03-01",
    #         "provinceAreaId" : "062",
    #         "dataType" : "DAY_AHEAD",
    #         "curveTypes" : "PARTITION_PRICE_FORECAST",
    #     }
    #
    #     getVersionRes = CommonClass.execRequest(session=self.session,method=getVersionMethod,url=getVersionUrl,params=getVersionParam).json()
    #
    #     print(getVersionRes)
    #
    #     firstVersion = ""
    #     firstVersionDate = ""
    #     try:
    #         firstVersion = getVersionRes["data"][0]["versionNo"]
    #         firstVersionDate = getVersionRes["data"][0]["versionName"][:10]
    #         print(firstVersion)
    #         print(firstVersionDate)
    #
    #     except Exception :
    #
    #         print("该日期无价格预测版本")
    #
    #         return
    #
    #     priceType = ["HE_XI","HE_DONG"]
    #
    #     for t in priceType:
    #
    #         getPriceDataUrl = self.domain + "/tads/gansu/api/public/data/partition/price"
    #         getPriceDataMethod = "GET"
    #         getPriceDataParam = {
    #             "startDate" :  "2023-03-01",
    #             "endDate" :  "2023-03-01",
    #             "provinceAreaId" :  "062",
    #             "timeSegment" :  "SEG_96",
    #             "valueType" :  "AVG",
    #             "partition" :  t,
    #             "versionNo" :  firstVersion,
    #         }
    #
    #         getPriceDataRes = CommonClass.execRequest(session=self.session, method=getPriceDataMethod, url=getPriceDataUrl,
    #                                                 params=getPriceDataParam).json()
    #
    #         print(getPriceDataRes)
    #
    #
    #
    #
    #
    #
    #     pass

    def getPriceVersionData(self, startDate, endDate):

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        detailRes = [

        ]
        outputDataLsit = []

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            dateStr1 = datetime.strftime(sd, "%m%d")
            sd += timedelta(days=1)

            getVersionUrl = self.domain + "/tads/gansu/api/public/data/version/info"
            getVersionMethod = "GET"
            getVersionParam = {
                "date": dateStr,
                "provinceAreaId": "062",
                "dataType": "DAY_AHEAD",
                "curveTypes": "PARTITION_PRICE_FORECAST",
            }

            getVersionRes = CommonClass.execRequest(session=self.session, method=getVersionMethod, url=getVersionUrl,
                                                    params=getVersionParam).json()

            # print(dateStr, "版本返回：",getVersionRes)

            firstVersion = ""
            firstVersionName = ""
            firstVersionDate = ""
            firstVersionDateStr = ""


            onedayRes = {
            }
            detailRes.append(onedayRes)

            try:
                firstVersion = getVersionRes["data"][0]["versionNo"]
                firstVersionName = getVersionRes["data"][0]["versionName"][:10]
                # print(firstVersion)
                # print(firstVersionName)
            except Exception:
                onedayRes["date"] = dateStr
                onedayRes["info"] = "该日期没有价格预测版本"
                onedayRes["result"] = "False"


            try:
                firstVersionDate = datetime.strptime(firstVersionName, "%Y-%m-%d")
                firstVersionDateStr = firstVersionDate.strftime("%m%d")
                firstVersionDate += timedelta(days=2)
                if firstVersionDate == sd:
                    onedayRes["date"] = dateStr
                    onedayRes["info"] = "该日期最新的价格版本名称是D-1"
                    onedayRes["result"] = "True"
                    onedayRes["versionName"] = getVersionRes["data"][0]["versionName"]
                else:
                    onedayRes["date"] = dateStr
                    onedayRes["info"] = "该日期最新的价格版本名称不是D-1"
                    onedayRes["result"] = "False"
                    onedayRes["versionName"] = getVersionRes["data"][0]["versionName"]

            except Exception:
                print(dateStr, "该日期的版本名称不包含日期")
                onedayRes["date"] = dateStr
                onedayRes["info"] = "该日期最新的价格版本名称不包含日期"
                onedayRes["result"] = "False"
                onedayRes["versionName"] = getVersionRes["data"][0]["versionName"]

            outputDataDic = {
                "sheetName": dateStr1 + "(" + firstVersionDateStr + "预测)",
                "date": {
                    "col": 1,
                    "dataList": [[dateStr] for i in range(0, 96)]
                },
                "hexiDayAheadPrice": {
                    "col": 3,
                    "dataList": [[None] for i in range(0, 96)]
                },
                "hexiDayAheadForecastPrice": {
                    "col": 4,
                    "dataList": [[None] for i in range(0, 96)]
                },
                "heDongDayAheadPrice": {
                    "col": 6,
                    "dataList": [[None] for i in range(0, 96)]
                },
                "heDongDayAheadForecastPrice": {
                    "col": 7,
                    "dataList": [[None] for i in range(0, 96)]
                },
            }

            priceType = {
                "HE_XI" : ["hexiDayAheadPrice","hexiDayAheadForecastPrice"],
                "HE_DONG" : ["heDongDayAheadPrice","heDongDayAheadForecastPrice"],
            }



            for t in priceType.keys():
                getPriceDataUrl = self.domain + "/tads/gansu/api/public/data/partition/price"
                getPriceDataMethod = "GET"
                getPriceDataParam = {
                    "startDate": dateStr,
                    "endDate": dateStr,
                    "provinceAreaId": "062",
                    "timeSegment": "SEG_96",
                    "valueType": "AVG",
                    "partition": t,

                }

                if firstVersion !="":
                    getPriceDataParam["versionNo"] = firstVersion

                getPriceDataRes = CommonClass.execRequest(session=self.session, method=getPriceDataMethod,
                                                          url=getPriceDataUrl,
                                                          params=getPriceDataParam).json()

                dayAheadPrice = priceType[t][0]
                dayAheadForecastPrice = priceType[t][1]

                # 日前价格
                dayAheadPriceList = getPriceDataRes["data"]["dataList"][0]["dayAheadPrice"]
                # 日前价格预测
                dayAheadForecastPriceList = getPriceDataRes["data"]["dataList"][0]["dayAheadForecastPrice"]
                print(t, "日前价格为：", dayAheadPriceList)
                print(t, "日前价格预测为：", dayAheadForecastPriceList)

                if dayAheadPriceList != [] and dayAheadPriceList != None :
                    outputDataDic[dayAheadPrice]["dataList"] = [[dayAheadPriceList[i]] for i in range(0,96)]
                if dayAheadForecastPriceList != [] and dayAheadForecastPriceList != None :
                    outputDataDic[dayAheadForecastPrice]["dataList"] = [[dayAheadForecastPriceList[i]] for i in range(0,96)]



            # print(json.dumps(outputDataDic,indent=4))
            print(outputDataDic)
            outputDataLsit.append(outputDataDic)
        print(detailRes)

        self.outputPriceFile(outputDataLsit,detailRes)


        pass

    def outputPriceFile(self,outputPriceList,detailRes):

        tempPath = CommonClass.mkDir("gs", "muban", "价格情况统计模板.xlsx", isGetStr=True)
        # templateE = ExcelHepler(tempPath)
        # template = templateE.getTemplateStyle("模板")
        # templateE.close()
        savePath = CommonClass.mkDir("gs", "导出", "价格情况统计.xlsx", isGetStr=True)
        e = ExcelHepler(tempPath)
        for oneDay in outputPriceList:

            sheetName = oneDay["sheetName"]

            # e.newExcel(sheetName=sheetName, templateStyle=template)
            e.copySheet("模板",sheetName)
            for key in oneDay:
                if key =="sheetName":
                    continue
                col = oneDay[key]["col"]
                dataList = oneDay[key]["dataList"]
                e.writePriceData(sheetName,2,col,dataList)

        e.saveFile(savePath)
        e.close()

        detailSavePath = CommonClass.mkDir("gs", "导出", "价格结果详情.xlsx", isGetStr=True)
        detailE = ExcelHepler()
        detailE.writeDetailData(detailRes,"Sheet1")
        detailE.saveFile(detailSavePath)
        detailE.close()

    def genetateDayAheadPrice(self):

        resL = []

        for i in range(0, 4):
            tempL = []

            for i in range(0,24):
                if random.randint(0, 50) == 1:
                    tempL.append(None)
                else:
                    tempL.append(random.randint(4000, 100000) / 100)


            resL.append(tempL)

        # print(resL)
        return resL

    #  生成日前价格
    def genetateDayAheadPriceFile(self,startDate,endDate,unitNameList=["风电调度单元","光伏调度单元"]):

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")
        yearStr = startDate[:4]

        tempPath = CommonClass.mkDir("gs", "muban", "公有私有价格导入模板.xlsx", isGetStr=True)
        template = None
        templateE = ExcelHepler(tempPath)
        try:
            template = templateE.getTemplateStyle("sheet")
        finally:
            templateE.close()

        while sd <= ed:
            startDateStr = sd.strftime("%Y%m%d")


            # 场站名称-日前电厂结算价格-20230717
            filenameList = []
            for unitName in unitNameList:
                privatePriceFileName =  unitName + "-日前电厂结算价格-" + startDateStr +".xlsx"
                filenameList.append(privatePriceFileName)
            # 日前统一结算点价格20230828
            publicPriceFileName =  "日前统一结算点价格" + startDateStr +".xlsx"

            filenameList.append(publicPriceFileName)
            print(filenameList)

            for filename in filenameList:
                p = ""
                if "日前统一结算点价格" in filename:
                    p = "日前统一结算点价格"
                else:
                    p = "日前电厂结算价格"

                resL = self.genetateDayAheadPrice()

                # 输出文件

                savePath = CommonClass.mkDir("gs", "导出","价格", p, yearStr, filename, isGetStr=True)

                e = ExcelHepler()
                try:
                    e.newExcel("sheet", template)
                    e.writeDayAheadPrice(resL)

                    e.saveFile(savePath)
                finally:
                    e.close()

            sd += timedelta(days=1)

        pass

        pass

    #  上传日前结算点价格
    def uploadPublicDayAheadPrice(self):

        path = CommonClass.mkDir("gs", "导出","价格","日前统一结算点价格",isGetStr=True)

        url = self.domain + "/datacenter/gs/api/data/import/create/multi"

        for root, dirs, files in os.walk(path):

            for filename in files:

                    # print(filename)
                    filePath = os.path.join(root, filename)

                    formdata = {
                        "fileNames": [filename],
                        "provinceAreaId": "062",
                        "dataType": "TRADE_RESULT",
                        "type": "PUBLIC",
                        "templateNameList":["日前河东分区价格","日前河西分区价格","日前出清节点价格","日前出清电能价格","实时河东分区价格","实时河西分区价格","实时出清节点价格","实时出清电能价格","日前统一结算点价格","实时统一结算点价格"]

                    }

                    fileList = [
                        ("files", (filename, open(filePath, "rb")))
                    ]

                    res = CommonClass.execRequest(self.session, method="post", url=url, data=formdata,
                                                  files=fileList).json()

                    print(filename, "上传情况：", res)

        pass

    #  上传日前电厂结算价格
    def uploadPrivateDayAheadPrice(self):

        path = CommonClass.mkDir("gs", "导出","价格","日前电厂结算价格",isGetStr=True)

        url = self.domain + "/tads/gansu/api/power/trade/pri/data/import/create/multi"

        for root, dirs, files in os.walk(path):

            for filename in files:

                    # print(filename)
                    filePath = os.path.join(root, filename)

                    formdata = {
                        "provinceAreaId": "062",
                        "sysType": "NEWENERGY",
                        "templateNameList":[filename]
                    }

                    fileList = [
                        ("files", (filename, open(filePath, "rb")))
                    ]

                    res = CommonClass.execRequest(self.session, method="post", url=url, data=formdata,
                                                  files=fileList).json()

                    print(filename, "上传情况：", res)

        pass


    #  生成全网日滚动
    def genetatePublicDailyRollData(self):

        # ele = [None for i in range(0,24)]
        # maxP = [None for i in range(0,24)]
        # minP = [None for i in range(0,24)]
        # avgP = [None for i in range(0,24)]
        # midP = [None for i in range(0,24)]

        resL = []

        for i in range(0,24):
            tempL = []

            tempL.append(random.randint(0, 20000) / 100)
            tempL.append(random.randint(0, 90000) / 100)
            tempL.append(random.randint(0, 90000) / 100)
            tempL.append(random.randint(0, 90000) / 100)
            tempL.append(random.randint(0, 90000) / 100)

            ifNone = True
            if ifNone:
                for i in range(0,4):
                    if random.randint(0, 10) == 1:
                        tempL[i] = None


            resL.append(tempL)

        # print(resL)
        return resL


        pass

    #导出日滚动文件
    def genetatePublicDailyRollFile(self,startDate,endDate):

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")
        yearStr = startDate[:4]

        tempPath = CommonClass.mkDir("gs", "muban", "yyyy年mm月dd日日滚动交易(yyyy-m-dd).xlsx", isGetStr=True)
        template = None
        templateE = ExcelHepler(tempPath)
        try :
            template = templateE.getTemplateStyle("市场交易信息")
        finally:
            templateE.close()

        while sd <= ed:
            startDateStr = sd.strftime("%Y-%#m-%#d")

            for i in range(1,29):
                beforeDate = sd - timedelta(days=i)
                beforeDateStr = beforeDate.strftime( "%Y年%m月%d日")

                # yyyy年mm月dd日日滚动交易(yyyy-m-dd)
                fileName = beforeDateStr + "日滚动交易("+ startDateStr +")"
                print(fileName)

                resL = self.genetatePublicDailyRollData()

                # 输出文件

                savePath = CommonClass.mkDir("gs", "导出","全网日滚动",yearStr, fileName+".xlsx", isGetStr=True)

                e = ExcelHepler()
                try:
                    e.newExcel("市场交易信息",template)
                    e.writeDailyRoll(resL)

                    e.saveFile(savePath)
                finally:
                    e.close()


            sd += timedelta(days=1)



        pass

    #  上传全网日滚动
    def uploadPublicDailyRoll(self):

        path = CommonClass.mkDir("gs", "导出","全网日滚动",isGetStr=True)

        url = self.domain + "/datacenter/gs/api/data/import/create/multi"

        for root, dirs, files in os.walk(path):

            for filename in files:


                    filePath = os.path.join(root, filename)

                    formdata = {
                        "fileNames": [filename],
                        "provinceAreaId": "062",
                        "dataType": "MLT_WHOLE_NET_INFO",
                    }

                    fileList = [
                        ("files", (filename, open(filePath, "rb")))
                    ]

                    res = CommonClass.execRequest(self.session, method="post", url=url, data=formdata,
                                                  files=fileList).json()

                    print(filename, "上传情况：", res)

        pass


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    gs_test = Gansu(testSession, yamlData, "test")



    # startDate = "2023-07-08"
    # endDate = "2023-09-08"

    # gs_test.getPriceVersionData(startDate,endDate)

    # for i in range(0,10):
    #     gs_test.genetatePublicDailyRoll()


    # data = gs_test.getContractData(startDate,startDate)
    # gs_test.writeContractReport(data)


    # gs_test.uploadPrivateData()

    # threadList = []
    #
    # count = 1
    #
    # for i in range(0,count):
    #     t =  Thread(target=gs_test.requestReport,args=(i,))
    #     t.start()
    #     print("线程【", t , "】正在执行.....")
    #     threadList.append( t)
    #
    # for i in range(0, count):
    #
    #     threadList[i].join()
    #
    # print("多线程结束")


    gs_test.genetateDayAheadPriceFile("2020-02-01", "2020-02-29")

    gs_test.login()
    gs_test.uploadPublicDayAheadPrice()
    gs_test.uploadPrivateDayAheadPrice()


    gs_test.genetatePublicDailyRollFile("2020-02-01", "2020-02-29")
    gs_test.login()
    gs_test.uploadPublicDailyRoll()



    gs_test.genetatePublicDailyRollFile("2020-03-01", "2020-12-31")
    gs_test.login()
    gs_test.uploadPublicDailyRoll()


    gs_test.genetateDayAheadPriceFile("2020-03-01", "2020-12-31")
    gs_test.login()
    gs_test.uploadPublicDayAheadPrice()
    gs_test.uploadPrivateDayAheadPrice()