=========================
ZenPack to support Redis
=========================

Description
===========
This ZenPack supports  devices that are using Redis. Redis is an open source, BSD licensed, 
advanced key-value cache and store often used to front-end databases.  Multiple instances of 
Redis can be run on a single box, through different ports, and each instance can address multiple databases.

This ZenPack is built with the zenpacklib library so does not have explicit code definitions for
device classes, device and component objects or zProperties.  Templates are also created through zenpacklib.
These elements are all created through the zenpack.yaml file in the main directory of the ZenPack.
See http://zenpacklib.zenoss.com/en/latest/index.html for more information on zenpacklib.

Note that if templates are changed in the zenpack.yaml file then when the ZenPack is reinstalled, the
existing templates will be renamed in the Zenoss ZODB database and the new template from the YAML file
will be installed; thus a backup is effectively taken.  Old templates should be deleted in the Zenoss GUI
when the new version is proven.

The ZenPack uses the redis-py Python library which is automatically installed with Zenoss 4 and later.
See https://pypi.python.org/pypi/redis for more information.  Zenoss also automatically installs the
redis package which is useful for checking and debugging - see http://redis.io/ .
The Redis INFO command is the only one used at present though provision has been made in the
modeler code to run and parse other Redis commands.

The ZenPack introduces 3 new zProperties for configuring Redis:
    * zRedisDb                  default is the list [0, 1, 2, 3]
    * zRedisPorts               default is [6401, 6402, 6403, 6404]
    * zRedisPassword            default is the null string

The ZenPack creates a new device object called RedisDevice and new component types for:
    * Port
    * Database

where RedisDevice -> contains many RedisPort components -> contains many RedisDb components.

The /Server/Linux/Redis device class is supplied with appropriate zProperties 
and templates applied. Although a modeler plugin is supplied, it is not automatically
added to this device class, so as not to override any /Server/Linux plugins inherited in the
local environment.  The zPythonClass standard property is set to ZenPacks.community.zplib.Redis.RedisDevice
for the device class.

THE zplibRedis MODELER PLUGIN MUST BE MANUALLY ADDED TO YOUR /Server/Linux/Redis DEVICE
CLASS AFTER THE ZENPACK HAS BEEN INSTALLED.

Component templates for Port and Database are supplied with:
    * Port
        * CommandsProcessed
        * ConnectedClients
        * KeyspaceHits
        * KeyspaceMisses
        * MemFragRatio
        * UsedMemory
        * UsedCpuUser
    * Database
        * Keys
        * Expires
        * TTL

All the templates are based on Python and a dsplugins.py is provided in the main Zenpack
directory which analyses the Redis INFO command and parses the data into the defined
datapoints. These Python templates require the PythonCollector ZenPack to be installed as a 
prerequisite (version >=1.6)

The component display for a Port has a dropdown menu to show all related Databases.  The Databases 
component has a link back to its related Port.


A /Redis Event Class is included  with the ZenPack and is configured into the templates.


Requirements & Dependencies
===========================

    * Zenoss Versions Supported:  4.x
    * External Dependencies: 
        * The zenpacklib package that this ZenPack is built on, requires PyYAML.  This is installed as 
      standard with Zenoss 5 and with Zenoss 4 with SP457.  To test whether it is installed, as
      the zenoss user, enter the python environment and import yaml:

        python

        
        import yaml
        yaml

        <module 'yaml' from '/opt/zenoss/lib/python2.7/site-packages/PyYAML-3.11-py2.7-linux-x86_64.egg/yaml/__init__.py'>

      If pyYAML is not installed, install it, as the zenoss user, with:

        easy_install PyYAML

      and then rerun the test above.

        * The ZenPack also requires the Python redis library but this is installed as standard
      with Zenoss 4.0 and above.    

    * ZenPack Dependencies: PythonCollector >= 1.6
    * Installation Notes: Restart zenoss entirely after installation
    * Configuration: Add the zplibRedis modeler plugin to the /Server/Linux/Redis device class



Download
========
Download the appropriate package for your Zenoss version from the list
below.

* Zenoss 4.0+ `Latest Package for Python 2.7`_

ZenPack installation
======================

This ZenPack can be installed from the .egg file using either the GUI or the
zenpack command line. To install in development mode, from github - 
https://github.com/jcurry/ZenPacks.community.zplib.Redis  use the ZIP button
(top left) to download a tgz file and unpack it to a local directory, say,
$ZENHOME/local.  Install from $ZENHOME/local with:

zenpack --link --install ZenPacks.community.zplib.Redis

Restart zenoss after installation.

Device Support
==============

This ZenPack has been tested against Version 2.8.8 of Redis on Linux.


Change History
==============
* 1.0.0
   * Initial Release

Screenshots
===========

See the screenshots directory.


.. External References Below. Nothing Below This Line Should Be Rendered

.. _Latest Package for Python 2.7: https://github.com/jcurry/ZenPacks.community.zplib.Redis/blob/master/dist/ZenPacks.community.zplib.Redis-1.0.0-py2.7.egg?raw=true

Acknowledgements
================

This ZenPack has been developed under contract to TuneIn Inc who have generously open-sourced
it to the community.

