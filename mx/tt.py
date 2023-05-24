from datetime import timedelta

import requests

from common.common import CommonClass
from generate_data import *

from threading import Thread

yamlPath = r"D:\code\python\calCase\mx\config\mx_interface.yaml"



class Mengxi:

    def __init__(self,session, yamlData, type):
        self.domain = None
        self.loginInfo = None
        self.session = session
        self.provinceId = "15"
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

    def createUnit(self,unitsInfo):

        url = self.domain + "/mxfire/api/unit/basic"
        method = "POST"
        for unit in unitsInfo:
            data = {
               "businessType": unit['businessType'],
               "isNew":   True,
               "edit": True,
               "unitName": unit['unitName'],
               "acNodeIds" : ["e4dbf97d8200200d0182007fbd0b0002"],
            }
            print(data)
            res = CommonClass.execRequest(self.session,method=method,url=url,json=data)
            print(res)
        pass

    def getFireUnit(self):
        url = self.domain + "/mxfire/api/unit/list"
        method = "GET"
        res = CommonClass.execRequest(self.session, method=method, url=url).json()['data']
        unitsInfo = []

        for r in res:
            unitsInfo.append(
                {
                    "unitId" : r['id'],
                    "unitName" : r['unitName'],
                    "businessType" : r['businessType'],
                }
            )
        return unitsInfo


    def deleteUnit(self,filterUnits=[]):

        unitsInfo = self.getFireUnit()

        method = "DELETE"
        for unit in unitsInfo:

            if unit['unitName'] in filterUnits:
                continue

            url = self.domain + "/mxfire/api/ex/unit/basic/" +  unit['unitId']

            res = CommonClass.execRequest(self.session, method=method, url=url).json()
            print(res)

        pass

    def report(self,name):

        url = self.domain +"/mxgroup/fire/api/report/template/download"

        params = {
            "templateId" :  "e4dc741e88374808018842a1260e001d"  ,
            "startDate" :   "2023-05-01",
            "endDate" :   "2023-05-15",
            "reportName" :  "2132023-05-01～2023-05-15" ,
        }
        print("=====",name,"开始执行...")
        res = CommonClass.execRequest(self.session,method="GET",url=url,params=params).json()
        print(name,"接口返回：",res)
        print("=====", name, "执行完成...")

    # 变动成本
    def createCost(self,startDate,endDate):
        url = self.domain +"/mxfire/api/unit/cost/info"

        sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            d1Str = datetime.datetime.strftime(sd, "%Y-%m-%d")


            jsonData = [
                {
                    "unitVarCost" :  {
                        "COAL_CONSUMPTION" : 4 ,
                        "COAL_UNIT_PRICE" :  4 ,
                        "DYNAMIC_COST" :  44 ,
                        "costType" : "DYNAMIC_COST" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "isNew" :   True,
                        "sourceType" :   "ENTER",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  4,
                     },
                    "unitVarCostDetailList" : [{
                        "endPower" : 444   ,
                        "functionType" :    "AX2_BX_C",
                        "segmentOrder" :  1  ,
                        "startPower" :   5 ,
                        "valueB" :   0 ,
                        "valueB" :   0 ,
                        "valueC" :   44 ,
                    }]
                },
                {
                    "unitVarCost": {
                        "COAL_CONSUMPTION": 4,
                        "COAL_UNIT_PRICE": 4,
                        "DYNAMIC_COST": 44,
                        "costType": "COAL_CONSUMPTION",
                        "edit": True,
                        "effectiveDate": d1Str,
                        "isNew": True,
                        "sourceType": "ENTER",
                        "unitId": "e4d4edd488000c700188037f49950015",
                        "value": 4,
                    },
                    "unitVarCostDetailList": [{
                        "endPower": 444,
                        "functionType": "AX2_BX_C",
                        "segmentOrder": 1,
                        "startPower": 5,
                        "valueB": 0,
                        "valueB": 0,
                        "valueC": 44,
                    }]
                },

                {
                    "unitVarCost": {
                        "COAL_CONSUMPTION": 4,
                        "COAL_UNIT_PRICE": 4,
                        "DYNAMIC_COST": 44,
                        "costType": "COAL_UNIT_PRICE",
                        "edit": True,
                        "effectiveDate": d1Str,
                        "isNew": True,
                        "sourceType": "ENTER",
                        "unitId": "e4d4edd488000c700188037f49950015",
                        "value": 4,
                    },
                     "unitVarCostDetailList" : [{
                        "endPower" : 444   ,
                        "functionType" :    "AX2_BX_C",
                        "segmentOrder" :  1  ,
                        "startPower" :   5 ,
                        "valueB" :   0 ,
                        "valueB" :   0 ,
                        "valueC" :   44 ,
                    }]
                },
            ]

            res = CommonClass.execRequest(self.session,method="POST",url=url,json=jsonData).json()
            print(res)

            sd  += timedelta(days=1)
        pass

    # 运行信息
    def createRunInfo(self,startDate,endDate):
        url = self.domain +"/mxfire/api/product/run/info"

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            d1Str = datetime.strftime(sd, "%Y-%m-%d")


            jsonData = [
                {
                    "date" : d1Str ,
                    "edit" :  False ,
                    "maxCapacity" :  444 ,
                    "maxPower" :  444 ,
                    "minPower" : 3 ,
                    "remark" :   "",
                    "unitId" :   "e4d4edd488000c700188037f49950015",
                    "unitStatus" :  "RUN" ,
                }
            ]

            res = CommonClass.execRequest(method="POST",url=url,json=jsonData).json()
            print(res)

            sd  += timedelta(days=1)

    # 调频中标
    def createWinning(self,startDate,endDate):

        url = self.domain +"/mxfire/api/unit/cost/info"

        sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            d1Str = datetime.datetime.strftime(sd, "%Y-%m-%d")


            jsonData = [
                {
                    "unitVarCost" :  {
                        "TIME_POINT_015" : 2 ,
                        "TIME_POINT_415" :  2 ,
                        "TIME_POINT_815" :  2 ,
                        "TIME_POINT_1215" :  2 ,
                        "TIME_POINT_1615" :  2 ,
                        "TIME_POINT_2015" :  2 ,
                        "costType" : "TIME_POINT_015" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "index" :   0,
                        "key" :   0,
                        "sourceType" :   "ENTER",
                        "updateTime" :   "2023-05-24 12:47:04",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  2,
                     },
                    "unitVarCostDetailList" : [{
                        "endPower" : 444   ,
                        "functionType" :    "AX2_BX_C",
                        "segmentOrder" :  1  ,
                        "startPower" :   5 ,
                        "valueB" :   0 ,
                        "valueB" :   0 ,
                        "valueC" :   2 ,
                    }]
                },
                {
                    "unitVarCost" :  {
                        "TIME_POINT_015" : 2 ,
                        "TIME_POINT_415" :  2 ,
                        "TIME_POINT_815" :  2 ,
                        "TIME_POINT_1215" :  2 ,
                        "TIME_POINT_1615" :  2 ,
                        "TIME_POINT_2015" :  2 ,
                        "costType" : "TIME_POINT_415" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "index" :   0,
                        "key" :   0,
                        "sourceType" :   "ENTER",
                        "updateTime" :   "2023-05-24 12:47:04",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  2,
                     },
                    "unitVarCostDetailList": [{
                        "endPower": 444,
                        "functionType": "AX2_BX_C",
                        "segmentOrder": 1,
                        "startPower": 5,
                        "valueB": 0,
                        "valueB": 0,
                        "valueC": 44,
                    }]
                },

                {
                    "unitVarCost" :  {
                        "TIME_POINT_015" : 2 ,
                        "TIME_POINT_415" :  2 ,
                        "TIME_POINT_815" :  2 ,
                        "TIME_POINT_1215" :  2 ,
                        "TIME_POINT_1615" :  2 ,
                        "TIME_POINT_2015" :  2 ,
                        "costType" : "TIME_POINT_815" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "index" :   0,
                        "key" :   0,
                        "sourceType" :   "ENTER",
                        "updateTime" :   "2023-05-24 12:47:04",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  2,
                     },
                     "unitVarCostDetailList" : [{
                        "endPower" : 444   ,
                        "functionType" :    "AX2_BX_C",
                        "segmentOrder" :  1  ,
                        "startPower" :   5 ,
                        "valueB" :   0 ,
                        "valueB" :   0 ,
                        "valueC" :   44 ,
                    }]
                },
                {
                    "unitVarCost" :  {
                        "TIME_POINT_015" : 2 ,
                        "TIME_POINT_415" :  2 ,
                        "TIME_POINT_815" :  2 ,
                        "TIME_POINT_1215" :  2 ,
                        "TIME_POINT_1615" :  2 ,
                        "TIME_POINT_2015" :  2 ,
                        "costType" : "TIME_POINT_1215" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "index" :   0,
                        "key" :   0,
                        "sourceType" :   "ENTER",
                        "updateTime" :   "2023-05-24 12:47:04",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  2,
                     },
                    "unitVarCostDetailList": [{
                        "endPower": 444,
                        "functionType": "AX2_BX_C",
                        "segmentOrder": 1,
                        "startPower": 5,
                        "valueB": 0,
                        "valueB": 0,
                        "valueC": 44,
                    }]
                },
                {
                    "unitVarCost" :  {
                        "TIME_POINT_015" : 2 ,
                        "TIME_POINT_415" :  2 ,
                        "TIME_POINT_815" :  2 ,
                        "TIME_POINT_1215" :  2 ,
                        "TIME_POINT_1615" :  2 ,
                        "TIME_POINT_2015" :  2 ,
                        "costType" : "TIME_POINT_1615" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "index" :   0,
                        "key" :   0,
                        "sourceType" :   "ENTER",
                        "updateTime" :   "2023-05-24 12:47:04",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  2,
                     },
                    "unitVarCostDetailList": [{
                        "endPower": 444,
                        "functionType": "AX2_BX_C",
                        "segmentOrder": 1,
                        "startPower": 5,
                        "valueB": 0,
                        "valueB": 0,
                        "valueC": 44,
                    }]
                },
                {
                    "unitVarCost" :  {
                        "TIME_POINT_015" : 2 ,
                        "TIME_POINT_415" :  2 ,
                        "TIME_POINT_815" :  2 ,
                        "TIME_POINT_1215" :  2 ,
                        "TIME_POINT_1615" :  2 ,
                        "TIME_POINT_2015" :  2 ,
                        "costType" : "TIME_POINT_2015" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "index" :   0,
                        "key" :   0,
                        "sourceType" :   "ENTER",
                        "updateTime" :   "2023-05-24 12:47:04",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  2,
                     },
                    "unitVarCostDetailList": [{
                        "endPower": 444,
                        "functionType": "AX2_BX_C",
                        "segmentOrder": 1,
                        "startPower": 5,
                        "valueB": 0,
                        "valueB": 0,
                        "valueC": 44,
                    }]
                },
            ]

            res = CommonClass.execRequest(self.session,method="POST",url=url,json=jsonData).json()
            print(res)

            sd  += timedelta(days=1)
        pass

    # 电价信息
    def createExtend(self,startDate,endDate):
        url = self.domain +"/mxfire/api/unit/extend/info"

        sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            d1Str = datetime.datetime.strftime(sd, "%Y-%m-%d")


            jsonData = [
                {
                    "unitVarParam" :  {
                        "BENCHMARK_PRICE" : "1" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "isNew" :   True,
                        "paramType" :   "BENCHMARK_PRICE",
                        "sourceType" :   "ENTER",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  "1",
                     },
                    "unitVarParamDetailList" : [{
                        "endPower" : 444   ,
                        "functionType" :    "AX2_BX_C",
                        "segmentOrder" :  1  ,
                        "startPower" :   0 ,
                        "valueB" :   0 ,
                        "valueB" :   0 ,
                        "valueC" :   "1" ,
                    }]
                },

            ]

            res = CommonClass.execRequest(self.session,method="POST",url=url,json=jsonData).json()
            print(res)

            sd  += timedelta(days=1)
        pass

    # 厂用电率
    def createChang(self,startDate,endDate):
        url = self.domain +"/mxfire/api/unit/extend/info"

        sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            d1Str = datetime.datetime.strftime(sd, "%Y-%m-%d")


            jsonData = [
                {
                    "unitVarParam" :  {
                        "ACTUAL_STATION_RATE" : "2" ,
                        "REGULAR_STATION_RATE" : "2" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "isNew" :   True,
                        "paramType" :   "REGULAR_STATION_RATE",
                        "sourceType" :   "ENTER",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  "2",
                     },
                    "unitVarParamDetailList" : [{
                        "endPower" : 444   ,
                        "functionType" :    "AX2_BX_C",
                        "segmentOrder" :  1  ,
                        "startPower" :   0 ,
                        "valueB" :   0 ,
                        "valueB" :   0 ,
                        "valueC" :   "1" ,
                    }]
                },

                {
                    "unitVarParam" :  {
                        "ACTUAL_STATION_RATE" : "2" ,
                        "REGULAR_STATION_RATE" : "2" ,
                        "edit" : True ,
                        "effectiveDate" :   d1Str,
                        "isNew" :   True,
                        "paramType" :   "ACTUAL_STATION_RATE",
                        "sourceType" :   "ENTER",
                        "unitId" :   "e4d4edd488000c700188037f49950015",
                        "value" :  "2",
                     },
                    "unitVarParamDetailList": [{
                        "endPower": 444,
                        "functionType": "AX2_BX_C",
                        "segmentOrder": 1,
                        "startPower": 0,
                        "valueB": 0,
                        "valueB": 0,
                        "valueC": "1",
                    }]
                },

            ]

            res = CommonClass.execRequest(self.session,method="POST",url=url,json=jsonData).json()
            print(res)

            sd  += timedelta(days=1)
        pass

    # 燃料情况
    def createFuel(self,startDate,endDate):
        url = self.domain +"/mxfire/api/fuel/info"

        sd = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.datetime.strptime(endDate, "%Y-%m-%d")

        while sd <= ed:
            d1Str = datetime.datetime.strftime(sd, "%Y-%m-%d")


            jsonData = [
                {
                    "date" : d1Str,
                    "economicUsabilityCoalStore" : "3" ,
                    "edit" : False ,
                    "fuelStore" : "2" ,
                    "peakCoalAvailableHour" : "4" ,

                },
            ]

            res = CommonClass.execRequest(self.session,method="POST",url=url,json=jsonData).json()
            print(res)

            sd  += timedelta(days=1)
        pass


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    mx_test = Mengxi(testSession,yamlData,"test")

    mx_test.login()
    # mx_test.createCost("2022-01-01","2024-01-02")
    # mx_test.createWinning("2022-01-01","2024-01-02")
    # mx_test.createExtend("2022-01-01","2024-01-02")
    # mx_test.createChang("2022-01-01","2024-01-02")
    mx_test.createFuel("2022-01-01","2024-01-02")

    # print(mx_test.getFireUnit())
    # d = generateUnit(60,"蒙西")
    # mx_test.createUnit(d)

    # print(mx_test.getFireUnit())
    # num = 4
    #
    # t = []
    # for i in range(0,num):
    #     t.append(Thread(target=mx_test.report, args=("线程"+str(i),)))
    #
    #
    # for i in range(0,num):
    #     t[i].start()
