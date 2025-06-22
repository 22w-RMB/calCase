
class DispatchUnit:

    def __init__(self,dispatch_unit_id,dispatch_unit_name,sys_generation_unit=None):
        self.__dispatch_unit_name = dispatch_unit_name
        self.__dispatch_unit_id = dispatch_unit_id
        self.__sys_generation_unit = sys_generation_unit

    @property
    def dispatch_unit_name(self):
        return self.__dispatch_unit_name

    @dispatch_unit_name.setter
    def dispatch_unit_name(self,value):
        self.__dispatch_unit_name = value

    @property
    def dispatch_unit_id(self):
        return self.__dispatch_unit_id

    @dispatch_unit_id.setter
    def dispatch_unit_id(self,value):
        self.__dispatch_unit_id = value

    @property
    def sys_generation_unit(self):
        return self.__sys_generation_unit

    @sys_generation_unit.setter
    def sys_generation_unit(self,value):
        self.__sys_generation_unit = value

class BusinessUnit:

    def __init__(self,business_unit_id,business_unit_name,sys_trade_unit=None):
        self.__business_unit_name = business_unit_name
        self.__business_unit_id = business_unit_id
        self.__sys_trade_unit = sys_trade_unit

    @property
    def business_unit_name(self):
        return self.business_unit_name

    @business_unit_name.setter
    def business_unit_name(self,value):
        self.__business_unit_name = value

    @property
    def business_unit_id(self):
        return self.__business_unit_id

    @business_unit_id.setter
    def business_unit_id(self,value):
        self.__business_unit_id = value

    @property
    def sys_trade_unit(self):
        return self.__sys_trade_unit

    @sys_trade_unit.setter
    def sys_trade_unit(self,value):
        self.__sys_trade_unit = value

class PublicData:

    def __init__(self,area=None,market_type=None,type=None,date_data_dict={}):
        self.__area = None
        self.__market_type = None
        self.__type = None
        self.__date_data_dict = date_data_dict

    def add_date_data(self,date,data):
        self.__date_data_dict[date] = data

    @property
    def area(self):
        return self.__area

    @area.setter
    def area(self,value):
        self.__area = value

    @property
    def market_type(self):
        return self.__market_type

    @market_type.setter
    def market_type(self,value):
        self.__market_type = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self,value):
        self.__type = value

    @property
    def date_data_dict(self):
        return self.__date_data_dict

    @date_data_dict.setter
    def date_data_dict(self, value):
        self.__date_data_dict = value


if __name__ == '__main__':
    d = BusinessUnit("1","2")
    d.business_unit_id = "122"

    print(d.business_unit_id)