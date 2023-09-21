


class Tool:

    @staticmethod
    def data96To24list(dataList):


        data24List = [0 for i in range(0,24) ]

        if dataList == None:
            return data24List

        for i in range(0,24):

            tempL =  dataList[i*4:(i+1)*4]

            data24List[i] = sum( tempL)/len(tempL)


        return data24List

    @staticmethod
    def time96To24list(timeList):


        time24List = [0 for i in range(0,24) ]
        count = 0

        if timeList == None:
            return {
                "time24List": time24List,
                "count": count
            }

        # 处理00:00 开始的，如00:00-00:45

        for d in timeList:
            tempList = d.split("-")

            begin = int(tempList[0][:2])
            end = int(tempList[1][:2])


            while begin<=end:
                time24List[begin] = 1
                begin += 1
                count += 1

        return {
            "time24List": time24List,
            "count": count
        }

    @staticmethod
    def time24o24list(timeList):

        time24List = [0 for i in range(0,24) ]
        count = 0

        # 处理00:00 开始的，如00:00-01:00
        if time24List == None:
            return {
                "time24List": time24List,
                "count": count
            }


        for d in timeList:
            tempList = d.split("-")

            begin = int(tempList[0][:2])
            end = int(tempList[1][:2])-1


            while begin<=end:
                time24List[begin] = 1
                begin += 1
                count += 1

        return {

            "time24List":time24List,
            "count" : count
        }

    @staticmethod
    def time96To96list(timeList):

        time96Enum = {
            "00:00":1,
            "00:15":2,
            "00:30":3,
            "00:45":4,
            "01:00":5,
            "01:15":6,
            "01:30":7,
            "01:45":8,
            "02:00":9,
            "02:15":10,
            "02:30":11,
            "02:45":12,
            "03:00":13,
            "03:15":14,
            "03:30":15,
            "03:45":16,
            "04:00":17,
            "04:15":18,
            "04:30":19,
            "04:45":20,
            "05:00":21,
            "05:15":22,
            "05:30":23,
            "05:45":24,
            "06:00":25,
            "06:15":26,
            "06:30":27,
            "06:45":28,
            "07:00":29,
            "07:15":30,
            "07:30":31,
            "07:45":32,
            "08:00":33,
            "08:15":34,
            "08:30":35,
            "08:45":36,
            "09:00":37,
            "09:15":38,
            "09:30":39,
            "09:45":40,
            "10:00":41,
            "10:15":42,
            "10:30":43,
            "10:45":44,
            "11:00":45,
            "11:15":46,
            "11:30":47,
            "11:45":48,
            "12:00":49,
            "12:15":50,
            "12:30":51,
            "12:45":52,
            "13:00":53,
            "13:15":54,
            "13:30":55,
            "13:45":56,
            "14:00":57,
            "14:15":58,
            "14:30":59,
            "14:45":60,
            "15:00":61,
            "15:15":62,
            "15:30":63,
            "15:45":64,
            "16:00":65,
            "16:15":66,
            "16:30":67,
            "16:45":68,
            "17:00":69,
            "17:15":70,
            "17:30":71,
            "17:45":72,
            "18:00":73,
            "18:15":74,
            "18:30":75,
            "18:45":76,
            "19:00":77,
            "19:15":78,
            "19:30":79,
            "19:45":80,
            "20:00":81,
            "20:15":82,
            "20:30":83,
            "20:45":84,
            "21:00":85,
            "21:15":86,
            "21:30":87,
            "21:45":88,
            "22:00":89,
            "22:15":90,
            "22:30":91,
            "22:45":92,
            "23:00":93,
            "23:15":94,
            "23:30":95,
            "23:45":96,
        }

        time96List = [0 for i in range(0, 96)]
        count = 0

        # 处理00:00 开始的，如00:00-01:00
        if timeList == None:
            return {
                "time96List": time96List,
                "count": count
            }

        for d in timeList:
            tempList = d.split("-")

            begin = time96Enum[tempList[0]]-1
            end = time96Enum[tempList[1]]-1

            while begin <= end:
                time96List[begin] = 1
                begin += 1
                count += 1

        return {

            "time96List": time96List,
            "count": count
        }


if __name__ == '__main__':

    test = ["00:00-00:45","20:00-23:45"]
    #
    # print(Tool.time96To24list(test))

    # test1 = ["17:00-19:00"]
    # a = str(test1)

    print(Tool.time96To96list(test))

    # print(a)
    # print(type(eval(a)))

    pass