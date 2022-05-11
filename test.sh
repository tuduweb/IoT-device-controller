#!/bin/bash

install_apt(){
    echo install_apt
    echo ========================================================
    shift #移args
    trap "caught_error 'install_build-deps'" ERR
    sudo apt-get install -y $@
}

install_pipPackage(){
    echo install_pipPackage
    echo ========================================================
    which pip3 > /dev/null
    if [ $? -ne 0 ];then
        #没有安装pip3..
        echo "no pip3"
        sudo apt-get install python3-distutils
        webget /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
        
        cd /tmp/
        python3 ./get-pip.py

        which pip3 > /dev/null

        if [ $? -ne 0 ];then
            export PATH=$PATH:/home/pi/.local/bin
        fi
    fi

    pip3 install paho-mqtt==1.5.1
}

install_dependence(){
    echo install_opencv
    echo ========================================================
    install_apt python3-opencv
    echo ========================================================
    install_pipPackage
    echo ========================================================
}

#检查Python版本..如果不是支持范围下, 那么自行安装一个版本
check_python(){
    #
    echo "check python"
}


setconfig(){
	configpath=$appdir/mark
	[ -n "$(grep ${1} $configpath)" ] && sed -i "s#${1}=.*#${1}=${2}#g" $configpath || echo "${1}=${2}" >> $configpath
}

webget(){
	#参数【$1】代表下载目录，【$2】代表在线地址
	#参数【$3】代表输出显示，【$4】不启用重定向
	if curl --version > /dev/null 2>&1;then
		[ "$3" = "echooff" ] && progress='-s' || progress='-#'
		[ -z "$4" ] && redirect='-L' || redirect=''
		result=$(curl -w %{http_code} --connect-timeout 5 $progress $redirect -ko $1 $2)
		[ -n "$(echo $result | grep -e ^2)" ] && result="200"
	else
		if wget --version > /dev/null 2>&1;then
			[ "$3" = "echooff" ] && progress='-q' || progress='-q --show-progress'
			[ "$4" = "rediroff" ] && redirect='--max-redirect=0' || redirect=''
			certificate='--no-check-certificate'
			timeout='--timeout=3'
		fi
		[ "$3" = "echoon" ] && progress=''
		[ "$3" = "echooff" ] && progress='-q'
		wget $progress $redirect $certificate $timeout -O $1 $2
		[ $? -eq 0 ] && result="200"
	fi
}


gettar(){
    # dependence: tar
	webget /tmp/client.tar.gz $tarurl
	[ "$result" != "200" ] && echo "文件下载失败,请尝试使用其他安装源！" && exit 1

    # 尚未判断tar是否可运行
    mkdir -p $appdir > /dev/null
    tar -zxvf '/tmp/client.tar.gz' -C $appdir/
    [ $? -ne 0 ] && echo "文件解压失败！" && rm -rf /tmp/client.tar.gz && exit 1 
    [ -f "$appdir/mark" ] || echo '#标识controlClient运行状态的文件，不明勿动！' > $appdir/mark

    rm /tmp/client.tar.gz
}

getMainZip() {
    #https://data.educoder.net/api/myshixuns/download_file.json?tpiID=
    zipPath=/tmp/client.zip
    webget $zipPath $zipurl
	[ "$result" != "200" ] && echo "文件下载失败,请尝试使用其他安装源！" && exit 1

    # 尚未判断tar是否可运行
    mkdir -p $appdir > /dev/null
    unzip -o $zipPath -d $appdir/
    [ $? -ne 0 ] && echo "文件解压失败！" && rm -rf $zipPath && exit 1 
    [ -f "$appdir/mark" ] || echo '#标识controlClient运行状态的文件，不明勿动！' > $appdir/mark

    #rm $zipPath
}

echo "download :"$url
#tpiid=$tpiid
url_dl=$url
tarurl=$url_dl/bin/client.tar.gz
#zipurl=$url_dl/bin/client.zip
zipurl=https://data.educoder.net/api/myshixuns/download_file.json?tpiID=$tpiid
#https://data.educoder.net/api/myshixuns/download_file.json?tpiID=
appdir=~/appdemo


# 查看版本, 是否已经安装

# 根据版本, 查找diff, 增量安装

# 主程序tar包, 和其他程序打包到了一块 故一次性下载
getMainZip

source ~/appdemo/CI/build_support.sh


# 安装依赖库
install_dependence

# echo "hello world"

# 运行包中的脚本..进入到下一个阶段?
bash $appdir/boot.sh