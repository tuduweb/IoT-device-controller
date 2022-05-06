import os
import sys
import uuid

#from obc.utils.providers import DeviceInfoProvider
from obc.utils.providers import InfoProperty

TPIID = "s2fgtej4hk8v"

class SystemInit(object):

    def __init__(self, _tpiid = None, _uuid = None) -> None:

        self._currentFilePath = os.path.split(os.path.realpath(__file__))[0]
        #self.__device_provider = DeviceInfoProvider(os.path.join(self._currentFilePath, "config/app.json"))
        self.tpiid = _tpiid
        pass

    def init(self) -> bool:
        #print("hello world")
        infoProperty = InfoProperty(self.tpiid)
        
        print( infoProperty.toJson() )
        
        infoProperty.saveToFile(os.path.join(self._currentFilePath, "config/app.json"))
        
        jsonStr = infoProperty.loadFromFile(os.path.join(self._currentFilePath, "config/app.json"))
        print(jsonStr)
        
        return True

if __name__ == '__main__':
    # 读取并, 构建初次的json文件
    print('参数个数为:', len(sys.argv), '个参数。')
    print('参数列表:', str(sys.argv))

    print("生成的UUID", uuid.uuid4())

    instance = SystemInit(sys.argv[1])
    instance.init()

    print("success")