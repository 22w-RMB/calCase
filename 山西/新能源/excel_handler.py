import pandas as pd

import xlwings


class ExcelHeplerXlwing:


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
        if templateStyle == None:
            return

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


    def writeData(self,savePath,dataList,sheetName="Sheet1",beginRow=2,beginCol=1):

        ws = self.wb.sheets[sheetName]


        ws.range((beginRow,beginCol),(1000,100)).value = dataList


        self.saveFile(savePath)



    def getAllData(self,emunDict):

        datas = []
        ws = self.wb.sheets["Sheet1"]
        maxCol = ws.used_range.last_cell.column
        maxRow = ws.used_range.last_cell.row
        # print("====",maxRow)

        resList = []

        # print( ws.range(1,1) .value )
        try:

            header = ws.range((1,1),(1,maxCol)).value
            for i in range(0,len(header)):
                if header[i] in emunDict.keys():
                    header[i] = emunDict[header[i]]

            for i in range(2,maxRow+1):
                rowData = ws.range((i,1),(i,maxCol)).value

                resList.append(dict(zip(header,rowData)))

            # for i in range(2,maxRow+1):
            #
            #     d = {
            #
            #     }
            #     for j in range(1, maxCol + 1):
            #         header = ws.range(1,j) .value
            #
            #         if header in emunDict.keys():
            #             v = ws.range(i,j) .value
            #             d[emunDict[header]] = v
            #
            #
            #     resList.append(d)
        finally:
            self.close()

        return resList


    def getClearingData(self):
        ws = self.wb.sheets["Sheet1"]
        maxCol = ws.used_range.last_cell.column
        maxRow = ws.used_range.last_cell.row

        print(maxCol,maxRow )

        resList = []

        try:

            for i in range(2,maxRow+1):

                rowData = ws.range((i,1),(i,maxCol)).value
                resList.append(rowData)

        finally:
            self.close()

        print(resList)
        return resList


    def saveFile(self, savePath = None):

        if savePath is None:
            savePath = self.filePath
        print(savePath)
        # 保存
        self.wb.save(savePath)


    def close(self):
        self.wb.close()
        self.app.kill()



class ExcelHepler:


    def __init__(self , filePath=None,sheetName=0,header=None):

        if filePath != None:
            # print(header)
            self.df = pd.read_excel(io=filePath,sheet_name=sheetName,index_col=False ,header=None,names=header,keep_default_na=False)
            # print(self.df)
            # self.df.columns = header
            # print(dataFrame["1-电量"])
            # for row in self.df.itertuples(index=False):
                # print(getattr(row,"1-电量"))
                # print(row)

    def getDayEleDetail(self):

        return self.df

    def getMonthEleDetail(self):

        return self.df



    def close(self):
        pass


if __name__ == '__main__':
    path = r"D:\code\python\calCase\江西\导入文件\xx电厂-合同日电量明细-YYYY.xls"
    e = ExcelHepler(path, "合同分月查询结果")

    pass