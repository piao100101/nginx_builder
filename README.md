# Introduction
automatic build tools for nginx configuration which can generate specified location blocks by setting system environment.    
do some modification and encapsulation base on source code LinkedInAttic/nginx-config-builder. 

# Environment
```

#配置模式 开发环境选择development 生产环境production
SETTINGKIT_MODE=development

#location 信息 proxy=http时 proxy_pass代理 proxy=uwsgi时 uwsgi代理

SETTINGKIT_ITEM_LOCATION_0= "path=/api/&host=hr_back&port=3001&proxy=http&allow_ip=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
SETTINGKIT_ITEM_LOCATION_1 = "path=/&try_files=/index.html $uri.html $uri $uri/"

#server 块信息
SETTINGKIT_ITEM_SERVER_0 = "listen=3333&root=/pc"
SETTINGKIT_ITEM_SERVER_1 = "listen=3331&root=/apc"
SETTINGKIT_ITEM_SERVER_2 = "listen=3332&root=/cpc"

#i多个realip 以逗号分隔 此环境变量仅用于生产环境 开发环境可以不用写
SETTINGKIT_ITEM_REAL_IP = "35.186.245.2"

"""
全局的配置修改，请参考setting.py 
"""
```

```
python creator.py
```



