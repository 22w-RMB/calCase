import os.path
import random
import time

import yaml
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import base64
import requests

class CommonClass:


    @staticmethod
    def mkDir( *args, isGetStr=False):
        root = os.path.dirname(os.path.dirname(__file__))
        for i in args:
            root = os.path.join(root, i)
            if isGetStr == False:
                if not os.path.exists(root):
                    os.mkdir(root)

        return root

    @staticmethod
    def randomData(count, maxLimit,minLimit, decimalPlace):

        dataL = []

        for i in range(0,count):

            dataL.append( round( random.uniform(minLimit,maxLimit), decimalPlace )  )

        return dataL

    @staticmethod
    def randomBusinessType():

        return random.choice(["WIND","FIRE","PV"])

    # RSA 加密
    @staticmethod
    def encrpt(s, key):
        public_key = "-----BEGIN PUBLIC KEY-----\n" + key + "\n-----END PUBLIC KEY-----"
        rsakey = RSA.importKey(public_key)
        cipher = PKCS1_v1_5.new(rsakey)
        # 因为encryptor.encrypt方法其内部就实现了加密再次Base64加密的过程，所以这里实际是通过下面的1和2完成了JSEncrypt的加密方法
        encrpt_text = cipher.encrypt(s.encode())  # 1.对账号密码组成的字符串加密
        base64_text = base64.b64encode(encrpt_text)  # 2.对加密后的字符串base64加密

        return base64_text.decode()

    @staticmethod
    def login(session1: requests.Session, domain , loginInfo):


        password = loginInfo['password']
        if loginInfo['publicKey_url'] is not None:
            publicKeyUrl = domain + loginInfo['publicKey_url']
            key = session1.request(method="GET", url=publicKeyUrl ).json()['data']
            password = CommonClass.encrpt(loginInfo['password'], key)

        loginData = {
            "username": loginInfo['username'],
            "loginMode": loginInfo['loginMode'],
            "password": password
        }

        print(password)

        loginUrl = domain+loginInfo['login_url']
        r1 = session1.request(method="POST", url=loginUrl, params=loginData)
        print(r1.json())

        switchUrl = domain + loginInfo['switch_url']
        r2 = session1.request(method="GET", url=switchUrl)
        print(r2.json())

    # 读取yaml文件
    @staticmethod
    def readYaml(yamlFilePath):

        data: dict
        with open(yamlFilePath, 'r', encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return data


    # 处理频繁请求
    @staticmethod
    def execRequest(session, method, url,
            params=None, data=None, headers=None, cookies=None, files=None,
            auth=None, timeout=None, allow_redirects=True, proxies=None,
            hooks=None, stream=None, verify=None, cert=None, json=None):

        while True:
            try:
                res = session.request(method=method,  url=url,
            params=params, data=data, headers=headers, cookies=cookies, files=files,
            auth=auth, timeout=timeout, allow_redirects=allow_redirects, proxies=proxies,
            hooks=hooks, stream=stream, verify=verify, cert=cert, json=json)

                return res
            except Exception as e:
                print(str(e))
                time.sleep(0.1)



if __name__ == '__main__':


    # print(CommonClass.mkDir("hn","output","private_data","#1",isGetStr=True))
    # print(CommonClass.randomData(24,100,300,4))
    print(CommonClass.yamlData)