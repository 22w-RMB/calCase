import calendar

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
        "type2" : "原始功率预测"
    },
    "101":  {
        "name" : "申报短期功率预测",
        "type" : "场站发电数据",
        "type2" : "申报功率预测"
    },

    "401":  {
        "name" : "中长期总加曲线",
        "type" : "省内现货交易",
        "type2" : "中长期总加曲线"
    },
    "402":  {
        "name" : "日前出力计划",
        "type" : "省内现货交易",
        "type2" : "省内现货结果"
    },
    "403":  {
        "name" : "日内出力计划",
        "type" : "省内现货交易",
        "type2" : "省内现货结果"
    },
    "405":  {
        "name" : "日前节点电价",
        "type" : "省内现货交易",
        "type2" : "省内现货结果"
    },
    "406":  {
        "name" : "日内节点电价",
        "type" : "省内现货交易",
        "type2" : "省内现货结果"
    },
    "1001":  {
        "name" : "中长期基数电量",
        "type" : "省内现货交易",
        "type2" : "中长期基数电量"
    },
    "301": {
        "name": "省间日前结算电价",
        "type": "省间现货交易",
        "type2" : "省间日前交易结果"
    },
    "302": {
        "name": "省间日前结算电量",
        "type": "省间现货交易",
        "type2" : "省间日前交易结果"
    },
    "304": {
        "name": "省间日内结算电价",
        "type": "省间现货交易",
        "type2" : "省间日内交易结果"
    },
    "305": {
        "name": "省间日内结算电量",
        "type": "省间现货交易",
        "type2" : "省间日内交易结果"
    },
    "buySellContract" : {
        "name": "购售电合同",
        "type": "日清分单结算明细-中长期数据",
        "type2" : "日清分单结算明细-中长期数据"
    },
    "marketContract":{
        "name": "市场化合同",
        "type": "日清分单结算明细-中长期数据",
        "type2" : "日清分单结算明细-中长期数据"
    },
    "proInDayAhead":{
        "name": "日前数据",
        "type": "日清分单结算明细-日前数据",
        "type2" : "日清分单结算明细-日前数据"
    },
    "proInRealTime": {
        "name": "实时数据",
        "type": "日清分单结算明细-实时数据",
        "type2" : "日清分单结算明细-实时数据"
    },

    "501" :{
        "name": "日清分单",
        "type": "日清分单",
        "type2" : "日清分单"
    },
    "901": {
        "name": "月结算单",
        "type": "月结算单",
        "type2" : "月结算单"
    },

    "分时交易合同数据": {
        "name": "分时交易合同数据",
        "type": "中长期合同数据",
        "type2" : "分时交易合同数据"
    },
    "双边与挂牌合同数据": {
        "name": "双边与挂牌合同数据",
        "type": "中长期合同数据",
        "type2" : "双边与挂牌合同数据"
    }
}

def getBusinessTypeStr(businessTypeId):

    for b in businessType:
        if businessTypeId == b["id"]:
            return b["name"]
    return None


