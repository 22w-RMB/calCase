import datetime
import os
from datetime import timedelta
from tool import Tool
from common.common import CommonClass
from excel_handler import ExcelHepler
from mysqlTool import MysqlTool

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
    "时间段": "Period_of_time"
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


def a():


    for root , dirs ,files in os.walk(r"D:\code\python\calCase\河北\导入文件"):

        # print(root)
        # print(dirs)

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

            execData(tradingSession,startDate,endDate,fileDataList)

        # print(files)


def execData(tradingSession,startDate,endDate,fileDataList):


    for data in fileDataList:

        if data["period_time_coding"] == None:
            continue

        #分时段编码
        period_time_coding = data["period_time_coding"][:2]

        #
        period_of_StartTimeString = data["Period_of_time"][:10]
        period_of_EndTimeString = data["Period_of_time"][11:]


        sd = datetime.datetime.strptime(period_of_StartTimeString, "%Y-%m-%d")
        ed = datetime.datetime.strptime(period_of_EndTimeString, "%Y-%m-%d")

        days = (ed-sd).days+1

        month = data["Period_of_time"][:7]

        onedayData = getOneDayData(month, period_time_coding, data["ele"]/days, data["price"])
        print()

        if onedayData == None:
            continue

        daysData = generate(sd,ed,onedayData)
        print(daysData)

        writeSql(data,tradingSession,month,daysData,startDate,endDate)


def writeSql(data,tradingSession,month,daysData,startDate,endDate):

    db = MysqlTool()

    for date in daysData:
        contract_name = ""
        buyer_name = None
        if "buyer_name" in data.keys():
            contract_name = tradingSession + data["buyer_name"]
            buyer_name = data["buyer_name"]
        else:
            contract_name = tradingSession + data["seller_name"]

        d = {
            "contract_name": contract_name,
            "buyer_name": buyer_name,
            "seller_name": data["seller_name"] if "seller_name" in data.keys() else None,
            "period_time_coding": data["period_time_coding"][:2],
            "ele": str(daysData[date]["ele"]),
            "price": str(daysData[date]["price"]),
            "date": date,
            "start_date": startDate,
            "end_date": endDate,
            "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "month": month
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

            if pType == None:
                continue

            if pTypeRatio == 0:
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
    writeDataPeak(dataPeakyaml)
    # a()
    pass