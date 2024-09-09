import datetime
import os.path

import xlwings


class ExcelHepler:


    def __init__(self , filePath=None):

        self.app = xlwings.App(visible=False,add_book=False)
        self.app.display_alerts = False
        self.app.screen_updating = False
        self.wb = None
        if filePath is not None:
            self.wb = self.app.books.open(filePath)
        else:
            self.wb = self.app.books.add()

        pass

    def getTemplateStyle(self, sheetName="Sheet1"):

        return self.wb.sheets[sheetName].range("A1").expand().value

    def copySheet(self,sourceSheetName,resSheetName):
        self.wb.sheets[sourceSheetName].copy(name=resSheetName)

    def newExcel(self, sheetName="Sheet1", templateStyle=None):

        # self.wb = self.app.books.add()

        if sheetName != "Sheet1":
            self.wb.sheets.add(sheetName)

        self.wb.sheets[sheetName].range("A1").options(expand="table").value = templateStyle

    def writeColData(self,colList,dataList,beginRowList,savePath,sheetName="Sheet1"):
        if len(colList) != len(dataList):
            print("输入的列数组和数据数组不一致！！！！")
            return

        ws = self.wb.sheets[sheetName]


        for i in range(0,len(colList)):

            row = beginRowList[i]
            col = colList[i]
            if len(dataList[i]) == 0:
                continue
            # for data in dataList[i]:
            #     ws.range(row,col).value = data
            #     row += 1
            ws.range((row,col),(row+1000,col)).value = [[j] for j in dataList[i] ]


        self.saveFile(savePath)

    # 针对甘肃用的
    def writeRowData(self,data):
        ws = self.wb.sheets["Sheet1"]
        for i in range(0,len(data)):

            ws.range((i+2, 1), (i+2, 5)).value = data[i]

    #
    def getDailyRollData(self,sheetName="市场交易信息"):
        ws = self.wb.sheets[sheetName]
        dataList = ws.range((2, 1), (25, 6)).value

        return dataList

    # 针对甘肃用的
    def getAllData(self):

        datas = []
        ws = self.wb.sheets["Sheet1"]
        maxRow = ws.used_range.last_cell.row
        print("====",maxRow)
        for i in range(2,maxRow+1):
            datas.append(
                [
                   # "时段类型":  ws.range(i,1).value,
                   ws.range(i, 1).value,
                   # "交易单元":
                   ws.range(i, 2).value,
                   # "买卖方向":  ,
                   "买入" if ws.range(i, 3).value=="买方" else "卖出",
                   # "成交电量":  ,
                   ws.range(i, 4).value,
                   # "成交均价":  ,
                    ws.range(i, 5).value,
                   # "申报日期":  ,
                    str.split(str(ws.range(i, 7).value),".")[0],
                   # "标的日期":  ,
                    str.split(str(ws.range(i, 8).value),".")[0],
                    # str.split(str(ws.range(i, 7).value), ".")[0]+str.split(str(ws.range(i, 8).value),".")[0]
                ]
            )

        return datas


    # 针对甘肃用的
    def getYuanshigonglvData(self,monthStr):

        datas = []
        num = len(self.wb.sheets)


        dateData = {}

        for i in range(0,num):
            sht = self.wb.sheets[i]


            shtName = sht.name
            shtName = shtName[0:(len(shtName)-1)]

            strFormat = monthStr + shtName

            dateFormat = datetime.datetime.strptime(strFormat, "%Y-%m-%d")

            strFormat = dateFormat.strftime("%Y%m%d")


            dateData[strFormat] = {

            }

            d1List = []
            d2List = []

            for i in range(3,99) :
                d1List.append(sht.range(i, 4).value)
                d2List.append(sht.range(i, 3).value)

            dateData[strFormat]['D-1原始功率预测'] = d1List
            dateData[strFormat]['D-2原始功率预测'] = d2List

        return dateData


    def writePriceData(self,sheetName,beginRow,col,dataList):
        ws = self.wb.sheets[sheetName]
        ws.range((beginRow, col), (beginRow + 95, col)).value = dataList

    def writeDetailData(self,detailDataList,sheetName):
        enumStr = {
            "date" : "日期",
            "info" : "详细信息",
            "result" : "结果",
            "versionName" : "版本名称",
        }
        outputList = []
        header = [enumStr[key] for key in enumStr]
        outputList.append(header)
        for data in detailDataList:
            tempL = [data[key] for key in data]
            outputList.append(tempL)


        ws = self.wb.sheets[sheetName]
        ws.range((1, 1), (1000, 20)).value = outputList


    def writeDailyRoll(self,dataList,sheetName="市场交易信息"):
        self.wb.sheets['Sheet1'].delete()
        ws = self.wb.sheets[sheetName]
        # print(dataList)
        ws.range((2, 1), (300000, 10)).value = dataList
        pass


    def writeDayAheadPrice(self,dataList,sheetName="sheet"):
        self.wb.sheets['Sheet1'].delete()
        ws = self.wb.sheets[sheetName]
        print(dataList)
        ws.range((2, 2), (5, 25)).value = dataList
        pass


    def saveFile(self, savePath = None):

        if savePath is None:
            savePath = self.filePath
        print(savePath)
        # 保存
        self.wb.save(savePath)


    def close(self):
        self.wb.close()
        self.app.kill()




if __name__ == '__main__':


    pass