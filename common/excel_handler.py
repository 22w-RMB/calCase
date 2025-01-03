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