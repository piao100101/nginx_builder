#-*- coding:utf-8 -*-
from nginx.config.api import Config, Section, KeyValueOption,Location,Map,KeyOption
from collections import namedtuple,OrderedDict
from nginx.config.api import Block
from nginx.config.helpers import duplicate_options


import settingkit
import os
import copy
from lib import LocationDataModel,ServerDataModel
import setting

os.environ["SETTINGKIT_ITEM_LOCATION_0"] = "path=/api/&host=hr_back&port=3001&proxy=http"
os.environ["SETTINGKIT_ITEM_LOCATION_1"] = "path=/&try_files=/index.html $uri.html $uri $uri/"
os.environ["SETTINGKIT_ITEM_REAL_IP"] = "35.186.245.2"
os.environ["SETTINGKIT_ITEM_LOGGING"] = "(BOOL)1"
#os.environ["SETTINGKIT_MODE"] = "production"
os.environ["SETTINGKIT_ITEM_SERVER_0"] = "listen=3333&root=/pc"
#os.environ["SETTINGKIT_ITEM_SERVER_1"] = "listen=3331&root=/apc"
#os.environ["SETTINGKIT_ITEM_SERVER_2"] = "listen=3332&root=/cpc"

"""
初始化settingkit
获取当前环境,默认为development
"""

settingkit.initialize()
mode = settingkit.get_mode()
env = setting.Production if mode == "production" else setting.Development

nginx_server = settingkit.get_array_as_kv("SERVER")
server_data_obj = ServerDataModel(nginx_server)
args=[]


"""
add RealIP
"""
if settingkit.get_as_list("REAL_IP"):
      env.server_conf["set_real_ip_from"] = env.server_conf["set_real_ip_from"] + settingkit.get_as_list("REAL_IP")
     
""" 
location block 处理
处理环境变量的location参数
"""
nginx_location = settingkit.get_array_as_kv("LOCATION")
location_data_obj = LocationDataModel(nginx_location)
location_config=Config()

for obj in location_data_obj:
      location_block={}
      host = obj.host if obj.host else obj.path
      if mode == "development":           
            if obj.proxy=="http" or obj.proxy=="https":
              if obj.port:
                reverse_proxy = "{proxy}://{host}:{port}".format(proxy=obj.proxy,host=host,port=obj.port)
              else:
                reverse_proxy = "{proxy}://{host}".format(proxy=obj.proxy,host=host)                    
              location_block = {"proxy_pass":reverse_proxy}
            if obj.proxy and obj.proxy=="uwsgi":
                  reverse_proxy = "${host}_upstream:{port}".format(host=host,port=obj.port)
                  location_block = {"include":"/etc/nginx/uwsgi_params","uwsgi_pass":reverse_proxy}
      else:
            if obj.proxy and obj.proxy=="http":
                  reverse_proxy = "${host}_upstream:{port}".format(host=host,port=obj.port)
                  location_block = {"proxy_pass":reverse_proxy}
            if obj.proxy and obj.proxy=="uwsgi":
                  reverse_proxy = "${host}_upstream:{port}".format(host=host,port=obj.port)
                  location_block = {"include":"/etc/nginx/uwsgi_params","uwsgi_pass":reverse_proxy}              
       
      if obj.rewrite:           
            location_block["rewrite"]=obj.rewrite

      if obj.try_files:
            location_block["try_files"]=obj.try_files
      
      location = Location(
            obj.path,           
            **location_block     
      )
      if obj.allow_ip != ["all"]:
            allow_ip = duplicate_options('allow',obj.allow_ip)
            deney = KeyValueOption('deny',value="all")
            location.sections.add(allow_ip,deney)
                                                  
      location_config.sections.add(location)
      
"""
location block 处理 
处理setting.py
"""
for location in env.location_conf:
      for key,value in location.items():
            l = Location(key,None)
            for v in value:
                  l.sections.add(KeyOption(v))
      location_config.sections.add(l)      



      
"""
  server block 处理
"""      
if mode == "production":     
      env.server_conf["set"] = ['${host}_upstream {host}.default.svc.cluster.local'.format(host=obj.host) for obj in location_data_obj if obj.host]
      env.server_conf["resolver"] = ['kube-dns.kube-system']

for obj in server_data_obj: 
      env.server_conf["listen"]=obj.listen
      env.server_conf["root"]=obj.root
      server = Section(
            'server',
            'true',
            Config(None,**env.server_conf),
            location_config
      )
      args.append(server)
      
args=tuple(args)

"""
  构建server block
"""  
nginx = Config(
     "true",
      Config(None,**env.global_config),
      *args            
)
print nginx


