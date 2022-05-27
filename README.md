## 一键安装脚本

### 脚本

```bash
export url='http://42.192.50.210:8082/' && export tpiid=10779044 && echo $tpiid > /tmp/educoder.cfg && wget -q -O /tmp/install.sh $url/install.sh && bash /tmp/install.sh

export url='http://42.192.50.210:8082/' && export tpiid=10779044 && wget -q -O /tmp/install.sh $url/install.sh && bash /tmp/install.sh
```

适配平台

```bash
export tpiID=10681875 && wget -O userfiles.zip https://website/api/myshixuns/download_file.json?tpiID=10681875 && unzip -d userfiles/ userfiles.zip && cd userfiles/ && sh run.sh
```

### 注意事项