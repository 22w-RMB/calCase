import os
import datetime

from common.common import CommonClass
from excel_handler import ExcelHepler
from 河北.mysqlTool import MysqlTool
from tool import Tool


class PrivateData:


    def __init__(self):
        pass

    def importClearingFile(self):

        clearingFilePath = CommonClass.mkDir("河北","私有数据","出清结果",isGetStr=True)
        if  os.path.exists(clearingFilePath) == False:
            return

        for root, dirs, files in os.walk(clearingFilePath):

            for file in files:
                filePath = os.path.join(root, file)
                filename = file.replace(".xlsx", "")
                dateNum = filename[10:]
                date = dateNum[:4] + "-" + dateNum[4:6] + "-" + dateNum[6:]
                e = ExcelHepler(filePath)
                fileDataList = e.getClearingData()
                print(fileDataList)

                self.execClearingData(fileDataList, date ,"dayAhead")

    def execClearingData(self,fileDataList, date ,dataType):

        dataClearing = {

        }

        for i in range(0,len(fileDataList)):

            if i % 96 == 0:
                dataClearing[fileDataList[i][3]] = {
                    "ele" : [None for j in range(0,96)],
                    "price" : [None for j in range(0,96)],
                    "power" : [None for j in range(0,96)],

                }

            dataClearing[fileDataList[i][3]]["ele"][i%96] = fileDataList[i][5] /4
            dataClearing[fileDataList[i][3]]["price"][i%96] = fileDataList[i][6]
            dataClearing[fileDataList[i][3]]["power"][i%96] = fileDataList[i][5]

        db = MysqlTool()
        print()
        for unit in dataClearing:

            d = {
                "date": date,
                "unit": unit,
                "ele": str(dataClearing[unit]["ele"]),
                "power": str(dataClearing[unit]["power"]),
                "price": str(dataClearing[unit]["price"]),
                "dataType": dataType,
                "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            db.insertClearingData(d)

        db.close()

    def queryClearingData(self,unit=None,startDate=None,endDate=None,dataType=["dayAhead"]):

        d = {
            "unit": unit,
            "start_date": startDate,
            "end_date": endDate,
            "clearing_type": dataType,
        }

        db = MysqlTool()

        queryRes = db.queryClearingData(d)

        # print(queryRes)
        db.close()


        for r in queryRes:
            r["ele"] = Tool.data96To24list(eval( r["ele"]))
            r["power"] = Tool.data96To24list(eval( r["power"]))
            r["price"] = Tool.data96To24list(eval( r["price"]))

        resD = {

        }


        for r in queryRes:
            date = datetime.date.strftime(r["date"] ,"%Y-%m-%d")
            if date not in resD:
                resD[date] = {}

            if r["unit"] not in resD[date]:
                resD[date][r["unit"]] = {
                    "ele" : r["ele"],
                    "power" : r["power"],
                    "price" : r["price"],
                }

        print(resD)
        return resD



if __name__ == '__main__':

    p = PrivateData()
    p.queryClearingData()