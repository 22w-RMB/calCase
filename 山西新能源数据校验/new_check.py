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

# 省间通道
interProvinceClearingPowerChannelName = [
    "总加-日前",
    "总加-日内",
    "山西送上海-日前",
    "山西送浙江-日前",
    "山西送重庆-日前",
    "山西送江西-日前",
    "山西送吉林-日前",
    "山西送苏南-日前",
    "山西送陕西-日前",
    "山西送冀北-日前",
    "山西送湖北-日前",
    "山西送宁夏-日前",
    "山西送蒙东-日前",
    "山西送四川主网-日前",
    "山西送安徽-日前",
    "山西送甘肃东部-日前",
    "山西送冀北-日内",
    "山西送天津-日内",
    "山西送浙江-日内",
    "山西送陕西-日内",
    "山西送河北-日内",
    "山西送上海-日内",
    "山西送吉林-日内",
]

# 联络线通道
callWirePowerChannelName = [
    "总加日前",
    "河北负荷日前",
    "华北负荷日前",
    "京津唐日前",
    "山西送京津唐日前",
    "山西送雁淮日前",
    "山西送锡泰日前",
    "特高压长南线日前",
    "特高压雁淮直流外送日前",
    "山西送雁淮(月计划)日前",
    "山西送京津唐(省间现货)日前",
    "山西送河北(省间现货)日前",
    "山西送锡泰(省间现货)日前",
    "山西送锡泰(月计划)日前",
    "山西送雁淮(省间现货)日前",
    "山西送京津唐(月计划)日前",
    "山西送河北(华北跨省)日前",
    "京津唐送雁淮(月计划)日前",
    "山西送河北(月计划)日前",
    "山西送京津唐(华北跨省)日前",
    "京津唐送雁淮(省间现货)日前",
    "长南线(月计划)日前",
    "长南线(省间现货)日前",
    "京津唐送雁淮(过境)日前",
    "总加实时",
    "河北负荷实时",
    "华北负荷实时",
    "京津唐实时",
    "山西送京津唐实时",
    "山西送雁淮实时",
    "特高压雁淮直流外送实时",
    "山西送锡泰实时",
    "特高压长南线实时",
    "山西送雁淮(月计划)实时",
    "山西送京津唐(省间现货)实时",
    "山西送河北(省间现货)实时",
    "山西送锡泰(省间现货)实时",
    "山西送锡泰(月计划)实时",
    "山西送雁淮(省间现货)实时",
    "山西送京津唐(月计划)实时",
    "山西送河北(华北跨省)实时",
    "京津唐送雁淮(月计划)实时",
    "山西送河北(月计划)实时",
    "山西送京津唐(华北跨省)实时",
    "京津唐送雁淮(省间现货)实时",
    "长南线(月计划)实时",
    "长南线(省间现货)实时",
]

def getBusinessTypeStr(businessTypeId):

    for b in businessType:
        if businessTypeId == b["id"]:
            return b["name"]
    return None


def find_missing_dates(given_dates, date_format="%Y-%m-%d", allDateLen=None):
    # 将给定的日期字符串转换为datetime对象，并排序
    given_dates = sorted([datetime.strptime(date, date_format) for date in given_dates])

    # 初始化一个列表来存储缺失的日期范围
    missing_ranges = []

    if given_dates == []:
        return "√"

    if len(given_dates) == allDateLen:
        return "无数据"

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


