import copy
import math
import os
from datetime import datetime, timedelta

import pandas
import pandas as pd

from 江西.cal.excel_handler import ExcelHepler,ExcelHeplerXlwing
from 江西.cal.mysqlTool import MysqlTool
from 江西.cal.otherTool import Tool
from common.common import CommonClass
import re
import calendar

from 江西.cal.private_data import PrivateData

unitYamlPath = CommonClass.mkDir("江西","config","unit_config.yaml",isGetStr=True)
dataPeakyamlPath = CommonClass.mkDir("江西","config","峰平谷.yaml",isGetStr=True)
unitInfoConfig = CommonClass.readYaml(unitYamlPath)
contractTypeEnum ={
    "市场化" : {
        "年度双边协商" : ["1","年度双边协商"],
        "月度交易" : ["2","月度交易" ],
        "月内连续融合" : ["3","月内连续交易"],
        "d-3日24时段滚动撮合" : ["6","d-3日24时段滚动撮合"],
        "省间外送" : ["7","省间外送电"],
    },
    "代理购电": {
        "年度代理购电挂牌": ["8", "年度代理购电"],
        "月度交易": ["9", "月度交易"],
        "月内连续融合": ["10", "月内连续交易"],
        "d-3日24时段滚动撮合": ["11", "d-3日24时段滚动撮合"],
    },
}
dataTypeEnum = {
    "24时" : "1",
    "日" : "2",
    "月" : "3",
}


contractTypeEnum1 = {
    "市场化":
        ["市场化,年度双边协商" ,
        "市场化,月度交易" ,
        "市场化,月内连续融合" ,
        "市场化,d-3日24时段滚动撮合" ,
        "市场化,省间外送" ],
    "代理购电":
        ["代理购电,年度代理购电挂牌" ,
        "代理购电,月度交易" ,
        "代理购电,月内连续融合" ,
        "代理购电,d-3日24时段滚动撮合" ]
}


# 根据账单别名和交易名称获取机组
def getUnitByOtherName(otherNameType,otherName,tenantName):

    unitsInfo = unitInfoConfig[tenantName]

    res = {
        "units" : [],
        "count" : 0,
    }

    delimiters = [';', '；']

    if otherNameType == "账单别名":

        for unit in unitsInfo:
            unitShortNameList = []
            if unit["unitShortName"] != None:
                # 分割多种符号
                unitShortNameList = re.split('|'.join(map(re.escape, delimiters)), unit["unitShortName"])
            unitShortNameList.append(unit["unitName"])
            if otherName in unitShortNameList:
                res["units"].append(unit["unitName"])
                res["count"] += 1

    if otherNameType == "交易单元名称":

        for unit in unitsInfo:
            controlUnitNameList = []
            if unit["controlUnitName"] != None:
                # 分割多种符号
                controlUnitNameList = re.split('|'.join(map(re.escape, delimiters)), unit["controlUnitName"])
            controlUnitNameList.append(unit["unitName"])
            if otherName in controlUnitNameList:
                res["units"].append(unit["unitName"])
                res["count"] += 1

    return res

# 将查询到的合同计算成24点结果
def cal24Info(dataList,lenght=24,isFilterNone=False):

    eleRes = [None for i in range(0,lenght)]
    priceRes = [None for i in range(0,lenght)]
    feeRes = [None for i in range(0,lenght)]

    for data in dataList:

        ele = data["ele"]
        price = data["price"]

        for i in range(0,lenght):

            if isFilterNone:
                if ele[i] == None or price[i]==None:
                    continue

            if ele[i] != None :
                eleRes[i] = ele[i] + (0 if eleRes[i] == None else eleRes[i])

            if ele[i] != None  and price[i] != None :
                feeRes[i] = (ele[i] * price[i]) + (0 if feeRes[i] == None else feeRes[i])

            if eleRes[i] != None  and feeRes[i] != None :
                priceRes[i] = feeRes[i] / eleRes[i]

            #
            # price[i] = 0 if price[i] == None else price[i]
            #
            # if eleRes[i] == None:
            #     eleRes[i] = ele[i]
            # if  feeRes[i] == None:
            #     feeRes[i] += (ele[i] * price[i])
            # if priceRes[i] == None:
            #     priceRes[i] = price[i]
            #     feeRes[i] = None
            # else:
            #     eleRes[i] += ele[i]
            #     feeRes[i] += (ele[i] * price[i])
            #     if eleRes[i] != 0 :
            #         priceRes[i] = feeRes[i] / eleRes[i]

    eleSum = 0
    priceSum = 0
    feeSum = 0


    for i in range(0,lenght):
        if eleRes[i] != None:
            eleSum += eleRes[i]
        if feeRes[i] != None:
            feeSum += feeRes[i]

    if eleSum != 0:
        priceSum = feeSum / eleSum

    # print("电量24点结果",eleRes)
    # print("电价24点结果",priceRes)
    # print("费用24点结果",feeRes)
    # print("总电量",eleSum)
    # print("均价",priceSum)
    # print("总费用",feeSum)

    return {
        "ele" : eleRes,
        "price" : priceRes,
        "fee" : feeRes,
        "eleSum" : eleSum,
        "priceSum" : priceSum,
        "feeSum" : feeSum,
        "lenght" : lenght,
    }

