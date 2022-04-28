import time
import datetime

while(True):
    print("Hello world!", datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S'))
    time.sleep(1)