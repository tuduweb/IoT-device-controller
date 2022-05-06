## 一键安装脚本

### 脚本

```bash
export url='http://172.20.144.113:8080/' && export tpiid=123456 && echo $tpiid > /tmp/educoder.cfg && wget -q -O /tmp/install.sh $url/install.sh && sh /tmp/install.sh
```

### 注意事项