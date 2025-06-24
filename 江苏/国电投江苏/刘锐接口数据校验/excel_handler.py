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


    def write_contract(self,savePath,filter_contract_data_res_dict):

        ws1 = self.wb.sheets["合同名称"]
        ws2 = self.wb.sheets["交易单元"]
        ws3 = self.wb.sheets["日期"]

        ws1.range('a2:zz100000').value = filter_contract_data_res_dict['合同名称']
        ws2.range('a2:zz100000').value = filter_contract_data_res_dict['交易单元']
        ws3.range('a2:zz100000').value = filter_contract_data_res_dict['日期']

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