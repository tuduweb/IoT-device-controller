#import paho.mqtt.client as mqtt
import os
import sys
import json
import time
from obc.obc import OBCProvider
from obc.controller.controller import OBCController, grapCamera

TPIID = "s2fgtej4hk8v"
_currentFilePath = os.path.split(os.path.realpath(__file__))[0]

# 预留平台控制任务接口
'''
#input: 平台下发任务.. argList: 评测脚本, 评测用例, 评测代码地址即版本库
#output: 给平台的回复, 回复给下发任务后加上_rst的主题 评测结果
'''
def on_super_message(topic, payload, qos, userdata):
    pass

def on_tpi_message(topic, payload, qos, userdata):

    if payload.get('actionId') == 'grapCamera':
        grapCamera()
        reply_param = obc.ReplyPara()
        reply_param.timeout_ms = 5 * 1000
        reply_param.code = 0
        reply_param.status_msg = "GrapCameraSuccess"
        res = {
            "imageKey": "123.jpg"
        }

        json_out = {
            "method": "action_reply",
            "code": reply_param.code,
            #"clientToken": clientToken,
            "status": reply_param.status_msg,
            "response": res
        }

        obc.publish(topic + '_rst', json_out, 0)
        pass
    pass



def on_connect(flags, rc, userdata):
    logger.debug("%s:flags:%d,rc:%d,userdata:%s" % (sys._getframe().f_code.co_name, flags, rc, userdata))
    ### 连接上后订阅相关topic
    obc.subscribe('$thing/down/control/mqtt_' + TPIID, 0)
    obc.subscribe('$plaform/down/control/mqtt_' + TPIID, 0)
    pass

def on_disconnect(rc, userdata):
    logger.debug("%s:rc:%d,userdata:%s" % (sys._getframe().f_code.co_name, rc, userdata))
    pass


def on_message(topic, payload, qos, userdata):
    logger.debug("%s:topic:%s,payload:%s,qos:%s,userdata:%s" % (sys._getframe().f_code.co_name, topic, payload, qos, userdata))

    if payload.get('actionId') == 'grapCamera':
        
        _res, _data = grapCamera()

        reply_param = obc.ReplyPara()
        reply_param.timeout_ms = 5 * 1000
        reply_param.code = 0
        reply_param.status_msg = "GrapCameraSuccess"
        res = {
            "imageKey": "123.jpg"
        }

        json_out = {
            "method": "action_reply",
            "code": reply_param.code,
            #"clientToken": clientToken,
            "status": reply_param.status_msg,
            "response": res
        }

        obc.publish(topic + '_rst', json_out, 0)

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
obc = OBCProvider(device_file=_deviceFilePath)

_logFilePath = os.path.join(_currentFilePath, 'logs/app.log')
logger = obc.logInit(obc.LoggerLevel.DEBUG, _logFilePath, 1024 * 1024 * 10, 5, enable=True)

obc.registerMqttCallback(on_connect, on_disconnect,
                            on_message, on_publish,
                            on_subscribe, on_unsubscribe)

obc.connect()


while True:
    time.sleep(0.1)
