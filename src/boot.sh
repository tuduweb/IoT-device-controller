#!/bin/sh

CURRENT_DIR=$(cd $(dirname $0); pwd)

# 加入启动参数表
declare -i i=0
bootLog=$CURRENT_DIR'/logs/boot.out'
i=$(cat $bootLog)

#first boot register
if [ $i -lt 1 ]; then
    tpiid=$(cat /tmp/educoder.cfg)
    echo "tpiid "$tpiid
    python3 $CURRENT_DIR/systemInit.py $tpiid > /tmp/systemInit.out 2>&1
    cat /tmp/systemInit.out | grep "success" > /dev/null
    if [  $? == 0 ]; then
        i+=1
        sed -i "1c ${i}" $bootLog
    fi
fi

if [ $i -gt 0 ]; then
    i+=1
    echo "$i"
    sed -i "1c ${i}" $bootLog

    rm /tmp/appLog.out > /dev/null 2>&1
    touch /tmp/appLog.out
    chmod 777 /tmp/appLog.out
    echo "hello pi~" >> /tmp/appLog.out

    #python3 /home/pi/remoteControlApp/app.py > /tmp/appLog.out 2>&1
    python3 $CURRENT_DIR/pahoApp.py
    # > /tmp/appLog.out 2>&1
fi