import random
import datetime

import pythoncom

from common.common import CommonClass
from common.excel_handler import ExcelHepler




def generateUnit(count,prefix=""):

    unitList = []

    prefix = prefix + "#"

    for i in range(0,count):

        unitList.append(
            {
                "unitName" : prefix + str(i+1),
                "businessType" : CommonClass.randomBusinessType(),
            }
             )

    return  unitList

