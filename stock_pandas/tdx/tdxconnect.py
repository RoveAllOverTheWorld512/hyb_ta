# -*- coding: utf-8 -*-
"""
Created on 2019-11-04 11:34:45

author: huangyunbin

email: huangyunbin@sina.com

QQ: 592440193

"""

import configparser
cfg = configparser.ConfigParser()
cfg.read(r'D:\new_hxzq_hc\connect1.cfg')

r = cfg.options("HQHOST")

hostnum = cfg.getint("HQHOST", 'hostnum') 
hq_hosts = []   
for i in range(hostnum):
    name = 'hostname' + str(i + 101)[1:]
    name = cfg.get('HQHOST', name)
    ip = 'IPAddress' + str(i + 101)[1:]
    ip = cfg.get('HQHOST', ip)
    port = 'Port' + str(i + 101)[1:]
    port = cfg.getint('HQHOST', port)
    hq_hosts.append((name, ip, port))

