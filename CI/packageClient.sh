
echo packageClient
echo -----------------------------------------------

CURRENT_DIR=$(cd $(dirname $0); pwd)
PARENT_DIR=$(cd $(dirname $0);cd ..; pwd)

echo $CURRENT_DIR

#packageDist=$CURRENT_DIR'/../src'

# 打包前的单元测试

# 打包src
rm bin/client.tar.gz > /dev/null
tar -zcvf bin/client.tar.gz -C src/ .



## 一些问题 ###
#tar: Removing leading `/home/hehao/remoteControl/IoT-device-controller/CI/../' from member names
#其原因是tar默认为相对路径，使用绝对路径的话就回报这个错，可以使用-P参数（注意大写）解决这个问题
