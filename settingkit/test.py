#-*- coding:utf-8 -*-


import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append("..")
import settingkit

os.environ["SETTINGKIT_MODE"] = "development"
os.environ["SETTINGKIT_MODE_LOCK"] = "1"
os.environ["SETTINGKIT_ITEM_TEST_NAME"] = "test_name"
os.environ["SETTINGKIT_ITEM_TEST_NICK_NAME"] = "(STR)nick_name"
os.environ["SETTINGKIT_ITEM_TEST_AGE"] = "(INT)10"
os.environ["SETTINGKIT_ITEM_TEST_PHONE"] = "1111111111"
os.environ["SETTINGKIT_ITEM_TEST_FLAG_TRUE"] = "(BOOL)1"
os.environ["SETTINGKIT_ITEM_TEST_FLAG_FALSE"] = "(BOOL)0"
os.environ["SETTINGKIT_ITEM_TEST_SCORE_0"] = "(INT)80"
os.environ["SETTINGKIT_ITEM_TEST_SCORE_1"] = "(INT)81"
os.environ["SETTINGKIT_ITEM_TEST_SCORE_2"] = "(INT)82"
os.environ["SETTINGKIT_ITEM_TEST_SCORE_3"] = "(INT)83"
os.environ["SETTINGKIT_ITEM_TEST_SCORE_4"] = "(INT)84"
settingkit.initialize()

print settingkit.get_mode()

v = settingkit.get("TEST_NAME")
print "TEST_NAME={}, TYPE={}".format(v, type(v))

v = settingkit.get("TEST_NICK_NAME")
print "TEST_NICK_NAME={}, TYPE={}".format(v, type(v))

v = settingkit.get("TEST_AGE")
print "TEST_AGE={}, TYPE={}".format(v, type(v))

v = settingkit.get("TEST_PHONE")
print "TEST_PHONE={}, TYPE={}".format(v, type(v))

v = settingkit.get_as_int("TEST_PHONE")
print "TEST_PHONE={}, TYPE={}".format(v, type(v))

v = settingkit.get("TEST_FLAG_TRUE")
print "TEST_FLAG_TRUE={}, TYPE={}".format(v, type(v))

v = settingkit.get("TEST_FLAG_FALSE")
print "TEST_FLAG_FALSE={}, TYPE={}".format(v, type(v))

v = settingkit.get_as_str("TEST_FLAG_TRUE")
print "TEST_FLAG_TRUE={}, TYPE={}".format(v, type(v))

v = settingkit.get_as_str("TEST_FLAG_FALSE")
print "TEST_FLAG_FALSE={}, TYPE={}".format(v, type(v))

v = settingkit.get_array_count("TEST_SCORE")
print "TEST_SCORE_COUNT={}, TYPE={}".format(v, type(v))

v = settingkit.get_array("TEST_SCORE")
print "TEST_SCORE_ARRAY={}, TYPE={}".format(v, type(v))

v = settingkit.get_dict("TEST_SCORE")
print "TEST_SCORE_DICT={}, TYPE={}".format(v, type(v))

