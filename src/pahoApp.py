#import paho.mqtt.client as mqtt
import os
import sys
import json
import time

from obc.obc import OBCProvider
from obc.controller.controller import OBCController, grapCamera

_currentFilePath = os.path.split(os.path.realpath(__file__))[0]

# 预留平台控制任务接口
'''
#input: 平台下发任务.. argList: 评测脚本, 评测用例, 评测代码地址即版本库
#output: 给平台的回复, 回复给下发任务后加上_rst的主题 评测结果
'''
# def on_super_message(topic, payload, qos, userdata):
#     pass

# def on_tpi_message(topic, payload, qos, userdata):

#     if payload.get('actionId') == 'grapCamera':
#         grapCamera()
#         reply_param = obc.ReplyPara()
#         reply_param.timeout_ms = 5 * 1000
#         reply_param.code = 0
#         reply_param.status_msg = "GrapCameraSuccess"
#         res = {
#             "imageKey": "123.jpg"
#         }

#         json_out = {
#             "method": "action_reply",
#             "code": reply_param.code,
#             #"clientToken": clientToken,
#             "status": reply_param.status_msg,
#             "response": res
#         }

#         obc.publish(topic + '_rst', json_out, 0)
#         pass
#     pass

#### 待封装
import time
import cv2
from typing import Tuple

def grapCamera() -> Tuple[int, dict]:
    cap=cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    start_time = time.time()
    sucess,img=cap.read()
    cv2.imwrite('/tmp/touge-grap.jpg', img)
    end_time = time.time()
    print("Time:",end_time-start_time)
    cap.release()
    return 0, '/tmp/touge-grap.jpg'
########## END

def on_connect(flags, rc, userdata):
    tpiid = obc.get_tpiid()
    print("tpiid", tpiid)
    logger.debug("%s:flags:%d,rc:%d,userdata:%s tpiid:%s" % (sys._getframe().f_code.co_name, flags, rc, userdata, tpiid))
    ### 连接上后订阅相关topic
    obc.subscribe('$thing/control/mqtt_' + str(tpiid), 0)
    obc.subscribe('$plaform/control/mqtt_' + str(tpiid), 0)

    #平台适配
    obc.subscribe(str(tpiid), 0)
    pass

def on_disconnect(rc, userdata):
    logger.debug("%s:rc:%d,userdata:%s" % (sys._getframe().f_code.co_name, rc, userdata))
    pass

from obc.utils.upload import upload

def on_message(topic, payload, qos, userdata):
    logger.debug("%s:topic:%s,payload:%s,qos:%s,userdata:%s" % (sys._getframe().f_code.co_name, topic, payload, qos, userdata))

    if topic == str(obc.get_tpiid()) and payload.get('testCases'):
        testCases = payload.get('testCases')
        if isinstance(testCases, str):
            testCases = json.loads(testCases)
        # 暂时只考虑一个case的情况
        print(testCases[0], type(testCases[0]))
        testCase = testCases[0]
        
        params = json.loads(testCase.get('input')) #python dict
        print(testCase.get('input'), params, type(params))




        if(params.get('actionId') == 'checkLink'):

            _res = os.system("echo "+ str(int(time.time())) +" > /tmp/checkLink.txt")

            _res, _data = upload("/tmp/checkLink.txt", obc.get_tpiid(),  os.path.basename("checkLink.txt"))
            json_out = {
                "uuid": payload.get("uuid"),
            }
            obc.publish(topic + '_rst', json_out, 0)

            pass



        elif(params.get('actionId') == 'grapCamera'):

            #_res, _filePath = grapCamera()
            _res = 0
            _filePath = "/home/hehao/remoteControl/IoT-device-controller/demo.jpg"
            if _res != 0:
                logger.error("error occur when grapCamera")
                pass

            _res, _data = upload(os.path.join(_currentFilePath, _filePath), obc.get_tpiid(),  os.path.basename(_filePath))
            #print(_res, _data)

            if _res != 0:
                logger.error("error when update file : message %s", _data["message"])
                return
            
            reply_param = obc.ReplyPara()
            reply_param.timeout_ms = 5 * 1000
            reply_param.code = 0
            reply_param.status_msg = "GrapCameraSuccess"
            res = {
                "imageKey": os.path.basename(_data["fileKey"])
            }

            json_out = {
                "uuid": payload.get("uuid"),
                "method": "action_reply",
                "code": reply_param.code,
                #"clientToken": clientToken,
                "status": reply_param.status_msg,
                "response": res
            }

            obc.publish(topic + '_rst', json_out, 0)

        elif(params.get('actionId') == 'controlLed'):
            pass


    # ### 需要加入其他判断
    # if payload.get('actionId') == 'grapCamera' or topic == str(obc.get_tpiid()):

    #     #_res, _filePath = grapCamera()
    #     _res = 0
    #     _filePath = "/home/hehao/remoteControl/IoT-device-controller/demo.jpg"
    #     if _res != 0:
    #         logger.error("error occur when grapCamera")
    #         pass

    #     _res, _data = upload(os.path.join(_currentFilePath, _filePath), obc.get_tpiid())
    #     #print(_res, _data)

    #     if _res != 0:
    #         logger.error("error when update file : message %s", _data["message"])
    #         return
        
    #     reply_param = obc.ReplyPara()
    #     reply_param.timeout_ms = 5 * 1000
    #     reply_param.code = 0
    #     reply_param.status_msg = "GrapCameraSuccess"
    #     res = {
    #         "imageKey": os.path.basename(_data["fileKey"])
    #     }

    #     json_out = {
    #         "uuid": payload.get("uuid"),
    #         "method": "action_reply",
    #         "code": reply_param.code,
    #         #"clientToken": clientToken,
    #         "status": reply_param.status_msg,
    #         "response": res
    #     }

    #     obc.publish(topic + '_rst', json_out, 0)
    #     #obc.publish(str(obc.get_tpiid()) + '_rst', {}, 0)

    pass


def on_publish(mid, userdata):
    logger.debug("%s:mid:%d,userdata:%s" % (sys._getframe().f_code.co_name, mid, userdata))
    pass


def on_subscribe(mid, granted_qos, userdata):
    logger.debug("%s:mid:%d,granted_qos:%s,userdata:%s" % (sys._getframe().f_code.co_name, mid, granted_qos, userdata))
    pass


def on_unsubscribe(mid, userdata):
    logger.debug("%s:mid:%d,userdata:%s" % (sys._getframe().f_code.co_name, mid, userdata))
    pass

_deviceFilePath = os.path.join(_currentFilePath, 'config/device_info.json')
_appFilePath = os.path.join(_currentFilePath, 'config/app.json')
obc = OBCProvider(device_file=_deviceFilePath, app_file=_appFilePath)

_logFilePath = os.path.join(_currentFilePath, 'logs/app.log')
logger = obc.logInit(obc.LoggerLevel.DEBUG, _logFilePath, 1024 * 1024 * 10, 5, enable=True)

obc.registerMqttCallback(on_connect, on_disconnect,
                            on_message, on_publish,
                            on_subscribe, on_unsubscribe)

obc.connect()

# @obc.action.route('grapCamera')
# def action_grapCamera():
#     print("hello world")
#     return "hello world"

# logger.debug("actions %s" % obc.actions())

# MainThread Loop
while True:
    time.sleep(0.1)