# 合同日电量明细校验
def dayEleDetailCheck(rowData,tenantName):
    keyNotNoneList = [
        "合同类型",
        "交易序列名称",
        "售方名称",
        "合同日期",
    ]

    keyIncludeField = {
        "市场化": ["年度双边协商", "月度交易", "d-3日24时段滚动撮合"],
        "代理购电": ["年度代理购电挂牌", "月度交易", "d-3日24时段滚动撮合"],
    }

    # 判断字段是否为空
    for key in keyNotNoneList:
        if rowData[key] == "":
            return {
                    "row": rowData.name + 1,
                    "info": "字段【" + key + "】为空",
                    "isContinue": True,
                }

    sell_name = rowData["售方名称"]
    unitInfo = getUnitByOtherName("账单别名",sell_name,tenantName)
    if unitInfo["count"] == 0 :
        return {
            "row": rowData.name + 1,
            "info": "售方名称【" + key + "】匹配不到机组",
            "isContinue": True,
        }

    # 判断合同类型是否正确
    contractType1 = rowData["合同类型"]
    if contractType1 not in keyIncludeField.keys():
        return {
            "row": rowData.name + 1,
            "info": "合同类型【" + key + "】不存在",
            "isContinue": True,
        }
    contractType2List = keyIncludeField[contractType1]
    contractType2 = None
    for i in range(0,len(contractType2List)+1):
        if i == len(contractType2List):
            return {
            "row": rowData.name + 1,
            "info": "合同序列【" + key + "】不包含对应关键字",
            "isContinue": True,
        }
        contractType2 = keyIncludeField[contractType1][i]
        if contractType2 in rowData["交易序列名称"]:
            break


    return {
        "contractType1":  contractType1,
        "contractType2":  contractType2,
        "unitInfo":  unitInfo,
        "isContinue":  False,
    }

# 合同日电量明细处理
def execDayEleDetail(filePath,fileName,sheetName,tenantName,year):

    header = [
        "序号",
        "合同名称",
        "合同类型",
        "交易序列名称",
        "售方名称",
        "购方名称",
        "购电类型",
        "合同日期",
        "日合计-电量",
        "日合计-均价",
    ]
    for i in range(1,25):
        header.append(str(i)+"-电量")
        header.append(str(i)+"-电价")

    e = ExcelHepler(filePath,sheetName,header)
    df = e.getDayEleDetail()


    resultDataList = {}
    errorInfoList = []


    for row in range(0,df.shape[0]):

        if row <=1:
            continue

        print("=============正在执行第" , row , "条")

        checkRes = dayEleDetailCheck(df.iloc[row],tenantName)
        if checkRes["isContinue"] :
            errorInfoList.append(checkRes)
            continue

        contractType1 = checkRes["contractType1"]
        contractType2 = checkRes["contractType2"]
        sell_name = df.iloc[row]["售方名称"]
        date = df.iloc[row]["合同日期"]
        transactionSequenceName = df.iloc[row]["交易序列名称"]
        buyer_name = df.iloc[row]["购方名称"] if df.iloc[row]["购方名称"]!=None else ""
        unitName = checkRes["unitInfo"]["units"][0]

        uniqueId = "-".join([contractType1,sell_name,date,transactionSequenceName,buyer_name])
        contractName = sell_name+buyer_name+transactionSequenceName
        ele = [None for i in range(0,24)]
        price = [None for i in range(0,24)]

        for i in range(0,24):
            eleData = df.iloc[row][str(i+1)+"-电量"]
            priceData = df.iloc[row][str(i+1)+"-电价"]
            if eleData != "" :
                ele[i] = eleData
            if priceData != "" :
                price[i] = priceData

        if uniqueId not in resultDataList.keys():
            resultDataList[uniqueId] = {
                "contractName" : contractName,
                "contractType1" : contractType1,
                "contractType2" : contractType2,
                "sell_name" : sell_name,
                "buyer_name" : buyer_name,
                "date" : date,
                "transactionSequenceName" : transactionSequenceName,
                "ele" : ele,
                "price" : price,
                "unitName" : unitName,
            }

        else:
            calRes = cal24Info(
                [
                    {"ele": ele ,"price":price},
                    {"ele":  resultDataList[uniqueId]["ele"] ,"price":resultDataList[uniqueId]["price"]}
                ]
            )

            resultDataList[uniqueId]["ele"] = calRes["ele"]
            resultDataList[uniqueId]["price"] = calRes["price"]



    # print(resultDataList)
    writeContract(resultDataList)


