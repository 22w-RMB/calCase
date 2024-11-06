import os.path
import re

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

            for sht in self.wb.sheets:
                if sht.name == sheetName:
                    sht.delete()

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


    '''
        输出私有数据概况
    '''
    def writePrivateOverviewData(self, savePath,sheetName,dataDict):

        ws = self.wb.sheets[sheetName]
        print("开始遍历")
        l = []

        for k,v in dataDict.items():
            #  获取场站个数
            vLen = len(v.keys())
            #  获取无数据的场站
            filterNoDataList = list(filter(lambda x:v[x]=="无数据",v.keys()))
            filterNoDataListLen = len(filterNoDataList)
            #  获取数据齐全的场站
            filterCompleteDataList = list(filter(lambda x:v[x]=="√",v.keys()))
            filterCompleteDataListLen = len(filterCompleteDataList)

            #  获取部分数据缺失的场站个数
            filterIncompleteDataListLen = vLen - filterNoDataListLen - filterCompleteDataListLen

            if filterNoDataListLen == vLen:
                l.append(["所有场站无数据"])
            elif filterIncompleteDataListLen == 0 and filterNoDataListLen != 0:
                l.append(["、".join(filterNoDataList) + "无数据"])
            elif filterIncompleteDataListLen != 0 and filterNoDataListLen != 0:
                l.append(["部分场站缺少数据或无数据"])
            elif filterCompleteDataListLen == vLen:
                l.append(["所有场站数据齐全"])
            else:
                l.append([None])


        ws.range((3, 6), (500000, 6)).value = l
        print("遍历结束")
        self.saveFile(savePath)


    '''
        输出公有数据概况
    '''
    def writePublicDetailData(self,savePath,sheetName,dataDict,rowColInfo):

        ws = self.wb.sheets[sheetName]
        cellAdress = rowColInfo.get('cellAdress')
        keyConfigList = ws.range(cellAdress).value
        valueList = [dataDict.get(k) for k in keyConfigList]
        # ws.range(cellAdress).value = valueList
        ws.range(cellAdress).options(transpose=True).value = valueList
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
    # first_book = xlwings.Book()
    # second_book = xlwings.Book()
    # first_book.sheets[0]['A1'].value = 'some value'
    #
    # # Copy to same Book with the default location and name
    # first_book.sheets[0].copy()
    #
    # # Copy to same Book with custom sheet name
    # first_book.sheets[0].copy(name='copied')
    #
    # # Copy to second Book requires to use before or after
    # first_book.sheets[0].copy(after=second_book.sheets[0])


    #
    # dict1 = {
    #     "a" : {
    #         "m" :2
    #     },
    #     "b" : {
    #         "b" :2
    #     },
    #     "c" :  {
    #         "m" :2
    #     }
    # }
    #
    # print(list(filter(lambda x: dict1[x]['m']==None, dict1)))
    try:
        e = ExcelHeplerXlwing(r'D:\code\python\calCase\山西新能源数据校验\导出\华润验收清单模版.xlsx')
        e.writePublicDetailData(None,"公有数据测试明细",{},{'cellAdress': "c3:c106"})
    finally:
        e.close()

    # print("vaera3b"[:-2])

    pass