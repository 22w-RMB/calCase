import os.path

import xlwings


class ExcelHepler:


    def __init__(self , filePath):

        self.app = xlwings.App(visible=False,add_book=False)
        self.app.display_alerts = False
        self.app.screen_updating = False
        self.wb = self.app.books.open(filePath)

        pass

    def getTemplateStyle(self, sheetName="Sheet1"):

        return self.wb.sheets[sheetName].range("A1").expand().value

    def newExcel(self, sheetName="Sheet1", templateStyle=None):

        self.wb = self.app.books.add()

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



    def saveFile(self, savePath = None):

        if savePath is None:
            savePath = self.filePath

        # 保存
        self.wb.save(savePath)


    def close(self):
        self.wb.close()
        self.app.kill()




if __name__ == '__main__':


    pass