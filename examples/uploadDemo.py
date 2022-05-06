import os
import requests
import json
import time

_currentFilePath = os.path.split(os.path.realpath(__file__))[0]

def upload():
    #构建formdata

    url = " https://data.educoder.net/api/myshixuns/upload_file"

    filekey = 'pic-%s.jpg' % int(time.time())

    files = {'file': (filekey, open(os.path.join(_currentFilePath, "../demo.jpg"), 'rb'))} #, 'application/vnd.ms-excel', {'Expires': '0'}
    headers = {}
    #注意 headers里主要注释掉Content-type才可以上传成功
    r = requests.post(url=url, data={'tpiID': 4597995}, files=files, headers=headers)
    res = json.loads(r.text)
    if res["status"] == 0:
        # 上传成功
        return 0, {"fileKey": filekey}
        pass
    return -1, res

if __name__ == '__main__':
    print(upload())