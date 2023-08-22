import datetime
import os
from datetime import timedelta
from tool import Tool
from common.common import CommonClass
from excel_handler import ExcelHepler
from mysqlTool import MysqlTool
from private_data import PrivateData

dataTyamlPath = CommonClass.mkDir("河北","config","T.yaml",isGetStr=True)
dataPeakyamlPath = CommonClass.mkDir("河北","config","峰平谷.yaml",isGetStr=True)
configyamlPath = CommonClass.mkDir("河北","config","hb_interface.yaml",isGetStr=True)



dataTyaml = CommonClass.readYaml(dataTyamlPath)
dataPeakyaml = CommonClass.readYaml(dataPeakyamlPath)

enumD = {
    "购方名称": "buyer_name",
    "售方名称": "seller_name",
    "分时段编码": "period_time_coding",
    "售方电量": "ele",
    "售方电价": "price",
    "时间段": "Period_of_time",
    "时间类型": "timeType",
    "交易单元": "seller_name",
    "成交电量": "ele",
    "成交均价": "price",
    "成交电量（日均）": "ele",
    "出清电价": "price",
}

contractTypeEnum = {
    "中长期市场化":
        ["年度双边协商" ,
        "月度集中竞价" ,
        "周滚动撮合" ,
        "日滚动撮合" ,
        "日集中竞价" ],
    "市场代购电":
        ["月度代理购电" ,
        "月内代理购电" ,
        "上下调交易" ,
        "题材电量挂牌" ,
        "张河湾抽水电量" ]
}

print(dataTyaml)
print(dataPeakyaml)