# 合同分月查询校验
def monthEleDetailCheck(rowData,tenantName):
    keyNotNoneList = [
        "合同类型",
        "交易序列名称",
        "售方名称",
    ]

    keyIncludeField = {
        "市场化": ["月内连续融合", "省间外送"],
        "代理购电": ["月内连续融合"],
    }

    # 判断字段是否为空
    for key in keyNotNoneList:
        if rowData[key] == "":
            return {
                    "row": rowData.name + 1,
                    "info": "字段【" + key + "】为空",
                    "isContinue": True,
                }

    sell_name = rowData["售方名称"]

    unitInfo = getUnitByOtherName("交易单元名称",sell_name,tenantName)
    if unitInfo["count"] == 0 :
        return {
            "row": rowData.name + 1,
            "info": "售方名称【" + sell_name + "】匹配不到机组",
            "isContinue": True,
        }

    # 判断合同类型是否正确
    contractType1 = rowData["合同类型"]
    if contractType1 not in keyIncludeField.keys():
        return {
            "row": rowData.name + 1,
            "info": "合同类型【" + contractType1 + "】不存在",
            "isContinue": True,
        }
    contractType2List = keyIncludeField[contractType1]
    contractType2 = None
    for i in range(0,len(contractType2List)+1):
        if i == len(contractType2List):
            return {
            "row": rowData.name + 1,
            "info": "合同序列【" + rowData["交易序列名称"] + "】不包含对应关键字",
            "isContinue": True,
        }
        contractType2 = keyIncludeField[contractType1][i]
        if contractType2 in rowData["交易序列名称"]:
            break


    return {
        "contractType1":  contractType1,
        "contractType2":  contractType2,
        "unitInfo":  unitInfo,
        "isContinue":  False,
    }


# 合同分月查询处理
def execMonthEleDetail(filePath,fileName,sheetName,tenantName,year):
    header = [
        "序号",
        "交易序列名称",
        "售方名称",
        "购方名称",
        "时段类型",
        "合同电量",
        "合同电价",
    ]

    for i in range(1,13):
        header.append(str(i)+"-月电量")
    for i in range(1,13):
        header.append(str(i)+"-月电价")
    header.append("合同类型")
    header.append("合同名称")

    e = ExcelHepler(filePath,sheetName,header)
    df = e.getMonthEleDetail()
    #
    # rowList = []
    # for row in range(0,df.shape[0]):
    #     rowList.append(row)
    #
    # df.reset_index()
    resultDataList = {}
    errorInfoList = []

    # print(df)

    for row in range(0,df.shape[0]):

        if row <=1:
            continue

        print("=============正在执行第" , row , "条")

        checkRes = monthEleDetailCheck(df.iloc[row],tenantName)
        if checkRes["isContinue"] :
            errorInfoList.append(checkRes)
            continue

        contractType1 = checkRes["contractType1"]
        contractType2 = checkRes["contractType2"]
        sell_name = df.iloc[row]["售方名称"]
        transactionSequenceName = df.iloc[row]["交易序列名称"]
        buyer_name = df.iloc[row]["购方名称"] if df.iloc[row]["购方名称"]!=None else ""
        unitInfo = checkRes["unitInfo"]

        uniqueId = contractType1+sell_name+transactionSequenceName+buyer_name
        contractName = sell_name+buyer_name+transactionSequenceName
        ele = [None for i in range(0,12)]
        price = [None for i in range(0,12)]

        for i in range(0,12):
            eleData = df.iloc[row][str(i+1)+"-月电量"]
            priceData = df.iloc[row][str(i+1)+"-月电价"]
            if eleData != "" :
                ele[i] = eleData
            if priceData != "" :
                price[i] = priceData

        if uniqueId not in resultDataList.keys():
            resultDataList[uniqueId] = {
                "contractName" : contractName,
                "contractType1" : contractType1,
                "contractType2" : contractType2,
                "sell_name" : sell_name,
                "buyer_name" : buyer_name,
                "transactionSequenceName" : transactionSequenceName,
                "ele" : ele,
                "price" : price,
                "unitInfo" : unitInfo,
            }

        else:
            calRes = cal24Info(
                [
                    {"ele": ele ,"price":price},
                    {"ele":  resultDataList[uniqueId]["ele"] ,"price":resultDataList[uniqueId]["price"]}
                ],
                lenght=12
            )

            resultDataList[uniqueId]["ele"] = calRes["ele"]
            resultDataList[uniqueId]["price"] = calRes["price"]

    finalDataDic = {}
    finalDataCount = 0

    for key in resultDataList:

        monthEle = resultDataList[key]["ele"]
        monthPrce = resultDataList[key]["price"]
        unitCount = resultDataList[key]["unitInfo"]["count"]
        units = resultDataList[key]["unitInfo"]["units"]

        for i in range(0,12):
            if monthEle[i] == None and monthPrce[i]==None:
                continue
            # 每个月的天数
            daysCount = calendar.monthrange(int(year), i+1)[1]
            # 所有机组每一天的电量
            dayEleData = monthEle[i]/daysCount if monthEle[i] != None else None
            # 所有机组每一天24点的电量
            time24EleData = dayEleData/24 if dayEleData != None else None

            # 每个机组每一天24点的电量和电价
            unitTime24EleData = time24EleData / unitCount if time24EleData != None else None
            unitTime24PriceData = monthPrce[i]  if monthPrce[i] != None else None

            for j in range(0,daysCount):
                dateStr = "-".join([year,str(i+1),str(j+1)])

                for unit in units:
                    tempDic = copy.deepcopy(resultDataList[key])
                    tempDic["unitName"] = unit
                    tempDic["ele"] = [unitTime24EleData for i in range(0,24)]
                    tempDic["price"] = [unitTime24PriceData for i in range(0,24)]
                    tempDic["date"] = dateStr
                    finalDataDic[finalDataCount] = tempDic
                    finalDataCount += 1


    # print(finalDataDic)
    # print(errorInfoList)
    writeContract(finalDataDic)

