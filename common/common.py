import os.path
import random


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

if __name__ == '__main__':


    print(CommonClass.mkDir("hn","output","private_data","#1",isGetStr=True))
    print(CommonClass.randomData(24,100,300,4))