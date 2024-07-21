import os.path

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

    def writeData(self, savePath,sheetName,dataList):

        ws = self.wb.sheets[sheetName]

        i = 2
        for item in dataList:

            data = [ item[key] for key in item.keys() ]

            ws.range((i, 1), (i, 20)).value = data
            ws.range('A1:zz5000').columns.autofit()
            i += 1


        self.saveFile(savePath)




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