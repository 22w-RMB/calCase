import datetime

import requests

from common.common import CommonClass

yamlPath = r"D:\code\python\calCase\jituance\config\mx_interface.yaml"


class Jituance:

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

        print(resJson)

        terminalList = []
        if len(resJson['data']) == 0:
            return terminalList

        for d in resJson['data']:
            terminalName = d['ownerId']
            unitsList = []

            for unit in d['children']:
                unitsList.append(
                    {
                        "unitId": unit['unitId'],
                        "unitName": unit['unitName'],
                    }
                )

            terminalList.append([terminalName, unitsList])

        return terminalList

    # 请求省间的私有数据
    def resquestPrivateData(self, url, terminalList, privteDataUpload):

        # 设置开始日期、结束日期
        # startDate = "2023-04-21"
        # endDate = "2023-05-03"

        startDate = "2023-05-01"
        endDate = "2023-05-02"
        method = "GET"

        # 请求url
        resquestUrl = self.domain + url

        terminalDict = {}
        '''
        terminalDict  用于记录所有该省份所有企业的所有机组的上传情况, 格式如下

            {
              “企业”：{
                    “机组”：{
                            “日期”：{
                                "DAEle":[],
                                "DAPrice":[],
                                "InEle":[],
                                "InPrice":[],
                            }
                        }
                }
            }

        '''

        for terminal in terminalList:

            # 用于记录单个企业下所有机组的数据
            unitsDict = {}

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
                    "unitIds": unit['unitId'],
                }

                # print(param)

                # 发起请求
                res = CommonClass.execRequest(self.session, method=method, url=resquestUrl, params=param).json()
                # print(res)

                # 如果日期范围内都没有数据， 接口会返回 [] ，即长度为0 ，此时跳过
                if len(res['data']) == 0:
                    privteDataUpload[terminal[0]][unit['unitName']] = startDate + " 到 " + endDate + " 这段时间没有导入数据"
                    continue

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

                    # 获取该条数据是日前还是日内的
                    typeName = r['marketType']

                    # 获取电量
                    datesDict[datestr][typeName + "Ele"] = r['ele']['data']
                    # 获取电价
                    datesDict[datestr][typeName + "price"] = r['price']['data']

                    typeStr = "日前" if typeName == "DA" else "日内"

                    # 记录每种类型的数据上传情况
                    if len(r['ele']['data']) == 0:
                        privteDataUpload[terminal[0]][unit['unitName']].append(datestr + " " + typeStr + "电量未上传")
                    if len(r['price']['data']) == 0:
                        privteDataUpload[terminal[0]][unit['unitName']].append(datestr + " " + typeStr + "电价未上传")

                unitsDict[unit['unitName']] = datesDict

            terminalDict[terminal[0]] = unitsDict

        return terminalDict

    def getHuanengOuputData(self, startDate, endDate, provinceIds):

        resquestUrl = self.domain + "/huaneng/group/api/group/private/data/query/spot/data"

        method = "GET"

        param = {
            "startDate": startDate,
            "endDate": endDate,
            "provinceIds": provinceIds,
        }

        res = CommonClass.execRequest(self.session, method=method, url=resquestUrl, params=param).json()

        terminalDict = {}
        for r in res['data'][0]['newProvinceTradeDOS']:
            if r['orgId'] not in terminalDict:
                terminalDict[r['orgId']] = {}

            datestr = r['date'][0:10]

            for d in r['dataTradeDOS']:
                if d['unitName'] not in terminalDict[r['orgId']]:
                    terminalDict[r['orgId']][d['unitName']] = {}

                terminalDict[r['orgId']][d['unitName']].update(
                    {
                        datestr: {
                            "DAEle": d['daClearEle'],
                            "DAPrice": d['daClearPrice'],
                            "INEle": d['rtClearEle'],
                            "INPrice": d['rtClearPrice'],
                        }
                    }
                )

        return terminalDict

    def execProvinceInfo(self, provinceInfo):

        # 记录所有省份的上传情况
        allProvinceDataUploadStatus = []

        for province in provinceInfo:

            # 每个省份的获取机组的url
            getUintUrl = province["url"] + "/api/org/org/tree"

            terminalList = jtc_hn.getUnitId(getUintUrl)
            # print(terminalList)

            # 判断获取机组的接口是否返回为空
            if len(terminalList) == 0:
                allProvinceDataUploadStatus.append(
                    {
                        province['provinceName']: "该省份没有场站"
                    }
                )

                continue

            # 每个省份的获取私有数据的url
            resquestPrivateDataUrl = province["url"] + "/api/province/clearing/result/list"

            provincePrivteDataUpload = {}

            terminalDataDict = jtc_hn.resquestPrivateData(resquestPrivateDataUrl, terminalList,
                                                          provincePrivteDataUpload)

            allProvinceDataUploadStatus.append(
                {
                    province['provinceName']: provincePrivteDataUpload
                }
            )

            # print(terminalDataDict)
        print(allProvinceDataUploadStatus)


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    jtc_hn = Jituance(testSession, yamlData, "hn")

    jtc_hn.login()

    provinceInfo = [

        {"provinceName": "青海", "url": "/qinghaigroup", "provinceIds": 63, },
        {"provinceName": "四川", "url": "/sichuangroup", "provinceIds": 51, },
        {"provinceName": "西藏", "url": "/xizanggroup", "provinceIds": 54, },
        {"provinceName": "天津", "url": "/tianjingroup", "provinceIds": 12, },
        {"provinceName": "蒙东", "url": "/mengdonggroup", "provinceIds": 150, },
        {"provinceName": "宁夏", "url": "/ningxiagroup", "provinceIds": 64, },
        {"provinceName": "新疆", "url": "/xinjianggroup", "provinceIds": 65, },
        {"provinceName": "蒙西", "url": "/mengxigroup", "provinceIds": 15, },

    ]

    # jtc_hn.execProvinceInfo(provinceInfo)

    res = jtc_hn.getHuanengOuputData("2023-05-01", "2023-05-02", 63)
    print(res)

    getUintUrl = "/qinghaigroup/api/org/org/tree"

    terminalList = jtc_hn.getUnitId(getUintUrl)

    # print(terminalList)

    resquestPrivateDataUrl = "/qinghaigroup/api/province/clearing/result/list"
    privteDataUpload = {}

    terminalDict = jtc_hn.resquestPrivateData(resquestPrivateDataUrl, terminalList, privteDataUpload)

    print(terminalDict)
    print(privteDataUpload)