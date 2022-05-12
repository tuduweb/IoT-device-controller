# Halt on errors
# set -eE

############# install_dependence #############
# install_build-deps() {
#     shift
#     status "Install OBS build dependencies"
#     trap "caught_error 'install_build-deps'" ERR

#     sudo apt-get install -y $@
# }

# # $@ 表示所有参数
# install_obs-deps() {
#     shift
#     status "Install OBS dependencies"
#     #$ trap "commands" signals #接收到signals指定的信号时，执行commands命令。
#     trap "caught_error 'install_obs-deps'" ERR

#     if [ -z "${DISABLE_PIPEWIRE}" ]; then
#         sudo apt-get install -y $@ libpipewire-0.3-dev
#     else
#         sudo apt-get install -y $@
#     fi
# }

    # step "Fetching OBS tags..."
    # /usr/bin/git fetch origin --tags

install_apt(){
    echo install_apt
    echo ========================================================
    shift #移args
    trap "caught_error 'install_build-deps'" ERR
    #sudo apt-get install -y $@
    sudo apt-get install -y python3-opencv
    if [ $? -ne 0 ];then
        exit 1
    fi
    trap "" ERR
}

install_pipPackage(){
    echo install_pipPackage
    echo ========================================================
    which pip3 > /dev/null
    if [ $? -ne 0 ];then
        #没有安装pip3..
        echo "no pip3"
        sudo apt-get install python3-distutils -y
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
	configpath=$clashdir/mark
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
    #似乎没有默认覆盖
    unzip -o $zipPath -d $appdir/
    [ $? -ne 0 ] && echo "文件解压失败！" && rm -rf $zipPath && exit 1 
    [ -f "$appdir/mark" ] || echo '#标识controlClient运行状态的文件，不明勿动！' > $appdir/mark

    #rm $zipPath
}

# 安装目录设置程序
# setdir(){
#     if [ -n "$systype" ];then
#         [ "$systype" = "Padavan" ] && dir=/etc/storage
#         [ "$systype" = "asusrouter" ] && dir=/jffs
#         [ "$systype" = "mi_snapshot" ] && dir=/data
#     else
#         echo -----------------------------------------------
#         $echo "\033[33m安装ShellClash至少需要预留约1MB的磁盘空间\033[0m"	
#         $echo " 1 在\033[32m/etc目录\033[0m下安装(适合root用户)"
#         $echo " 2 在\033[32m/usr/share目录\033[0m下安装(适合Linux设备)"
#         $echo " 3 在\033[32m当前用户目录\033[0m下安装(适合非root用户)"
#         $echo " 4 手动设置安装目录"
#         $echo " 0 退出安装"
#         echo -----------------------------------------------
#         read -p "请输入相应数字 > " num
#         #设置目录
#         if [ -z $num ];then
#             echo 安装已取消
#             exit 1;
#         elif [ "$num" = "1" ];then
#             dir=/etc
#         elif [ "$num" = "2" ];then
#             dir=/usr/share
#         elif [ "$num" = "3" ];then
#             dir=~/.local/share
#             mkdir -p ~/.config/systemd/user
#         elif [ "$num" = "4" ];then
#             echo -----------------------------------------------
#             echo '可用路径 剩余空间:'
#             df -h | awk '{print $6,$4}'| sed 1d 
#             echo '路径是必须带 / 的格式，注意写入虚拟内存(/tmp,/opt,/sys...)的文件会在重启后消失！！！'
#             read -p "请输入自定义路径 > " dir
#             if [ -z "$dir" ];then
#                 $echo "\033[31m路径错误！请重新设置！\033[0m"
#                 setdir
#             fi
#         else
#             echo 安装已取消！！！
#             exit 1;
#         fi
#     fi

#     if [ ! -w $dir ];then
#         $echo "\033[31m没有$dir目录写入权限！请重新设置！\033[0m" && sleep 1 && setdir
#     else
#         $echo "目标目录\033[32m$dir\033[0m空间剩余：$(dir_avail $dir)"
#         read -p "确认安装？(1/0) > " res
#         [ "$res" = "1" ] && clashdir=$dir/clash || setdir
#     fi
# }


############################ 主程序 ############################
# webget /tmp/clashversion https://raw.githubusercontent.com/juewuy/ShellClash/1.5.1/bin/release_version
# cat /tmp/clashversion

# [ "$result" = "200" ] && versionsh=$(cat /tmp/clashversion | grep "versionsh" | awk -F "=" '{print $2}')
# [ -z "$release_new" ] && release_new=$versionsh

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

# 处理tpiid
echo $tpiid > /tmp/educoder.cfg

# 主程序tar包, 和其他程序打包到了一块 故一次性下载
getMainZip

source ~/appdemo/CI/build_support.sh


# 安装依赖库
install_dependence

# echo "hello world"

# 运行包中的脚本..进入到下一个阶段?
bash $appdir/boot.sh