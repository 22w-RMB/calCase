import os
import datetime

from common.common import CommonClass
from excel_handler import ExcelHeplerXlwing
from 江西.cal.mysqlTool import MysqlTool
from 江西.cal.otherTool import Tool

class PrivateData:

    def __init__(self):
        pass


    def importClearingFile(self):

        clearingFilePath = CommonClass.mkDir("江西","导入文件","私有数据",isGetStr=True)
        if  os.path.exists(clearingFilePath) == False:
            return

        for root, dirs, files in os.walk(clearingFilePath):

            for file in files:
                filePath = os.path.join(root, file)
                filename = file.replace(".xls", "")
                dateNum = filename.split("-")[1]
                name = filename.split("-")[0]
                date = dateNum[:4] + "-" + dateNum[4:6] + "-" + dateNum[6:]
                e = ExcelHeplerXlwing(filePath)
                fileDataList = e.getClearingData()
                print("====",fileDataList)

                dataT ="dayAhead" if "日前" in name else "dayReal"

                self.execClearingData(fileDataList, date ,dataT)

    def execClearingData(self,fileDataList, date ,dataType):

        dataClearing = {

        }

        for i in range(0,len(fileDataList)):

            if i % 96 == 0:
                dataClearing[fileDataList[i][1]] = {
                    "ele" : [None for j in range(0,96)],
                    "price" : [None for j in range(0,96)],
                    "power" : [None for j in range(0,96)],

                }

            dataClearing[fileDataList[i][1]]["ele"][i%96] = fileDataList[i][3] /4
            dataClearing[fileDataList[i][1]]["price"][i%96] = fileDataList[i][4]
            dataClearing[fileDataList[i][1]]["power"][i%96] = fileDataList[i][3]

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

    @staticmethod
    def queryClearingData(unit=None,startDate=None,endDate=None,dataType=["dayAhead"]):

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


        # for r in queryRes:
        #     date = datetime.date.strftime(r["date"] ,"%Y-%m-%d")
        #     if date not in resD:
        #         resD[date] = {}
        #
        #     if r["unit"] not in resD[date]:
        #         resD[date][r["unit"]] = {
        #             "ele" : r["ele"],
        #             "power" : r["power"],
        #             "price" : r["price"],
        #         }

        # print(resD)
        return queryRes



if __name__ == '__main__':

    p = PrivateData()
    p.importClearingFile()
