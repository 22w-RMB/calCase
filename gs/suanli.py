

from excel_handler import ExcelHepler

import datetime
from dateutil.parser import parse

def rigundong():
    sourceFilePath = r"D:\code\python\calCase\gs\输入\客户提供的\分时合同\安北三月份D+3交易.xlsx"

    outputPath = r"D:\code\python\calCase\gs\导出\客户的\分时合同"

    mubanPath = r"D:\code\python\calCase\gs\muban\分时合同模板.xlsx"

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

    for i in range(0, len(datas)):

        data = datas[i]
        # key = data[5]+"-"+ data[6]

        shenbaoriqi = parse(data[5]).strftime("%Y-%m-%d")
        biaodiriqi = parse(data[6]).strftime("%Y年%m月%d日")
        key = "(" + shenbaoriqi + ")甘肃省发电侧" + biaodiriqi + "日滚动交易.xlsx"

        value = data[0:5]

        if key not in resDict.keys():
            resDict[key] = []
        resDict[key].append(value)

    print(resDict)

    for key in resDict.keys():
        e = ExcelHepler()
        e.newExcel(templateStyle=temValue)
        e.writeRowData(resDict[key])
        savePath = outputPath + "\\" + key
        e.saveFile(savePath)
        e.close()



def yuanshigonglv():
    outputPath = r"D:\code\python\calCase\gs\导出\客户的\原始功率"
    sourceFilePath = r"D:\code\python\calCase\gs\输入\客户提供的\原始功率\安马第二风电原始功率.xlsx"


    mubanPath = r"D:\code\python\calCase\gs\muban\原始功率.xls"

    monthStr = "2023-03-"



    # print(strFormat)


    sourceE = ExcelHepler(sourceFilePath)

    datas = sourceE.getYuanshigonglvData(monthStr)
    print(datas)

    sourceE.close()

    mubanExcel = ExcelHepler(filePath=mubanPath)
    temValue = mubanExcel.getTemplateStyle()
    mubanExcel.close()



    for date in datas:

        for key in datas[date]:
            savePath = "甘电投安马第二(200.5MW)风电场-" +key +"-"+date + ".xls"
            e = ExcelHepler()
            e.newExcel(templateStyle=temValue)
            # e.writeRowData(resDict[key])
            savePath = outputPath + "\\" + savePath
            e.writeColData([2],[datas[date][key]],[2],savePath)

            e.close()


yuanshigonglv()