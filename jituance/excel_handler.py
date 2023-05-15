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


    def newExcel(self,provinceName,privteDataUpload):

        if type(privteDataUpload) == str:
            self.wb.sheets["Sheet1"].range(1,2).value = privteDataUpload
            return

        for terminal in privteDataUpload:

            self.wb.sheets.add(terminal)

            ws = self.wb.sheets[terminal]

            terminalDict = privteDataUpload[terminal]

            col = 2

            for unit in terminalDict:


                unitStatusType = type(terminalDict[unit])
                # print(unitStatusType)
                # print(terminalDict[unit])
                l = []

                l.append([unit])

                if unitStatusType == list:
                    status = [[status] for status in terminalDict[unit]]
                    l.extend(status )

                elif unitStatusType == str:

                    l.append([terminalDict[unit]])


                print("=================", l)
                ws.range((1,col),(100000,col)).value = l

                col += 1

        # savePath = "D:\code\python\calCase\jituance\output\上传状态导出\\" + provinceName + ".xlsx"
        # self.saveFile(savePath)
        # self.close()


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