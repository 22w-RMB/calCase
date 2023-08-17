import time
from datetime import timedelta

from cal import queryDataT
from cal import queryDataPeak
import requests
from common.common import CommonClass


configyamlPath = CommonClass.mkDir("河北","config","hb_interface.yaml",isGetStr=True)



class Hebei:

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


    def createTData(self):

        url = self.domain+"/datacenter/hb/api/mlt/config/setting/t"

        dataT = queryDataT()

        for date in dataT:

            for t in dataT[date]:
                d = dataT[date][t]
                requestParam = {
                     "createTime": "2023-08-17 23:26:09",
                     "ifSplit": 0 if d["haveRatio"] == False else 1 ,
                     "periodName": t,
                     "periodNon": d["time"],
                     "splitRatio": [d["ratio"]["tip"] , d["ratio"]["peak"], d["ratio"]["flat"], d["ratio"]["valley"]],
                     "startRunDate": date,
                     "updateTime": "2023-08-17 23:26:09"
                }
                # print(requestParam)

                res = CommonClass.execRequest(self.session,method="POST",url=url,json=requestParam).json()
                print(res)

        pass

    def createPeak(self):

        url = self.domain + "/datacenter/hb/api/mlt/config/setting/ppv"

        peakEnum = {
            "tip" : 0,
            "peak" : 1,
            "flat" : 2,
            "valley" : 3,
        }

        dataT = queryDataPeak()


        for date in dataT:
            requestParam = []
            i = 1
            for peakD in dataT[date]:
                for timeData in  dataT[date][peakD]:
                    requestParam.append(
                        {
                            "startRunDate": date + "-01",
                            "startTime": timeData[:5],
                            "endTime": timeData[6:],
                            "type": peakEnum[peakD],
                            "periodOrder": i
                        }
                    )

                    i += 1

            print(requestParam)
            res = CommonClass.execRequest(self.session, method="POST", url=url, json=requestParam).json()
            print(res)

        pass



if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(configyamlPath)

    hebei_test = Hebei(testSession,yamlData,"test")

    hebei_test.login()
    # hebei_test.createTData()
    hebei_test.createPeak()



