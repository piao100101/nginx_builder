#-*- coding:utf-8 -*-

import os

try:
    import gevent
except Exception as e:
    gevent = None


def _parse_type_str(type_str):
    type_obj = type_str

    if not type_str:
        return type_obj

    if type_str[0] != "(":
        return type_obj

    type_str_header = type_str[1:type_str.index(")")]
    type_str_body = type_str[type_str.index(")") + 1:]
    if type_str_header == "BOOL":
        type_obj = True if type_str_body == "1" else False
    elif type_str_header == "INT":
        type_obj = int(type_str_body)
    else:
        type_obj = type_str_body

    return type_obj

def _parse_kv_str_as_dict(kv_str, parse_type_str=True):
    kv_dict = {}

    if not kv_str:
        return kv_dict

    for v in kv_str.split("&"):
        kv = v.split("=")
        if len(kv) != 2:
            continue

        kv_dict[kv[0]] = _parse_type_str(kv[1]) if parse_type_str else kv[1]

    return kv_dict

def _parse_list_str_as_list(list_str, parse_type_str=True):
    list_list = []

    if not list_str:
        return list_list

    if type(list_str) != str and type(list_str) != unicode:
        return list_list

    for v in list_str.split(","):
        list_list.append(_parse_type_str(v) if parse_type_str else v)

    return list_list


class SettingObj(object):
    pass


class SettingItemSource(object):
    ENV = 1
    OBJ = 2
    REMOTE = 3
    RUNTIME = 4


class SettingItemPermission(object):
    R = 1
    W = 2


class SettingItem(object):
    def __init__(self, name, obj, raw, source, permission):
        self.name = name
        self.obj = obj
        self.raw = raw
        self.source = source
        self.permission = permission
        self.ParseRaw()

    def SetRaw(self, raw):
        self.raw = raw
        self.ParseRaw()

    def ParseRaw(self):
        if not self.raw:
            return

        if self.raw[0] == "(":
            obj_type = self.raw[1:self.raw.index(")")]
            obj_value = self.raw[self.raw.index(")") + 1:]
            if obj_type == "BOOL":
                self.obj = True if obj_value == "1" else False
            elif obj_type == "INT":
                self.obj = int(obj_value)
            elif obj_type == "STR":
                self.obj = obj_value
            else:
                self.obj = obj_value
        else:
            self.obj = self.raw


class SettingMode(object):
    def __init__(self, name):
        self.name = name
        self.runtime_version = 0
        self.items_by_source = {}
        self.items = {}

    def ClearItem(self, source):
        items_by_source = self.items_by_source.get(source)
        if not items_by_source:
            return

        items_by_source.clear()

    def AddItem(self, item):
        items_by_source = self.items_by_source.get(item.source)
        if not items_by_source:
            items_by_source = {}
            self.items_by_source[item.source] = items_by_source

        items_by_source[item.name] = item

    def GetItem(self, name):
        return self.items.get(name, None)

    def GetItemArray(self, name):
        item_array = []
        i = 0
        while True:
            item = self.items.get("{}_{}".format(name, i))
            if not item:
                break

            item_array.append(item)
            i += 1

        return item_array

    def GetItemArrayCount(self, name):
        i = 0
        while True:
            item = self.items.get("{}_{}".format(name, i))
            if not item:
                break

            i += 1

        return i

    def GetItemDict(self, name):
        item_dict = {}
        key_prefix = "{}_".format(name)
        for key in self.items.keys():
            if not key.startswith(key_prefix):
                continue

            final_key = key[len(key_prefix):]
            item_dict[final_key] = self.items[key]
        return item_dict

    def GetItemAll(self):
        return self.items

    def RefreshItem(self):
        self.items.clear()
        self.items.update(self.items_by_source.get(SettingItemSource.OBJ, {}))
        self.items.update(self.items_by_source.get(SettingItemSource.REMOTE, {}))
        self.items.update(self.items_by_source.get(SettingItemSource.RUNTIME, {}))
        self.items.update(self.items_by_source.get(SettingItemSource.ENV, {}))


