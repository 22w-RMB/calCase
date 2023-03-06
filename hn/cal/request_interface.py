import requests

from common.common import CommonClass
from hn.cal.generate_data import *

yamlPath = r"D:\code\python\calCase\hn\config\hn_interface.yaml"



class Henan:

    def __init__(self,session, yamlData, type):
        self.domain = None
        self.loginInfo = None
        self.session = session
        self.provinceId = "41"
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

        url = self.domain + "/hnfire/api/unit/basic"
        method = "POST"
        for unit in unitsInfo:
            data = {
               "businessType": unit['businessType'],
               "isNew":   True,
               "edit": True,
               "provinceId": self.provinceId,
               "unitName": unit['unitName'],
            }
            print(data)
            # CommonClass.execRequest(self.session,method=method,url=url,data=data)
        pass

    def getFireUnit(self):
        url = self.domain + "/hnfire/api/org/org/tree"
        method = "GET"
        res = CommonClass.execRequest(self.session, method=method, url=url).json()['data']
        unitsInfo = []

        for r in res[0]['children']:
            unitsInfo.append(
                {
                    "unitId" : r['unitId'],
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

            url = self.domain + "/hnfire/api/unit/basic/" +  unit['unitId']

            res = CommonClass.execRequest(self.session, method=method, url=url).json()
            print(res)

        pass

if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    hn_test = Henan(testSession,yamlData,"test")

    hn_test.login()

    hn_test.createUnit(generateUnit(4,"华苏"))
    # hn_test.getFireUnit()
    hn_test.deleteUnit(filterUnits=['开封#1','开封#2','开封#3'])