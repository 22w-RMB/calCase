import random
import datetime

import pythoncom

from common.common import CommonClass
from common.excel_handler import ExcelHepler


hn_private_data_path  = CommonClass.mkDir( *["hn" , "output","private_data"],isGetStr=True)

hn_tem_path  = CommonClass.mkDir( *["hn" , "template"],isGetStr=True)

hn_out_path  = CommonClass.mkDir( *["hn" , "output"],isGetStr=True)



def generateUnit(count,prefix=""):

    unitList = []

    prefix = prefix + "#"

    for i in range(0,count):

        unitList.append(
            {
                "unitName" : prefix + str(i+1),
                "businessType" : CommonClass.randomBusinessType(),
            }
             )

    return  unitList


def outputPrivateData( startDate, days , unitsInfo, templateInfo):

    temList = []
    for t in templateInfo:
        templatePath = CommonClass.mkDir(hn_tem_path, t + ".xlsx", isGetStr=True)

        e = ExcelHepler(templatePath)
        templateValue = e.getTemplateStyle()
        e.close()

        temList.append(
            {
                "temName" : t,
                "temValue" : templateValue
            }
        )

    print(temList)

    e = ExcelHepler()

    for unit in unitsInfo:
        unitName = unit['unitName']
        date = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        for i in range(0,days):
            dateStr = datetime.datetime.strftime(date,"%Y%m%d")

            for t in temList:
                filename = unitName + "-" + t["temName"] + "-"+ dateStr + ".xlsx"
                outputFilePath = CommonClass.mkDir(hn_out_path,filename,isGetStr=True)

                print(outputFilePath)

                e.newExcel(templateStyle=t["temValue"])

                e.saveFile(outputFilePath)

            date += datetime.timedelta(days=1)
        # filename = unit[unitName]


    e.close()

def outputPrivateDataThread( startDate, days , unitsInfo, templateInfo,queue):

    pythoncom.CoInitialize()

    temList = []
    for t in templateInfo:
        templatePath = CommonClass.mkDir(hn_tem_path, t + ".xlsx", isGetStr=True)

        e = ExcelHepler(templatePath)
        templateValue = e.getTemplateStyle()
        e.close()

        temList.append(
            {
                "temName" : t,
                "temValue" : templateValue
            }
        )

    print(temList)

    e = ExcelHepler()

    for unit in unitsInfo:
        unitName = unit['unitName']
        date = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        for i in range(0,days):
            dateStr = datetime.datetime.strftime(date,"%Y%m%d")

            for t in temList:
                filename = unitName + "-" + t["temName"] + "-"+ dateStr + ".xlsx"
                outputFilePath = CommonClass.mkDir(hn_out_path,filename,isGetStr=True)

                print(outputFilePath)

                e.newExcel(templateStyle=t["temValue"])

                e.saveFile(outputFilePath)

                queue.put([filename,outputFilePath])
            date += datetime.timedelta(days=1)

    queue.put(None)
        # filename = unit[unitName]


    e.close()



# print(hn_private_data_path)


if __name__ == '__main__':
    print(generateUnit(4, prefix="华苏"))

    templateInfo = ["实时出清结果","日前出清结果","电厂实际上网电量"]