def generateDayMonthData(resultDataList):

    dayDataDic = {}
    monthDataDic = {}

    for key in resultDataList:
        data = resultDataList[key]
        dayDataKey = "-".join([data["contractName"] , data["unitName"] , data["date"][:7] ,  data["contractType1"] , data["contractType2"]])
        monthDataKey = "-".join([data["contractName"] , data["unitName"] , data["date"][:7] ,  data["contractType1"], data["contractType2"]])


    pass

# 写入到数据库
def writeContract(resultDataList):
    writeSqlList = []


    for key in resultDataList:
        data = resultDataList[key]

        # if "瑞金二期厂/20kV.#3机国网江西电力江西电力市场2023年年度代理购电挂牌交易（正式）" == data["contractName"]:
        #     print(resultDataList[key])


        writeSqlList.append(
            (
                data["contractName"],
                data["unitName"],
                None if data["buyer_name"]=="" else data["buyer_name"],
                data["sell_name"],
                str(data["ele"]),
                str(data["price"]),
                data["date"],
                data["contractType1"],
                data["contractType2"],
                "24时",
            )
        )

    # print(writeSqlList[0])
    db = MysqlTool()
    db.insertContract(writeSqlList)
    db.close()

# 查询本地数据
def queryLocalContract(unitName,contractName,contractType1,contractType2,startDate,endDate,dataType):

    d = {
        "unit": unitName,
        "contract_name": contractName,
        "contract_type1": contractType1,
        "contract_type2": contractType2,
        "dataType": dataType,
        "start_date": startDate,
        "end_date": endDate,
    }

    db = MysqlTool()

    queryRes = db.queryContract(d)

    # print(queryRes)
    db.close()

    for r in queryRes:
        r["ele"] = eval(r["ele"].replace("null", "None"))
        r["price"] = eval(r["price"].replace("null", "None"))

    return queryRes

# 查询测试环境数据
def queryRemoteContract(unitName):

    d = {
        "unit_name": unitName,
    }

    db = MysqlTool(host="192.168.1.76",
        port=3306,
        user="adss_jx_test",
        password="qinghua123@",
        database="adss_jx_test",
        charset="utf8",)

    queryRes = db.queryRemoteContractData(d)

    # print(queryRes)
    db.close()

    for r in queryRes:
        r["ele"] = eval(r["ele"].replace("null", "None"))
        r["price"] = eval(r["price"].replace("null", "None"))

    return queryRes

