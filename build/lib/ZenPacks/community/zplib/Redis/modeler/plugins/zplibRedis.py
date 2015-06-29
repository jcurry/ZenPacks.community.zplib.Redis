"""Models Redis devices using the redis package

Simply connect to a redis server and issue the info command.  Spit out the
results in a Nagios format.
"""

import redis

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

# Zenoss Imports
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap


class zplibRedis(PythonPlugin):

    """Redis modeler plugin"""

    #relname = 'redisPorts'
    #modname = 'ZenPacks.community.zplib.Redis.RedisPort'

    requiredProperties = (
        'zRedisPorts',
        'zRedisDbs',
        'zRedisPassword',
        )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """Asynchronously collect data from device. Return a deferred."""
        log.info("%s: collecting data", device.id)

        redisPortList = getattr(device, 'zRedisPorts', None)
        if not redisPortList:
            log.error(
                "No zRedisPorts property set - please set this for the device")

            returnValue(None)
            
        redisPassword = getattr(device, 'zRedisPassword', None)
        if not redisPassword:
            # If no password set then use the null string - don't use None
            redisPassword = ''

        # response format is { <port no> : {'info':{ <info port response> }} , <port no> : {'client_list'{ <client port response> }} ,.....    }
        # where <info port response> format is { '<key name>':<key value>, '<key name>':<key value>, ......    }
        # wndhere <client port response> format is [ { '<key name>':<key value>, '<key name>':<key value>, ......    }]

        response = {}   
        for p in redisPortList:
            try:
                p_int = int(p)
                log.info("Issuing redis.Redis(host=%s, port=%s, password=%s) \n" % (device.manageIp, p_int, redisPassword))
                d = redis.Redis(host=device.manageIp, port=p_int, password=redisPassword)
                
                res={}
                res['info'] = yield d.info()
                res['client_list'] = yield d.client_list()
                response[p_int] = res
                #log.info('Response is %s \n' % (response))
            except Exception, e:
                log.error(
                    "%s: %s", device.id, e)
                returnValue(None)

        log.info('Response is %s \n' % (response))
        returnValue(response)

    def process(self, device, results, log):
        """Process results. Return iterable of datamaps or None."""

        maps = []
        ports = []
        #rm = self.relMap()

        redisDbs = getattr(device, 'zRedisDbs', None)
        if not redisDbs:
            # If no zRedisDbs then set to [0]
            redisDbs = [0, ]

        # zProperty zRedisDbs is list of integers eg [0,1,2,3].  key into data like db0, db1, db2, db3
        dbkeys = []
        for db in redisDbs:
            dbkeys.append('db'+str(db))
        log.info('dbkeys is %s \n ' % (dbkeys))

        dbData = {}
        for k,v in results.iteritems():
            portId = 'Port_' + self.prepId(str(k))

            dbDatak = {}
            log.info(' k is %s /n' % (k))
            for d in dbkeys:
                log.info(' In for loop for dbkeys - d is %s \n' % (d))
                v1= v['info'].get(d, None)
                log.info(' v1 is %s \n' % (v1))
                if v1:
                    log.info(' d is %s  and data  (v1) is %s \n' % (d, v1))
                    #dbData[d] = v1
                    dbDatak[d] = v1
            dbData[portId] = dbDatak

            ports.append(ObjectMap(data={
                'id': portId,
                'title': 'Port ' + str(k),
                'port_number': k,
                'redis_mode': v['info'].get('redis_mode', None),
                'role': v['info'].get('role', None),
                'redis_version': v['info'].get('redis_version', None),
                'uptime': v['info'].get('uptime_in_days', None),
                }))

        log.info('dbData is %s \n' % (dbData))
        maps.append(RelationshipMap(
            relname = 'redisPorts',
            modname = 'ZenPacks.community.zplib.Redis.RedisPort',
            objmaps = ports ))

        # Databases
        #maps.extend(self.getRedisDbRelMap(device, dbData, 'redisPorts/%s' % (portId), log))
        maps.extend(self.getRedisDbRelMap(device, dbData, log))

        return maps

    def getRedisDbRelMap(self, device, dbData, log):
        rel_maps = []

        log.info('In getRedisDbRelMap - dbData is %s  \n' % (dbData))
        for k,v in dbData.iteritems():
            compname = 'redisPorts/%s' % (k)
            object_maps = []
            for k1, v1 in v.iteritems():
		db_number = int(k1[-1])
		db_avg_ttl = v1.get('avg_ttl', None)
		db_keys = v1.get('keys', None)
		object_maps.append(ObjectMap(data={
		    'id': k + '_' + self.prepId(k1),
		    'title': k + '_' + self.prepId(k1),
		    'db_number': db_number,
		    'db_avg_ttl': db_avg_ttl,
		    'db_keys': db_keys,
		    }))
            rel_maps.append(RelationshipMap(
                compname = compname,
		relname = 'redisDbs',
		modname = 'ZenPacks.community.zplib.Redis.RedisDb',
		objmaps = object_maps))

        return rel_maps


