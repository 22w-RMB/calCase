import os
import queue
import threading

import requests

from common.common import CommonClass
from hn.cal.generate_data import *

# yamlPath = r"D:\code\python\calCase\hn\config\jx_interface.yaml"
yamlPath = r"D:\code\pyhton\calCase\hn\config\hn_interface.yaml"



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


    #直接把文件夹下面的文件进行导入
    def importPrivate(self):

        url = self.domain + "/hnfire/api/hn/data/import/private/multi"
        method = "POST"

        # proxy = "106.14.255.124:80"
        # proxies = {
        #     "http": proxy,
        #     "https": proxy,
        # }

        self.session.keep_alive = False

        for root,dirs,files in os.walk(hn_out_path):
            print(root)
            print(dirs)
            print(files)
            for file in files:
                # data = {
                #    "date": "2023-03-18",
                #    "fileNames":   file,
                # }
                # fileParam = {"files":open(CommonClass.mkDir(root,file,isGetStr=True),"rb")}

                importDatas = [
                    ("date", (None, "2023-03-18")),
                    ("fileNames", (None, file)),
                    ("files", (file, open(CommonClass.mkDir(root,file,isGetStr=True),"rb")))
                ]

                print(file)
            #
                res = CommonClass.execRequest(self.session,sleepTime=2, method=method, url=url,files=importDatas).json()
                print(res)
        # pass

    def importPrivateThread(self, queue):

        url = self.domain + "/hnfire/api/hn/data/import/private/multi"
        method = "POST"

        # proxy = "106.14.255.124:80"
        # proxies = {
        #     "http": proxy,
        #     "https": proxy,
        # }

        self.session.keep_alive = False

        while True:
            data = queue.get()
            if data is None:
                print("所有文件已经导入")
                break

            importDatas = [
                ("date", (None, "2023-03-18")),
                ("fileNames", (None, data[0])),
                ("files", (data[0], open(data[1], "rb")))
            ]

            print(importDatas)
            #
            res = CommonClass.execRequest(self.session, sleepTime=2, method=method, url=url, files=importDatas).json()
            print(res)

            queue.task_done()


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    hn_test = Henan(testSession,yamlData,"test")

    hn_test.login()

    # hn_test.createUnit(generateUnit(4,"华苏"))
    unitsInfo = hn_test.getFireUnit()
    # hn_test.deleteUnit(filterUnits=['开封#1','开封#2','开封#3'])

    templateInfo = ["实时出清结果","日前出清结果","电厂实际上网电量"]
    # outputPrivateData("2023-01-01", 120, unitsInfo, templateInfo)
    # hn_test.importPrivate()

    q = queue.Queue()

    thread1 = threading.Thread(target=outputPrivateDataThread,args=("2023-01-01", 1, unitsInfo, templateInfo,q))

    thread2 = threading.Thread(target= hn_test.importPrivateThread,args=(q,))

    # 启动线程
    thread1.start()
    thread2.start()

    # 等待队列中的所有数据被处理完毕
    q.join()

    # 所有数据已处理完毕，退出程序
    print("All items processed. Exiting...")