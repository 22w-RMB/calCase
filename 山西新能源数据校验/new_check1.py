from 山西新能源数据校验.common import CommonClass
from 山西新能源数据校验.excel_handler import ExcelHeplerXlwing
from datetime import datetime, timedelta
import requests

businessType = [
            {
                "name": "风电",
                "id": "1"
            },
            {
                "name": "光伏",
                "id": "2"
            },
            {
                "name": "水电",
                "id": "3"
            },
            {
                "name": "火电",
                "id": "4"
            },
            {
                "name": "核电",
                "id": "5"
            },
            {
                "name": "生物质",
                "id": "6"
            },
            {
                "name": "虚拟电厂",
                "id": "7"
            },
            {
                "name": "其他",
                "id": "8"
            },
            {
                "name": "太阳能",
                "id": "9"
            }
        ]

dataItemDic = {
    "001":  {
        "name" : "原始短期功率预测",
        "type" : "场站发电数据",
        "otherType":"原始功率预测",
    },
    "101":  {
        "name" : "申报短期功率预测",
        "type" : "场站发电数据",
        "otherType":"申报功率预测",
    },

    "401":  {
        "name" : "中长期总加曲线",
        "type" : "省内现货交易",
        "otherType":"中长期总加曲线",
    },
    "402":  {
        "name" : "日前出力计划",
        "type" : "省内现货交易",
        "otherType":"省内现货结果",
    },
    "403":  {
        "name" : "日内出力计划",
        "type" : "省内现货交易",
        "otherType":"省内现货结果",
    },
    "405":  {
        "name" : "日前节点电价",
        "type" : "省内现货交易",
        "otherType":"省内现货结果",
    },
    "406":  {
        "name" : "日内节点电价",
        "type" : "省内现货交易",
        "otherType":"省内现货结果",
    },
    "1001":  {
        "name" : "中长期基数电量",
        "type" : "省内现货交易",
        "otherType":"中长期基数电量",
    },
    "301": {
        "name": "省间日前结算电价",
        "type": "省间现货交易",
        "otherType":"省间日前交易结果",
    },
    "302": {
        "name": "省间日前结算电量",
        "type": "省间现货交易",
        "otherType":"省间日前交易结果",
    },
    "304": {
        "name": "省间日内结算电价",
        "type": "省间现货交易",
        "otherType":"省间日内交易结果",
    },
    "305": {
        "name": "省间日内结算电量",
        "type": "省间现货交易",
        "otherType":"省间日内交易结果",
    },
    "buySellContract" : {
        "name": "购售电合同",
        "type": "日清分单结算明细-中长期数据",
        "otherType":"日清分单结算明细-中长期数据",
    },
    "marketContract":{
        "name": "市场化合同",
        "type": "日清分单结算明细-中长期数据",
        "otherType":"日清分单结算明细-中长期数据",
    },
    "proInDayAhead":{
        "name": "日前数据",
        "type": "日清分单结算明细-日前数据",
        "otherType":"日清分单结算明细-日前数据",
    },
    "proInRealTime": {
        "name": "实时数据",
        "type": "日清分单结算明细-实时数据",
        "otherType":"日清分单结算明细-实时数据",
    },

    "501" :{
        "name": "日清分单",
        "type": "日清分单",
        "otherType":"日清分单",
    },
    "901": {
        "name": "月结算单",
        "type": "月结算单",
        "otherType":"月结算单",
    },

    "分时交易合同数据": {
        "name": "分时交易合同数据",
        "type": "中长期合同数据",
        "otherType":"分时交易合同数据",
    },
    "双边与挂牌合同数据": {
        "name": "双边与挂牌合同数据",
        "type": "中长期合同数据",
        "otherType":"双边与挂牌合同数据",
    }
}

