from datetime import timedelta

import requests

from common.common import CommonClass

from threading import Thread

dataTyamlPath = CommonClass.mkDir("河北","config","T.yaml",isGetStr=True)
dataPeakyamlPath = CommonClass.mkDir("河北","config","峰平谷.yaml",isGetStr=True)
configyamlPath = CommonClass.mkDir("河北","config","hb_interface.yaml",isGetStr=True)



yamlData1 = CommonClass.readYaml(dataTyamlPath)
yamlData2 = CommonClass.readYaml(dataPeakyamlPath)

print(yamlData1)
print(yamlData2)


