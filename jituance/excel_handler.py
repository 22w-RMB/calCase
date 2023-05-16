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


    def outPrivateDataStatus(self,privteDataUpload):

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


                # print("=================", l)
                ws.range((1,col),(100000,col)).value = l
                ws.range('A1:zz5000').columns.autofit()
                col += 1

    def outCompareStatus(self, compareStatus):

        enum = {
            "provinceUnit": "省间是否有机组",
            "unitMiss": "机组缺失表",
            "nameCompare": "机组和企业名称比较表",
            "dataCompare": "数据比较表",
            "info": "比较结果",
            "unitId": "机组ID",
            "provinceUnitName": "在省间系统的机组名称",
            "provinceTerminalName": "在省间系统的企业名称",
            "huanengUnitName": "在华能集团侧的机组名称",
            "huanengTerminalName": "在华能集团侧的企业名称",
            "date": "数据日期",
            "type": "数据项",
            "num": "第几个时刻点，从1开始",
        }


        for cs in compareStatus:
            self.wb.sheets.add(enum[cs])

            if compareStatus[cs] == []:

                continue

            ws = self.wb.sheets[enum[cs]]

            i = 2
            for item in compareStatus[cs] :

                if i == 2:
                    head = [ enum[key] for key in item]
                    ws.range((1, 2), (1, 10)).value = head

                data = [ item[key] for key in item ]

                ws.range((i, 2), (i, 10)).value = data
                ws.range('A1:zz5000').columns.autofit()
                i += 1

                # status = [[status] for status in terminalDict[unit]]


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