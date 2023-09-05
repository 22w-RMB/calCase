import datetime
import json
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

def queryContract(tradingSession=None,buyer_name=None,trading_session_month=None,seller_name=None,period_time_coding=None,startDate=None,endDate=None,contractType=None):


    d = {
        "trading_session": tradingSession,
        "buyer_name": buyer_name,
        "seller_name": seller_name,
        "period_time_coding": period_time_coding,
        "start_date": startDate,
        "end_date": endDate,
        "contract_type": contractType,
        "trading_session_month": trading_session_month,
    }

    db = MysqlTool()

    queryRes = db.queryContract(d)

    # print(queryRes)
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
            if price[i] == None:
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
        "中长期市场化",
        "市场代购电",
        "日集中竞价",
        "日滚动撮合",
        "周滚动撮合",
        "月度集中竞价",
        "年度双边协商",
        "月度代理购电",
        "月内代理购电",
        "上下调交易",
        "题材电量挂牌",
        "张河湾抽水电量",
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

    # print(buildResList)
    return buildResList

# 输出到excel
def outputData(units,startDate,endDate):

    sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

    resData = {}

    resData["24点汇总"] = buildOutputData(units, startDate, endDate)

    dateResData = []
    dateResData.append(
        ["机组"	,"合约类型","电量/电价",	"合计/均值"],
    )


    while sd <= ed:
        dateStr = datetime.datetime.strftime(sd, "%Y-%m-%d")
        dateResData[0].append(dateStr)

        # resData[dateStr] = buildOutputData(units, dateStr, dateStr)

        # 日期 +1
        sd += timedelta(days=1)


    for date in resData:

        if len(dateResData)-1 < len(resData[date]):
            for data in resData[date]:
                dateResData.append(data[0:4])
            continue

        for i in range(0,len(resData[date])):
            dateResData[i+1].append(resData[date][i][3])



    tempPath = CommonClass.mkDir("河北","导出模板","模板.xlsx",isGetStr=True)
    templateE = ExcelHepler(tempPath)
    template = templateE.getTemplateStyle("Sheet1")
    templateE.close()

    # print(resData)

    savePath = CommonClass.mkDir("河北","导出模板","持仓总览结果.xlsx",isGetStr=True)
    e = ExcelHepler()
    for date in resData:
        e.newExcel(sheetName=date,templateStyle=template)
        e.writeData(savePath,resData[date],date)

    # e.newExcel(sheetName="日维度", templateStyle=None)
    # e.writeData(savePath, dateResData, "日维度",beginRow=1)

    e.close()

    pass


# 构建合同分析输出的数据
def execAnalysisData(units,startDate,endDate,tradingSession=None,contractType=None):

    sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

    resData = {
        "收益分析" : [],
        "盈亏分析" : [],
        "电量分析" : [],
        "汇总统计" : [],
        "峰平谷分和T1~T6统计" : [],
    }

    dataList = []
    contractDataList = []
    clearingDataList = []

    while sd <= ed:

        calContractDataList = []
        calClearingDataList = []

        dateStr = datetime.datetime.strftime(sd, "%Y-%m-%d")

        for unit in units:

            queryRes = queryContract(tradingSession=tradingSession, seller_name=[unit], period_time_coding=None, startDate=dateStr,
                                     endDate=dateStr, contractType=contractType)
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
        calClearingDataRes = cal24Info(calClearingDataList)


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

    # print(dataList)
    pRatio = calPeakRatio(dataList)
    tRatio = calTRatio(dataList)

    resData["峰平谷分和T1~T6统计"].append(
        ["数据","尖峰","高峰","平段","低谷","T1","T2","T3","T4","T5","T6"]
    )
    resData["峰平谷分和T1~T6统计"].append(
        ["电量（MWh）",pRatio['tip'][0],pRatio['peak'][0],pRatio['flat'][0],pRatio['valley'][0],
         tRatio["T1"][0],tRatio["T2"][0],tRatio["T3"][0],tRatio["T4"][0],tRatio["T5"][0],tRatio["T6"][0],
         ]
    )
    resData["峰平谷分和T1~T6统计"].append(
        ["占比（%）",pRatio['tip'][1],pRatio['peak'][1],pRatio['flat'][1],pRatio['valley'][1],
         tRatio["T1"][1],tRatio["T2"][1],tRatio["T3"][1],tRatio["T4"][1],tRatio["T5"][1],tRatio["T6"][1],
         ]
    )

    contractDataRes = cal24Info(contractDataList)
    clearingDataRes = cal24Info(clearingDataList)
    resData["汇总统计"].append(
        ["数值", contractDataRes["feeSum"]/10000,clearingDataRes["feeSum"]/10000,
         (contractDataRes["feeSum"]-clearingDataRes["feeSum"])/10000,contractDataRes["eleSum"],
         contractDataRes["priceSum"],clearingDataRes["priceSum"]
         ]
    )

    outputAnalysisData(resData)
    return  resData

