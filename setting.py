#-*- coding:utf-8 -*-
import copy



class common:

    #nginx 全局参数

    global_config = {
                    "proxy_set_header":["X-Real-IP $remote_addr","Host $http_host","X-Forwarded-For $proxy_add_x_forwarded_for"],
                    "keepalive_requests": "5000",
                    "gzip": "on",
                    "keepalive_disable" : "none",
                    "gzip_min_length": "100",
                    "gzip_buffers": "4 16k",
                    "gzip_comp_level": "2",
                    "gzip_types": "text/plain application/javascript application/x-javascript text/css application/xml text/javascript application/x-httpd-php image/jpeg image/gif image/png",
                    "proxy_connect_timeout": "5s",
                    "proxy_read_timeout": "5s",
                    }

    
     # server block
    server_conf = {                  
                    "listen": '8088 backlog=10240',
                    "real_ip_header": "X-Forwarded-For",
                    "real_ip_recursive": "on",
                    "root":"/mobile",
                    "set_real_ip_from": ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16'],
                    "access_log": "/dev/stdout main",
                    "error_log": "/dev/stderr warn",                         
                  } 
    

 
    # location block
    location_conf = [
                     {"/healthz/":['return 200 "ok"']},                   
                    ]

       
class Development(common):
#    global_config = copy.deepcopy(common.global_config)
#    server_conf = copy.deepcopy(common.server_conf)
#    location_conf = copy.deepcopy(common.location_conf)
    
#    extra_conf = {
#        "access_log":"/var/log/nginx/access.log",
#        "error_log": "/var/log/nginx/error.log warn"
#       }
#    server_conf= dict(server_conf,**extra_conf)

    pass
class Production(common):
    pass

    
