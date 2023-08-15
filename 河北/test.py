import datetime
import os
from datetime import timedelta
from tool import Tool
import requests

from common.common import CommonClass
from excel_handler import ExcelHepler
from threading import Thread

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

        # print(period_of_StartTimeString)
        # print(period_of_EndTimeString)


        period_of_StartTime = datetime.datetime.strptime(period_of_StartTimeString)
        period_of_EndTime = datetime.datetime.strptime(period_of_EndTimeString)

        month = data["Period_of_time"][:7]

        if month not in dataTyaml.keys():
            print(month, "该月份未设置分时段编码")
            continue

        if period_time_coding not in  dataTyaml[month].keys():
            print(month, "该月份未设置",period_time_coding,"分时段编码")
            continue

        if dataTyaml[month][period_time_coding]["haveRatio"] == True:
            # 查峰平谷
            if month not in dataPeakyaml.keys():
                print(month, "该月份未设置峰平谷")
                continue

            pTypes = [ "tip", "peak","flat" , "valley"]


            for pType in pTypes:
                pTypeTime = dataPeakyaml[month][pType]
                pTypeRatio = dataTyaml[month][period_time_coding]["ratio"]["pType"]


            continue

        if dataTyaml[month][period_time_coding]["haveRatio"] == False:
            time24List = Tool.time24o24list( dataTyaml[month][period_time_coding]["time"] )

            pass
    pass

if __name__ == '__main__':


    a()