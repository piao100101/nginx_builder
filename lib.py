#-*- coding:utf-8 -*-

from collections import namedtuple
class LocationDataModel:
  location_data = namedtuple('location_data',['path','host','rewrite','try_files','proxy','port','allow_ip'])  
  def __init__(self,nginx_location):
        self._locations = [ self.location_data(item.get("path"),item.get("host"),item.get("rewrite"),item.get("try_files"),item.get("proxy"),item.get("port"),item.get("allow_ip","all").split(",")) for item in nginx_location ]
 
  def __len__(self):
        return len(self._locations)
 
  def __getitem__(self, position):
        return self._locations[position]


class ServerDataModel:
  location_data = namedtuple('server_data',['listen','root'])  
  def __init__(self,server_location):
        self._locations = [ self.location_data(item.get("listen"),item.get("root")) for item in server_location ]
 
  def __len__(self):
        return len(self._locations)
 
  def __getitem__(self, position):
        return self._locations[position]
