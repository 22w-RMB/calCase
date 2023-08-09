import datetime
import time
from decimal import Decimal

import requests
import json
from datetime import datetime,timedelta

from common.common import CommonClass
from excel_handler import ExcelHepler
from jituance.getCost import Fire

yamlPath = r"D:\code\python\calCase\jituance\config\mx_interface.yaml"
# yamlPath = r"D:\code\pyhton\calCase\jituance\config\mx_interface.yaml"




recordEnum = {
            "mltContractEle": "中长期合同电力",
            "mltContractPrice": "中长期合同电价",
            "daClearEle" : "日前电量",
            "daClearPrice" : "日前电价",
            "rtClearEle" : "实时电量",
            "rtClearPrice" : "实时电价",
            "rtPowerEle": "实际电力",
            "rtPowerPrice": "实际电价",
            "runCapacity" : "运行容量",
            "variableCost" : "变动成本",
        }

class Jituance:

    def __init__(self, session, yamlData, type):
        self.domain = None
        self.loginInfo = None
        self.yamlData = yamlData
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

    #获取变动成本
    def getCost(self, startDate, endDate, fireUrl, userInfo):

        session = requests.Session()

        fire_hn = Fire(session, self.yamlData, "hn")
        # 如果没有火电应用
        if fireUrl == "":
            return  []

        res = fire_hn.execProvinceInfo(startDate, endDate, fireUrl, userInfo)
        # res = []
        session.close()

        return res

    # 请求省间的私有数据
    def resquestProvincePrivateData(self,startDate,endDate, url, terminalList):

        mapEnum = {
            "DAEle" : ["日前电量","daClearEle"],
            "DAPrice" : ["日前电价","daClearPrice"],
            "INEle" : ["实时电量","rtClearEle"],
            "INPrice" : ["实时电价","rtClearPrice"],
        }

        method = "GET"

        # 请求url
        resquestUrl = self.domain + url


        terminalDict = {}
        '''
        terminalDict  用于记录所有该省份所有企业的所有机组的数据, 格式如下

            {
                “机组id”：{
                        "机组名":  unitName  ,
                        "企业名":  terminalName  ,
                        “日期”：{
                            "daClearEle":[],
                            "daClearPrice":[],
                            "rtClearEle":[],
                            "rtClearPrice":[],
                            "runCapacity":[],
                            "variableCost":[],
                        }
                    }
            }

        '''

        for terminal in terminalList:

            for unit in terminal[1]:

                param = {
                    "startDate": startDate,
                    "endDate": endDate,
                    "unitIds": unit['unitId'],
                }

                # 发起请求
                res = CommonClass.execRequest(self.session, method=method, url=resquestUrl, params=param).json()
                # print(res)

                # 初始化数据
                terminalDict.update( self.createEmptyData(startDate,endDate,terminal,unit) )

                # 如果日期范围内都没有数据， 接口会返回 [] ，即长度为0 ，此时跳过
                if len(res['data']) == 0:
                    continue

                dateData = terminalDict[unit['unitId']]["dateData"]

                for r in res['data']:

                    # 截取日期，截取后的格式： YYYY-MM-DD
                    datestr = r['date'][0:10]

                    # 获取该条数据是日前还是日内的
                    typeName = r['marketType']

                    # 获取电量
                    dateData[datestr][mapEnum[typeName + "Ele"][1]] = r['ele']['data']
                    # 获取电价
                    dateData[datestr][mapEnum[typeName + "Price"][1]] = r['price']['data']

                    # 获取运行容量
                    if typeName == "IN":
                        calRunCapPower = []

                        # 判断运行容量
                        if unit["capacity"] is not None :

                            if r['ele']['data'] != []:

                                for d in r['ele']['data']:
                                    if d is None:
                                        calRunCapPower.append(d)
                                        continue
                                    if d >= (unit['capacity'] * 0.05):
                                        calRunCapPower.append(unit['capacity'])
                                    else:
                                        calRunCapPower.append(0)

                        dateData[datestr]["runCapacity"] = calRunCapPower
        return terminalDict

    # 请求蒙西省内的私有数据
    def resquestMXInPrivateData(self, startDate, endDate, url, terminalList):

        method = "GET"

        mapEnum = {
            "fittingPower": ["中长期合同电力", "mltContractEle"],
            "dayAheadClearingPower": ["日前出清电力", "daClearEle"],
            "realTimeClearingPower": ["实时出清电力", "rtClearEle"],
            "actualMeasuredPower": ["实际计量电力", "rtPowerEle"],
            "fittingPrice": ["中长期合同电价", "mltContractPrice"],
            "realTimeClearingPrice": ["实时出清电价", "rtClearPrice"],
        }

        # 请求url
        resquestUrl = self.domain + url

        terminalDict = {}

        for terminal in terminalList:

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

                # 初始化数据
                terminalDict.update(self.createEmptyData(startDate, endDate, terminal, unit))

                # 如果日期范围内都没有数据， 接口会返回 [] ，即长度为0 ，此时跳过
                if len(res['data']) == 0:
                    continue

                # datesDict  记录单个机组每一天的私有数据
                dateData = terminalDict[unit['unitId']]["dateData"]

                for r in res['data']:

                    # 截取日期，截取后的格式： YYYY-MM-DD
                    datestr = r['date'][0:10]

                    for key in mapEnum:
                        if "Power" in key:
                            dateData[datestr][mapEnum[key][1]] = [ d/4 if d is not None else None for d in r[key]]
                        else:
                            dateData[datestr][mapEnum[key][1]] = r[key]

                    # 判断运行容量
                    if unit["capacity"] is not None:

                        calRunCapPower = []
                        if r["realTimeClearingPower"] != []:

                            for d in r["realTimeClearingPower"]:
                                if d is None:
                                    calRunCapPower.append(d)
                                    continue

                                if d >= (unit['capacity'] * 0.05):
                                    calRunCapPower.append(unit['capacity'])
                                else:
                                    calRunCapPower.append(0)

                        dateData[datestr]["runCapacity"] = calRunCapPower

        return terminalDict

    # 初始化空的私有数据
    def createEmptyData(self, startDate, endDate, terminal, unit):

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        dataDict = {}

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            dataDict[dateStr] = {}

            for key in recordEnum:
                dataDict[dateStr][key] = []

            # 日期 +1
            sd += timedelta(days=1)

        return {
            unit['unitId'] :  {
                "dateData" : dataDict,
                "unitName": unit['unitName'],
                "terminalName": terminal[0],
                "capacity": unit['capacity'],
                "businessType": unit['businessType']
            }
        }

    # 请求华能的交易数据
    def getHuanengOuputData(self, startDate, endDate, provinceIds, queryType):


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

            if queryType == "省内":
                # 省内新能源
                responseData.extend(res['data'][0]['inNewProvinceTradeDOS'])
                # 省内其他类型
                responseData.extend(res['data'][0]['inProvinceTradeDOS'])

            elif queryType == "省间":
                # 省间新能源
                responseData.extend(res['data'][0]['newProvinceTradeDOS'])
                # 省间其他类型
                responseData.extend(res['data'][0]['provinceTradeDOS'])

            sd = d2 + timedelta(days=1)

        terminalDict = {}

        for rd in responseData:

            datestr = rd['date'][0:10]

            for dtd in rd['dataTradeDOS']:
                if dtd['id'] not in terminalDict:
                    terminalDict[dtd['id']] = {}
                    terminalDict[dtd['id']]['dateData'] = {}

                tempDict = {}

                for key in recordEnum:
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

    # 比较私有数据和华能集团侧的数据
    def compare(self, provincePrivteData, huanengOutputData, compareStatus):

        # enum = {
        #     "mltContractEle": "中长期合同电力",
        #     "mltContractPrice": "中长期合同电价",
        #     "daClearEle" : "日前电量",
        #     "daClearPrice" : "日前电价",
        #     "rtClearEle" : "实时电量",
        #     "rtClearPrice" : "实时电价",
        #     "rtClearPrice": "实时电价",
        #     "rtPowerEle": "实际电力",
        #     "runCapacity" : "运行容量",
        #     "variableCost" : "变动成本",
        # }

        enum = recordEnum

        # 省间系统无场站时，即 provincePrivteData = {}
        if provincePrivteData == {} :
            compareStatus['provinceUnit'] .append(
                {
                    "info" : "省的系统无场站"
                }
            )

        for p in provincePrivteData:

            provinceDateDatass = provincePrivteData[p]['dateData']

            for date in provinceDateDatass:
                provinceOneDateData = provinceDateDatass[date]

                for item in provinceOneDateData:

                    if len(provinceOneDateData[item]) == 0:
                        if (item == "variableCost") and (provincePrivteData[p]['businessType'] != "FIRE" ):
                            continue

                        compareStatus['uploadStatus'].append({
                            "info": "该机组该日的的 【"+enum[item] +"】 数据未设置",
                            "unitId": p,
                            "date": date,
                            "type": enum[item],
                            "provinceUnitName": provincePrivteData[p]["unitName"],
                            "provinceTerminalName": provincePrivteData[p]["terminalName"],
                        })

                        continue


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

                haveDataInfo = "=====且省有数据" if haveData else "省没有数据"

                print("=================华能没有该机组"+ p)
                compareStatus['unitMiss'].append( {
                    "info" : "该机组只有省系统有，集团侧没有找到该机组" + haveDataInfo,
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
                        "info": "该机组的省系统和华能集团侧的名称不一致",
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
                        "info": "该机组所在的电厂的省的系统和华能集团侧的名称不一致",
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
                                "info": "该机组的 【"+enum[item] +"】 省的数据为空，集团侧数据不为空",
                                "unitId": p,
                                "date": date,
                                "type": enum[item],
                                "num": "无",
                                "provinceData": "无",
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
                                "info": "该机组的 【"+enum[item] +"】 集团侧数据为空，省的数据不为空",
                                "unitId": p,
                                "date": date,
                                "type": enum[item],
                                "num": "无",
                                "provinceData": str(provinceOneDateData[item]),
                                "huanengData": "无",
                                "provinceUnitName": provincePrivteData[p]["unitName"],
                                "huanengUnitName": huanengOutputData[p]['unitName'],
                                "provinceTerminalName": provincePrivteData[p]["terminalName"],
                                "huanengTerminalName": huanengOutputData[p]['terminalName']
                            })
                            pass

                        continue

                    # 判断每个时刻点数据是否一致
                    for i in range(0, len(provinceOneDateData[item])):
                        pDecimalData = provinceOneDateData[item][i]
                        hDecimalData = huanengOneDateData[item][i]
                        print(pDecimalData)
                        print(hDecimalData)
                        if (pDecimalData is None) and (hDecimalData is None):

                            continue
                        elif (pDecimalData is None) or (hDecimalData is None):
                            pass

                        else:

                            pDecimalData = Decimal(str(provinceOneDateData[item][i]))
                            pDecimalData = pDecimalData.quantize(Decimal("0.00"), rounding="ROUND_HALF_UP")

                            hDecimalData = Decimal(str(huanengOneDateData[item][i])).quantize(Decimal("0.00"),
                                                                                              rounding="ROUND_HALF_UP")

                            # 如果时刻点的数据一样则跳过
                            if (pDecimalData - hDecimalData).copy_abs() <= Decimal("0.01"):
                                # print("数据正确。日期：" + date + "。 机组：" +  provincePrivteData[p]["unitName"] + "。类型 " + enum[item])
                                continue

                        print("=======================================数据错误")

                        # 如果时刻点的数据不一样，则记录错误
                        compareStatus['dataCompare'].append({
                            "info": "该机组" + date + " 的 【" + enum[item] + "】 不一致",
                            "unitId": p,
                            "date": date,
                            "type": enum[item],
                            "num": i + 1,
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
                    "info": "该机组只有集团侧有，省的系统没有找到该机组。" + haveDataInfo,
                    "unitId": h,
                    "provinceUnitName": "",
                    "provinceTerminalName": "",
                    "huanengUnitName": huanengOutputData[h]["unitName"],
                    "huanengTerminalName": huanengOutputData[h]["terminalName"]
                })




        pass

    # 输出执行结果
    def outAllCompareStatus(self, allProvinceCompareStatus , queryType):
        enum = {
            "dataCompare": "数据比较表",
            "unitMiss": "机组缺失表",
            "nameCompare": "机组和企业名称比较表",
            "provinceUnit": "是否有机组",
            "uploadStatus": "上传情况表",
        }

        a = {
            "head" : ["省份","数据错误机组个数","机组缺失个数","机组和企业名称不一致个数","是否有机组",]
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
            savePath = "D:\code\python\calCase\jituance\output\\"+  queryType +  "比较情况导出\\" + enum[type] + ".xlsx"
            e.saveFile(savePath)
            e.close()

        e = ExcelHepler()
        e.outALL(a)
        savePath = "D:\code\python\calCase\jituance\output\\"+  queryType +  "比较情况导出\汇总.xlsx"
        e.saveFile(savePath)
        e.close()

        pass

        # pass

    # 执行入口
    def execProvinceInfo(self, startDate,endDate,info):

        # 记录所有省份的比较结果
        allProvinceCompareStatus = {}

        # 记录数据不一致的省份
        errorProvince = []

        for queryType in info:

            provinceInfo = info[queryType]

            for province in provinceInfo:

                cost = self.getCost(startDate, endDate, province['fireUrl'], province['userInfo'])
                # cost = []
                # print(cost)
                print("==========获取变动成本正常")

                CommonClass.switchTenantId(self.session,self.domain,province['tenantId'])
                print("===========当前省份为：" ,province['provinceName'])

                # 每个省份的获取机组的url
                getUnitUrl = ""
                if queryType == "省内":
                    getUnitUrl = province["url"] + "/fire/api/org/org/tree"
                elif queryType == "省间":
                    getUnitUrl = province["url"] + "/api/org/org/tree"

                # 获取该省份的机组信息
                terminalList = self.getUnitId(getUnitUrl)
                # print(terminalList)
                print("==========获取机组正常")

                privteData = {}

                if queryType == "省内":
                    resquestPrivateDataUrl = province["url"] + province["privateUrl"]
                    privteData = getattr(self, province["privateMethodName"] )(startDate,endDate,resquestPrivateDataUrl, terminalList)

                elif queryType == "省间":

                    # 每个省份的获取私有数据的url
                    resquestPrivateDataUrl = province["url"] + "/api/province/clearing/result/list"
                    # 获取省间私有数据
                    privteData = self.resquestProvincePrivateData(startDate,endDate,resquestPrivateDataUrl, terminalList)
                    print("==========获取私有数据正常")

                CommonClass.updateKey(privteData, cost, "variableCost")

                # 记录华能集团返回的数据
                huanengOutputData = self.getHuanengOuputData(startDate,endDate, province["provinceIds"],queryType)
                # print(huanengOutputData)
                print("==========获取华能数据正常")

                compareStatus = {
                    "provinceUnit" : [],
                    "unitMiss" :[] ,
                    "nameCompare" : [],
                    "dataCompare" : [],
                    "uploadStatus" : [],
                }

                self.getUnitInfo(terminalList,compareStatus)
                # self.compare(privteData,huanengOutputData, compareStatus)

                if len(compareStatus["dataCompare"]) != 0:
                    errorProvince.append(province['provinceName'])

                allProvinceCompareStatus[province["provinceName"]] = compareStatus

            self.outAllCompareStatus(allProvinceCompareStatus,queryType)

            print(queryType, "数据不一致的省份： ", errorProvince)


    # 判断机组装机容量
    def getUnitInfo(self, terminalList , compareStatus):

        for terminal in terminalList:

            terminalName = terminal[0]
            unitList = terminal[1]

            for unit in unitList:

                if unit['capacity'] == None:


                    compareStatus['uploadStatus'].append({
                        "info": "该机组的 【装机容量】 数据未设置",
                        "unitId": unit['unitId'],
                        "type": "装机容量",
                        "provinceUnitName": unit["unitName"],
                        "provinceTerminalName": terminalName,
                    })



if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    jtc_hn = Jituance(testSession, yamlData, "hn")

    jtc_hn.login()

    province = [

        {"provinceName": "青海", "url": "/qinghaigroup", "provinceIds": 63,
         "tenantId":  "e4f35ef0861bd6020186a6938ab216dd" , "fireUrl" : "/qinghaifire" ,
         "userInfo":[ {"username": "qh-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "四川", "url": "/sichuangroup", "provinceIds": 51,
         "tenantId":  "e4f8c059825cddf50183459ebc7223eb" , "fireUrl" : "/sichuanfire",
         "userInfo":[ {"username": "sc-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "西藏", "url": "/xizanggroup", "provinceIds": 54,
         "tenantId": "e4f35ef0861bd6020186a6d3483718ba"  , "fireUrl" : "" ,
         "userInfo":[ {"username": "","password": ""} ,]
         },
        {"provinceName": "天津", "url": "/tianjingroup", "provinceIds": 12,
         "tenantId": "e4f8c059825cddf5018345ad48fc2451"  , "fireUrl" : "/tianjinfire" ,
         "userInfo":[ {"username": "tj-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "蒙东", "url": "/mengdonggroup", "provinceIds": 150,
         "tenantId":  "e4f8c059825cddf50183459e32ae23e9" , "fireUrl" : "/mengdongfire" ,
         "userInfo":[ {"username": "md-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "宁夏", "url": "/ningxiagroup", "provinceIds": 64,
         "tenantId":  "e4f8c059825cddf5018345af600e2462" , "fireUrl" : "/ningxiafire" ,
         "userInfo":[ {"username": "nx-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "新疆", "url": "/xinjianggroup", "provinceIds": 65,
         "tenantId":  "e4f35ef0861bd6020186a6c8bed0182d" , "fireUrl" : "/xinjiangfire" ,
         "userInfo":[ {"username": "xj-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "蒙西", "url": "/mengxigroup", "provinceIds": 15,
         "tenantId":  "e4d20ccb81bcf0170181cbebbaec01c3" , "fireUrl" : "/mxfire" ,
         "userInfo":[ {"username": "mx-test","password": "qinghua123@"} ,]
         },

        {"provinceName": "河北", "url": "/hebeigroup", "provinceIds": 13,
         "tenantId":  "e4f8c059825cddf5018345a768bd2431" , "fireUrl" : "/hebeifire" ,
         "userInfo":[ {"username": "hb-test","password": "qinghua123@"} ,]
         },
        # {"provinceName": "甘肃", "url": "/gansugroup", "provinceIds": 62,
        #  "tenantId":  "e4f8c059825cddf50183630233c82afc" , "fireUrl" : "/gansufire" ,
        #  "userInfo":[ {"username": "gs-test","password": "qinghua123@"} ,]
        #  },
        {"provinceName": "辽宁", "url": "/liaoninggroup", "provinceIds": 21,
         "tenantId":  "e4f8c059825cddf5018345b24f912483" , "fireUrl" : "/lnfire" ,
         "userInfo":[ {"username": "ln-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "吉林", "url": "/standardgroup", "provinceIds": 22,
         "tenantId":  "e4f8c059825cddf50183459bd6aa23e6" , "fireUrl" : "/standardfire" ,
         "userInfo":[ {"username": "jl-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "黑龙江", "url": "/heilongjianggroup", "provinceIds": 23,
         "tenantId":  "e4f35ef0861bd6020186a6c6792c1824" , "fireUrl" : "/heilongjiangfire" ,
         "userInfo":[ {"username": "hlj-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "陕西", "url": "/shan_xigroup", "provinceIds": 61,
         "tenantId":  "e4f8c059825cddf50183459b042523e3" , "fireUrl" : "/shan_xifire" ,
         "userInfo":[ {"username": "shanxi-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "山西", "url": "/shanxigroup", "provinceIds": 14,
         "tenantId":  "e4f8c059825cddf5018345b0c5652472" , "fireUrl" : "/shanxifire" ,
         "userInfo":[ {"username": "sx-test","password": "qinghua123@"} ,]
         },
        {"provinceName": "福建", "url": "/fujiangroup", "provinceIds": 35,
         "tenantId":  "e4f8c059825cddf50183d52654403d29" , "fireUrl" : "/fujianfire" ,
         "userInfo":[ {"username": "fj-test","password": "qinghua123@"} ,]
         },



    ]

    provinceIn = [
        {"provinceName": "蒙西", "url": "/mxgroup", "provinceIds": 15,
         "tenantId":  "e4d20ccb81bcf0170181cbebbaec01c3" , "fireUrl" : "/mxfire" ,
         "privateUrl" :  "/fire/api/mx/data/analysis/clearing" , "privateMethodName" : "resquestMXInPrivateData",
         "userInfo":[ {"username": "mx-test","password": "qinghua123@"} ,]
         },
    ]

    info = {
        # "省内" : provinceIn,
        "省间" : province,
    }

    # startDate = "2023-04-27"
    # endDate = "2023-05-03"

    startDate = "2023-05-23"
    endDate = "2023-05-23"



    jtc_hn.execProvinceInfo(startDate,endDate,info)