dataItemList = [
    "原始功率预测",
    "申报功率预测",
    "中长期总加曲线",
    "中长期基数电量",
    "省内现货结果",
    "省间日前交易结果",
    "省间日内交易结果",
    "日清分单",
    "日清分单结算明细-日前数据",
    "日清分单结算明细-实时数据",
    "日清分单结算明细-中长期数据",
    "月结算单",
]

def getBusinessTypeStr(businessTypeId):

    for b in businessType:
        if businessTypeId == b["id"]:
            return b["name"]
    return None


class Shanxi:

    def __init__(self,session, info):
        self.domain = None
        self.loginInfo = None
        self.session = session
        self.domain = info['url_domain']
        self.loginInfo = info['logininfo']
        self.tenantId = info['tenantId']
        self.loginInfo["switch_url"] += self.tenantId


    def login(self):
        CommonClass.login(self.session, self.domain, self.loginInfo)

    def getUnit(self):
        url = self.domain + "/sxAdss/api/common/user/list"
        method = "GET"

        res = CommonClass.execRequest(self.session, method=method, url=url).json()['data'][0]["orgOsDetailDTOS"]
        unitsInfo = []

        for r in res:
            unitsInfo.append(
                {
                    "unitId" : r['osOrgId'],
                    "unitName" : r['osOrgName'],
                    "businessType" : getBusinessTypeStr(r['businessType']),
                }
            )
        return unitsInfo

    #场站发电数据、省内现货出清结果、中长期基数
    def getStationPowerGenerationStatus(self,startDate,endDate,unitInfo):

        url = self.domain + "/sxAdss/api/private/data/detail"
        method = "GET"

        haveDataResList = []

        for unit in unitInfo:

            paramDic1 = {
                "osOrgId" : unit["unitId"],
                "dataType" : 3,
                "startTime" : startDate,
                "endTime" : endDate,

            }
            paramDic2 = {
                "osOrgId" : unit["unitId"],
                "dataType" : 4,
                "startTime" : startDate,
                "endTime" : endDate,

            }
            paramDic3 = {
                "osOrgId" : unit["unitId"],
                "dataItemEnum" : "MLT_BASE_ELE",
                "startTime" : startDate,
                "endTime" : endDate,

            }

            response = []
            print("场站发电数据", unit["unitName"])
            response.extend( CommonClass.execRequest(self.session, params=paramDic1,method=method, url=url).json()['data'])
            print("现货出清数据", unit["unitName"])
            response.extend( CommonClass.execRequest(self.session, params=paramDic2,method=method, url=url).json()['data'])
            print("中长期基数电量", unit["unitName"])
            response.extend( CommonClass.execRequest(self.session, params=paramDic3,method=method, url=url).json()['data'])

            if response == []:
                continue

            for d in response:
                dateStr = d["date"][:10]
                dataItem = d["dataItem"]
                dataList = d["data"]

                if dataList == None:
                    continue

                else:
                    tt = ""
                    if dataItem =="1001":
                        if CommonClass.judgeListIsZero(dataList) == True:
                            tt = "-ZERO"

                    # 日期-数据项-机组
                    tempStr = dateStr + "-" + dataItem + "-" + unit["unitId"] +tt
                    haveDataResList.append(tempStr)

        return haveDataResList


    #日清分单、月结算单
    def getSettlementStatus(self,startDate,endDate,unitInfo):


        url = self.domain + "/sxAdss/api/private/data/getPrivateAndPrivateItem"
        method = "GET"

        haveDataResList = []

        for unit in unitInfo:
            print("结算单",unit["unitName"])
            paramDic = {
                "orgIds" : unit["unitId"],
                "startTime" : startDate,
                "endTime" : endDate,

            }

            response = CommonClass.execRequest(self.session, params=paramDic,  method=method, url=url).json()['data']["uploadList"]
            if response == []:
                continue

            for d in response:
                dateStr = d["date"][:10]
                monthStr = d["date"][:7]
                dataItem = d["dataItem"]

                outputItem = ["501","901"]

                if dataItem not in outputItem:
                    continue

                else:
                    # 日期-数据项
                    tempStr = None
                    if dataItem =="901":
                        tempStr = monthStr + "-" + dataItem + "-" + unit["unitId"]
                    elif dataItem =="501":
                        tempStr = dateStr + "-" + dataItem + "-" + unit["unitId"]
                    haveDataResList.append(tempStr)

        return haveDataResList


    #日清分单明细
    def getDaySettlementDetailStatus(self, startDate, endDate, unitInfo):

        url = self.domain + "/sxAdss/api/daily/clearing/summarize"
        method = "GET"

        haveDataResList = []

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)

            for unit in unitInfo:
                print("日清分单明细", unit["unitName"],dateStr)
                paramDic = {
                    "osOrgId": unit["unitId"],
                    "startDate": dateStr,
                    "endDate": dateStr,
                    "expectantIndex": "DAILY_CLEARING_DETAIL",
                    "formalIndex": "DAILY_CLEARING",

                }

                response = \
                CommonClass.execRequest(self.session, params=paramDic, method=method, url=url).json()['data'][
                    "dailyClearingDetailData"]["detailData"]

                if response == None:
                    continue

                for dataItem in response.keys():

                    if dataItem not in dataItemDic.keys():
                        continue

                    if response[dataItem]["ele"] == [] and \
                            response[dataItem]["fee"] == [] and \
                            response[dataItem]["price"] ==[]:
                        continue

                    tempStr = dateStr + "-" + dataItem + "-" + unit["unitId"]

                    haveDataResList.append(tempStr)

        return haveDataResList

    #中长期合同：方法1，只判断总电量，需要每天遍历
    def getContractStatus1(self,startDate,endDate,unitInfo):

        url = self.domain + "/sxAdss/api/mlt/position/detail"
        method = "POST"

        haveDataResList = []

        dataItems = {
            "分时交易合同数据": {
                "contractTypeIds": ["1"],
            },
            "双边与挂牌合同数据": {
                "contractTypeIds": ["2","3"],
            }
        }

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            sd += timedelta(days=1)

            for unit in unitInfo:
                print("日清分单明细", unit["unitName"], dateStr)
                for dataItem in dataItems.keys():

                    josnDic = {
                        "contractNames": [],
                        "contractTypeIds": dataItems[dataItem]["contractTypeIds"],
                        "datePeriodDTOS": [{
                            "startDate": dateStr,
                            "endDate": dateStr
                        }],
                        "eleDiameter": "ONLINE_ELE",
                        "isSeparate": False,
                        "labelIds": [],
                        "mergeType": "NONE",
                        "mltTimePeriodDTO": {
                            "timePeriods": [],
                            "timeSegment": "POINT_96"
                        },
                        "orgId": self.tenantId,
                        "ownerIds": [unit["unitId"]],
                        "tradingModeIds": ["4", "5"]
                    }

                    response = \
                    CommonClass.execRequest(self.session, json=josnDic, method=method, url=url).json()['data'][
                        "mltContractRespDTO"]
                    # print(dateStr)
                    # print(response)

                    if response == None:
                        continue

                    # 通过电量判断是否有数据
                    if response["contractTotalEle"] == None:
                        continue

                    tempStr = dateStr + "-" + dataItem + "-" + unit["unitId"]

                    haveDataResList.append(tempStr)

        return haveDataResList

    #中长期合同：方法2，判断每一天96点电量，不用每天遍历
    def getContractStatus(self,startDate,endDate,unitInfo):

        url = self.domain + "/sxAdss/api/mlt/position/detail"
        method = "POST"

        haveDataResList = []

        dataItems = {
            "分时交易合同数据": {
                "contractTypeIds": ["1"],
            },
            "双边与挂牌合同数据": {
                "contractTypeIds": ["2","3"],
            }
        }


        for unit in unitInfo:
            print("中长期数据", unit["unitName"])
            for dataItem in dataItems.keys():

                josnDic = {
                    "contractNames": [],
                    "contractTypeIds": dataItems[dataItem]["contractTypeIds"],
                    "datePeriodDTOS": [{
                        "startDate": startDate,
                        "endDate": endDate
                    }],
                    "eleDiameter": "ONLINE_ELE",
                    "isSeparate": False,
                    "labelIds": [],
                    "mergeType": "NONE",
                    "mltTimePeriodDTO": {
                        "timePeriods": [],
                        "timeSegment": "POINT_96"
                    },
                    "orgId": self.tenantId,
                    "ownerIds": [unit["unitId"]],
                    "tradingModeIds": ["4", "5"]
                }

                response = \
                CommonClass.execRequest(self.session, json=josnDic, method=method, url=url).json()['data'][
                    "mltContractRespDTO"]["mltPositionDetailDetailDTOList"]
                # print(dateStr)
                # print(response)

                if response == None:
                    continue

                for r in response:
                    eleList = r["contractEle"]
                    if CommonClass.judgeListIsNone(eleList) :
                        continue

                    dateStr = r["date"][:10]

                    tempStr = dateStr + "-" + dataItem + "-" + unit["unitId"]

                    haveDataResList.append(tempStr)

        return haveDataResList


    def statisticsUploadStatus(self, startDate,endDate ):
        unitInfo = self.getUnit()

        dataStatusList = []
        dataStatusList.extend(self.getContractStatus(startDate,endDate,unitInfo)   )
        dataStatusList.extend(self.getDaySettlementDetailStatus(startDate,endDate,unitInfo)   )
        dataStatusList.extend(self.getSettlementStatus(startDate,endDate,unitInfo)   )
        dataStatusList.extend(self.getStationPowerGenerationStatus(startDate,endDate,unitInfo)   )
        print(dataStatusList)
        print("上传状态已爬取完成")

        outputList = []

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        # 月结算已经判断过了就把这个月存到里面
        monthTrueList = []

        while sd <= ed:

            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            monthStr = dateStr[:7]

            for unit in unitInfo:

                unitName = unit["unitName"]
                unitId = unit["unitId"]

                for dataItem in dataItemDic.keys():

                    s = dateStr

                    if dataItem == "901":
                        s = monthStr

                        if (monthStr+"-"+unitId) in monthTrueList:
                            continue
                        monthTrueList.append(monthStr+"-"+unitId)

                    tempStr = s + "-" + dataItem + "-" + unitId
                    dateItemName = dataItemDic[dataItem]["name"]
                    dateItemType = dataItemDic[dataItem]["type"]

                    if dataItem == "1001":
                        if (tempStr+"-ZERO") in dataStatusList:
                            outputList.append(
                                {
                                    "日期": s,
                                    "数据类型": dateItemType,
                                    "数据项": dateItemName,
                                    "场站名称": unitName,
                                    "结果": "该日所有时刻点为0",
                                }
                            )
                            continue

                    if tempStr in dataStatusList:
                        outputList.append(
                            {
                                "日期": s,
                                "数据类型": dateItemType,
                                "数据项": dateItemName,
                                "场站名称": unitName,
                                "结果": "已经上传该数据项",
                            }
                        )
                        continue

                    outputList.append(
                        {
                            "日期" :  s,
                            "数据类型" :  dateItemType,
                            "数据项" : dateItemName ,
                            "场站名称" :  unitName,
                            "结果" :  "未上传该数据项",
                        }
                    )

            sd += timedelta(days=1)

        return outputList


    def statisticsUploadStatus1111(self, startDate,endDate ):


        unitsInfo = self.getUnit()
        checkItemResultDict = self.initDict(unitsInfo, startDate, endDate)

        dataStatusList = []
        # dataStatusList.extend(self.getContractStatus(startDate,endDate,unitsInfo)   )
        dataStatusList.extend(self.getDaySettlementDetailStatus(startDate,endDate,unitsInfo)   )
        dataStatusList.extend(self.getSettlementStatus(startDate,endDate,unitsInfo)   )
        dataStatusList.extend(self.getStationPowerGenerationStatus(startDate,endDate,unitsInfo)   )
        print(dataStatusList)
        print("上传状态已爬取完成")

        outputList = []

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")
        # 月结算已经判断过了就把这个月存到里面
        monthTrueList = []

        while sd <= ed:

            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            monthStr = dateStr[:7]
            sd += timedelta(days=1)

            for unit in unitsInfo:

                unitName = unit["unitName"]
                unitId = unit["unitId"]

                for dataItem in dataItemDic.keys():


                    s = dateStr

                    if dataItem == "901":
                        s = monthStr

                        if (monthStr+"-"+unitId) in monthTrueList:
                            continue

                    tempStr = s + "-" + dataItem + "-" + unitId
                    dateItemName = dataItemDic[dataItem]["name"]
                    dateItemType = dataItemDic[dataItem]["otherType"]

                    if dateItemType not in checkItemResultDict.keys():
                        continue

                    if dataItem == "1001":
                        if (tempStr+"-ZERO") in dataStatusList:
                            checkItemResultDict[dateItemType][unitName][s] = "所有时刻点都为0"
                            continue

                    checkItemResultDict[dateItemType][unitName][s] = "无数据"

        print(checkItemResultDict)
        return outputList


    def initDict(self,unitsInfo,startDate,endDate):

        d = {}
        unitNameList = [info["unitName"] for info in unitsInfo]

        for item in dataItemList:
            d[item] = {}
            for unit in unitNameList:
                d[item][unit] = {}
                sd = datetime.strptime(startDate, "%Y-%m-%d")
                ed = datetime.strptime(endDate, "%Y-%m-%d")
                while sd <= ed:

                    dateStr = datetime.strftime(sd, "%Y-%m-%d")
                    if item == "月结算单":
                        dateStr = datetime.strftime(sd, "%Y-%m")
                    sd += timedelta(days=1)
                    d[item][unit][dateStr] = "有数据"

        return d


    def outputData(self,outputList):
        # print(outputList)
        try:
            print("获取模板")
            tempPath = CommonClass.mkDir("山西新能源数据校验",  "导出", "导出模板.xlsx", isGetStr=True)
            print(tempPath)
            templateE = ExcelHeplerXlwing(tempPath)
            template = templateE.getTemplateStyle("Sheet1")
        finally:
            templateE.close()

        # 获取当前时间
        now = datetime.now()

        # 转换为文本
        text_time = now.strftime('%Y-%m-%d-%H.%M.%S')

        savePath = CommonClass.mkDir("山西新能源数据校验",  "导出", text_time+"输出结果.xlsx", isGetStr=True)
        e = ExcelHeplerXlwing()

        try:
            print("开始导出")
            e.newExcel(sheetName="数据上传结果", templateStyle=template)
            e.writeData(savePath, "数据上传结果",outputList)
            print("导出结束")
        finally:
            e.close()

    def execMain(self, startDate,endDate ):
        outputList = self.statisticsUploadStatus1111(startDate,endDate)
        # self.outputData(outputList)

if __name__ == '__main__':


    info = {
        "url_domain" :  "https://adssx-test-gzdevops3.tsintergy.com",
        "logininfo" : {
            "publicKey_url" :  None,
            "login_url" :  "/usercenter/web/login",
            "switch_url" :  "/usercenter/web/switchTenant?tenantId=" ,
            "username" :  "zhanzw_czc",
            "password" :  "passwd123@",
            "loginMode" :  2,
        },
        "tenantId" : "e4f736aa7cc47f7c017ce4c3ac2302bc",
    }


    testSession = requests.Session()
    sx = Shanxi(testSession,info)
    sx.login()

    startDate = "2024-06-23"
    endDate = "2024-06-23"

    # unitInfo = sx.getUnit()
    sx.execMain(startDate,endDate)


    pass

