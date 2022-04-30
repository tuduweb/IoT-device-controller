#import paho.mqtt.client as mqtt
import json

import time

access_key = "MoVNHexgySseNvZuQvjR-aBPsRnOST06X1YVzXW9"
secret_key = "9Ho3IMrZTF9a4c-6aX8HCdnzIiEzMtnsdrju1xAy"
#要上传的空间
bucket_name = 'educoder-control'

## configs

"""
QCloud Device Info
"""
PRODUCT_ID = "OLER6OOJDJ"
DEVICE_NAME = "test2"
DEVICE_KEY = "lyHtcytkme4rXidAwYoqkw=="
"""
MQTT topic
"""
TPIID = "s2fgtej4hk8v"
MQTT_DEVICE_CONTROL_TOPIC = "$thing/down/control/"+TPIID+"/"
MQTT_DEVICE_CONTROLUP_TOPIC = "$thing/up/control/"+TPIID+"/"
MQTT_SERVER = '172.20.144.112'#PRODUCT_ID + ".iotcloud.tencentdevices.com"
MQTT_PORT = 1883
MQTT_CLIENT_ID = 'raspberry'
MQTT_USERNAME = "raspberryusername"
MQTT_PASSWORD = "raspberrypassword"


# # The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code "+str(rc))

#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#     client.subscribe("$SYS/#")
#     client.subscribe(MQTT_DEVICE_CONTROL_TOPIC)
#     #client.subscribe(MQTT_DEVICE_CONTROLUP_TOPIC)

# # The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload) + " " + str(userdata), client)

#     data = json.loads(msg.payload)

#     print(data)


#     ## 执行程序..

#     ## 判断是否有相关程序包在本地, 没有的话先拉取到本地

#     ## 执行, 并等待..

#     time.sleep(5)#阻塞了所有


#     reply = {
#         "method": "action_reply",
#         'code' : 0,
#         #'clientToken': data.get('clientToken'),
#         'status': "action execute success!",
#         'response':   {
#             #"imageKey": filekey
#         }
#     }
#     res = client.publish('$thing/up/action/'+TPIID + '/', json.dumps(reply))
#     print(res)

#     # # json_out = {
#     # #         "method": "action_reply",
#     # #         "code": replyPara.code,
#     # #         "clientToken": clientToken,
#     # #         "status": replyPara.status_msg,
#     # #         "response": response
#     # #     }

#     # # clientToken = payload["clientToken"]
#     # # reply_param = qcloud.ReplyPara()
#     # # reply_param.code = 0
#     # # reply_param.timeout_ms = 5 * 1000
#     # # reply_param.status_msg = "action execute success!"
#     # # reply_param
#     # filekey = 'pic-%s.jpg' % int(time.time())
#     # token = q.upload_token(bucket_name, filekey, 3600)
#     # ret, info = qiniu.put_file(token, filekey, './100kb.jpg', version='v2') 

#     # print(info)
#     # print(ret)

#     # reply = {
#     #     "method": "action_reply",
#     #     'code' : 0,
#     #     'clientToken': data.get('clientToken'),
#     #     'status': "action execute success!",
#     #     'response':   {
#     #         "imageKey": filekey
#     #     }
#     # }

#     # if data.get('method') == 'action':
#     #     print("action action")
#     #     res = client.publish('$thing/up/action/OLER6OOJDJ/'+DEVICE_NAME, json.dumps(reply))
#     #     print(res)


# def on_publish(client, userdata, mid):
#     print(userdata)
#     print(mid)


from obc.obc import OBCProvider
import os

_currentFilePath = os.path.split(os.path.realpath(__file__))[0]

# client = mqtt.Client(MQTT_CLIENT_ID)
# client.on_connect = on_connect
# client.on_message = on_message
# client.on_publish = on_publish

# client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
# client.connect(MQTT_SERVER, MQTT_PORT, 60)

#q = qiniu.Auth(access_key, secret_key)

import sys
def on_connect(flags, rc, userdata):
    logger.debug("%s:flags:%d,rc:%d,userdata:%s" % (sys._getframe().f_code.co_name, flags, rc, userdata))
    pass

def on_disconnect(rc, userdata):
    logger.debug("%s:rc:%d,userdata:%s" % (sys._getframe().f_code.co_name, rc, userdata))
    pass


def on_message(topic, payload, qos, userdata):
    logger.debug("%s:topic:%s,payload:%s,qos:%s,userdata:%s" % (sys._getframe().f_code.co_name, topic, payload, qos, userdata))
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
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

#client.loop_forever()

# mqtt连接, 并且进入Loop
obc.connect()


while True:
    time.sleep(0.1)