import datetime
import decimal
import time
from decimal import Decimal

import requests
import json
from datetime import datetime,timedelta

from common.common import CommonClass
from excel_handler import ExcelHepler

yamlPath = r"D:\code\python\calCase\jituance\config\mx_interface.yaml"
# yamlPath = r"D:\code\pyhton\calCase\jituance\config\mx_interface.yaml"


class ProvinceIn:

    def __init__(self, session, yamlData, type):
        self.domain = None
        self.loginInfo = None
        self.session = session
        # self.provinceId = "15"
        if type == "test":
            self.domain = yamlData['url_domain']['test_domain']
            self.loginInfo = yamlData['logininfo']['test_info']
        elif type == "tcloud":
            self.domain = yamlData['url_domain']['tcloud_domain']
            self.loginInfo = yamlData['logininfo']['tcloud_info']
        elif type == "hn":
            self.domain = yamlData['url_domain']['hn_domain']
            self.loginInfo = yamlData['logininfo']['hn_info']

    def login(self):
        CommonClass.login(self.session, self.domain, self.loginInfo)

    # 获取省份下所有企业的所有机组
    def getUnitId(self, url):

        resquestUrl = self.domain + url
        method = "GET"

        resJson = CommonClass.execRequest(self.session, method=method, url=resquestUrl).json()

        # print(resJson)

        terminalList = []
        if len(resJson['data']) == 0:
            return terminalList

        for d in resJson['data']:
            terminalName = d['ownerName']
            unitsList = []

            for unit in d['children']:
                unitsList.append(
                    {
                        "unitId": unit['unitId'],
                        "unitName": unit['unitName'],
                        "capacity": unit['capacity'],
                        "businessType": unit['businessType'],
                    }
                )

            terminalList.append([terminalName, unitsList])

        return terminalList

    # 请求省内的私有数据
    def resquestPrivateInData(self,startDate,endDate, url, terminalList):

        # 设置开始日期、结束日期
        # startDate = "2023-04-21"
        # endDate = "2023-05-03"

        # startDate = "2023-06-01"
        # endDate = "2023-06-02"
        method = "GET"

        enum = {
            "fittingPower" : ["中长期合同电力", "mltContractEle"],
            "dayAheadClearingPower" : ["日前出清电力","daClearEle"],
            "realTimeClearingPower" : ["实时出清电力","rtClearEle"],
            "actualMeasuredPower" : ["实际计量电力","rtPowerEle"],
            "fittingPrice" : ["中长期合同电价","mltContractPrice"],
            "realTimeClearingPrice" : ["实时出清电价","rtClearPrice"],
        }

        # 请求url
        resquestUrl = self.domain + url
        privteDataUpload = {}

        terminalDict = {}
        '''
        terminalDict  用于记录所有该省份所有企业的所有机组的上传情况, 格式如下

            {
                “机组id”：{
                        "机组名":  unitName  ,
                        "企业名":  terminalName  ,
                        “日期”：{
                            "DAEle":[],
                            "DAPrice":[],
                            "InEle":[],
                            "InPrice":[],
                        }
                    }
            }

        '''

        if len(terminalList) == 0:
            privteDataUpload
            return {
                "privteDataUpload" : "该省份没有场站",
                "terminalDict" : terminalDict,
            }

        for terminal in terminalList:

            # 用于记录单个企业下所有机组的数据
            # unitsDict = {}

            privteDataUpload[terminal[0]] = {}
            '''
                {
                    "企业":{
                        "机组": [ "02-01日前电价已上传", "02-01日前电量已上传",  .....]
                    }
                }
            '''

            for unit in terminal[1]:

                param = {
                    "startDate": startDate,
                    "endDate": endDate,
                    "deviceId": unit['unitId'],
                    "businessType": unit['businessType'],
                }


                # 发起请求
                res = CommonClass.execRequest(self.session, method=method, url=resquestUrl, params=param).json()
                # print(res)

                # 如果日期范围内都没有数据， 接口会返回 [] ，即长度为0 ，此时跳过
                if len(res['data']) == 0:
                    privteDataUpload[terminal[0]][unit['unitName']] = startDate + " 到 " + endDate + " 这段时间没有导入数据"

                    terminalDict.update( self.createData(startDate,endDate,terminal,unit) )

                    continue

                terminalDict[unit['unitId']] = {}
                terminalDict[unit['unitId']]["dateData"] = {}
                # datesDict  记录单个机组每一天的私有数据
                datesDict = {}

                # unit['unitName'] 为机组名，以列表形式存储每一天、每种类型数据上传情况
                privteDataUpload[terminal[0]][unit['unitName']] = []

                for r in res['data']:

                    # 截取日期，截取后的格式： YYYY-MM-DD
                    datestr = r['date'][0:10]

                    # 如果字典不存在该日期的数据，则初始化
                    if datestr not in datesDict:
                        datesDict[datestr] = {}

                    # print()

                    for key in enum:

                        datesDict[datestr][enum[key][1]] =  r[key]

                        if r[key] == []:
                            privteDataUpload[terminal[0]][unit['unitName']].append(datestr + " 【" + enum[key][0] + "】 未上传")

                    datesDict[datestr]["runCapacity"] = []

                    calRunCapPower = []
                    # 判断运行容量
                    if unit["capacity"] is not None :

                        if  r["realTimeClearingPower"] != []:
                            calRunCapPower = r["realTimeClearingPower"]

                    if calRunCapPower != [] :

                        for power in calRunCapPower:
                            resPower = None
                            if power is not None:
                                if power >= (unit['capacity'] * 0.05):
                                    resPower = unit['capacity']
                                else:
                                    resPower = 0

                            datesDict[datestr]["runCapacity"].append(resPower)



                terminalDict[unit['unitId']]["dateData"] = datesDict
                terminalDict[unit['unitId']].update(
                    { "unitName" : unit['unitName'] ,
                      "terminalName":terminal[0]
                      }
                )

            # terminalDict[terminal[0]] = unitsDict

        return {
                "privteDataUpload" : privteDataUpload,
                "terminalDict" : terminalDict,
            }


    # 当省内私有数据返回为空时，构建数据
    def createData(self, startDate, endDate, terminal, unit):

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        dataDict = {}

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            dataDict[dateStr] = {}

            dataDict[dateStr]["DAEle"] = []
            dataDict[dateStr]["DAPrice"] = []
            dataDict[dateStr]["INEle"] = []
            dataDict[dateStr]["INPrice"] = []


            # 日期 +1
            sd += timedelta(days=1)



        return {
            unit['unitId'] :  {
                "dateData" : dataDict,
                "unitName": unit['unitName'],
                "terminalName": terminal[0]
             }
        }


    # 输出省内私有数据上传状态到文件
    def outPrivateStatus(self,provinceName,privteDataUpload):

        e = ExcelHepler()
        e.outPrivateDataStatus(privteDataUpload)
        savePath = "D:\code\python\calCase\jituance\output\蒙西省内\\" + provinceName + "-省内数据上传情况.xlsx"

        e.saveFile(savePath)
        e.close()

        pass




    # 获取华能交易数据导出
    def getHuanengOuputData(self, startDate, endDate, provinceIds):

        enum = {
            "mltContractEle" : ["中长期合同电力", "mltContractEle"],
            "daClearEle" : ["日前出清电力","daClearEle"],
            "rtClearEle" : ["实时出清电力","rtClearEle"],
            "rtPowerEle" : ["实际计量电力","rtPowerEle"],
            "mltContractPrice" : ["中长期合同电价","mltContractPrice"],
            "rtClearPrice" : ["实时出清电价","rtClearPrice"],
            "runCapacity" : ["运行容量","runCapacity"],
        }


        CommonClass.switchTenantId(self.session,self.domain,"tsintergy")

        resquestUrl = self.domain + "/huaneng/group/api/group/private/data/query/spot/data"

        method = "GET"
        responseData = []

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")


        while sd <= ed:
            d1Str = datetime.strftime(sd, "%Y-%m-%d")

            d2 = sd + timedelta(days=10)

            if d2 >= ed:
                d2 = ed

            d2Str = datetime.strftime(d2, "%Y-%m-%d")

            param = {
                "startDate": d1Str,
                "endDate": d2Str,
                "provinceIds": provinceIds,
            }

            time.sleep(1)
            res = CommonClass.execRequest(self.session, method=method, url=resquestUrl, params=param).json()


            # 省内新能源
            responseData.extend(res['data'][0]['inNewProvinceTradeDOS'])
            # 省内其他类型
            responseData.extend(res['data'][0]['inProvinceTradeDOS'])
            # print(responseData)

            sd = d2 + timedelta(days=1)

        terminalDict = {}

        for rd in responseData:

            datestr = rd['date'][0:10]

            for dtd in rd['dataTradeDOS']:
                if dtd['id'] not in terminalDict:
                    terminalDict[dtd['id']] = {}
                    terminalDict[dtd['id']]['dateData'] = {}

                tempDict = {}

                for key in enum:
                    tempDict[key] = dtd[key]


                # 记录日期数据
                terminalDict[dtd['id']]['dateData'].update(
                    {
                        datestr: tempDict,
                    }
                )

                # 记录机组名称和企业名称
                terminalDict[dtd['id']].update(
                    {
                        "unitName": dtd['unitName'],
                        "terminalName": rd['orgName']
                    }
                )

        return terminalDict

    def execProvinceInfo(self, startDate,endDate,provinceInfo):

        # 记录所有省份的上传情况
        allProvinceDataUploadStatus = []

        # 记录所有省份的比较结果
        allProvinceCompareStatus = {}

        # 记录数据不一致的省份
        errorProvince = []

        for province in provinceInfo:

            CommonClass.switchTenantId(self.session,self.domain,province['tenantId'])

            # 每个省份的获取机组的url
            getUintUrl = province["url"] + "/fire/api/org/org/tree"

            # 获取该省份省间的机组信息
            terminalList = self.getUnitId(getUintUrl)
            # print(terminalList)
            print("==========获取机组正常")


            # 每个省份的获取私有数据的url
            resquestPrivateDataUrl = province["url"] + "/fire/api/mx/data/analysis/clearing"

            # 获取私有数据
            responsePrivateData = self.resquestPrivateInData(startDate,endDate,resquestPrivateDataUrl, terminalList)

            print("==========获取私有数据正常")

            # 记录省内私有数据，如果没有数据则为{}
            provincePrivteData = responsePrivateData['terminalDict']
            # print(provincePrivteData)

            # 记录该省份上传的情况
            provincePrivteDataUpload = responsePrivateData['privteDataUpload']
            print("==========")


            # 记录华能集团返回的数据
            huanengOutputData = self.getHuanengOuputData(startDate,endDate, province["provinceIds"] )
            print("==========获取华能数据正常")

            compareStatus = {
                "provinceUnit" : [],
                "unitMiss" :[] ,
                "nameCompare" : [],
                "dataCompare" : [],
            }


        #     # print(provincePrivteData)
        #     # print(huanengOutputData)

            self.compare(provincePrivteData,huanengOutputData, compareStatus)

            if len(compareStatus["dataCompare"]) != 0:
                errorProvince.append(province['provinceName'])

            allProvinceCompareStatus[province["provinceName"]] = compareStatus

            self.outPrivateStatus( province['provinceName'],provincePrivteDataUpload)

        self.outAllCompareStatus(allProvinceCompareStatus)
            # print(terminalDataDict)
        print(errorProvince)



    def outAllCompareStatus(self, allProvinceCompareStatus):
        enum = {
            "dataCompare": "数据比较表",
            "unitMiss": "机组缺失表",
            "nameCompare": "机组和企业名称比较表",
            "provinceUnit": "省间是否有机组",
        }


        a = {
            "head" : ["省份","数据错误机组个数","机组缺失个数","机组和企业名称不一致个数","省间是否有机组",]

        }

        for type in enum:

            compareStatus = {}

            for province in allProvinceCompareStatus:

                if province not in a:
                    a[province] = []
                    a[province].append(province)

                compareStatus[province] = allProvinceCompareStatus[province][type]


                if type == "dataCompare" :
                    unitids = []
                    for i in allProvinceCompareStatus[province][type]:
                        unitids.append(i['unitId'])

                    a[province].append( len(set(unitids)))
                elif type == "provinceUnit":
                    if len(allProvinceCompareStatus[province][type]) > 0:
                        a[province].append("省间系统没有机组")
                    else:
                        a[province].append("有")

                else:
                    a[province].append(len(allProvinceCompareStatus[province][type]))


            e = ExcelHepler()
            e.outAllCompareStatus(compareStatus)
            savePath = "D:\code\python\calCase\jituance\output\蒙西省内\\" + enum[type] + ".xlsx"
            e.saveFile(savePath)
            e.close()

        e = ExcelHepler()
        e.outALL(a)
        savePath = "D:\code\python\calCase\jituance\output\蒙西省内\汇总.xlsx"
        e.saveFile(savePath)
        e.close()

        pass

        # pass


    def compare(self, provincePrivteData, huanengOutputData, compareStatus):

        enum = {
            "mltContractEle" : "中长期合同电量",
            "daClearEle" : "日前出清电量",
            "rtClearEle" : "实时出清电量",
            "rtPowerEle" : "实际计量电量",
            "mltContractPrice" : "中长期合同电价",
            "rtClearPrice" : "实时出清电价",
            "runCapacity" : "运行容量",
        }

        # 省间系统无场站时，即 provincePrivteData = {}
        if provincePrivteData == {} :
            compareStatus['provinceUnit'] .append(
                {
                    "info" : "省间系统无场站"
                }
            )

        for p in provincePrivteData:

            # 判断华能有没有该机组
            if p not in huanengOutputData:

                haveData = False

                provinceDateDatas = provincePrivteData[p]['dateData']

                # 判断带该机组在省间有没有数据
                for date in provinceDateDatas:
                    provinceOneDateData = provinceDateDatas[date]

                    for item in provinceOneDateData:

                        if len(provinceOneDateData[item]) == 0:
                            continue

                        haveData = True
                        break

                haveDataInfo = "=====且省间有数据" if haveData else "省间没有数据"

                print("=================华能没有该机组"+ p)
                compareStatus['unitMiss'].append( {
                    "info" : "该机组只有省间系统有，集团侧没有找到该机组" + haveDataInfo,
                    "unitId" : p,
                    "provinceUnitName" : provincePrivteData[p]["unitName"],
                    "provinceTerminalName" : provincePrivteData[p]["terminalName"],
                    "huanengUnitName" : "",
                    "huanengTerminalName" : "",
                } )

                continue

            # 比较机组所在的机组名称是否一致
            if provincePrivteData[p]['unitName'] != huanengOutputData[p]['unitName']:
                compareStatus['nameCompare'].append(
                    {
                        "info": "该机组的省间和华能集团侧的名称不一致",
                        "unitId": p,
                        "provinceUnitName": provincePrivteData[p]["unitName"],
                        "huanengUnitName": huanengOutputData[p]['unitName'],
                        "provinceTerminalName": provincePrivteData[p]["terminalName"],
                        "huanengTerminalName": huanengOutputData[p]['terminalName']
                    }
                )

            # 比较机组所在的电厂名称是否一致
            if provincePrivteData[p]['terminalName'] != huanengOutputData[p]['terminalName']:
                compareStatus['nameCompare'].append(
                    {
                        "info": "该机组所在的电厂的省间和华能集团侧的名称不一致",
                        "unitId": p,
                        "provinceUnitName": provincePrivteData[p]["unitName"],
                        "huanengUnitName": huanengOutputData[p]['unitName'],
                        "provinceTerminalName": provincePrivteData[p]["terminalName"],
                        "huanengTerminalName": huanengOutputData[p]['terminalName']
                    }
                )

            # 获取省间和集团侧的日期数据
            provinceDateDatas = provincePrivteData[p]['dateData']
            huanengDateDatas = huanengOutputData[p]['dateData']
            for date in provinceDateDatas:

                # 获取省间和集团侧对应日期的数据
                provinceOneDateData = provinceDateDatas[date]
                huanengOneDateData = huanengDateDatas[date]

                for item in provinceOneDateData:

                    # 判断数组长度是否一致
                    if len(provinceOneDateData[item]) != len(huanengOneDateData[item]):

                        # 省内为空，集团侧不为空
                        if len(provinceOneDateData[item]) == 0 :
                            compareStatus['dataCompare'].append({
                                "info": "该机组的 【"+enum[item] +"】 省间数据为空，集团侧数据不为空",
                                "unitId": p,
                                "date": date,
                                "type": enum[item],
                                "num": "无",
                                "provinceData": "",
                                "huanengData": str(huanengOneDateData[item]),
                                "provinceUnitName": provincePrivteData[p]["unitName"],
                                "huanengUnitName": huanengOutputData[p]['unitName'],
                                "provinceTerminalName": provincePrivteData[p]["terminalName"],
                                "huanengTerminalName": huanengOutputData[p]['terminalName']
                            })

                            pass

                        # 集团侧为空，省间不为空
                        if len(huanengOneDateData[item]) == 0:
                            compareStatus['dataCompare'].append({
                                "info": "该机组的 【"+enum[item] +"】 集团侧数据为空，省间数据不为空",
                                "unitId": p,
                                "date": date,
                                "type": enum[item],
                                "num": "无",
                                "provinceData": str(provinceOneDateData[item]),
                                "huanengData": "",
                                "provinceUnitName": provincePrivteData[p]["unitName"],
                                "huanengUnitName": huanengOutputData[p]['unitName'],
                                "provinceTerminalName": provincePrivteData[p]["terminalName"],
                                "huanengTerminalName": huanengOutputData[p]['terminalName']
                            })
                            pass

                        continue


                    # 如果数据为空则打印出来
                    # if len(provinceOneDateData[item]) == 0 :
                    #
                    #     print("数据正确。日期：" + date + "。 机组：" +
                    #     provincePrivteData[p]["unitName"] + "。类型 " + enum[item] + "为空")
                    #     pass


                    # 判断每个时刻点数据是否一致
                    for i in range(0,len(provinceOneDateData[item])):
                        pDecimalData = provinceOneDateData[item][i]
                        hDecimalData = huanengOneDateData[item][i]
                        if ( pDecimalData is None )or (hDecimalData is None):

                            pass
                        else:
                            pDecimalData = Decimal(str(provinceOneDateData[item][i]))
                            if "Ele" in item:
                                pDecimalData = (pDecimalData/Decimal("4"))
                            pDecimalData = pDecimalData.quantize(Decimal("0.00"), rounding="ROUND_HALF_UP")

                            hDecimalData = Decimal(str(huanengOneDateData[item][i])).quantize(Decimal("0.00"), rounding="ROUND_HALF_UP")

                        # 如果时刻点的数据一样则跳过
                        if (pDecimalData  -  hDecimalData).copy_abs() <= Decimal("0.01"):
                            # print("数据正确。日期：" + date + "。 机组：" +  provincePrivteData[p]["unitName"] + "。类型 " + enum[item])
                            continue

                        print("=======================================数据错误" )

                        # 如果时刻点的数据不一样，则记录错误
                        compareStatus['dataCompare'].append({
                            "info": "该机组" + date + " 的 【"+ enum[item] +"】 不一致",
                            "unitId": p,
                            "date" : date,
                            "type" : enum[item],
                            "num" : i+1,
                            "provinceData": str(pDecimalData),
                            "huanengData": str(hDecimalData),
                            "provinceUnitName": provincePrivteData[p]["unitName"],
                            "huanengUnitName": huanengOutputData[p]['unitName'],
                            "provinceTerminalName": provincePrivteData[p]["terminalName"],
                            "huanengTerminalName": huanengOutputData[p]['terminalName']
                        })

                        break


        # 判断华能集团侧的机组在省间有没有
        for h in huanengOutputData:

            if h not in provincePrivteData:

                haveData = False

                huanengDateDatas = huanengOutputData[h]['dateData']

                # 判断带该机组在华能集团侧有没有数据
                for date in huanengDateDatas:
                    huanengOneDateData = huanengDateDatas[date]

                    for item in huanengOneDateData:

                        if len(huanengOneDateData[item]) == 0:
                            continue

                        haveData = True
                        break

                haveDataInfo = "=====且集团侧有数据" if haveData else "集团侧没有数据"

                compareStatus['unitMiss'].append({
                    "info": "该机组只有集团侧有，省间系统没有找到该机组。" + haveDataInfo,
                    "unitId": h,
                    "provinceUnitName": "",
                    "provinceTerminalName": "",
                    "huanengUnitName": huanengOutputData[h]["unitName"],
                    "huanengTerminalName": huanengOutputData[h]["terminalName"]
                })




        pass




if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    jtc_hn = ProvinceIn(testSession, yamlData, "hn")

    jtc_hn.login()

    provinceInfo = [

        {"provinceName": "蒙西", "url": "/mxgroup", "provinceIds": 15,"tenantId":  "e4d20ccb81bcf0170181cbebbaec01c3" , },

    ]

    startDate = "2023-04-21"
    endDate = "2023-04-21"



    jtc_hn.execProvinceInfo(startDate,endDate,provinceInfo)

    # print(jtc_hn.getHuanengOuputData(startDate, endDate, 15))