# 和测试环境比较数据
def compareContract(unitName,contractName,contractType1,contractType2,startDate,endDate,dataType):

    errorDetail = {
        "日期" :[],
        "类型" :[],
        "维度" :[],
        "错误信息" :[],
        "合同名称" :[],
        "合同品种" :[],
        "合同类型" :[],
        "算例单点数据" :[],
        "系统单点数据" :[],
        "错误位置" :[],
        "算例所有数据" :[],
        "系统所有数据" :[],
    }

    localDataList = queryLocalContract(unitName, contractName, contractType1, contractType2, startDate, endDate, dataType)
    remoteDataList = queryRemoteContract(unitName)

    # print(localDataList)

    remoteDataDic = {}

    for remoteData in remoteDataList:

        dateStr = remoteData["date"]
        cType = "" if remoteData["contract_type"] == None else remoteData["contract_type"]
        cName = "" if remoteData["name"] ==None else remoteData["name"]
        dType = ""



        if remoteData["data_type"] == "1":
            dType = "月"
        elif remoteData["data_type"] == "2":
            dType = "日"
        elif remoteData["data_type"] == "3":
            dType = "24时"

        key = "-".join([cType,cName,dateStr,dType])
        remoteDataDic[key] = remoteData



    for localData in localDataList:

        dateStr = localData["date"].strftime("%Y-%m-%d")
        # print(dateStr)

        ct1 = localData["contract_type1"]
        ct2 = localData["contract_type2"]
        cTypeName = contractTypeEnum[ct1][ct2][1]
        cType = contractTypeEnum[ct1][ct2][0]
        cName= localData["contract_name"]
        dType = localData["dataType"]

        key = "-".join([cType,cName,dateStr,dType])


        if key not in remoteDataDic.keys():
            errorDetail["日期"].append(dateStr)
            errorDetail["类型"].append(None)
            errorDetail["维度"].append(None)
            errorDetail["错误信息"].append("系统数据库找不到该合同")
            errorDetail["合同名称"].append(cName)
            errorDetail["合同品种"].append(ct1)
            errorDetail["合同类型"].append(cTypeName)
            errorDetail["算例单点数据"].append(None)
            errorDetail["系统单点数据"].append(None)
            errorDetail["错误位置"].append(None)
            errorDetail["算例所有数据"].append(None)
            errorDetail["系统所有数据"].append(None)



            continue

        localEleList = localData["ele"]
        localPriceList = localData["price"]
        remoteEleList = remoteDataDic[key]["ele"]
        remotePriceList = remoteDataDic[key]["price"]

        isEleError = False
        isPriceError = False

        for i in range(0,len(localEleList)):

            localEleData = round(localEleList[i],4) if localEleList[i] != None else None
            remoteEleData = round(remoteEleList[i],4) if remoteEleList[i] != None else None
            localPriceData = round(localPriceList[i],4) if localPriceList[i] != None else None
            remotePriceData = round(remotePriceList[i],4) if remotePriceList[i] != None else None

            if localEleData != remoteEleData and isEleError == False:
                errorDetail["日期"].append(  dateStr )
                errorDetail["类型"].append("电量")
                errorDetail["维度"].append(dType)
                errorDetail["错误信息"].append("电量不一致")
                errorDetail["合同名称"].append(cName)
                errorDetail["合同品种"].append(ct1)
                errorDetail["合同类型"].append(cTypeName)
                errorDetail["算例单点数据"].append(localEleData)
                errorDetail["系统单点数据"].append(remoteEleData)
                errorDetail["错误位置"].append(i+1)
                errorDetail["算例所有数据"].append(localEleList)
                errorDetail["系统所有数据"].append(remoteEleList)


                isEleError = True

            if localPriceData != remotePriceData and isPriceError == False:
                errorDetail["日期"].append(dateStr)
                errorDetail["类型"].append("电价")
                errorDetail["维度"].append(dType)
                errorDetail["错误信息"].append("电价不一致")
                errorDetail["合同名称"].append(cName)
                errorDetail["合同品种"].append(ct1)
                errorDetail["合同类型"].append(cTypeName)
                errorDetail["算例单点数据"].append(localPriceData)
                errorDetail["系统单点数据"].append(remotePriceData)
                errorDetail["错误位置"].append(i + 1)
                errorDetail["算例所有数据"].append(localPriceList)
                errorDetail["系统所有数据"].append(remotePriceList)

                isPriceError = True

    dd = pd.DataFrame(errorDetail)
    # print(len(errorDetail["errorInfo"]))

    errorPath = CommonClass.mkDir("江西","导出模板","对比结果.xlsx",isGetStr=True)
    print(errorPath)
    dd.to_excel(errorPath,index=False)
    print(dd)
    pass

# 获取合同电量明细
def getContractDetail(contractName,unitName,contractType1,startDate,endDate):

    res = queryLocalContract(unitName=unitName, contractName=contractName,contractType1=contractType1,contractType2=None,
                        startDate=startDate, endDate=endDate,dataType=["24时"])


    sd = datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.strptime(endDate, "%Y-%m-%d")

    dateData = {

    }
    monthData = {

    }

    while sd <= ed:
        dateStr = datetime.strftime(sd, "%Y-%m-%d")
        sd += timedelta(days=1)

        dateData[dateStr] = {
            "ele" : [None for i in range(0,24)],
            "price" : [None for i in range(0,24)],
        }

    for i in range(1,13):

        month = "2023-"+ str(i).rjust(2,"0")
        monthData[month] = {
            "ele": [None for i in range(0, 24)],
            "price": [None for i in range(0, 24)],
        }

    for r in res:

        dateStr = datetime.strftime(r["date"], "%Y-%m-%d")

        sourceData = dateData[dateStr]
        currentData = {
            "ele" : r["ele"],
            "price" : r["price"],
        }
        cal24Res = cal24Info([sourceData,currentData])

        dateData[dateStr]["ele"] = cal24Res["ele"]
        dateData[dateStr]["price"] = cal24Res["price"]
        dateData[dateStr]["eleSum"] = cal24Res["eleSum"]
        dateData[dateStr]["priceSum"] = cal24Res["priceSum"]

        monthSourceData = monthData[dateStr[:7]]
        cal24Res = cal24Info([monthSourceData, currentData])

        monthData[dateStr[:7]]["ele"] = cal24Res["ele"]
        monthData[dateStr[:7]]["price"] = cal24Res["price"]
        monthData[dateStr[:7]]["eleSum"] = cal24Res["eleSum"]
        monthData[dateStr[:7]]["priceSum"] = cal24Res["priceSum"]


    dateDataList = []

    for date in dateData:
        # print(dateData[date])

        if "eleSum" not in dateData[date].keys():
            continue

        eleList = [date,"电量",dateData[date]["eleSum"],]
        eleList.extend(dateData[date]["ele"])
        priceList = [date, "电价",dateData[date]["priceSum"],]
        priceList.extend(dateData[date]["price"])
        dateDataList.append(eleList)
        dateDataList.append(priceList)


    monthDataList = [
        ["月份"],
        ["电量"],
        ["电价"]
    ]

    for month in monthData:

        if "eleSum" not in monthData[month].keys():
            continue

        monthDataList[0].append(month)
        monthDataList[1].append(monthData[month]["eleSum"])
        monthDataList[2].append(monthData[month]["priceSum"])



    tempPath = CommonClass.mkDir("江西", "导出模板", "电量明细模板.xlsx", isGetStr=True)
    templateE = ExcelHeplerXlwing(tempPath)
    template = templateE.getTemplateStyle("Sheet1")
    templateE.close()

    savePath = CommonClass.mkDir("江西", "导出模板", contractName[0]+"电量明细结果.xlsx", isGetStr=True)
    e = ExcelHeplerXlwing()
    e.newExcel(sheetName="Sheet1", templateStyle=template)
    e.writeData(savePath, dateDataList, "Sheet1")

    e.newExcel(sheetName="月维度", templateStyle=None)
    e.writeData(savePath, monthDataList, "月维度",beginRow=1)

    e.close()

    pass

