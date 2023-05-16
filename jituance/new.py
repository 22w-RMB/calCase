import datetime

import requests
import json
from datetime import datetime,timedelta

from common.common import CommonClass
from excel_handler import ExcelHepler

yamlPath = r"D:\code\python\calCase\jituance\config\mx_interface.yaml"
# yamlPath = r"D:\code\pyhton\calCase\jituance\config\mx_interface.yaml"


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
                    }
                )

            terminalList.append([terminalName, unitsList])

        return terminalList

    # 请求省间的私有数据
    def resquestPrivateData(self,startDate,endDate, url, terminalList):

        # 设置开始日期、结束日期
        # startDate = "2023-04-21"
        # endDate = "2023-05-03"

        # startDate = "2023-06-01"
        # endDate = "2023-06-02"
        method = "GET"

        # 请求url
        resquestUrl = self.domain + url
        privteDataUpload = {}

        terminalDict = {}
        '''
        terminalDict  用于记录所有该省份所有企业的所有机组的上传情况, 格式如下

            {
                “机组id”：{
                        "机组名":  unitName  ,
                        "企业名":  terminalName  ,
                        “日期”：{
                            "DAEle":[],
                            "DAPrice":[],
                            "InEle":[],
                            "InPrice":[],
                        }
                    }
            }

        '''

        if len(terminalList) == 0:
            privteDataUpload
            return {
                "privteDataUpload" : "该省份没有场站",
                "terminalDict" : terminalDict,
            }

        for terminal in terminalList:

            # 用于记录单个企业下所有机组的数据
            # unitsDict = {}

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

                # terminalDict["unitName"] = unit['unitName']

                # print(param)

                # 发起请求
                res = CommonClass.execRequest(self.session, method=method, url=resquestUrl, params=param).json()
                # print(res)

                # 如果日期范围内都没有数据， 接口会返回 [] ，即长度为0 ，此时跳过
                if len(res['data']) == 0:
                    privteDataUpload[terminal[0]][unit['unitName']] = startDate + " 到 " + endDate + " 这段时间没有导入数据"

                    terminalDict.update( self.createData(startDate,endDate,terminal,unit) )

                    continue

                terminalDict[unit['unitId']] = {}
                terminalDict[unit['unitId']]["dateData"] = {}
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
                    datesDict[datestr][typeName + "Price"] = r['price']['data']

                    typeStr = "日前" if typeName == "DA" else "日内"

                    # 记录每种类型的数据上传情况
                    if len(r['ele']['data']) == 0:
                        privteDataUpload[terminal[0]][unit['unitName']].append(datestr + " " + typeStr + "电量未上传")
                    if len(r['price']['data']) == 0:
                        privteDataUpload[terminal[0]][unit['unitName']].append(datestr + " " + typeStr + "电价未上传")

                terminalDict[unit['unitId']]["dateData"] = datesDict
                terminalDict[unit['unitId']].update(
                    { "unitName" : unit['unitName'] ,
                      "terminalName":terminal[0]
                      }
                )

            # terminalDict[terminal[0]] = unitsDict

        return {
                "privteDataUpload" : privteDataUpload,
                "terminalDict" : terminalDict,
            }


    # 当省间私有数据返回为空时，构建数据
    def createData(self, startDate, endDate, terminal, unit):

        sd = datetime.strptime(startDate, "%Y-%m-%d")
        ed = datetime.strptime(endDate, "%Y-%m-%d")

        dataDict = {}

        while sd <= ed:
            dateStr = datetime.strftime(sd, "%Y-%m-%d")
            dataDict[dateStr] = {}

            dataDict[dateStr]["DAEle"] = []
            dataDict[dateStr]["DAPrice"] = []
            dataDict[dateStr]["INEle"] = []
            dataDict[dateStr]["INPrice"] = []


            # 日期 +1
            sd += timedelta(days=1)



        return {
            unit['unitId'] :  {
                "dateData" : dataDict,
                "unitName": unit['unitName'],
                "terminalName": terminal[0]
             }
        }


    # 输出省间私有数据上传状态到文件
    def outPrivateStatus(self,provinceName,privteDataUpload):

        e = ExcelHepler()
        e.newExcel(provinceName,privteDataUpload)
        savePath = "D:\code\python\calCase\jituance\output\上传状态导出\\" + provinceName + ".xlsx"

        e.saveFile(savePath)
        e.close()

        pass


    # 获取华能交易数据导出
    def getHuanengOuputData(self, startDate, endDate, provinceIds):

        CommonClass.switchTenantId(self.session,self.domain,"tsintergy")

        resquestUrl = self.domain + "/huaneng/group/api/group/private/data/query/spot/data"

        method = "GET"

        param = {
            "startDate": startDate,
            "endDate": endDate,
            "provinceIds": provinceIds,
        }

        res = CommonClass.execRequest(self.session, method=method, url=resquestUrl, params=param).json()

        terminalDict = {}

        responseData = []
        # 省间新能源
        responseData.extend(res['data'][0]['newProvinceTradeDOS'])
        # 省间其他类型
        responseData.extend(res['data'][0]['provinceTradeDOS'])


        for rd in responseData:

            datestr = rd['date'][0:10]

            for dtd in rd['dataTradeDOS']:
                if dtd['id'] not in terminalDict:
                    terminalDict[dtd['id']] = {}
                    terminalDict[dtd['id']]['dateData'] = {}

                # 记录日期数据
                terminalDict[dtd['id']]['dateData'].update(
                    {
                        datestr: {
                            "DAEle": dtd['daClearEle'],
                            "DAPrice": dtd['daClearPrice'],
                            "INEle": dtd['rtClearEle'],
                            "INPrice": dtd['rtClearPrice'],
                        },
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

    def execProvinceInfo(self, startDate,endDate,provinceInfo):

        # 记录所有省份的上传情况
        allProvinceDataUploadStatus = []

        for province in provinceInfo:

            CommonClass.switchTenantId(self.session,self.domain,province['tenantId'])

            # 每个省份的获取机组的url
            getUintUrl = province["url"] + "/api/org/org/tree"

            # 获取该省份省间的机组信息
            terminalList = self.getUnitId(getUintUrl)
            # print(terminalList)


            # 每个省份的获取私有数据的url
            resquestPrivateDataUrl = province["url"] + "/api/province/clearing/result/list"

            # 获取私有数据
            responsePrivateData = self.resquestPrivateData(startDate,endDate,resquestPrivateDataUrl, terminalList)

            # 记录省间私有数据，如果没有数据则为{}
            provincePrivteData = responsePrivateData['terminalDict']

            # 记录该省份上传的情况
            provincePrivteDataUpload = responsePrivateData['privteDataUpload']

            # 记录华能集团返回的数据
            huanengOutputData = self.getHuanengOuputData(startDate,endDate, province["provinceIds"] )

            compareStatus = {
                "provinceUnit" : [],
                "unitMiss" :[] ,
                "nameCompare" : [],
                "dataCompare" : [],
                # "shibai" : []
            }
            self.compare(provincePrivteData,huanengOutputData, compareStatus)

            print(compareStatus['unitMiss'])

            # self.outPrivateStatus( province['provinceName'],provincePrivteDataUpload)

            # print(terminalDataDict)
        # print(allProvinceDataUploadStatus)

    def compare(self, provincePrivteData, huanengOutputData, compareStatus):

        enum = {
            "DAEle" : "日前电量",
            "DAPrice" : "日前电价",
            "INEle" : "日内电量",
            "INPrice" : "日内电价",
        }

        # 省间系统无场站时，即 provincePrivteData = {}
        if provincePrivteData == {} :
            compareStatus['provinceUnit'] .append( "省间系统无场站")

        for p in provincePrivteData:

            # 判断华能有没有该机组
            if p not in huanengOutputData:
                compareStatus['unitMiss'].append( {
                    "info" : "该机组只有省间系统有，集团侧没有找到该机组" ,
                    "unitId" : p,
                    "provinceUnitName" : provincePrivteData[p]["unitName"],
                    "provinceTerminalName" : provincePrivteData[p]["terminalName"],
                } )

                continue

            # 比较机组所在的机组名称是否一致
            if provincePrivteData[p]['unitName'] != huanengOutputData[p]['unitName']:
                compareStatus['nameCompare'].append(
                    {
                        "info": "该机组的省间和华能集团侧的名称不一致",
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
                        "info": "该机组所在的电厂的省间和华能集团侧的名称不一致",
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

                        if len(provinceOneDateData[item]) == 0 :
                            # 省间为空，集团侧不为空
                            compareStatus['dataCompare'].append({
                                "info": "该机组的 【"+enum[item] +"】 省间数据为空，集团侧数据不为空",
                                "unitId": p,
                                "date": date,
                                "type": enum[item],
                                "provinceUnitName": provincePrivteData[p]["unitName"],
                                "huanengUnitName": huanengOutputData[p]['unitName'],
                                "provinceTerminalName": provincePrivteData[p]["terminalName"],
                                "huanengTerminalName": huanengOutputData[p]['terminalName']
                            })

                            pass

                        if len(huanengOneDateData[item]) == 0:
                            # 集团侧为空，省间不为空
                            compareStatus['dataCompare'].append({
                                "info": "该机组的 【"+enum[item] +"】 集团侧数据为空，省间数据不为空",
                                "unitId": p,
                                "date": date,
                                "type": enum[item],
                                "provinceUnitName": provincePrivteData[p]["unitName"],
                                "huanengUnitName": huanengOutputData[p]['unitName'],
                                "provinceTerminalName": provincePrivteData[p]["terminalName"],
                                "huanengTerminalName": huanengOutputData[p]['terminalName']
                            })
                            pass


                    # 如果数据为空则打印出来
                    # if len(provinceOneDateData[item]) == 0 :
                    #
                    #     print("数据正确。日期：" + date + "。 机组：" +
                    #     provincePrivteData[p]["unitName"] + "。类型 " + enum[item] + "为空")
                    #     pass


                    # 判断每个时刻点数据是否一致
                    for i in range(0,len(provinceOneDateData[item])):

                        # 如果时刻点的数据一样则跳过
                        if provinceOneDateData[item][i]  ==  huanengOneDateData[item][i]:
                            # print("数据正确。日期：" + date + "。 机组：" +  provincePrivteData[p]["unitName"] + "。类型 " + enum[item])
                            continue

                        print("=======================================数据错误" )

                        # 如果时刻点的数据不一样，则记录错误
                        compareStatus['dataCompare'].append({
                            "info": "该机组" + date + " 的 【"+ enum[item] +"】 不一致",
                            "unitId": p,
                            "date" : date,
                            "type" : enum[item],
                            "num" : i+1,
                            "provinceUnitName": provincePrivteData[p]["unitName"],
                            "huanengUnitName": huanengOutputData[p]['unitName'],
                            "provinceTerminalName": provincePrivteData[p]["terminalName"],
                            "huanengTerminalName": huanengOutputData[p]['terminalName']
                        })

                        break


        # 判断华能集团侧的机组在省间有没有
        for h in provincePrivteData:

            if h not in huanengOutputData:

                compareStatus['unitMiss'].append({
                    "info": "该机组只有集团侧有，省间系统没有找到该机组",
                    "unitId": p,
                    "huanengUnitName": provincePrivteData[p]["unitName"],
                    "huanengTerminalName": provincePrivteData[p]["terminalName"]
                })



        pass


if __name__ == '__main__':
    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)

    jtc_hn = Jituance(testSession, yamlData, "hn")

    jtc_hn.login()

    provinceInfo = [

        {"provinceName": "青海", "url": "/qinghaigroup", "provinceIds": 63, "tenantId":  "e4f35ef0861bd6020186a6938ab216dd" , },
        # {"provinceName": "四川", "url": "/sichuangroup", "provinceIds": 51,"tenantId":  "e4f8c059825cddf50183459ebc7223eb" , },
        # {"provinceName": "西藏", "url": "/xizanggroup", "provinceIds": 54, "tenantId": "e4f35ef0861bd6020186a6d3483718ba"  ,},
        # {"provinceName": "天津", "url": "/tianjingroup", "provinceIds": 12, "tenantId": "e4f8c059825cddf5018345ad48fc2451"  ,},
        # {"provinceName": "蒙东", "url": "/mengdonggroup", "provinceIds": 150,"tenantId":  "e4f8c059825cddf50183459e32ae23e9" , },
        # {"provinceName": "宁夏", "url": "/ningxiagroup", "provinceIds": 64, "tenantId":  "e4f8c059825cddf5018345af600e2462" ,},
        # {"provinceName": "新疆", "url": "/xinjianggroup", "provinceIds": 65,"tenantId":  "e4f35ef0861bd6020186a6c8bed0182d" , },
        # {"provinceName": "蒙西", "url": "/mengxigroup", "provinceIds": 15,"tenantId":  "e4d20ccb81bcf0170181cbebbaec01c3" , },

    ]

    # startDate = "2023-04-21"
    # endDate = "2023-05-03"

    startDate = "2023-04-27"
    endDate = "2023-04-27"

    # startDate = "2023-06-01"
    # endDate = "2023-06-01"


    jtc_hn.execProvinceInfo(startDate,endDate,provinceInfo)

    # res = jtc_hn.getHuanengOuputData("2023-06-01", "2023-06-02", 63)
    # print(res)

    # getUintUrl = "/qinghaigroup/api/org/org/tree"
    #
    # terminalList = jtc_hn.getUnitId(getUintUrl)
    #
    # print(terminalList)
    #
    # resquestPrivateDataUrl = "/qinghaigroup/api/province/clearing/result/list"
    # privteDataUpload = {}
    #
    # terminalDict = jtc_hn.resquestPrivateData("2023-06-01", "2023-06-02",resquestPrivateDataUrl, terminalList)
    #
    # print(terminalDict["terminalDict"])
    # print(privteDataUpload)


    # jtc_hn.outPrivateStatus("青海",privteDataUpload)