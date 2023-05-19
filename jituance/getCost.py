import datetime
import time

import requests
import json
from datetime import datetime,timedelta

from common.common import CommonClass
from excel_handler import ExcelHepler

yamlPath = r"D:\code\python\calCase\jituance\config\mx_interface.yaml"
# yamlPath = r"D:\code\pyhton\calCase\jituance\config\mx_interface.yaml"


class Fire:

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

    def login(self,username,password):

        # 登录
        CommonClass.loginUseNameAndPass(self.session, self.domain, self.loginInfo,username,password)

        # 获取所有企业
        getApplicationUrl = self.domain + "/usercenter/web/pf/tenant/user/application"

        resJson = CommonClass.execRequest(session=self.session,method="GET",url=getApplicationUrl).json()

        resData = resJson['data']

        userTenant = []

        for d in resData:

            tenantId = d['tenantId']
            terminalName = d['name']

            resApp = d['applications']

            for app in resApp:
                if "公司交易辅助决策系统" in app['name']:
                    print("===========", terminalName)

                    userTenant.append(
                        {
                            "tenantId": tenantId,
                            "terminalName": terminalName
                        }
                    )

                    break

        return userTenant

    def getCost(self,userTenant,provinceUrl,startDate,endDate):

        res = {}
        for ut in userTenant:

            CommonClass.switchTenantId(self.session,self.domain,ut['tenantId'])

            unitsInfo = self.getFireUnitData(ut['terminalName'],provinceUrl)
            for unit in unitsInfo:
                if unit["businessType"]  == "FIRE":
                    res.update(
                        self.getFireCostData(provinceUrl, unit['unitId'], startDate, endDate)
                    )

        return res

    def getFireUnitData(self,terminalName,provinceUrl):
        # 发起机组请求

        getUnitUrl = self.domain + provinceUrl +"/api/unit/list"
        unitResJson = CommonClass.execRequest(self.session,method="GET",url=getUnitUrl).json()

        unitInfo = []

        for data in unitResJson['data']:

            unitInfo.append(
                {
                    "unitId" : data["id"],
                    "unitName" : data["unitName"],
                    "capacity" : data["capacity"],
                    "terminalName" : terminalName,
                    "businessType" : data["businessType"]
                }
            )

        # print(unitInfo)
        return unitInfo



    def getFireCostData(self,provinceUrl,unitId,startDate,endDate):


        getCostUrl = self.domain + provinceUrl +"/api/unit/cost/list"

        param = {
            "unitIds":[unitId],
            "typeList": ["DYNAMIC_COST"]
        }


        costList = []

        costResJson = CommonClass.execRequest(self.session,method="GET",url=getCostUrl,params=param).json()

        # print(costResJson)

        for data in costResJson['data']:
            unitVarCost = data['unitVarCost']
            costType = unitVarCost['costType']

            if costType == "DYNAMIC_COST":
                costList.append(
                    {
                        "effectiveDate" : unitVarCost["effectiveDate"]  ,
                        "value": unitVarCost["value"]
                    }
                )
            pass

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        resCostList = {}

        while sd <= ed:

            tmpDate = datetime.strptime("2000-01-01", "%Y-%m-%d")
            d1Str = datetime.strftime(sd, "%Y-%m-%d")
            resCostList[d1Str] = {}

            tempCost = ""
            for cost in costList:

                d = datetime.strptime(cost['effectiveDate'],"%Y-%m-%d")
                if d > sd:
                    continue

                if d >= tmpDate:
                    tmpDate = d
                    tempCost = cost['value']

            dateCost = []
            if tempCost != "":
                dateCost = [float(tempCost) for i in range(0,96)]

            resCostList[d1Str]['variableCost'] = dateCost


            sd += timedelta(days=1)

        return {
            unitId : {
                "dateData" : resCostList
            }
        }



    def getLoginInfo(self):

        '''
           {
                省份：{
                    “username”:
                    "password"
                }
           }

        :return:
        '''



    def execProvinceInfo(self, startDate,endDate,fireUrl,userInfo):


            userInfo = [
                {
                    "username": "mx-test",
                    "password": "qinghua123@"
                }
            ]
            unitCostList = {}

            for user in userInfo:

                userTenant = self.login(user['username'],user['password'])
                unitCostList.update(
                    self.getCost(userTenant, fireUrl, startDate, endDate)
                )

            return unitCostList


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    jtc_hn = Fire(testSession, yamlData, "hn")

    startDate = "2023-04-21"
    endDate = "2023-04-21"

    res = jtc_hn.execProvinceInfo(startDate,endDate,"/mxfire",[])
    print(res)


    # jtc_hn.execProvinceInfo(startDate,endDate,provinceInfo)