# 输出到excel
def outputAnalysisData(resData):



    tempPath = CommonClass.mkDir("河北","导出模板","合同分析模板.xlsx",isGetStr=True)
    # templateE = ExcelHepler(tempPath)



    savePath = CommonClass.mkDir("河北","导出模板","合同分析结果.xlsx",isGetStr=True)
    e = ExcelHepler(tempPath)

    # print(json.dumps(resData, ensure_ascii=False, indent=4))

    for sheetName in resData:
        print("============",sheetName)
        # template = templateE.getTemplateStyle(sheetName)
        # e.newExcel(sheetName=sheetName,templateStyle=template)
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

    # print(eleRes)
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

    # print(eleRes)
    return eleRes


def importFile(tradingSessionMonth):


    for categories in contractTypeEnum:
        for contractType in contractTypeEnum[categories]:

            # if contractType !="月度集中竞价":
            #     continue

            contractTypePath = CommonClass.mkDir("河北","导入文件",tradingSessionMonth,contractType,isGetStr=True)
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
                    # print(fileDataList)

                    bugList = [
                        "日集中竞价",
                        # "日滚动撮合",
                        "周滚动撮合",
                        "月度集中竞价",
                        # "年度双边协商",
                        # "月度代理购电",
                        "月内代理购电",
                        # "上下调交易",
                        "题材电量挂牌",
                        "张河湾抽水电量",
                    ]

                    status = "买入" if contractType in bugList else "卖出"

                    execData(tradingSession,startDate,endDate,fileDataList,contractType,status,tradingSessionMonth)

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


def execData(tradingSession,startDate,endDate,fileDataList,contractType,isSell,tradingSessionMonth):

    deleteContract(startDate, endDate, tradingSession)

    # 处理分时段标识配置的文件
    if contractType in ["日集中竞价","日滚动撮合"]:
        execScrolData(fileDataList, tradingSession, startDate, endDate,contractType,isSell,tradingSessionMonth)

    else:

        execTData(fileDataList, tradingSession, startDate, endDate,contractType,isSell,tradingSessionMonth)


def execTData(fileDataList,tradingSession,startDate,endDate,contractType,isSell,tradingSessionMonth):

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
        # print(daysData)
        writeSql(data, tradingSession, month, daysData, startDate, endDate,contractType,tradingSessionMonth)

#日滚动撮合、日集中竞价
def execScrolData(fileDataList,tradingSession,startDate,endDate,contractType,isSell,tradingSessionMonth):
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

        # print(daysData)
        writeSql(data, tradingSession, month, daysData, startDate, startDate, contractType,tradingSessionMonth)


def writeSql(data,tradingSession,month,daysData,startDate,endDate, contractType,tradingSessionMonth):

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
            "trading_session_month": tradingSessionMonth,
        }

        # print(d)
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


def compareData(tradingSession=None, seller_name=None, period_time_coding=None, startDate=None, endDate=None):
    dataLists = queryContract(tradingSession=tradingSession, seller_name=seller_name, period_time_coding=period_time_coding, startDate=startDate,
                        endDate=endDate)

    mTool1 = MysqlTool(
        host="192.168.1.76",
        port=3306,
        user="pps_datacenter_test",
        password="qinghua123@",
        database="datacenter_hebei",
        charset="utf8",
    )

    mTool2 = MysqlTool(
        host="192.168.1.76",
        port=3306,
        user="hb_fire",
        password="qinghua123@",
        database="hb_fire_test",
        charset="utf8",
    )

    resultList = [
        # ["交易场次名称", "机组名称", "月份", "时段标识配置","合同日期" ,"类型", "数据不一致开始时刻点","测试环境数据","算例数据","测试环境所有时刻点数据","算例所有时刻点数据"]

    ]

    for data in dataLists:

        calendarQueryDict = {
            "month": [data["trading_session_month"]] ,
            "trade_name" :  [data["trading_session"]]
        }
        calendarQueryResIdList = mTool1.queryCalendar(calendarQueryDict)

        contractQueryDict = {
            "calendar_id":calendarQueryResIdList,
            "own_enterprise" : [data["seller_name"]],
        }

        if data["buyer_name"] != None:
            contractQueryDict["opposite_enterprise"] =  [data["buyer_name"]]

        contractQueryResIdList = mTool2.queryTestContractData(contractQueryDict)

        dateStr = data["date"].strftime("%Y-%m-%d")

        contractDetailQueryDict = {
            "contract_id" : contractQueryResIdList,
            "run_date" : [dateStr],
            "period_name" : [data["period_time_coding"]],
        }

        contractDetailRes = mTool2.queryTestContractDetail(contractDetailQueryDict)

        for res in contractDetailRes:
            res["ele"] = eval( res["ele"].replace("null","None") )
            res["price"] = eval( res["price"].replace("null","None") )
        # print(contractDetailRes)

        for i in range(0,24):


            eleTestData = round(contractDetailRes[0]["ele"][i],6) if contractDetailRes[0]["ele"][i]!=None else None
            eleCalData = round(data["ele"][i],6) if data["ele"][i]!=None else None

            if eleTestData != eleCalData:
                resultList.append(
                    [data["trading_session_month"],data["trading_session"], data["buyer_name"],data["seller_name"],data["month"],data["period_time_coding"],
                     str(dateStr),"电量",i+1,eleTestData,eleCalData,str(contractDetailRes[0]["ele"]),str(data["ele"]),
                     contractDetailRes[0]["id"],contractDetailRes[0]["contract_id"],
                     ]
                )
            break

        for i in range(0, 24):

            priceTestData = round(contractDetailRes[0]["price"][i], 6) if contractDetailRes[0]["price"][i]!=None else None
            priceCalData = round(data["price"][i], 6) if data["price"][i]!=None else None


            if priceTestData != priceCalData:
                resultList.append(
                    [data["trading_session_month"],data["trading_session"], data["buyer_name"], data["seller_name"], data["month"], data["period_time_coding"], str(dateStr),
                     "电价", i + 1, priceTestData, priceCalData, str(contractDetailRes[0]["price"]), str(data["price"]),
                     contractDetailRes[0]["id"],contractDetailRes[0]["contract_id"],
                     ]
                )
            break

    print(resultList)
    outComareData(resultList)
    mTool1.close()
    mTool2.close()