class Setting(object):
    def __init__(self):
        self.runtime_extend_obj = None
        self.scope = ""
        self.modes = {}
        self.mode = ""
        self.mode_obj = None
        self.mode_lock = False
        self.obj_modules = []

    def GetScope(self):
        return self.scope

    def GetMode(self):
        return self.mode_obj.name

    def IsModeLocked(self):
        return self.mode_lock

    def GetItem(self, name, value_default):
        item = self.mode_obj.GetItem(name)
        if not item:
            return value_default

        return item.obj

    def GetItemAsInt(self, name, value_default):
        item = self.mode_obj.GetItem(name)
        if not item:
            return value_default

        try:
            return int(item.obj)
        except Exception as e:
            return value_default

    def GetItemAsBool(self, name, value_default):
        item = self.mode_obj.GetItem(name)
        if not item:
            return value_default

        try:
            obj_type = type(item.obj)
            if obj_type == bool:
                return item.obj
            elif obj_type == str or obj_type == unicode:
                return item.obj == "1"
            else:
                return value_default
        except Exception as e:
            return value_default

    def GetItemAsStr(self, name, value_default):
        item = self.mode_obj.GetItem(name)
        if not item:
            return value_default

        try:
            return str(item.obj)
        except Exception as e:
            return value_default

    def GetItemAsKV(self, name):
        item = self.mode_obj.GetItem(name)
        return _parse_kv_str_as_dict(item.obj if item else "")

    def GetItemAsList(self, name):
        item = self.mode_obj.GetItem(name)
        return _parse_list_str_as_list(item.obj if item else "")

    def GetItemArray(self, name):
        item_array = self.mode_obj.GetItemArray(name)
        return map(lambda l : l.obj, item_array)

    def GetItemArrayCount(self, name):
        return self.mode_obj.GetItemArrayCount(name)

    def GetItemArrayAsKV(self, name):
        item_array = self.GetItemArray(name)
        for i in range(0, len(item_array)):
            item_array[i] = _parse_kv_str_as_dict(item_array[i])
        return item_array

    def GetItemDict(self, name):
        _item_dict = self.mode_obj.GetItemDict(name)
        item_dict = {}
        for k, v in _item_dict.items():
            item_dict[k] = v.obj
        return item_dict

    def GetItemDictAsKV(self, name):
        item_dict = self.GetItemDict(name)
        for key in item_dict.keys():
            item_dict[key] = _parse_kv_str_as_dict(item_dict[key])
        return item_dict

    def GetItemAll(self):
        all_item = {}
        items = self.mode_obj.GetItemAll()
        for k, v in items.items():
            all_item[k] = v.obj

        return all_item

    def SetItem(self, name, value):
        mode_obj = self.mode_obj
        item = mode_obj.GetItem(name)
        if item and item.source == SettingItemSource.RUNTIME:
            item.SetRaw(value)
        else:
            item = SettingItem(name, None, value, SettingItemSource.RUNTIME, 0)
            mode_obj.AddItem(item)
            mode_obj.RefreshItem()

        if self.runtime_extend_obj:
            self.runtime_extend_obj.SetItem(self.scope, mode_obj.name, item.name, item.raw)
            self.runtime_extend_obj.IncreaseVersion(self.scope, mode_obj.name)

    def SetRuntimeExtend(self, runtime_extend_cls):
        self.runtime_extend_obj = runtime_extend_cls()
        self.SpawnRuntimeUpdate()
        return True

    def RefreshAllMode(self):
        for k, v in self.modes.items():
            v.RefreshItem()

    def Load(self):
        self.LoadAllModeFromEnviroment()
        self.LoadAllModeFromObject()
        self.RefreshAllMode()

    def LoadAllModeFromEnviroment(self):
        scope = os.getenv("SETTINGKIT_SCOPE")
        self.scope = scope if scope else ""

        mode = os.getenv("SETTINGKIT_MODE")
        self.mode = mode if mode else "development"

        mode_lock = os.getenv("SETTINGKIT_MODE_LOCK")
        self.mode_lock = mode_lock == "1"

        self.mode_obj = SettingMode(self.mode)
        self.modes[self.mode_obj.name] = self.mode_obj

        for k, v in os.environ.items():
            if not k.startswith("SETTINGKIT_ITEM_"):
                continue

            item_name = k[len("SETTINGKIT_ITEM_"):]
            item_raw = v

            item = SettingItem(item_name, None, item_raw, SettingItemSource.ENV, SettingItemPermission.R)
            self.mode_obj.AddItem(item)

        obj_modules = os.getenv("SETTINGKIT_OBJ_MODULES")
        if obj_modules:
            self.obj_modules.extend(obj_modules.split(";"))
        else:
            self.obj_modules.append("settings")

    def LoadAllModeFromObject(self):
        for obj_module_name in self.obj_modules:
            obj_module = None

            try:
                obj_module = __import__(obj_module_name, fromlist=[""])
            except Exception as e:
                continue

            for k, v in obj_module.__dict__.items():
                if not isinstance(v,type) or not issubclass(v, SettingObj):
                    continue

                if self.mode_lock and k != self.mode_obj.name:
                    continue

                mode_obj = self.modes.get(k)
                if not mode_obj:
                    mode_obj = SettingMode(k)
                    self.modes[mode_obj.name] = mode_obj

                for kk, vv in self.SettingObjToDict(v).items():
                    if kk == "SETTINGKIT_SCOPE" and not self.scope:
                        self.scope = vv

                    item = SettingItem(kk, vv, "", SettingItemSource.OBJ, SettingItemPermission.R)
                    mode_obj.AddItem(item)

    def LoadFromRemote(self):
        pass

    def LoadFromRuntime(self, mode_obj):
        if not self.runtime_extend_obj:
            return

        ver = self.runtime_extend_obj.GetVersion(self.scope, mode_obj.name)
        if ver <= mode_obj.runtime_version:
            return

        mode_obj.ClearItem(SettingItemSource.RUNTIME)
        items = self.runtime_extend_obj.GetAllItems(self.scope, mode_obj.name)
        for k, v in items.items():
            item = SettingItem(k, None, v, SettingItemSource.RUNTIME, 0)
            mode_obj.AddItem(item)

        #todo:ver changed

        mode_obj.runtime_version = ver
        mode_obj.RefreshItem()

    def UpdateMode(self):
        if self.mode_lock:
            return

        mode = self.runtime_extend_obj.GetMode(self.scope)
        if mode and mode != self.mode:
            self.ChangeMode(mode)

    def ChangeMode(self, mode, runtime_extend_set_mode=False):
        if self.mode_lock:
            return False, "mode:{} locked".format(self.mode)

        if mode == self.mode:
            return False, "mode:{} is current".format(self.mode)

        mode_obj = self.modes.get(mode)
        if not mode_obj:
            return False, "mode:{} is not support".format(mode)

        self.LoadFromRuntime(mode_obj)

        if runtime_extend_set_mode:
            self.runtime_extend_obj.SetMode(self.scope, mode)

        print "{}->{}".format(self.mode, mode_obj.name)
        self.mode_obj = mode_obj
        self.mode = self.mode_obj.name
        return True, ""

    def SettingObjToDict(self, setting_obj):
        dic = {}
        if setting_obj != SettingObj:
            for base in setting_obj.__bases__:
                dic.update(self.SettingObjToDict(base))
        for k, v in setting_obj.__dict__.iteritems():
            if not k.startswith('__') and not isinstance(v,classmethod):
                dic[k] = v
        return dic

    def SpawnRuntimeUpdate(self):
        if gevent:
            gevent.spawn(self.RuntimeUpdate)

    def RuntimeUpdate(self):
        if not gevent:
            return
        while True:
            self.UpdateMode()
            self.LoadFromRuntime(self.mode_obj)
            gevent.sleep(10)


