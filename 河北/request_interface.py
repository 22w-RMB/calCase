from threading import Thread

from cal import queryDataT
from cal import queryDataPeak
import requests
from common.common import CommonClass
from datetime import datetime

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

    def deleteT(self):

        qeuryUrl = self.domain + "/datacenter/hb/api/mlt/config/query/t"
        qeuryParam = {
            "startDate":"2023-01",
            "endDate": "2023-12",
        }
        # print(requestParam)

        qeuryRes = CommonClass.execRequest(self.session, method="GET", url=qeuryUrl, params=qeuryParam).json()
        print(qeuryRes)

        deleteUrl = self.domain + "/datacenter/hb/api/mlt/config/delete/t"

        for res in qeuryRes["data"]:

            deleteParam = {
                "id" : res['id']
            }

            deleteRes = CommonClass.execRequest(self.session, method="Delete", url=deleteUrl, params=deleteParam).json()
            print(deleteRes)

    def deleteCalendar(self):
        qeuryUrl = self.domain + "/datacenter/hb/api/mlt/trade/calendar/data"

        monthList = [
            "2023-01",
            "2023-02",
            "2023-03",
            "2023-04",
            "2023-05",
            "2023-06",
            "2023-07",
            "2023-08",
            "2023-09",
            "2023-10",
            "2023-11",
            "2023-12",
            ]

        for month in monthList:


            qeuryParam = {
                "month": month,
                "provinceAreaId": "013",
            }
            # print(requestParam)

            qeuryRes = CommonClass.execRequest(self.session, method="GET", url=qeuryUrl, params=qeuryParam).json()
            print(qeuryRes)

            deleteUrl = self.domain + "/datacenter/hb/api/mlt/trade/calendar/delete"

            for res in qeuryRes["data"]:
                deleteParam = {
                    "id": res['id']
                }

                deleteRes = CommonClass.execRequest(self.session, method="Delete", url=deleteUrl, params=deleteParam).json()
                print(deleteRes)


    def queryContractTarget(self,name):
        url = self.domain +"/hbgroup/fire/api/mlt/data/holding"

        params = {"startDate":"2023-01-01","endDate":"2023-12-31","unitIds":None,"dataDimensions":2,"conTractTradeTypeList":["1","2","3","4","5","6","7","8","9","10"]}

        print("=====",name,"开始执行...","\n",end='')
        res = CommonClass.execRequest(self.session,method="POST",url=url,json=params).json()["retCode"]
        print(name,"接口返回：",res ,"\n",end='')
        print(name," 时间：", datetime.now(),"\n",end='')
        print("=====", name, "执行完成...","\n",end='')


    def queryContractOverviewData(self,name):
        url = self.domain +"/hbgroup/fire/api/mlt/data/mltData"

        params = {"startDate":"2023-01-01","endDate":"2023-12-31","unitIds":["e4d4edc48a1cbf90018a1d6919b60000","e4d4edc48a1cbf90018a1d692fb70001","e4d4edc48a1cbf90018a1d693fa90002","e4d4edc48a1cbf90018a1d69505b0003","e4d4edc48a1cbf90018a1d6963ab0004","e4d4edc48a1cbf90018a1d697d280005","e4dc742088fc4a6a0188ff9dfb0700d2","e4fd338b896d7205018970df89d1001e","e4fd338b896d7205018970dfb8e8001f","e4d4ed8f8980a31a018985726dba0000","e4dc742b896cfc3c01896d2e4d300002","e4dc74cf89912d990189b07da49e0001","e4dc74cf89912d990189b0813b6c0003","e4dc74f289c8acd30189fd12b63f0012","e4fd338b896d7205018970e1bbd20020","e4fd338b896d72050189713d65db0061","e4fd338b896d72050189713d91fd0062","e4fd338b896d72050189713db5be0063"]}

        print("=====",name,"开始执行...","\n",end='')
        res = CommonClass.execRequest(self.session,method="POST",url=url,json=params).json()["retCode"]
        print(name,"接口返回：",res ,"\n",end='')
        print(name," 时间：", datetime.now(),"\n",end='')
        print("=====", name, "执行完成...","\n",end='')



if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(configyamlPath)

    hebei_test = Hebei(testSession,yamlData,"test")

    hebei_test.login()
    # hebei_test.createPeak()
    # hebei_test.deleteT()
    # hebei_test.createTData()

    # hebei_test.deleteCalendar()

    threadList = []

    queryContractOverviewDataNum = 1
    for i in range(0, queryContractOverviewDataNum):
        threadList.append(Thread(target=hebei_test.queryContractOverviewData, args=("【持仓总览详细数据查询】线程" + str(i),)))

    queryContractOverviewTargetNum = 1
    for i in range(0, queryContractOverviewTargetNum):
        threadList.append(Thread(target=hebei_test.queryContractTarget, args=("【持仓总览指标查询】线程" + str(i),)))


    for i in threadList:
        i.start()