# 计算峰平谷占比
def calPeakRatio(dataList):

    eleRes = {
        "sum": [0,100],
        "tip": [None,None],
        "peak": [None,None],
        "flat": [None,None],
        "valley": [None,None],
    }

    allPeak = CommonClass.readYaml(dataPeakyamlPath)
    for dateStr in allPeak:
        for key in allPeak[dateStr]:
            allPeak[dateStr][key] = Tool.time96To96list( allPeak[dateStr][key] )['time96List']


    def max_leq(nums, max_value):
        return max(filter(lambda x: x <= max_value, nums))

    for data in dataList:
        # 计算总电量
        for i in range(0, 24):

            if data["ele"][i] == None:
                continue

            if eleRes["sum"][0] == None:
                eleRes["sum"][0] = data["ele"][i]
            else:
                eleRes["sum"][0] += data["ele"][i]


        dateStr = datetime.strftime(data["date"], "%Y-%m-%d")

        if dateStr < min(allPeak.keys()):
            continue

        dateStr = max_leq( allPeak.keys(),dateStr)

        datePeak = allPeak[dateStr]


        for peakType in eleRes:

            if peakType not in datePeak.keys():
                continue

            for i in range(0,96):

                dataEleIndex = math.floor(i/4)

                if datePeak[peakType][i] == 1:
                    if data["ele"][dataEleIndex] == None:
                        continue

                    if eleRes[peakType][0] == None:
                        eleRes[peakType][0] = data["ele"][dataEleIndex]/4
                    else:
                        eleRes[peakType][0] += data["ele"][dataEleIndex]/4

            pass

    # 计算峰平谷占比
    for key in eleRes:
        if key == "sum":
            continue

        if eleRes[key][0] ==None :
            continue
        eleRes[key][1] =  eleRes[key][0] / eleRes["sum"][0] * 100

    print("==========",eleRes)
    return eleRes


# 构建合同分析输出的数据
def execAnalysisData(startDate,endDate,contractName=None,unitName=None,contractType1=None):

    sd = datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.strptime(endDate, "%Y-%m-%d")

    resData = {
        "收益分析" : [],
        "盈亏分析" : [],
        "电量分析" : [],
        "汇总统计" : [],
        "峰平谷统计" : [],
    }

    dataList = []
    contractDataList = []
    clearingDataList = []

    while sd <= ed:

        calContractDataList = []
        calClearingDataList = []

        dateStr = datetime.strftime(sd, "%Y-%m-%d")

        for unit in unitName:

            queryRes =  queryLocalContract(unitName=[unit],
                             contractName=contractName,
                             contractType1=contractType1,
                             contractType2=None,
                             startDate=dateStr, endDate=dateStr, dataType=["24时"])
            calRes = cal24Info(queryRes)

            clearing = PrivateData.queryClearingData(unit=[unit], startDate=dateStr, endDate=dateStr, dataType=["dayAhead"])
            # print("===========",clearing)

            contractDataList.append(
                {
                    "ele": calRes["ele"],
                    "price": calRes["price"],
                }
            )
            clearingDataList.append(
                {
                    "ele": calRes["ele"],
                    "price": [None for i in range(0, 24)] if len(clearing) == 0 else clearing[0]["price"],
                }
            )

            dataList.extend(
                queryRes
            )

            calContractDataList.append(
                {
                    "ele" : calRes["ele"],
                    "price" : calRes["price"],
                }
            )

            calClearingDataList.append(
                {
                    "ele" : calRes["ele"],
                    "price" : [None for i in range(0,24)] if len(clearing)==0 else clearing[0]["price"],
                }
            )

            # data["持仓电量"] = calRes["ele"]
            # data["持仓均价"] = calRes["price"]
            # data["费用"] = calRes["fee"]
            # data["总电量"] = calRes["eleSum"]
            # data["总均价"] = calRes["priceSum"]
            # data["总费用"] = calRes["feeSum"]
            # data["日前出清电价"] = clearing["price"]
            #
            # dataList.append(data)

        calContractDataRes = cal24Info(calContractDataList)
        calClearingDataRes = cal24Info(calClearingDataList,isFilterNone=True)


        aa =  [dateStr,None,None,"合同电量（MWh）", ]

        bb =  [dateStr,None,None,"合同价格（元/MWh）", ]
        cc =  [dateStr,None,None,"合同日前加权价格（元/MWh）", ]
        dd =  [dateStr,None,None,"合同电费", ]
        ee =  [dateStr,None,None,"现货电费（元）", ]
        ff =  [dateStr,None,None,"中长期对比日前盈亏（元）", ]

        aa.extend(calContractDataRes["ele"])
        bb.extend(calContractDataRes["price"])
        cc.extend(calClearingDataRes["price"])
        dd.extend(calContractDataRes["fee"] )
        ee.extend(calClearingDataRes["fee"] )

        ffData = []
        for i in range(0, 24):
            if (calContractDataRes["fee"][i] == None) or (calClearingDataRes["fee"][i] ==None):
                ffData.append(None)
                continue
            ffData.append(calContractDataRes["fee"][i]-calClearingDataRes["fee"][i])
        ff.extend(ffData)

        resData["收益分析"].append(dd)
        resData["收益分析"].append(bb)
        resData["收益分析"].append(aa)
        resData["盈亏分析"].append(ff)
        resData["盈亏分析"].append(ee)
        resData["电量分析"].append(aa)
        resData["电量分析"].append(bb)
        resData["电量分析"].append(cc)


        # 日期 +1
        sd += timedelta(days=1)


    pRatio = calPeakRatio(dataList)

    resData["峰平谷统计"].append(
        ["数据","尖峰","高峰","平段","低谷"]
    )
    resData["峰平谷统计"].append(
        ["电量（MWh）",pRatio['tip'][0],pRatio['peak'][0],pRatio['flat'][0],pRatio['valley'][0],
         ]
    )
    resData["峰平谷统计"].append(
        ["占比（%）",pRatio['tip'][1],pRatio['peak'][1],pRatio['flat'][1],pRatio['valley'][1],
         ]
    )

    contractDataRes = cal24Info(contractDataList)
    clearingDataRes = cal24Info(clearingDataList)
    resData["汇总统计"].append(
        ["数值", contractDataRes["feeSum"] / 10000, clearingDataRes["feeSum"] / 10000,
         (contractDataRes["feeSum"] - clearingDataRes["feeSum"]) / 10000, contractDataRes["eleSum"],
         contractDataRes["priceSum"], clearingDataRes["priceSum"]
         ]
    )

    outputAnalysisData(resData)
    return  resData


