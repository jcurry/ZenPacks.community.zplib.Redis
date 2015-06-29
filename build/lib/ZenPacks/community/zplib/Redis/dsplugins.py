# Setup logging
import logging
log = logging.getLogger('zen.zplibRedis')

# PythonCollector Imports
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import PythonDataSourcePlugin

# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

import redis

class zplibRedisDeviceData(PythonDataSourcePlugin):
    """ Redis Device data source plugin """

    # List of device attributes you might need to do collection.
    proxy_attributes = (
        'zRedisPorts',
        'zRedisDbs',
        'zRedisPassword',
        )

    @classmethod
    def config_key(cls, datasource, context):
	#return (
	    #context.device().id,
	    #datasource.getCycleTime(context),
	    #context.id,
	    #'zplibRedisDeviceData',
	    #)
	# One call to the Redis API will get data for device and components
	#   so don't include context.id in the config_key return

	    return (
		context.device().id,
		datasource.getCycleTime(context),
		'zplibRedisDeviceData',
		)

    @classmethod
    def params(cls, datasource, context):
        # Don't need any params - zProperties passed as proxy_attributes
        return 

    @inlineCallbacks
    def collect(self, config):
        data = self.new_data()

        for datasource in config.datasources:
	    if not datasource.zRedisPorts:
		# If no zRedisPorts then set to [0,]
		datasource.zRedisPorts = [0, ]
	    if not datasource.zRedisPassword:
		# If no password set then use the null string - don't use None
		datasource.zRedisPassword = ''

            response = {}
	    for p in datasource.zRedisPorts:
		try:
		    p_int = int(p)
		    #log.info("Issuing redis.Redis(host=%s, port=%s, password=%s) \n" % (datasource.manageIp, p_int, datasource.zRedisPassword))
		    d = redis.Redis(host=datasource.manageIp, port=p_int, password=datasource.zRedisPassword)
		    res={}
		    res['info'] = yield d.info()
		    res['client_list'] = yield d.client_list()
		    response[p_int] = res
		    #log.info('Response is %s \n' % (response))
		except Exception, e:
		    log.error(
			"Failed to get zplibRedis data from %s: %s", datasource.device, e)
		    continue

	    dbkeys = []
	    for db in datasource.zRedisDbs:
		dbkeys.append('db'+str(db))
	    #log.info('dbkeys is %s \n ' % (dbkeys))
	    dbData = {}

            for k,v in response.iteritems():
                portId = 'Port_' + str(k)
                dbDatak = {}
	        # zProperty zRedisDbs is list of integers eg [0,1,2,3].  key into data like db0, db1, db2, db3
                if  datasource.component == portId:
		    for datapoint_id in (x.id for x in datasource.points):
			if not v['info'].has_key(datapoint_id):
			    continue
			try:
			    value = v['info'][datapoint_id]
			    #if isinstance(value, basestring):
			    #    value = value.strip(' %')
			    #value = float(value)
			except (TypeError, ValueError):
			    # Sometimes values are NA or not available.
			    continue
			dpname = '_'.join((datasource.datasource, datapoint_id))
			data['values'][datasource.component][dpname] = (value, 'N')
                else:
                    for d in dbkeys:
                        if not v['info'].has_key(d):
                            continue
                	dpointtest = portId + '_' + d
                        if datasource.component == dpointtest:
			    for datapoint_id in (x.id for x in datasource.points):
				try:
				    # v['info'] is now of the format eg. 'db0': { 'keys': 1234, 'expires': 2345, 'avg_ttl': 3456}
				    v1 = v['info'].get(d, None)
                                    if not v1.has_key(datapoint_id):
                                        continue
				    if v1.has_key(datapoint_id):
				      value = v1[datapoint_id]
				except (TypeError, ValueError):
				    continue
				dpname = '_'.join((datasource.datasource, datapoint_id))
				data['values'][datasource.component][dpname] = (value, 'N')

        returnValue(data)




