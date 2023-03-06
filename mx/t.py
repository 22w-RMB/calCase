import time

import requests

from common.common import CommonClass

yamlPath = r"D:\code\python\calCase\mx\config\mx_interface.yaml"


def sessionType(session, yamlData, type ):

    domain = None
    loginInfo = None
    if type == "test":
        domain = yamlData['url_domain']['test_domain']
        loginInfo = yamlData['logininfo']['test_info']
    elif type == "tcloud":
        domain = yamlData['url_domain']['tcloud_domain']
        loginInfo = yamlData['logininfo']['tcloud_info']
    elif type == "hn":
        domain = yamlData['url_domain']['hn_domain']
        loginInfo = yamlData['logininfo']['hn_info']

    CommonClass.login(session, domain, loginInfo)



def netUnitInfo(session,yamlData):

    domain = yamlData['url_domain']['test_domain']

    queryUrl = domain + "/mxgroup/fire/api/overhaul/unit"
    queryRes = session.request(method="GET",url = queryUrl).json()['data']
    unitIdList = []
    for item in queryRes:
        unitIdList.append(item['id'])
    print(unitIdList)


    deleteUrl = domain + "/mxgroup/fire/api/overhaul/unit"
    for id in unitIdList:
        # time.sleep(1)
        param = { "id" : id }
        res = CommonClass.execRequest(session=session,method="DELETE", url=deleteUrl,params=param).json()

        print(res)


if __name__ == '__main__':


    testSession = requests.Session()

    yamlData = CommonClass.readYaml(yamlPath)
    sessionType(testSession,yamlData,"test")

    netUnitInfo(testSession,yamlData)