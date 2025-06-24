
class DispatchUnit:

    def __init__(self,dispatch_unit_id,dispatch_unit_name,sys_generation_unit=None):
        self._dispatch_unit_name = dispatch_unit_name
        self._dispatch_unit_id = dispatch_unit_id
        self._sys_generation_unit = sys_generation_unit

    @property
    def dispatch_unit_name(self):
        return self._dispatch_unit_name

    @dispatch_unit_name.setter
    def dispatch_unit_name(self,value):
        self._dispatch_unit_name = value

    @property
    def dispatch_unit_id(self):
        return self._dispatch_unit_id

    @dispatch_unit_id.setter
    def dispatch_unit_id(self,value):
        self._dispatch_unit_id = value

    @property
    def sys_generation_unit(self):
        return self._sys_generation_unit

    @sys_generation_unit.setter
    def sys_generation_unit(self,value):
        self._sys_generation_unit = value

class BusinessUnit:

    def __init__(self,business_unit_id,business_unit_name,sys_trade_unit=None):
        self._business_unit_name = business_unit_name
        self._business_unit_id = business_unit_id
        self._sys_trade_unit = sys_trade_unit

    @property
    def business_unit_name(self):
        return self._business_unit_name

    @business_unit_name.setter
    def business_unit_name(self,value):
        self._business_unit_name = value

    @property
    def business_unit_id(self):
        return self._business_unit_id

    @business_unit_id.setter
    def business_unit_id(self,value):
        self._business_unit_id = value

    @property
    def sys_trade_unit(self):
        return self._sys_trade_unit

    @sys_trade_unit.setter
    def sys_trade_unit(self,value):
        self._sys_trade_unit = value

class PublicData:

    def __init__(self,area=None,market_type=None,type=None):
        self._area = None
        self._market_type = None
        self._type = None
        self._date_data_dict = {}

    def add_date_data(self,date,data):
        self._date_data_dict[date] = data

    def add_date_dict_data(self,dict_data):
        self._date_data_dict.update(dict_data)

    @property
    def area(self):
        return self._area

    @area.setter
    def area(self,value):
        self._area = value

    @property
    def market_type(self):
        return self._market_type

    @market_type.setter
    def market_type(self,value):
        self._market_type = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self,value):
        self._type = value

    @property
    def date_data_dict(self):
        return self._date_data_dict

    @date_data_dict.setter
    def date_data_dict(self, value):
        self._date_data_dict = value

class ContractInfo:

    def __init__(self,trade_id,trade_name,contract_name,date,ele,price):
        self.trade_id = trade_id
        self.trade_name = trade_name
        self.contract_name = contract_name
        self.date = date
        self.ele = ele
        self.price = price

class ContractCalResult:

    def __init__(self,total_ele,total_price,toal_fee,ele,price,fee):
        self.total_ele = total_ele
        self.total_price = total_price
        self.ele = ele
        self.price = price
        self.total_fee = toal_fee
        self.fee = fee

class ContractErrorInfo:

    def __init__(self,trade_id,trade_name,date,contract_name,detail):
        self.trade_id = trade_id
        self.trade_name = trade_name
        self.contract_name = contract_name
        self.date = date
        self.detail = detail

    def get_info_list(self):

        return [self.trade_id,self.trade_name,self.contract_name,self.date,self.detail]

if __name__ == '__main__':
    d = BusinessUnit("1","2")
    d.business_unit_id = "122"

    print(d.business_unit_id)