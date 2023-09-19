import copy
import os
from datetime import datetime, timedelta

import pandas
from 江西.cal.excel_handler import ExcelHepler,ExcelHeplerXlwing
from 江西.cal.mysqlTool import MysqlTool
from common.common import CommonClass
import re
import calendar

unitYamlPath = CommonClass.mkDir("江西","config","unit_config.yaml",isGetStr=True)
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
        "年度代理购电挂牌": ["1", "年度代理购电"],
        "月度交易": ["2", "月度交易"],
        "月内连续融合": ["3", "月内连续交易"],
        "d-3日24时段滚动撮合": ["6", "d-3日24时段滚动撮合"],
    },
}
dataTypeEnum = {
    "24时" : "1",
    "日" : "2",
    "月" : "3",
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
            # 分割多种符号
            unitShortNameList = re.split('|'.join(map(re.escape, delimiters)), unit["unitShortName"])
            unitShortNameList.append(unit["unitName"])
            if otherName in unitShortNameList:
                res["units"].append(unit["unitName"])
                res["count"] += 1

    if otherNameType == "交易单元名称":

        for unit in unitsInfo:
            # 分割多种符号
            controlUnitNameList = re.split('|'.join(map(re.escape, delimiters)), unit["controlUnitName"])
            controlUnitNameList.append(unit["unitName"])
            if otherName in controlUnitNameList:
                res["units"].append(unit["unitName"])
                res["count"] += 1

    return res

# 将查询到的合同计算成24点结果
def cal24Info(dataList,lenght=24):

    eleRes = [None for i in range(0,lenght)]
    priceRes = [None for i in range(0,lenght)]
    feeRes = [None for i in range(0,lenght)]

    for data in dataList:

        ele = data["ele"]
        price = data["price"]

        for i in range(0,lenght):

            if ele[i] == None:
                continue
            if price[i] == None:
                continue

            if eleRes[i] == None:
                eleRes[i] = ele[i]
                priceRes[i] = price[i]
                feeRes[i] = eleRes[i]*priceRes[i]
            else:
                eleRes[i] += ele[i]
                feeRes[i] += (ele[i] * price[i])
                if eleRes[i] != 0 :
                    priceRes[i] = feeRes[i] / eleRes[i]

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
        buyer_name = df.iloc[row]["购方名称"]
        unitName = checkRes["unitInfo"]["units"][0]

        uniqueId = contractType1+sell_name+date+transactionSequenceName
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
                "buyer_name" : sell_name,
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
        buyer_name = df.iloc[row]["购方名称"]
        unitInfo = checkRes["unitInfo"]

        uniqueId = contractType1+sell_name+transactionSequenceName
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
                "buyer_name" : sell_name,
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
        "date" :[],
        "dataType" :[],
        "dataDimension" :[],
        "errorInfo" :[],
        "contractName" :[],
        "contractType" :[],
        "errorLocatValue" :[],
        "errorRemoteValue" :[],
        "errorLocation" :[],
        "localData" :[],
        "remoteData" :[],
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
            dType = "24时"
        elif remoteData["data_type"] == "2":
            dType = "日"
        elif remoteData["data_type"] == "3":
            dType = "月"

        key = "-".join([cType,cName,dateStr,dType])
        remoteDataDic[key] = remoteData

    # for key in remoteDataDic:
    #     print(key,remoteDataDic[key])

    # 合同类型+合同名称+日期+数据类型

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

        if key not in remoteDataDic:
            errorDetail["date"].append(dateStr)
            errorDetail["dataType"].append(None)
            errorDetail["dataDimension"].append(None)
            errorDetail["errorInfo"].append("系统数据库找不到该合同")
            errorDetail["contractName"].append(cName)
            errorDetail["contractType"].append(cTypeName)
            errorDetail["errorLocatValue"].append(None)
            errorDetail["errorRemoteValue"].append(None)
            errorDetail["errorLocation"].append(None)
            errorDetail["localData"].append(None)
            errorDetail["remoteData"].append(None)
            continue

        localEleList = localData["ele"]
        localPriceList = localData["price"]
        remoteEleList = remoteDataDic[key]["ele"]
        remotePriceList = remoteDataDic[key]["price"]

        isEleError = False
        isPriceError = False

        for i in range(0,len(localEleList)):

            localEleData = round(localEleList[i],6) if localEleList[i] != None else None
            remoteEleData = round(remoteEleList[i],6) if remoteEleList[i] != None else None
            localPriceData = round(localPriceList[i],6) if localPriceList[i] != None else None
            remotePriceData = round(remotePriceList[i],6) if remotePriceList[i] != None else None

            if localEleData != remoteEleData and isEleError == False:
                errorDetail["date"].append(  dateStr )
                errorDetail["dataType"].append("电量")
                errorDetail["dataDimension"].append(dataTypeEnum[dType])
                errorDetail["errorInfo"].append("电量不一致")
                errorDetail["contractName"].append(cName)
                errorDetail["contractType"].append(cTypeName)
                errorDetail["errorLocatValue"].append(localEleData)
                errorDetail["errorRemoteValue"].append(remoteEleData)
                errorDetail["errorLocation"].append(i+1)
                errorDetail["localData"].append(localEleList)
                errorDetail["remoteData"].append(remoteEleList)

                isEleError = True

            if localPriceData != remotePriceData and isPriceError == False:
                errorDetail["date"].append(dateStr)
                errorDetail["dataType"].append("电价")
                errorDetail["dataDimension"].append(dataTypeEnum[dType])
                errorDetail["errorInfo"].append("电价不一致")
                errorDetail["contractName"].append(cName)
                errorDetail["contractType"].append(cTypeName)
                errorDetail["errorLocatValue"].append(localPriceData)
                errorDetail["errorRemoteValue"].append(remotePriceData)
                errorDetail["errorLocation"].append(i + 1)
                errorDetail["localData"].append(localEleList)
                errorDetail["remoteData"].append(remoteEleList)

                isPriceError = True

    # print(len(errorDetail["errorInfo"]))
    pass

# 导入入口
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


    # print(dateData)


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

def importContract():
    improtPath = CommonClass.mkDir("江西", "导入文件", "合同", isGetStr=True)

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
    getContractDetail(["瑞金二期华能江西能源销售有限责任公司江西电力市场2023年1月份月内连续融合交易"],["测试#1机组"],
                      ["市场化"],"2023-01-01","2023-01-31")