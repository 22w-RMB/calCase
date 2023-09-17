import os
import queue
import threading

import requests

from common.common import CommonClass
from hn.cal.generate_data import *

yamlPath = r"D:\code\python\calCase\jx\config\jx_interface.yaml"
# yamlPath = r"D:\code\pyhton\calCase\jx\config\jx_interface.yaml"



class Jx:

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

    # 删除电力用户
    def deleteEleUser(self,numPerPage,totalPage):
        getUserUrl = self.domain + "/jxfire/api/customer/electricity/page"
        getUsermethod = "GET"

        deleteUrl = self.domain + "/jxfire/api/customer/electricity"
        deletemethod = "DELETE"

        eleUserList = []

        for i in range(0,totalPage):

            param = {
                "pageNum" :  i+1,
                "numPerPage" : numPerPage
            }

            res = CommonClass.execRequest(self.session,method=getUsermethod, url=getUserUrl,params=param).json()
            print(res)

            for d in res['data']['datas']:
                eleUserList.append(d['id'])


        print(eleUserList)

        for e in eleUserList:

            u = deleteUrl + "/" + e
            res = CommonClass.execRequest(self.session, method=deletemethod, url=u).json()
            print(res)

    # 删除售电公司
    def deleteES(self,numPerPage,totalPage):
        getUserUrl = self.domain + "/jxfire/api/customer/es/page"
        getUsermethod = "GET"

        deleteUrl = self.domain + "/jxfire/api/customer/es"
        deletemethod = "DELETE"

        eleUserList = []

        for i in range(0,totalPage):

            param = {
                "pageNum" :  i+1,
                "numPerPage" : numPerPage
            }

            res = CommonClass.execRequest(self.session,method=getUsermethod, url=getUserUrl,params=param).json()
            print(res)

            for d in res['data']['datas']:
                eleUserList.append(d['id'])


        print(eleUserList)

        for e in eleUserList:

            u = deleteUrl + "/" + e
            res = CommonClass.execRequest(self.session, method=deletemethod, url=u).json()
            print(res)

   # 删除发电企业
    def deleteOS(self,numPerPage,totalPage):
        getUserUrl = self.domain + "/jxfire/api/customer/os/page"
        getUsermethod = "GET"

        deleteUrl = self.domain + "/jxfire/api/customer/os"
        deletemethod = "DELETE"

        eleUserList = []

        for i in range(0,totalPage):

            param = {
                "pageNum" :  i+1,
                "numPerPage" : numPerPage
            }

            res = CommonClass.execRequest(self.session,method=getUsermethod, url=getUserUrl,params=param).json()
            print(res)

            for d in res['data']['datas']:
                eleUserList.append(d['id'])


        print(eleUserList)

        for e in eleUserList:

            u = deleteUrl + "/" + e
            res = CommonClass.execRequest(self.session, method=deletemethod, url=u).json()
            print(res)



if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    jx_test = Jx(testSession,yamlData,"hn")

    jx_test.login()

    jx_test.deleteEleUser(10,78)
    jx_test.deleteES(10,42)
    jx_test.deleteOS(10,9)