class SettingRuntimeExtend(object):
    def GetMode(self, scope):
        pass

    def SetMode(self, scope, mode):
        pass

    def GetVersion(self, scope, mode):
        pass

    def GetVersionChangedItems(self, scope, mode, version):
        pass

    def IncreaseVersion(self, scope, mode):
        pass

    def SetVersionChangedItems(self, scope, mode, version, items):
        pass

    def GetAllItems(self, scope, mode):
        pass

    def GetItem(self, scope, mode):
        pass

    def SetItem(self, scope, mode, name, value):
        pass

_setting_obj_default = Setting()
def initialize(**kwargs):
    _setting_obj_default.Load()
    return True, "settingkit_initialize_ok"

def get_scope():
    return _setting_obj_default.GetScope()

def get_mode():
    return _setting_obj_default.GetMode()

def is_mode_locked():
    return _setting_obj_default.IsModeLocked()

def change_mode(mode):
    return _setting_obj_default.ChangeMode(mode, True)

def set_runtime_extend(runtime_extend_cls=None):
    return _setting_obj_default.SetRuntimeExtend(runtime_extend_cls)

def set_item(name, value):
    return _setting_obj_default.SetItem(name, value)

def get_item(name, value_default=None):
    return _setting_obj_default.GetItem(name, value_default)

def get_item_as_int(name, value_default=0):
    return _setting_obj_default.GetItemAsInt(name, value_default)

def get_item_as_bool(name, value_default=False):
    return _setting_obj_default.GetItemAsBool(name, value_default)

def get_item_as_str(name, value_default=""):
    return _setting_obj_default.GetItemAsStr(name, value_default)

def get_item_as_kv(name):
    return _setting_obj_default.GetItemAsKV(name)

def get_item_as_list(name):
    return _setting_obj_default.GetItemAsList(name)

def get_item_array(name):
    return _setting_obj_default.GetItemArray(name)

def get_item_array_count(name):
    return _setting_obj_default.GetItemArrayCount(name)

def get_item_array_as_kv(name):
    return _setting_obj_default.GetItemArrayAsKV(name)

def get_item_dict(name):
    return _setting_obj_default.GetItemDict(name)

def get_item_dict_as_kv(name):
    return _setting_obj_default.GetItemDictAsKV(name)

def get_item_all():
    return _setting_obj_default.GetItemAll()

get = get_item
get_as_int = get_item_as_int
get_as_bool = get_item_as_bool
get_as_str = get_item_as_str
get_as_kv = get_item_as_kv
get_as_list = get_item_as_list
get_array = get_item_array
get_array_as_kv = get_item_array_as_kv
get_array_count = get_item_array_count
get_dict = get_item_dict
get_dict_as_kv = get_item_dict_as_kv
get_all = get_item_all
parse_type_str = _parse_type_str
parse_kv_str_as_dict = _parse_kv_str_as_dict
source = SettingItemSource
permission = SettingItemPermission
obj = SettingObj
runtime_extend = SettingRuntimeExtend

__all__ = []
