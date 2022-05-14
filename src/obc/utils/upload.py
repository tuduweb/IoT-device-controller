import os
import requests
import json
import time
from typing import Tuple

# from obc.utils.providers import DeviceInfoProvider

_currentFilePath = os.path.split(os.path.realpath(__file__))[0]

def upload(pathToFile, tpiId = None, fileName = "") -> Tuple[int, dict]:
    #构建formdata
    url = " https://data.educoder.net/api/myshixuns/upload_file"

    if fileName == "":
        #filekey = 'pic-%s.jpg' % int(time.time())
        fileName = os.path.basename(pathToFile)

    files = {'file': (fileName, open(pathToFile, 'rb'))}

    headers = {}
    #注意 headers里主要注释掉Content-type才可以上传成功
    r = requests.post(url=url, data={'tpiID': tpiId}, files=files, headers=headers) #4597995
    
    #print("fileKey", filekey)

    res = json.loads(r.text)
    print("res", res)
    if res["status"] == 0:
        # 上传成功
        return 0, {"fileKey": pathToFile if fileName == "" else fileName}
        pass
    return -1, res

if __name__ == '__main__':
    print(upload())