# 输出到excel
def outputAnalysisData(resData):

    print(resData)
    tempPath = CommonClass.mkDir("江西","导出模板","合同分析模板.xlsx",isGetStr=True)


    savePath = CommonClass.mkDir("江西","导出模板","合同分析结果.xlsx",isGetStr=True)
    e = ExcelHeplerXlwing(tempPath)


    for sheetName in resData:
        print("============",sheetName)
        e.writeData(savePath,resData[sheetName],sheetName)

    e.close()
    # templateE.close()
    pass


def ini():

    d = {
        "中长期总体": {
            "持仓电量": None,
            "持仓均价": None,
            "总电量": None,
            "总均价": None,
        },
    }

    for key in contractTypeEnum1:
        d[key] = {
                "持仓电量": None,
                "持仓均价": None,
                "总电量": None,
                "总均价": None,
            }
        for t in contractTypeEnum1[key]:
            d[t] = {
                "持仓电量": None,
                "持仓均价": None,
                "总电量": None,
                "总均价": None,
            }

    return d


# 构建持仓总览输出的数据
def buildOutputData(units,startDate,endDate):
    buildResList = []
    rankType=[
        "中长期总体",
        "市场化",
        "代理购电",
        "市场化,年度双边协商",
        "市场化,月度交易",
        "市场化,月内连续融合",
        "市场化,d-3日24时段滚动撮合",
        "市场化,省间外送",
        "代理购电,年度代理购电挂牌",
        "代理购电,月度交易",
        "代理购电,月内连续融合",
        "代理购电,d-3日24时段滚动撮合",
    ]

    allType = {
        "中长期总体": []
    }
    for key in contractTypeEnum1:
        allType[key] = contractTypeEnum1[key]
        allType["中长期总体"].extend(contractTypeEnum1[key])
        for t in contractTypeEnum1[key]:
            allType[t] = [t]

    all = {
        "汇总" : ini()
    }
    for t in allType:
        print("=========",t)
        contractType1 = None
        contractType2 = None

        if t == "市场化" or t == "代理购电":
            contractType1 = [t]
            contractType2 = [ kk.split(",")[1] for kk in contractTypeEnum1[t] ]
        elif t == "中长期总体":
            pass
        else:
            contractType1 = [t.split(",")[0]]
            contractType2 = [t.split(",")[1]]


        queryRes = queryLocalContract(unitName=units,
                                 contractName=None,
                                 contractType1=contractType1,
                                 contractType2=contractType2,
                                 startDate=startDate, endDate=endDate, dataType=["24时"])

        calRes = cal24Info(queryRes)
        all["汇总"][t]["持仓电量"] = calRes["ele"]
        all["汇总"][t]["持仓均价"] = calRes["price"]
        all["汇总"][t]["总电量"] = calRes["eleSum"]
        all["汇总"][t]["总均价"] = calRes["priceSum"]
    for unit in units:
        all[unit] = ini()

        for t in allType:
            contractType1 = None
            contractType2 = None
            if t == "中长期总体":
                pass
            if t == "市场化" or t == "代理购电":
                contractType1 = [t]
                contractType2 = [kk.split(",")[1] for kk in contractTypeEnum1[t]]
            elif t == "中长期总体":
                pass
            else:
                contractType1 = [t.split(",")[0]]
                contractType2 = [t.split(",")[1]]

            queryRes = queryLocalContract(unitName=[unit],
                                          contractName=None,
                                          contractType1=contractType1,
                                          contractType2=contractType2,
                                          startDate=startDate, endDate=endDate, dataType=["24时"])

            calRes = cal24Info(queryRes)
            all[unit][t]["持仓电量"] = calRes["ele"]
            all[unit][t]["持仓均价"] = calRes["price"]
            all[unit][t]["总电量"] = calRes["eleSum"]
            all[unit][t]["总均价"] = calRes["priceSum"]

    for unit in all:
        for t in rankType:
            eleList = [unit,t,"持仓电量",all[unit][t]["总电量"]]
            eleList.extend(all[unit][t]["持仓电量"])
            priceList = [unit, t, "持仓均价", all[unit][t]["总均价"]]
            priceList.extend(all[unit][t]["持仓均价"])
            buildResList.append(eleList)
            buildResList.append(priceList)

    # print(buildResList)
    return buildResList

