#!/usr/bin/env python
"""
Simply connect to a redis server and issue the info command.  Spit out the
results in a Nagios format.
"""

import redis

#myhost = '192.168.10.42' # zen42.class.example.org
myhost = '176.34.169.62' # zen42.class.example.org
myport = 16379
#myhost = '10.64.16.79' # sc01feedredis01
#myport = 6401

db = redis.Redis(host=myhost, port=myport)

# fetch stats
info_metrics = db.info()
# get config
config_metrics = db.config_get()
# get client_list
client_metrics = db.client_list()


print 'info metrics is %s\n\n' % (info_metrics)
print 'config metrics is %s\n\n' % (config_metrics)
print 'client metrics is %s' % (client_metrics)