def writeDataT(dataT):
    db = MysqlTool()

    for date in dataT:

        for period_time_coding in dataT[date]:
            ptc = dataT[date][period_time_coding]
            d = {
                "month": date,
                "period_time_coding": period_time_coding,
                "time": str(ptc["time"]),
                "haveRatio": str(ptc["haveRatio"]),
                "ratio": str(ptc["ratio"]),
                "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            print(d)
            db.insertSessionIdConfig(d)

    db.close()

    pass

def queryDataT():
    db = MysqlTool()

    queryRes = db.querySessionIdConfig()
    print(queryRes)

    d = {}
    for res in queryRes:
        month = res["month"]
        if month not in d.keys():
            d[month] = {}

        period_time_coding = res['period_time_coding']
        d[month][period_time_coding] = {}
        d[month][period_time_coding]["time"] = eval(res['time'])
        d[month][period_time_coding]["haveRatio"] = eval(res['haveRatio'])
        d[month][period_time_coding]["ratio"] = eval(res['ratio'])

    db.close()
    print(d)
    return d

def writeDataPeak(dataPeak):
    db = MysqlTool()

    for date in dataPeak:

        for peakType in dataPeak[date]:
            d = {
                "month": date,
                "peak_type": peakType,
                "time": str(dataPeak[date][peakType]),
                "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            print(d)
            db.insertPeakPinggu(d)

    db.close()

    pass

def queryDataPeak():
    db = MysqlTool()

    queryRes = db.queryPeakPinggu()
    print(queryRes)

    d = {}
    for res in queryRes:
        month = res["month"]
        if month not in d.keys():
            d[month] = {}

        peak_type = res['peak_type']
        d[month][peak_type] = {}
        d[month][peak_type] = eval(res['time'])

    db.close()
    print(d)
    return d

def queryContract(tradingSession=None,seller_name=None,period_time_coding=None,startDate=None,endDate=None,contractType=None):


    d = {
        "trading_session": tradingSession,
        "seller_name": seller_name,
        "period_time_coding": period_time_coding,
        "start_date": startDate,
        "end_date": endDate,
        "contract_type": contractType,
    }

    db = MysqlTool()

    queryRes = db.queryContract(d)

    print(queryRes)
    db.close()


    for r in queryRes:
        r["ele"] = eval( r["ele"])
        r["price"] = eval( r["price"])


    return queryRes

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

            if eleRes[i] == None:
                eleRes[i] = ele[i]
                priceRes[i] = 0 if price[i]==None else price[i]
                feeRes[i] = eleRes[i]*priceRes[i]
            else:
                eleRes[i] += ele[i]
                feeRes[i] += (ele[i]*(0 if price[i]==None else price[i]))
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

# 构建持仓总览输出的数据
def buildOutputData(units,startDate,endDate):
    buildResList = []
    rankType=[
        "中长期总体",
        "市场代购电",
        "中长期市场化",
        "月度代理购电",
        "月内代理购电",
        "上下调交易",
        "题材电量挂牌",
        "张河湾抽水电量",
        "年度双边协商",
        "月度集中竞价",
        "周滚动撮合",
        "日滚动撮合",
        "日集中竞价",
    ]

    allType = {
        "中长期总体": []
    }
    for key in contractTypeEnum:
        allType[key] = contractTypeEnum[key]
        allType["中长期总体"].extend(contractTypeEnum[key])
        for t in contractTypeEnum[key]:
            allType[t] = [t]

    all = {
        "汇总" : ini()
    }
    for t in allType:
        queryRes = queryContract(tradingSession=None, seller_name=units, period_time_coding=None, startDate=startDate,
                                 endDate=endDate, contractType=allType[t])

        calRes = cal24Info(queryRes)
        all["汇总"][t]["持仓电量"] = calRes["ele"]
        all["汇总"][t]["持仓均价"] = calRes["price"]
        all["汇总"][t]["总电量"] = calRes["eleSum"]
        all["汇总"][t]["总均价"] = calRes["priceSum"]
        ["汇总", ]
    print(allType)
    for unit in units:
        all[unit] = ini()

        for t in allType:
            queryRes = queryContract(tradingSession=None, seller_name=[unit], period_time_coding=None, startDate=startDate,
                      endDate=endDate,contractType=allType[t])

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

    print(buildResList)
    return  buildResList

# 输出到excel
def outputData(units,startDate,endDate):

    sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

    resData = {}

    while sd <= ed:
        dateStr = datetime.datetime.strftime(sd, "%Y-%m-%d")

        resData[dateStr] = buildOutputData(units, dateStr, dateStr)

        # 日期 +1
        sd += timedelta(days=1)

    tempPath = CommonClass.mkDir("河北","导出模板","模板.xlsx",isGetStr=True)
    templateE = ExcelHepler(tempPath)
    template = templateE.getTemplateStyle("Sheet1")
    templateE.close()

    print(resData)

    savePath = CommonClass.mkDir("河北","导出模板","结果.xlsx",isGetStr=True)
    e = ExcelHepler()
    for date in resData:
        e.newExcel(sheetName=date,templateStyle=template)
        e.writeData(savePath,resData[date],date)

    e.close()

    pass


# 构建持仓总览输出的数据
def execAnalysisData(units,startDate,endDate):

    sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

    resData = {}
    resList = []

    while sd <= ed:

        calContractDataList = []
        calClearingDataList = []

        dateStr = datetime.datetime.strftime(sd, "%Y-%m-%d")

        for unit in units:

            queryRes = queryContract(tradingSession=None, seller_name=[unit], period_time_coding=None, startDate=dateStr,
                                     endDate=dateStr, contractType=None)
            calRes = cal24Info(queryRes)

            clearing = PrivateData.queryClearingData(unit=[unit], startDate=dateStr, endDate=dateStr, dataType=["dayAhead"])
            print("===========",clearing)
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
        calClearingDataRes = cal24Info(calClearingDataList)

        print(calContractDataRes["eleSum"])
        print(calContractDataRes["price"])
        print(calContractDataRes["ele"])
        print(calClearingDataRes)

        resData[dateStr] = {
            "合同电费": calContractDataRes["fee"],
            "合同结算电价": calContractDataRes["price"],
            "合同日前加权均价": calClearingDataRes["price"],
            "合同电量": calContractDataRes["ele"],
            "现货电费": calClearingDataRes["fee"],
        }

        aa =  [dateStr,None,None,"合同电量（MWh）", ]

        bb =  [dateStr,None,None,"合同价格（元/MWh）", ]
        cc =  [dateStr,None,None,"合同日前加权价格（元/MWh）", ]
        dd =  [dateStr,None,None,"合同电费", ]
        ee =  [dateStr,None,None,"现货电费（元）", ]

        aa.extend(calContractDataRes["ele"])
        bb.extend(calContractDataRes["price"])
        cc.extend(calClearingDataRes["price"])
        dd.extend(calContractDataRes["fee"] )
        ee.extend(calClearingDataRes["fee"] )

        resList.append(aa)
        resList.append(bb)
        resList.append(cc)
        resList.append(dd)
        resList.append(ee)

        # 日期 +1
        sd += timedelta(days=1)

    print(resList)
    outputAnalysisData(resList)
    return  resData

# 输出到excel
def outputAnalysisData(resList):



    tempPath = CommonClass.mkDir("河北","导出模板","合同分析模板.xlsx",isGetStr=True)
    templateE = ExcelHepler(tempPath)
    template = templateE.getTemplateStyle("Sheet1")
    templateE.close()

    savePath = CommonClass.mkDir("河北","导出模板","合同分析结果.xlsx",isGetStr=True)
    e = ExcelHepler()
    e.newExcel(sheetName="Sheet1",templateStyle=template)
    e.writeData(savePath,resList,"Sheet1")

    e.close()

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

    for key in contractTypeEnum:
        d[key] = {
                "持仓电量": None,
                "持仓均价": None,
                "总电量": None,
                "总均价": None,
            }
        for t in contractTypeEnum[key]:
            d[t] = {
                "持仓电量": None,
                "持仓均价": None,
                "总电量": None,
                "总均价": None,
            }

    return d

def calTRatio(dataList):

    eleRes = {
        "sum": [0,100],
        "T1": [None,None],
        "T2": [None,None],
        "T3": [None,None],
        "T4": [None,None],
        "T5": [None,None],
        "T6": [None,None],
    }

    for data in dataList:
        period_time_coding = data["period_time_coding"]
        if period_time_coding == None:
            continue

        if period_time_coding in ["T6","T7" , "T8", "T9"]:
            period_time_coding ='T6'

        ele = None
        for i in range(0,24):
            if data["ele"][i] == None:
                continue
            if ele == None:
                ele = data["ele"][i]
            else:
                ele += data["ele"][i]

        if ele != None:
            eleRes["sum"][0] += ele

        if eleRes[period_time_coding][0] == None:
            eleRes[period_time_coding][0] = ele
        else:
            eleRes[period_time_coding][0] += ele



    for key in eleRes:
        if key == "sum":
            continue
        if eleRes[key][0] ==None :
            continue
        eleRes[key][1] =  eleRes[key][0] / eleRes["sum"][0] * 100

    print(eleRes)
    return eleRes

# 计算峰平谷占比
def calPeakRatio(dataList):

    eleRes = {
        "sum": [0,100],
        "tip": [None,None],
        "peak": [None,None],
        "flat": [None,None],
        "valley": [None,None],
    }

    allPeak = queryDataPeak()
    for month in allPeak:
        for key in allPeak[month]:
            allPeak[month][key] = Tool.time96To24list( allPeak[month][key] )['time24List']


    # print(allPeak)

    for data in dataList:
        # 计算总电量
        for i in range(0, 24):

            if data["ele"][i] == None:
                continue

            if eleRes["sum"][0] == None:
                eleRes["sum"][0] = data["ele"][i]
            else:
                eleRes["sum"][0] += data["ele"][i]


        month = data["month"]


        if month not in allPeak.keys():
            continue

        monthPeak = allPeak[month]

        for peakType in eleRes:

            if peakType not in monthPeak.keys():
                continue

            for i in range(0,24):


                if monthPeak[peakType][i] == 1:
                    if data["ele"][i] == None:
                        continue

                    if eleRes[peakType][0] == None:
                        eleRes[peakType][0] = data["ele"][i]
                    else:
                        eleRes[peakType][0] += data["ele"][i]

            pass

    # 计算峰平谷占比
    for key in eleRes:
        if key == "sum":
            continue

        if eleRes[key][0] ==None :
            continue
        eleRes[key][1] =  eleRes[key][0] / eleRes["sum"][0] * 100

    print(eleRes)
    return eleRes


def importFile():


    for categories in contractTypeEnum:
        for contractType in contractTypeEnum[categories]:

            # if contractType !="日集中竞价":
            #     continue

            contractTypePath = CommonClass.mkDir("河北","导入文件",contractType,isGetStr=True)
            if  os.path.exists(contractTypePath) == False:
                continue


            for root , dirs ,files in os.walk(contractTypePath):

                for file in files:
                    filePath = os.path.join(root,file)
                    filename = file.replace(".xlsx","")
                    tradingSession = filename.split("-")[0]
                    startDate = filename[len(tradingSession)+1:len(tradingSession)+11]
                    endDate = filename[len(tradingSession)+12:len(tradingSession)+32]
                    # print(filename)
                    # print(tradingSession)
                    # print(startDate)
                    # print(endDate)

                    e = ExcelHepler(filePath)
                    fileDataList = e.getAllData(enumD)
                    print(fileDataList)

                    execData(tradingSession,startDate,endDate,fileDataList,contractType,"卖出")

        # print(files)


def deleteContract(startDate,endDate,tradingSession):

    print("====开始删除合同")

    db = MysqlTool()


    d = {
        "trading_session": [tradingSession],
        "start_date": [startDate],
        "end_date": [endDate if endDate!="" else startDate ] ,
    }

    db.deleteContract(d)

    db.close()
    print("====合同删除完毕")
    pass


def execData(tradingSession,startDate,endDate,fileDataList,contractType,isSell):

    deleteContract(startDate, endDate, tradingSession)

    # 处理分时段标识配置的文件
    if contractType in ["日集中竞价","日滚动撮合"]:
        execScrolData(fileDataList, tradingSession, startDate, endDate,contractType,isSell)

    else:

        execTData(fileDataList, tradingSession, startDate, endDate,contractType,isSell)


def execTData(fileDataList,tradingSession,startDate,endDate,contractType,isSell):

    sell = 1

    if isSell !="卖出":
        sell = -1

    for data in fileDataList:
        if data["period_time_coding"] == None:
            continue

        # 分时段编码
        period_time_coding = data["period_time_coding"][:2]

        #
        period_of_StartTimeString = data["Period_of_time"][:10]
        period_of_EndTimeString = data["Period_of_time"][11:]

        sd = datetime.datetime.strptime(period_of_StartTimeString, "%Y-%m-%d")
        ed = datetime.datetime.strptime(period_of_EndTimeString, "%Y-%m-%d")

        days = (ed - sd).days + 1

        month = data["Period_of_time"][:7]

        onedayData = getOneDayData(month, period_time_coding, sell*data["ele"] / days, data["price"])

        if onedayData == None:
            continue

        daysData = generate(sd,ed,onedayData)
        print(daysData)
        writeSql(data, tradingSession, month, daysData, startDate, endDate,contractType)

#日滚动撮合、日集中竞价
def execScrolData(fileDataList,tradingSession,startDate,endDate,contractType,isSell):
    sell = 1

    if isSell != "卖出":
        sell = -1

    dic = {

    }

    for data in fileDataList:
        if data["seller_name"] not in dic.keys():
            dic[data["seller_name"]] = {}
            dic[data["seller_name"]]["seller_name"] = data["seller_name"]
            dic[data["seller_name"]]["ele"] = [None for i in range(0,24)]
            dic[data["seller_name"]]["price"] = [None for i in range(0,24)]

        res = Tool.time24o24list([data["timeType"]])
        time24List = res["time24List"]
        count = res["count"]

        # print("=========",data)
        for i  in range(0,24):
            if time24List[i] == 1:
                dic[data["seller_name"]]["ele"][i] = sell * data["ele"] / count
                dic[data["seller_name"]]["price"][i] =  data["price"]

    for key in dic:

        month = startDate[:7]
        daysData = {
            startDate : dic[key]
        }
        data = {
            "seller_name" : key
        }

        print(daysData)
        writeSql(data, tradingSession, month, daysData, startDate, startDate, contractType)


def writeSql(data,tradingSession,month,daysData,startDate,endDate, contractType):

    db = MysqlTool()

    for date in daysData:
        contract_name = ""
        buyer_name = None
        if "buyer_name" in data.keys():
            contract_name = tradingSession +"-" + data["buyer_name"] +"-"+ data["seller_name"]
            buyer_name = data["buyer_name"]
        else:
            contract_name = tradingSession +"-"+ data["seller_name"]

        d = {
            "trading_session": tradingSession,
            "contract_name": contract_name,
            "buyer_name": buyer_name,
            "seller_name": data["seller_name"] if "seller_name" in data.keys() else None,
            "period_time_coding": data["period_time_coding"][:2] if "period_time_coding" in data.keys() else None,
            "ele": str(daysData[date]["ele"]),
            "price": str(daysData[date]["price"]),
            "date": date,
            "start_date": startDate,
            "end_date": endDate,
            "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "month": month,
            "contract_type": contractType,
        }

        print(d)
        db.insertContract(d)

    db.close()

    pass


def getOneDayData(month,period_time_coding,ele,price):


    if month not in dataTyaml.keys():
        print(month, "该月份未设置分时段编码")
        return None

    if period_time_coding not in dataTyaml[month].keys():
        print(month, "该月份未设置", period_time_coding, "分时段编码")
        return None

    eleDateData = [None for i in range(0, 24)]
    priceDateData = [None for i in range(0, 24)]

    if dataTyaml[month][period_time_coding]["haveRatio"] == True:
        # 查峰平谷
        if month not in dataPeakyaml.keys():
            print(month, "该月份未设置峰平谷")
            return None

        pTypes = ["tip", "peak", "flat", "valley"]

        for pType in pTypes:
            pTypeRatio = dataTyaml[month][period_time_coding]["ratio"][pType]

            if pTypeRatio == None:
                continue

            if pTypeRatio == 0:
                continue

            if pType not in dataPeakyaml[month].keys():
                print(month, "该月份未设置", pType, "段")
                continue

            res = Tool.time96To24list(dataPeakyaml[month][pType])
            pTypeTimeList = res["time24List"]
            count = res["count"]

            if count == 0:
                print(month, "该月份未设置",pType,"段")
                return None

            perEle = ele * (pTypeRatio/100) / count
            perPrice = price

            for index in range(0, 24):

                if pTypeTimeList[index] == 1:
                    eleDateData[index] = perEle
                    priceDateData[index] = perPrice



    if dataTyaml[month][period_time_coding]["haveRatio"] == False:

        res = Tool.time24o24list(dataTyaml[month][period_time_coding]["time"])
        time24List = res["time24List"]

        count = res["count"]

        perEle = ele / count
        perPrice = price

        for index in range(0, 24):

            if time24List[index] == 1:
                eleDateData[index] = perEle
                priceDateData[index] = perPrice

        pass

    return {
        "ele" :eleDateData,
        "price" :priceDateData
    }


def generate(sd, ed, onedayData):

    dataDict = {}

    while sd <= ed:
        dateStr = datetime.datetime.strftime(sd, "%Y-%m-%d")
        dataDict[dateStr] = onedayData

        # 日期 +1
        sd += timedelta(days=1)

    return dataDict
    pass


if __name__ == '__main__':

    # writeDataT(dataTyaml)
    # writeDataPeak(dataPeakyaml)
    importFile()
    # outputData(["河北1#1机组"],"2023-01-01","2023-01-02")
    # queryDataT()
    # queryDataPeak()

    # res = queryContract(tradingSession=None, seller_name=None, period_time_coding=None, startDate="2023-01-01", endDate="2023-01-01")

    # cal24Info(res)
    # calTRatio(res)
    # calPeakRatio(res)
    # print(ini())

    # execAnalysisData(["河北1#1机组","河北1#2机组"],"2023-01-01","2023-01-02")


    pass