# 输出到excel
def outputData(units,startDate,endDate):

    sd = datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.strptime(endDate, "%Y-%m-%d")

    resData = {}

    resData["24点汇总"] = buildOutputData(units, startDate, endDate)

    dateResData = []
    dateResData.append(
        ["机组"	,"合约类型","电量/电价",	"合计/均值"],
    )

    while sd <= ed:
        dateStr = datetime.strftime(sd, "%Y-%m-%d")
        dateResData[0].append(dateStr)

        resData[dateStr] = buildOutputData(units, dateStr, dateStr)

        # 日期 +1
        sd += timedelta(days=1)


    for date in resData:

        if len(dateResData)-1 < len(resData[date]):
            for data in resData[date]:
                dateResData.append(data[0:4])
            continue

        for i in range(0,len(resData[date])):
            dateResData[i+1].append(resData[date][i][3])



    tempPath = CommonClass.mkDir("江西","导出模板","持仓总览模板.xlsx",isGetStr=True)
    templateE = ExcelHeplerXlwing(tempPath)
    template = templateE.getTemplateStyle("Sheet1")
    templateE.close()

    # print(resData)

    savePath = CommonClass.mkDir("江西","导出模板","持仓总览结果.xlsx",isGetStr=True)
    e = ExcelHeplerXlwing()
    for date in resData:
        e.newExcel(sheetName=date,templateStyle=template)
        e.writeData(savePath,resData[date],date)

    e.newExcel(sheetName="日维度", templateStyle=None)
    e.writeData(savePath, dateResData, "日维度",beginRow=1)

    e.close()

    pass



# 导入入口
def importContract():
    improtPath = CommonClass.mkDir("江西", "导入文件", "电厂3", isGetStr=True)

    for root, dirs, files in os.walk(improtPath):

        for file in files:
            filePath = os.path.join(root, file)
            filename = file.replace(".xlsx", "").replace(".xls", "")
            tenantName = filename.split("-")[0]
            fileType = filename.split("-")[1]
            year = filename.split("-")[2]

            if fileType == "合同日电量明细":
                execDayEleDetail(filePath, file, "合同分月查询结果", tenantName,year)
            if fileType == "合同分月查询":
                execMonthEleDetail(filePath, file, "Sheet1", tenantName, year)



if __name__ == '__main__':

    # importContract()
    # getUnitByOtherName(1, 2)
    # compareContract(["测试#1机组"],None,None,None,None,None,["24时"])
    # queryRemoteContract(["测试#1机组"])
    # getContractDetail(["瑞金二期华能江西能源销售有限责任公司江西电力市场2023年1月份月内连续融合交易"],["测试#1机组"],
    #                   ["市场化"],"2023-01-01","2023-01-31")
    #
    # res = queryLocalContract(unitName=["测试#1机组"],
    #                          contractName=["瑞金二期华能江西能源销售有限责任公司江西电力市场2023年1月份月内连续融合交易"],
    #                          contractType1=["市场化"],
    #                          contractType2=None,
    #                          startDate="2023-01-01", endDate="2023-01-31", dataType=["24时"])
    # #
    # print(res)
    # print(calPeakRatio(res))

    #
    execAnalysisData( startDate="2023-03-15", endDate="2023-03-16",
                      contractName=[
                          "测试1江西和惠配售电有限公司(增量配电网)年度代理购电挂牌交易（2至12月）",
                      ],
                      unitName=["开封#1"],
                      contractType1=["代理购电"])

    # outputData(["开封#1"], startDate="2023-03-15", endDate="2023-03-16")