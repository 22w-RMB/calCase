import os.path

import xlwings


class ExcelHeplerXlwing:


    def __init__(self , filePath=None):

        self.app = xlwings.App(visible=False,add_book=False)
        self.app.display_alerts = False
        self.app.screen_updating = False
        self.wb = None
        if filePath is not None:
            self.wb = self.app.books.open(r"{}".format(filePath))
        else:
            self.wb = self.app.books.add()

        pass

    def getTemplateStyle(self, sheetName="Sheet1"):

        return self.wb.sheets[sheetName].range("A1").expand().value

    def newExcel(self, sheetName="Sheet1", templateStyle=None):

        if sheetName != "Sheet1":
            self.wb.sheets.add(sheetName)
        if templateStyle == None:
            return

        self.wb.sheets[sheetName].range("A1").options(expand="table").value = templateStyle




    def copySheet(self,tempPath=None,tempSheet=None,sheetName=None):

        try:
            tempWb = xlwings.Book(tempPath)
            tempSht = tempWb.sheets[tempSheet]
            tempSht.copy(after=self.wb.sheets[0])
            self.wb.sheets[tempSheet].name = sheetName
        finally:
            tempWb.close()
            # tempWb.kill()

        pass

    def writeData(self, savePath,sheetName,dataList):

        ws = self.wb.sheets[sheetName]
        print("开始遍历")
        l = []
        for item in dataList:

            data = [ item[key] for key in item.keys() ]
            l.append(data)
            # ws.range((2, 1), (500000, 20)).value = data
            # ws.range('A1:zz500000').columns.autofit()
            # i += 1
        ws.range((2, 1), (500000, 20)).value = l
        print("遍历结束")
        self.saveFile(savePath)

    '''
        输出私有数据明细
    '''
    def writePrivateDetailData(self, savePath,sheetName,dataDict):

        ws = self.wb.sheets[sheetName]
        print("开始遍历")
        l = []
        print(dataDict)
        print("==",dataDict['原始功率预测'])
        unitsList = [ k  for k in dataDict['原始功率预测'].keys()]

        for unit in unitsList:
            print("==",unit)
            temp = []
            for k,v in dataDict.items():
                temp.append(v[unit])

            l.append(temp)
                # ws.range((2, 1), (500000, 20)).value = data
                # ws.range('A1:zz500000').columns.autofit()
                # i += 1
        ws.range((4, 2), (500000, 20)).value = l
        print("遍历结束")
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
    # Create two books and add a value to the first sheet of the first book
    first_book = xlwings.Book()
    second_book = xlwings.Book()
    first_book.sheets[0]['A1'].value = 'some value'

    # Copy to same Book with the default location and name
    first_book.sheets[0].copy()

    # Copy to same Book with custom sheet name
    first_book.sheets[0].copy(name='copied')

    # Copy to second Book requires to use before or after
    first_book.sheets[0].copy(after=second_book.sheets[0])

    pass