def find_missing_dates(given_dates, date_format="%Y-%m-%d"):
    # 将给定的日期字符串转换为datetime对象，并排序
    given_dates = sorted([datetime.strptime(date, date_format) for date in given_dates])


    # 初始化一个列表来存储缺失的日期范围
    missing_ranges = []

    temp_start = given_dates[0].strftime("%m.%d")
    temp_end = ""
    # 遍历参考日期范围内的每一天
    for i in range(1,len(given_dates)):

        flag1 = (given_dates[i] == (given_dates[i-1] + timedelta(days=1)))
        flag2 = (i==len(given_dates)-1)

        if flag1:
            temp_end = given_dates[i].strftime("%m.%d")
            if flag2:
                missing_ranges.append(f"{temp_start}-{temp_end}")

        else:
            if temp_end == "":
                missing_ranges.append(temp_start)
            else:
                missing_ranges.append(f"{temp_start}-{temp_end}")

                temp_end = ""
            temp_start = given_dates[i].strftime("%m.%d")
            if flag2:
                missing_ranges.append(given_dates[i].strftime("%m.%d"))



    if len(given_dates)==1:
        missing_ranges.append(temp_start)
    # 使用"/"连接缺失的日期范围，并返回结果字符串
    return "缺少" + "/".join(missing_ranges) + "数据"

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
            print("省内现货出清数据", unit["unitName"])
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

                    if CommonClass.judgeListIsNone( dataList ) == True:
                            continue
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
            print("===",response)
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


    def statisticsUploadStatus(self, startDate, endDate ):
        unitInfo = self.getUnit()

        dataStatusList = []
        dataStatusList.extend(self.getContractStatus(startDate,endDate,unitInfo)   )
        dataStatusList.extend(self.getDaySettlementDetailStatus(startDate,endDate,unitInfo)   )
        dataStatusList.extend(self.getSettlementStatus(startDate,endDate,unitInfo)   )
        dataStatusList.extend(self.getStationPowerGenerationStatus(startDate,endDate,unitInfo)   )
        # print(dataStatusList)
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
                    dateItemType2 = dataItemDic[dataItem]["type2"]

                    if dataItem == "1001":
                        if (tempStr+"-ZERO") in dataStatusList:
                            outputList.append(
                                {
                                    "日期": s,
                                    "数据类型": dateItemType,
                                    "数据类型2": dateItemType2,
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
                                "数据类型2": dateItemType2,
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
                            "数据类型2": dateItemType2,
                            "数据项" : dateItemName ,
                            "场站名称" :  unitName,
                            "结果" :  "未上传该数据项",
                        }
                    )

            sd += timedelta(days=1)


        return outputList

    def outputListTrans(self, outputList, startDate, endDate ):
        # print(outputList)
        unUploadDataList = list(filter(lambda x: x['结果'] != '已经上传该数据项', outputList))
        unitInfo = self.getUnit()

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

        resDict = {}
        dateLen = int(endDate[8:])

        for item in dataItemList:
            resDict[item] = {}

            for unit in unitInfo:
                resDict[item][unit['unitName']] = "√"
                filterItemList = list(filter(lambda x: (x["数据类型2"] == item) and (x["场站名称"] == unit['unitName'] ), unUploadDataList))


                # print(item, unit['unitName'], filterItemList)
                if filterItemList == []:
                    continue

                tempList1 = list(sorted(list(set((map(lambda x: x["日期"], filterItemList))))))
                # print(item, unit['unitName'], tempList1)

                # if item == "省内现货结果" and unit['unitName']=="大梁山风电场":
                #
                #     print("===111 ",filterItemList)
                #     print("===111 ",len(tempList1))
                #     return

                if item == "月结算单" or dateLen == len(tempList1):
                    resDict[item][unit['unitName']] = "无数据"
                else:
                    resDict[item][unit['unitName']] = find_missing_dates(tempList1)


        return resDict

    def outputListTransFile(self,outputDict,yearMonth):
        # print(outputList)
        try:
            print("获取模板")
            tempPath = CommonClass.mkDir("山西新能源数据校验",  "导出", "华润验收清单模版.xlsx", isGetStr=True)
            print(tempPath)
            # templateE = ExcelHeplerXlwing(tempPath)
            # template = templateE.getTemplateStyle("私有数据测试明细")

            # 获取当前时间
            now = datetime.now()
            savePath = CommonClass.mkDir("山西新能源数据校验", "导出", yearMonth + "验收清单.xlsx", isGetStr=True)
            e = ExcelHeplerXlwing()
            month = str(int(yearMonth[5:]))
            print("开始导出")
            # e.newExcel(sheetName=month + "月私有数据测试明细", templateStyle=template)
            e.copySheet(tempPath,"私有数据测试明细",month + "月私有数据测试明细")
            e.writePrivateDetailData(savePath, month + "月私有数据测试明细", outputDict)

            e.copySheet(tempPath, "私有数据", "私有数据（"+month + "月）")
            e.writePrivateOverviewData(savePath, "私有数据（"+month + "月）", outputDict)

            print("导出结束")


        finally:
            # templateE.close()
            e.close()


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

    def execMain(self, startDate=None,endDate=None,year=None,month=None ):

        if startDate is not None:
            outputList = self.statisticsUploadStatus(startDate,endDate)
            # self.outputData(outputList)
            outputDict = self.outputListTrans(outputList, startDate, endDate)
            self.outputListTransFile(outputDict, startDate[:7])
        else:
            start = 1
            end = 13
            if month is not None:
                start = month
                end = month+1
            for m in range(start,end):
                # 获取月份的第一天
                first_day = datetime(year, m, 1)

                # 获取月份的天数（考虑闰年）
                last_day_num = calendar.monthrange(year, m)
                print(last_day_num)
                # 获取月份的最后一天
                last_day = datetime(year, m, last_day_num[1])

                startDate = first_day.strftime("%Y-%m-%d")
                endDate = last_day.strftime("%Y-%m-%d")
                print(startDate,endDate)
                outputList = self.statisticsUploadStatus(startDate,endDate)
                # self.outputData(outputList)
                outputDict = self.outputListTrans(outputList,startDate,endDate)
                self.outputListTransFile(outputDict,startDate[:7])
if __name__ == '__main__':


    # info = {
    #     "url_domain" :  "https://adssx-test-gzdevops3.tsintergy.com",
    #     "logininfo" : {
    #         "publicKey_url" :  None,
    #         "login_url" :  "/usercenter/web/login",
    #         "switch_url" :  "/usercenter/web/switchTenant?tenantId=" ,
    #         "username" :  "zhanzw_czc",
    #         "password" :  "passwd123@",
    #         "loginMode" :  2,
    #     },
    #     "tenantId" : "e4f736aa7cc47f7c017ce4c3ac2302bc",
    # }

    info = {
        "url_domain" :  "https://pets.crnewenergy.com.cn",
        "logininfo" : {
            "publicKey_url" :  "/usercenter/web/pf/login/info/publicKey",
            "login_url" :  "/usercenter/web/login",
            "switch_url" :  "/usercenter/web/switchTenant?tenantId=" ,
            "username" :  "tsintergy",
            "password" :  "tsintergy@123",
            "loginMode" :  2,
        },
        "tenantId" : "tsintergy",
    }

    testSession = requests.Session()
    sx = Shanxi(testSession,info)
    sx.login()

    # startDate = "2024-08-05"
    # endDate = "2024-08-05"
    # sx.execMain(startDate,endDate)

    # unitInfo = sx.getUnit()

    sx.execMain(year=2024,month=8)

    # r = find_missing_dates(['2024-06-01', '2024-06-02','2024-06-03', '2024-06-24', '2024-06-25'] , date_format="%Y-%m-%d")
    # print(r)
    pass