def outComareData(resultList):
    tempPath = CommonClass.mkDir("河北", "导出模板", "对比结果模板.xlsx", isGetStr=True)

    savePath = CommonClass.mkDir("河北", "导出模板", "对比结果.xlsx", isGetStr=True)
    e = ExcelHepler(tempPath)

    # print(json.dumps(resData, ensure_ascii=False, indent=4))
    e.writeData(savePath, resultList )

    e.close()
    # templateE.close()

def getContractDetail(tradingSession,
                      buyer_name,seller_name,
                      startDate,
                      endDate,
                      trading_session_month
                      ):

    res = queryContract(tradingSession=tradingSession, buyer_name=buyer_name,seller_name=seller_name,
                        startDate=startDate, endDate=endDate,trading_session_month=trading_session_month)

    # print(res)

    sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

    dateData = {

    }
    monthData = {

    }

    while sd <= ed:
        dateStr = datetime.datetime.strftime(sd, "%Y-%m-%d")
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

        dateStr = datetime.datetime.strftime(r["date"], "%Y-%m-%d")

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
        eleList = [date,"电量",dateData[dateStr]["eleSum"],]
        eleList.extend(dateData[date]["ele"])
        priceList = [date, "电价",dateData[dateStr]["priceSum"],]
        priceList.extend(dateData[date]["price"])
        dateDataList.append(eleList)
        dateDataList.append(priceList)


    monthDataList = [
        ["月份"],
        ["电量"],
        ["电价"]
    ]

    for month in monthData:
        monthDataList[0].append(month)
        monthDataList[1].append(monthData[month]["eleSum"])
        monthDataList[2].append(monthData[month]["priceSum"])



    # print(dateDataList)

    tempPath = CommonClass.mkDir("河北", "导出模板", "电量明细模板.xlsx", isGetStr=True)
    templateE = ExcelHepler(tempPath)
    template = templateE.getTemplateStyle("Sheet1")
    templateE.close()

    name = res[0]["contract_name"]
    savePath = CommonClass.mkDir("河北", "导出模板", name+"电量明细结果.xlsx", isGetStr=True)
    e = ExcelHepler()
    e.newExcel(sheetName="Sheet1", templateStyle=template)
    e.writeData(savePath, dateDataList, "Sheet1")


    e.newExcel(sheetName="月维度", templateStyle=None)
    e.writeData(savePath, monthDataList, "月维度",beginRow=1)

    e.close()

    pass


if __name__ == '__main__':

    # writeDataT(dataTyaml)
    # writeDataPeak(dataPeakyaml)
    # importFile("2023-08")
    # outputData(["上安电厂1号机","上安电厂2号机","上安电厂3号机","上安电厂4号机","上安电厂5号机","上安电厂6号机",],"2023-01-01","2023-12-31")
    # queryDataT()
    # queryDataPeak()

    # res = queryContract(tradingSession=None, seller_name=None, period_time_coding=None, startDate="2023-01-01", endDate="2023-01-01")

    # cal24Info(res)
    # calTRatio(res)
    # calPeakRatio(res)
    # print(ini())

    # execAnalysisData(["河北1#1机组"],"2023-01-01","2023-01-31",["1月第一次周交易"],["周滚动撮合"])
    # execAnalysisData(["上安电厂1号机"],"2023-01-01","2023-01-02")

    # compareData(tradingSession=["交易场次名称（年度双边协商）"], seller_name=["上安电厂1号机"], period_time_coding=None,
    #             startDate="2023-01-01",
    #             endDate="2023-12-31")

    getContractDetail(tradingSession=["交易场次名称（年度双边协商）"],
                      buyer_name=["华能河北能源售电"],seller_name=["上安电厂1号机"],
                      startDate="2023-01-01",
                      endDate="2023-12-31",
                      trading_session_month = ["2023-08"]
                      )



    pass