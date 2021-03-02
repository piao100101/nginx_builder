#-*- coding:utf-8 -*-

import sys
import os
from setuptools import setup, find_packages, Extension

setup (
      name = 'actkit.settingkit',
      version = '1.0',
      author = '91Act',
      author_email = 'liuchen@91act.com',
      maintainer = 'liuchen',
      maintainer_email = 'liuchen@91act.com',
      description = "settingkit",
      namespace_packages = ['actkit'],
      packages = ['actkit.settingkit'],
      package_dir = {'actkit.settingkit' : ''}
)