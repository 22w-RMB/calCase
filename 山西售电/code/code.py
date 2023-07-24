import os

import requests

from common.common import CommonClass


yamlPath = r"D:\code\python\calCase\山西售电\config\山西售电_interface.yaml"



class ShanxiShoudian:

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


    def importData(self):

        for root,dirs,files in os.walk(r"D:\code\python\calCase\山西售电\file\实时出清电量"):

            if files == []:
                continue

            for file in files:

                # 日前出清电量处理

                # dateStr = file.replace("日前申报电量","").replace(".xlsx","")
                # date = dateStr[:4] + "-" + dateStr[4:6] + "-" + dateStr[6:]+ " 00:00:00"
                # print(date)

                # 实时出清电量处理
                dateStr = file.replace("实时出清电量","").replace(".xlsx","")
                date = dateStr + " 00:00:00"
                print(date)

                filePath = os.path.join(root,file)
                print(filePath)

                fileList = []
                fileList.append(
                    ("file", (file,
                               open(os.path.join(filePath), "rb"))
                     )
                )

                importDatas = [

                    ("provinceAreaId", (None, "014")),
                    ("dataType", (None, "TRADE_RESULT")),
                    ("date", (None, date)),
                ]

                importDatas.extend(fileList)

                print(importDatas)

                url = self.domain + "/sxpdtas/api/data/import/single"

                # 发起请求
                importRes = CommonClass.execRequest(self.session,method="post", url=url, files=importDatas)

                print(importDatas)
                print(importRes.json())


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    test = ShanxiShoudian(testSession,yamlData,"test")





