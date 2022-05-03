import logging
import threading
from enum import Enum
from enum import IntEnum

from utils.providers import LoggerProvider
from utils.providers import DeviceInfoProvider
from utils.providers import ConnClientProvider

from obc.manager.manager import TaskManager

import json

class OBCProvider(object):

    def __init__(self, device_file, domain = None, useWebsocket = None):

        self.__tls = True
        self.__useWebsocket = useWebsocket
        self.__key_mode = True
        self.__userdata = None#userdata
        self.__provider = None
        self.__protocol = None
        self.__domain = domain
        self.__host = ""

        self.__log_provider = LoggerProvider()
        self._logger = self.__log_provider.logger

        self.__device_info = DeviceInfoProvider(device_file)

        self.__hub_state = self.HubState.INITIALIZED

        """
        hub层注册到mqtt的回调
        """
        self.__user_on_connect = None
        self.__user_on_disconnect = None
        self.__user_on_publish = None
        self.__user_on_subscribe = None
        self.__user_on_unsubscribe = None
        self.__user_on_message = None

        """存放explorer层注册到hub层的回调函数
        只存放explorer层独有的功能所需的回调(诸如数据模板),
        类似on_connect等explorer和用户层都可能注册的回调在hub层使用专门的函数与之对应
        """
        self.__explorer_callback = {}

        """
        保存__on_subscribe()返回的mid和qos对,用以判断订阅是否成功
        """
        self.__subscribe_res = {}

        """ 存放用户注册的回调函数 """
        self.__user_callback = {}

        self.__user_topics = []
        self.__user_topics_subscribe_request = {}
        self.__user_topics_unsubscribe_request = {}
        self.__user_topics_request_lock = threading.Lock()
        self.__user_topics_unsubscribe_request_lock = threading.Lock()


        self.__loop_worker = self.LoopWorker()
        self.__event_worker = self.EventWorker()
        self.__register_event_callback()

        self.__protocol_init(domain, useWebsocket)


        pass
    
    class HubState(Enum):
        """ 连接状态 """
        INITIALIZED = 1
        CONNECTING = 2
        CONNECTED = 3
        DISCONNECTING = 4
        DISCONNECTED = 5
        DESTRUCTING = 6
        DESTRUCTED = 7
    
    class ErrorCode(Enum):
        ERR_NONE = 0  # 成功
        ERR_TOPIC_NONE = -1000  # topic为空
    
    class StateError(Exception):
        def __init__(self, err):
            Exception.__init__(self, err)
    
    class LoggerLevel(Enum):
        INFO = "info"
        DEBUG = "debug"
        WARNING = "warring"
        ERROR = "error"


    # 管理连接相关资源
    class LoopWorker(object):
        """ mqtt连接管理维护 """
        def __init__(self):
            self._connect_async_req = False
            self._exit_req = True
            self._runing_state = False
            self._exit_req_lock = threading.Lock()
            self._thread = TaskManager.LoopThread()

    class EventWorker(object):
        """ 事件管理 """
        def __init__(self):
            self._thread = TaskManager.EventCbThread()
        
        def _register_event_callback(self, connect, disconnect,
                                        message, publish, subscribe, unsubscribe):
            self._thread.register_event_callback(self.EventPool.CONNECT, connect)
            self._thread.register_event_callback(self.EventPool.DISCONNECT, disconnect)
            self._thread.register_event_callback(self.EventPool.MESSAGE, message)
            self._thread.register_event_callback(self.EventPool.PUBLISH, publish)
            self._thread.register_event_callback(self.EventPool.SUBSCRISE, subscribe)
            self._thread.register_event_callback(self.EventPool.UNSUBSCRISE, unsubscribe)

            self._thread.start()

        class EventPool(object):
            CONNECT = "connect"
            DISCONNECT = "disconnect"
            MESSAGE = "message"
            PUBLISH = "publish"
            SUBSCRISE = "subscribe"
            UNSUBSCRISE = "unsubscribe"

    class sReplyPara(object):
        def __init__(self):
            self.timeout_ms = 0
            self.code = -1
            self.status_msg = None

    class ReplyPara(object):
        def __init__(self):
            self.timeout_ms = 0
            self.code = -1
            self.status_msg = None

    def __assert(self, param):
        if param is None or len(param) == 0:
            raise ValueError('Invalid param.')


    def __protocol_reinit(self):
        self.__protocol_init(self.__domain, self.__useWebsocket)

    # 连接协议(mqtt/websocket)初始化
    def __protocol_init(self, domain=None, useWebsocket=False):
        # # 配置项
        auth_mode = self.__device_info.auth_mode
        device_name = self.__device_info.device_name
        product_id = self.__device_info.product_id
        device_secret = self.__device_info.device_secret
        ca = self.__device_info.ca_file
        cert = self.__device_info.cert_file
        key = self.__device_info.private_key_file

        uuid = self.__device_info.device_uuid
        tpiid = self.__device_info.plaform_tpiid

        # domain
        # """
        # 腾讯hub设备 海外版的domain需要按照官网格式拼接:product_id
        # 客户自定制的私有化 domain 透传
        # """
        # if useWebsocket is False:
        #     if domain is None or domain == "":
        #         self.__host = product_id + ".iotcloud.tencentdevices.com"
        # else:
        #     if domain is None or domain == "":
        #         self.__host = product_id + ".ap-guangzhou.iothub.tencentdevices.com"

        if domain is None or domain == "":
            self.__host = "172.20.144.112"

        if not (domain is None or domain == ""):
            self.__host = domain
        
        self.__provider = ConnClientProvider(self.__host, product_id, device_name, device_secret,
                                                websocket=useWebsocket, tls=self.__tls, logger=self._logger)

        self.__protocol = self.__provider.protocol

        # if auth_mode == "CERT":
        #     self.__protocol.set_cert_file(ca, cert, key)
        
        self.__protocol.register_event_callbacks(self.__on_connect,
                                                    self.__on_disconnect,
                                                    self.__on_message,
                                                    self.__on_publish,
                                                    self.__on_subscribe,
                                                    self.__on_unsubscribe)
        
        pass

    def setReconnectInterval(self, max_sec, min_sec):
        """Set mqtt reconnect interval

        Set mqtt reconnect interval
        Args:
            max_sec: reconnect max time
            min_sec: reconnect min time
        Returns:
            success: default
            fail: default
        """
        if self.__protocol is None:
            self._logger.error("Set failed: client is None")
            return
        self.__protocol.set_reconnect_interval(max_sec, min_sec)
        self.__protocol.config_connect()

    def setMessageTimout(self, timeout):
        """Set message overtime time

        Set message overtime time
        Args:
            timeout: mqtt keepalive value
        Returns:
            success: default
            fail: default
        """
        if self.__protocol is None:
            self._logger.error("Set failed: client is None")
            return
        self.__protocol.set_message_timout(timeout)

    def setKeepaliveInterval(self, interval):
        """Set mqtt keepalive interval

        Set mqtt keepalive interval
        Args:
            interval: mqtt keepalive interval
        Returns:
            success: default
            fail: default
        """
        if self.__protocol is None:
            self._logger.error("Set failed: client is None")
            return
        self.__protocol.set_keepalive_interval(interval)

    # def getProductID(self):
    #     """Get product id

    #     Get product id
    #     Args: None
    #     Returns:
    #         success: product id
    #         fail: None
    #     """
    #     return self.__device_info.product_id


    ######## connect && disconnect ########

    def connect(self):
        """Connect

        Device connect
        Args: None
        Returns:
            success: thread start result
            fail: thread start result
        """
        self.__loop_worker._connect_async_req = True
        with self.__loop_worker._exit_req_lock:
            self.__loop_worker._exit_req = False
        return self.__loop_worker._thread.start(self._loop)

    def disconnect(self):
        """Disconnect

        Device disconnect
        Args: None
        Returns:
            success: default
            fail: default
        """
        self._logger.debug("disconnect")
        if self.__hub_state is not self.HubState.CONNECTED:
            raise self.StateError("current state is not CONNECTED")
        self.__hub_state = self.HubState.DISCONNECTING
        if self.__loop_worker._connect_async_req is True:
            with self.__loop_worker._exit_req_lock:
                self.__loop_worker._exit_req = True

        self.__protocol.disconnect()
        self.__loop_worker._thread.stop()


    ##### 以下函数作为protocol直接调用的函数体 #####

    def __on_connect(self, client, user_data, session_flag, rc):
        if rc == 0:
            self.__protocol.reset_reconnect_wait()
            self.__hub_state = self.HubState.CONNECTED
            self.__event_worker._thread.post_message(self.__event_worker.EventPool.CONNECT, (session_flag, rc))

        pass

    def __on_disconnect(self, client, user_data, rc):
        if self.__hub_state == self.HubState.DISCONNECTING:
            self.__hub_state = self.HubState.DISCONNECTED
        elif self.__hub_state == self.HubState.DESTRUCTING:
            self.__hub_state = self.HubState.DESTRUCTED
        elif self.__hub_state == self.HubState.CONNECTED:
            self.__hub_state = self.HubState.DISCONNECTED
        else:
            self._logger.error("state error:%r" % self.__hub_state)
            return

        self.__user_topics_subscribe_request.clear()
        self.__user_topics_unsubscribe_request.clear()
        self.__user_topics.clear()

        # """
        # 将disconnect事件通知到explorer
        # """
        # ex_topic = "$explorer/from/disconnect"
        # if ex_topic in self.__explorer_callback:
        #     if self.__explorer_callback[ex_topic] is not None:
        #         self.__explorer_callback[ex_topic](client, self.__userdata, rc)
        #     else:
        #         self._logger.error("no callback for topic %s" % ex_topic)

        self.__event_worker._thread.post_message(self.__event_worker.EventPool.DISCONNECT, (rc))
        if self.__hub_state == self.HubState.DESTRUCTED:
            self.__event_worker._thread.stop()


        pass

    def __on_message(self, client, user_data, message):
        self.__event_worker._thread.post_message(self.__event_worker.EventPool.MESSAGE, (message))

    def __on_publish(self, client, user_data, mid):
        self.__event_worker._thread.post_message(self.__event_worker.EventPool.PUBLISH, (mid))
 
    def __on_subscribe(self, client, user_data, mid, granted_qos):
        qos = granted_qos[0]
        # todo:mid,qos
        self.__subscribe_res[mid] = qos
        self.__event_worker._thread.post_message(self.__event_worker.EventPool.SUBSCRISE, (qos, mid))

    def __on_unsubscribe(self, client, user_data, mid):
        self.__event_worker._thread.post_message(self.__event_worker.EventPool.UNSUBSCRISE, (mid))

    ##### 结束 protocol直接调用函数体 #####


    def __register_event_callback(self):
        self.__event_worker._register_event_callback(self.__user_connect,
                                                    self.__user_disconnect,
                                                    self.__user_message,
                                                    self.__user_publish,
                                                    self.__user_subscribe,
                                                    self.__user_unsubscribe)


    ##### 以下函数注册到event系统中 #####
    """
    处理用户回调
    基于explorer接入时会将用户回调赋值到本层用户回调函数
    """
    def __user_connect(self, value):
        # client, user_data, session_flag, rc = value
        session_flag, rc = value
        if self.__user_on_connect is not None:
            try:
                self.__user_on_connect(session_flag['session present'], rc, self.__userdata)
            except Exception as e:
                self._logger.error("on_connect process raise exception:%r" % e)
        pass

    def __user_disconnect(self, value):
        self.__user_on_disconnect(value, self.__userdata)
        pass

    def __user_publish(self, value):
        self.__user_on_publish(value, self.__userdata)
        pass

    def __user_subscribe(self, value):
        qos, mid = value
        self.__user_on_subscribe(qos, mid, self.__userdata)
        pass

    def __user_unsubscribe(self, value):
        self.__user_on_unsubscribe(value, self.__userdata)
        pass

    def __user_message(self, value):
        message = value
        topic = message.topic
        qos = message.qos
        payload = json.loads(message.payload.decode('utf-8'))
        # print(">>>>>>> from server:%s, topic:%s" % (payload, topic))

        topic_prefix = topic[0:topic.find("/")]
        
        ## 以下为腾讯云的规则..
        pos = topic.rfind("/")
        device_name = topic[pos + 1:len(topic)]

        topic_split = topic[0:pos]
        pos = topic_split.rfind("/")
        product_id = topic_split[pos + 1:len(topic_split)]
        client = product_id + device_name

        if topic_prefix == "$thing" or topic_prefix == "$template":
            self.__user_on_message(topic, payload, qos, self.__userdata)
            pass
        elif topic_prefix == "$sys":
            # 获取时间作为内部服务,不通知到用户
            pass
        elif topic_prefix == "$ota" or topic_prefix == "$rrpc":
            pass

        elif topic in self.__user_topics:
            if self.__user_callback[topic] is not None:
                self.__user_callback[topic](topic, qos, payload, self.__userdata)
            else:
                self._logger.error("no callback for topic %s" % topic)

        else:
            #在callback中找topic
            if self.__explorer_callback[topic] is not None:
                self.__explorer_callback[topic](topic, qos, payload, self.__userdata)
            self._logger.error("unknow topic:%s" % topic)
            pass

        pass
    ##### 结束 函数注册到event系统中 #####


    def registerMqttCallback(self, on_connect, on_disconnect,
                            on_message, on_publish,
                            on_subscribe, on_unsubscribe):
        """Register user mqtt callback

        Register user mqtt callback for mqtt
        Args:
            on_connect: mqtt connect callback
            on_disconnect: mqtt disconnect callback
            on_message: mqtt message callback
            on_publish: mqtt publish callback
            on_subscribe: mqtt subscribe callback
            on_unsubscribe: mqtt unsubscribe callback
        Returns:
            success: default
            fail: default
        """
        self.__user_on_connect = on_connect
        self.__user_on_disconnect = on_disconnect
        self.__user_on_message = on_message
        self.__user_on_publish = on_publish
        self.__user_on_subscribe = on_subscribe
        self.__user_on_unsubscribe = on_unsubscribe



    def _loop(self):
        if self.__hub_state not in (self.HubState.INITIALIZED,
                                     self.HubState.DISCONNECTED):
            raise self.StateError("current state is not in INITIALIZED or DISCONNECTED")
        self.__hub_state = self.HubState.CONNECTING

        if self.__protocol.connect() is not True:
            self.__hub_state = self.HubState.INITIALIZED
            return
    
        while True:
            if self.__loop_worker._exit_req:
                if self.__hub_state == self.HubState.DESTRUCTING:
                    self.__loop_worker._thread.stop()
                    self.__hub_state = self.HubState.DESTRUCTED
                break
            try:
                self.__hub_state = self.HubState.CONNECTING
                """
                实际连接
                """
                self.__protocol.reconnect()
            except (socket.error, OSError) as e:
                self._logger.error("mqtt reconnect error:" + str(e))
                # 失败处理 待添加
                if self.__hub_state == self.HubState.CONNECTING:
                    self.__hub_state = self.HubState.DISCONNECTED
                    self.__protocol.reset_reconnect_wait()

                    if self.__hub_state == self.HubState.DESTRUCTING:
                        self.__loop_worker._thread.stop()
                        self.__hub_state = self.HubState.DESTRUCTED
                        break
                    self.__protocol.reconnect_wait()
                continue
            """
            调用循环调用mqtt loop读取消息
            """
            self.__protocol.loop()
            """
            mqtt loop接口失败(异常导致的disconnect)
            1.将disconnect事件通知到用户
            2.清理sdk相关资源
            """
            if self.__hub_state == self.HubState.CONNECTED:
                self.__on_disconnect(None, None, -1)
            """
            清理线程资源
            """
            if self.__loop_worker._exit_req:
                if self.__hub_state == self.HubState.DESTRUCTING:
                    self.__loop_worker._thread.stop()
                    self.__hub_state = self.HubState.DESTRUCTED
                break
            self.__protocol.reconnect_wait()
        pass

    def logInit(self, level, filePath=None, maxBytes=0, backupCount=0, enable=True):
        """Log initialization

        Log initialization
        Args:
            level: log level, type is class LoggerLevel()
            enable: enable switch
        Returns:
            success: logger handle
            fail: None
        """
        # if self.__protocol is None:
        #     return None

        logger_level = 0
        provider = LoggerProvider()
        logger = provider.logger

        if enable is False:
            logger.disable_logger()
        else:
            if level.value == self.LoggerLevel.INFO.value:
                logger_level = logging.INFO
            elif level.value == self.LoggerLevel.DEBUG.value:
                logger_level = logging.DEBUG
            elif level.value == self.LoggerLevel.WARNING.value:
                logger_level = logging.WARNING
            elif level.value == self.LoggerLevel.ERROR.value:
                logger_level = logging.ERROR
            else:
                logger_level = logging.INFO

            logger.set_level(logger_level)
            logger.enable_logger()

            if (filePath is None or 
                maxBytes == 0 or backupCount == 0):
                self._logger.error("please set logger parameter:\n"
                                    "\tfilePath: log file path.\n"
                                    "\tmaxBytes: bytes of one file.\n"
                                    "\tbackupCount: file number.")
                return None

            logger.create_file(filePath, maxBytes, backupCount)
            #self.__protocol.enable_logger(logger.get_logger())

        return logger

    ##### 相关操作方法 #####
    def subscribe(self, topic, qos):
        """Subscribe topic

        Subscribe topic
        Args:
            topic: topic
            qos: mqtt qos
        Returns:
            success: zero and subscribe mid
            fail: negative number and subscribe mid
        """
        if self.__hub_state is not self.HubState.CONNECTED:
            raise self.StateError("current state is not CONNECTED")

        if isinstance(topic, tuple):
            topic, qos = topic

        if isinstance(topic, str):
            self.__user_topics_request_lock.acquire()
            rc, mid = self.__protocol.subscribe(topic, qos)
            if rc == 0:
                self.__user_topics_subscribe_request[mid] = [(topic, qos)]
            self.__user_topics_request_lock.release()
            return rc, mid
        # topic format [(topic1, qos),(topic2,qos)]

        if isinstance(topic, list):
            self.__user_topics_request_lock.acquire()
            rc, mid = self.__protocol.subscribe(topic)
            if rc == 0:
                self.__user_topics_subscribe_request[mid] = [topic]
            self.__user_topics_request_lock.release()
            return rc, mid

        pass

    def unsubscribe(self, topic):
        """Unsubscribe topic

        Unsubscribe topic what is subscribed
        Args:
            topic: topic
        Returns:
            success: zero and unsubscribe mid
            fail: negative number and unsubscribe mid
        """
        if self.__hub_state is not self.HubState.CONNECTED:
            raise self.StateError("current state is not CONNECTED")
        unsubscribe_topics = []
        if topic is None or len(topic) == 0:
            raise ValueError('Invalid topic.')
        if isinstance(topic, str):
            # topic判断
            unsubscribe_topics.append(topic)
        elif isinstance(topic, list):
            for tp in topic:
                unsubscribe_topics.append(tp)
            pass
        with self.__user_topics_unsubscribe_request_lock:
            if len(unsubscribe_topics) == 0:
                return self.ErrorCode.ERR_TOPIC_NONE, -1
            rc, mid = self.__protocol.unsubscribe(unsubscribe_topics)
            if rc == 0:
                self.__user_topics_unsubscribe_request[mid] = unsubscribe_topics
            return rc, mid
        pass

    def publish(self, topic, payload, qos):
        """Publish message

        Publish message
        Args:
            topic: topic
            payload: publish message
            qos: mqtt qos
        Returns:
            success: zero and publish mid
            fail: negative number and publish mid
        """
        if self.__hub_state is not self.HubState.CONNECTED:
            raise self.StateError("current state is not CONNECTED")
        if topic is None or len(topic) == 0:
            raise ValueError('Invalid topic.')
        if qos < 0:
            raise ValueError('Invalid QoS level.')

        return self.__protocol.publish(topic, json.dumps(payload), qos)
    


    