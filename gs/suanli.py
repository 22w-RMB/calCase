

from common.excel_handler import ExcelHepler

import datetime
from dateutil.parser import parse

sourceFilePath = r"D:\code\python\calCase\gs\muban\安北三月份D+3交易.xlsx"

outputPath = r"D:\code\python\calCase\gs\daochu"

mubanPath = r"D:\code\python\calCase\gs\muban\导出模板.xlsx"

a = "20220201"

print(parse(a))

print(parse(a).strftime("%Y年%m月%d日"))

sourceE = ExcelHepler(sourceFilePath)

datas = sourceE.getAllData()
print(datas)

sourceE.close()

mubanExcel = ExcelHepler(filePath=mubanPath)
temValue = mubanExcel.getTemplateStyle()
mubanExcel.close()




resDict = {}

for i in range(0,len(datas)):

    data = datas[i]
    # key = data[5]+"-"+ data[6]

    shenbaoriqi = parse(data[5]).strftime("%Y-%m-%d")
    biaodiriqi = parse(data[6]).strftime("%Y年%m月%d日")
    key = "("+shenbaoriqi + ")甘肃省发电侧" + biaodiriqi + "日滚动交易.xlsx"

    value = data[0:5]

    if key not in resDict.keys():
        resDict[key] = []
    resDict[key].append(value)


print(resDict)

for key in resDict.keys():

    e  = ExcelHepler()
    e.newExcel(templateStyle=temValue)
    e.writeRowData(resDict[key])
    savePath = outputPath+"\\"+key
    e.saveFile(savePath)
    e.close()