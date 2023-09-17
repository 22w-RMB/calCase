import pandas
from 江西.cal.excel_handler import ExcelHepler
from 江西.cal.mysqlTool import MysqlTool
from common.common import CommonClass
import re

unitYamlPath = CommonClass.mkDir("江西","config","unit_config.yaml",isGetStr=True)
unitInfoConfig = CommonClass.readYaml(unitYamlPath)


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
            if otherName in unitShortNameList:
                res["units"].append(unit["unitName"])
                res["count"] += 1

    if otherNameType == "交易单元名称":

        for unit in unitsInfo:
            # 分割多种符号
            controlUnitNameList = re.split('|'.join(map(re.escape, delimiters)), unit["controlUnitName"])
            if otherName in controlUnitNameList:
                res["units"].append(unit["unitName"])
                res["count"] += 1

    return res

# 将查询到的合同计算成24点结果
def cal24Info(dataList):

    eleRes = [None for i in range(0,24)]
    priceRes = [None for i in range(0,24)]
    feeRes = [None for i in range(0,24)]

    for data in dataList:

        ele = data["ele"]
        price = data["price"]

        for i in range(0,24):

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


    for i in range(0,24):
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
    }

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

def execDayEleDetail(filePath,fileName,sheetName,**kwargs):
    tenantName = "江西电厂1"

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

    e = ExcelHepler(filePath,sheetName,header,**kwargs)
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

def writeContract(resultDataList):
    writeSqlList = []


    for key in resultDataList:
        data = resultDataList[key]


        writeSqlList.append(
            (
                data["contractName"],
                data["unitName"],
                None if data["contractName"]=="" else data["contractName"],
                data["sell_name"],
                str(data["ele"]),
                str(data["price"]),
                data["date"],
                data["contractType1"],
                data["contractType2"],
                "日",
            )
        )

    print(writeSqlList[0])
    db = MysqlTool()
    db.insertContract(writeSqlList)
    db.close()

if __name__ == '__main__':
    path = r"D:\code\python\calCase\江西\导入文件\xx电厂-合同日电量明细-YYYY.xls"

    execDayEleDetail(path,"111","合同分月查询结果")

    # getUnitByOtherName(1, 2)