def getPublicMarketNoDayList(dataList,marketType=None,itemName=None,fieldType=None,fieldName=None,allDateList=None):

    # 过滤出日前或实时的数据
    filterList1 = list(filter(lambda x:x['marketType'] == marketType, dataList))
    # 如果是联络线或者通道或新能源，那么
    if fieldType is not None:
        filterList1 = list(filter(lambda x:x[fieldType] == fieldName, filterList1))
    # 进一步过滤出96点数据不为空的日期
    filterList2 = list(filter(lambda x: CommonClass.judgeListIsNone(x[itemName]) == False, filterList1))
    # 生成有数据的日期
    havaDataDate = [d['date'][:10] for d in filterList2]
    # 生成没有数据的日期
    noDataDate = list(set(allDateList) - set(havaDataDate))

    return noDataDate



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


    # 私有数据上传状态合并&处理
    def statisticsPrivateUploadStatus(self, startDate, endDate ):
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


    # 转换私有数据上传状态格式
    def privateOutputListTrans(self, outputList, startDate, endDate ):
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


    # 私有数据上传状态格式转换后输出到验收清单
    def privateOutputListTransFile(self,outputDict,yearMonth):
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


    # 私有数据最详细数据项的上传状态输出
    def privateOutputData(self,outputList):
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


    def execPrivateMain(self, startDate=None,endDate=None,year=None,month=None ):

        if startDate is not None:
            outputList = self.statisticsPrivateUploadStatus(startDate,endDate)
            # self.privateOutputData(outputList)
            outputDict = self.privateOutputListTrans(outputList, startDate, endDate)
            self.privateOutputListTransFile(outputDict, startDate[:7])
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
                outputList = self.statisticsPrivateUploadStatus(startDate,endDate)
                # self.privateOutputData(outputList)
                outputDict = self.privateOutputListTrans(outputList,startDate,endDate)
                self.privateOutputListTransFile(outputDict,startDate[:7])


    def publicMarketData(self,startDate,endDate):

        allDateList = []
        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")
        while sd <= ed:
            dateStr = datetime.strftime(sd,"%Y-%m-%d")
            allDateList.append(dateStr)
            sd += timedelta(days=1)

        marketMethod = "POST"
        marketUrl = self.domain +"/PublicDataManage/014/api/spot/market/info"
        marketJson = {
            "dateMerge": {
                "aggregateType": "AVG",
                "mergeType": "NONE"
            },
            "dateRanges": [{
                "start": startDate,
                "end": endDate
            }],
            "marketType": None,
            "provinceAreaId": "014",
            "timeSegment": {
                "aggregateType": None,
                "filterPoints": None,
                "segmentType": "SEG_96"
            },
            "statistics": {
                "groupType": "RANGE"
            }
        }
        responseData = CommonClass.execRequest(self.session,url=marketUrl,method=marketMethod,json=marketJson,).json()["data"]
        # print(responseData)

        itemUploadStatusDict = {}

        marketItemDict ={
            '日前节点边际电价' : [
                {
                    'dataListKey' : "marketClearingPrice",
                    'marketType' : "DAY_AHEAD",
                    'itemName' : "price",
                    'fieldType' : None,
                    'fieldName' : None,
                }
            ],
            '日前现货价格预测': [
                {
                    'dataListKey': "marketClearingPrice",
                    'marketType': "DAY_AHEAD",
                    'itemName': "priceForecast",
                    'fieldType': None,
                    'fieldName': None,
                }
            ],
            '现货出清电价': [
                {
                    'dataListKey': "marketClearingPrice",
                    'marketType': "DAY_AHEAD",
                    'itemName': "price",
                    'fieldType': None,
                    'fieldName': None,
                },
                {
                    'dataListKey': "marketClearingPrice",
                    'marketType': "REAL_TIME",
                    'itemName': "price",
                    'fieldType': None,
                    'fieldName': None,
                },
            ],
            '日前省间现货出清电价情况': [
                {
                    'dataListKey': "interProvinceClearingPrice",
                    'marketType': "DAY_AHEAD",
                    'itemName': "price",
                    'fieldType': None,
                    'fieldName': None,
                },
            ],
            '日内省间现货出清电价情况': [
                {
                    'dataListKey': "interProvinceClearingPrice",
                    'marketType': "REAL_TIME",
                    'itemName': "price",
                    'fieldType': None,
                    'fieldName': None,
                },
            ],
            '日前新能源负荷预测': [
                {
                    'dataListKey': "newEnergyPower",
                    'marketType': "DAY_AHEAD",
                    'itemName': "power",
                    'fieldType': "type",
                    'fieldName': "NEW_ENERGY",
                },
            ],
            '日前统调系统负荷预测': [
                {
                    'dataListKey': "systemLoad",
                    'marketType': "DAY_AHEAD",
                    'itemName': "power",
                    'fieldType': "type",
                    'fieldName': "SHORT_TERM_FORECAST",
                },
            ],
            '非市场化机组出力': [
                {
                    'dataListKey': "nonMarketUnitPower",
                    'marketType': "DAY_AHEAD",
                    'itemName': "power",
                    'fieldType': None,
                    'fieldName': None,
                },
                {
                    'dataListKey': "nonMarketUnitPower",
                    'marketType': "REAL_TIME",
                    'itemName': "power",
                    'fieldType': None,
                    'fieldName': None,
                },
            ],
            '可再生能源富余程度': [
                {
                    'dataListKey': "powerLimit",
                    'marketType': None,
                    'itemName': "limitStatus",
                    'fieldType': None,
                    'fieldName': None,
                },
            ],

        }

        # 对数据项批量处理
        for itemName,itemConfig in marketItemDict.items():
            set1 = set()
            for ic in itemConfig:
                noDayList = getPublicMarketNoDayList(responseData[ic['dataListKey']], marketType=ic['marketType'],
                                                     itemName=ic['itemName'], fieldType=ic['fieldType'],
                                                     fieldName=ic['fieldName'],allDateList=allDateList)
                set1 = set1.union(set(noDayList))

            itemUploadStatusDict[itemName] = find_missing_dates(list(set1),allDateLen=len(allDateList))
        print(itemUploadStatusDict)

        # 省间通道
        for channel in interProvinceClearingPowerChannelName:
            channelName = channel.split("-")[0]
            marketType = "DAY_AHEAD" if channel.split("-")[1] == "日前" else "REAL_TIME"
            itemUploadStatusDict["省间-"+channel] = find_missing_dates(
                getPublicMarketNoDayList(responseData['interProvinceClearingPower'], marketType=marketType,
                                         itemName="power", fieldType="channelName", fieldName=channelName, allDateList=allDateList),
                allDateLen=len(allDateList)
            )
            # print(channel, itemUploadStatusDict[channel])

        # 联络线通道
        for channel in callWirePowerChannelName:
            channelName = channel[:-2]
            marketType = "DAY_AHEAD" if "日前" in channel else "REAL_TIME"
            itemUploadStatusDict["联络线-"+channel] = find_missing_dates(
                getPublicMarketNoDayList(responseData['callWirePower'], marketType=marketType,
                                         itemName="power", fieldType="channelName", fieldName=channelName, allDateList=allDateList),
                allDateLen=len(allDateList)
            )
            # print(channel, itemUploadStatusDict[channel])




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

    # info = {
    #     "url_domain" :  "https://pets.crnewenergy.com.cn",
    #     "logininfo" : {
    #         "publicKey_url" :  "/usercenter/web/pf/login/info/publicKey",
    #         "login_url" :  "/usercenter/web/login",
    #         "switch_url" :  "/usercenter/web/switchTenant?tenantId=" ,
    #         "username" :  "tsintergy",
    #         "password" :  "tsintergy@123",
    #         "loginMode" :  2,
    #     },
    #     "tenantId" : "tsintergy",
    # }

    testSession = requests.Session()
    sx = Shanxi(testSession,info)
    sx.login()

    # startDate = "2024-08-05"
    # endDate = "2024-08-05"
    # sx.execPrivateMain(startDate,endDate)


    # sx.execPrivateMain(year=2024,month=8)


    startDate = "2024-08-01"
    endDate = "2024-08-31"
    sx.publicMarketData(startDate,endDate)

