#!/usr/bin/python3

# PERFORMANCE UTILS/SECURITY UPDATES SCRIPT
#
#   REQUIREMENT (MODULES)
#       python3-psutil - APT

import cgi	# cgi library
import cgitb	# debug cgi (displays useful web output if page fails!!)
cgitb.enable()

import json
import os
import psutil
import subprocess
import re

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


# (1) NESTED DICTIONARY - RESULTS FOR EACH AREA OF PERFORMANCE MONITOTING (ie. cpu/mem/procs) ARE
# ADDED TO A SINGLE GLOBAL DICTIONARY WITH A NESTED KEY STRUCTURE, WHERE A TOP LEVEL KEY REPRESENTING SPECIFIC STATISTIC AREA (ie. CPU_LOAD),
# THEN A FURTHER "NESTED KEY" CORRESPONDING TO UNIQUE INDEX FOR STATISTIC VALUE (ie. KEY "time_indec"
# FOLLOWED BY VALUE "load")
# (2) NESTED GLOBAL DICTIONARY THEN CONVERTED AND RETURNED AS "JSON" OBJECT!



# SCRIPT HEADER REQUIRED - SCRIPT FAILS IF NOT IN PLACE!!
def header():
	
	print("Content-Type: text/html\n\n")
	##        print("Content-Type: text/html;charset=utf-8")
	print()    



# ===============================
# 1. CPU LOAD AVERAGE (1/5/15)
# ===============================

def cpu_load():

    tup_time = ("1","5","15","100")
    tup_load = os.getloadavg()
    dict_load_avg = {}

    # Loop multiple tuple arrays in parallel
    #   - time index (1/5/15 mins)
    #   - load average (corresponding to relevant time index)
    for time,load in zip(tup_time,tup_load):

        # Nested dictionary - add results
        #   - nested key ['cpu_load']['time_index']
        #   - value (load avg for each nested key time index)
        #
        # check if 'cpu_load' top level key exists - if not add
        if 'cpu_load' not in dict_load_avg:

            dict_load_avg['cpu_load'] = { time : load}

        # append nested key if "cpu_load" key exists ([cpu_load][time]-> load)
        else:

            dict_load_avg['cpu_load'][time] = (load)


    return(dict_load_avg)



# =======================
# 2. CPU - IO WAIT TIME
# =======================

def cpu_io_stats():

    dict_io_stats = {}

    # cpustats - tuple element 5
    iowait = psutil.cpu_times().iowait

    # NEsted dictionary - add result
    dict_io_stats['cpu_iowait'] = iowait

    return dict_io_stats


# ============================
# 3. MEMORY USAGE - OUTPUT MB
# ============================


def mem_usage():

    # memory stats - extract
    #              - convert to MB (float x2 decimal places)
    mem = psutil.virtual_memory()

    dict_mem = {'mem_usage': {
        'mem_total' : "{0:.2f}".format(mem.total / 1024/ 1024),
        'mem_used_rss': "{0:.2f}".format(mem.used / 1024 / 1024),
        'mem_cached' : ("{0:.2f}".format(mem.cached / 1024/ 1024)),
        'mem_available' : ("{0:.2f}".format(mem.available / 1024/ 1024)),
        'mem_free' : ("{0:.2f}".format(mem.free / 1024/ 1024)),
        }
    }

    return dict_mem


# ===========================
# 4. DISK USAGE / READ/WRITE
# ===========================

def disk_usage():
    dict_device = {}

    # physical disk partition data extract - (ie. path/device/mountpoint)
    partition = psutil.disk_partitions(False)

    # loop partition data
    for disk in partition:

        # assign specific partition data to vars
        device = disk.device
        mount = disk.mountpoint
        filesystem = disk.fstype

        # exclude "SQUASH" devices (unecessary noise)
        filter = re.search('^squashfs',filesystem)

        if not filter:

            # disk usage stats object create - use "device path" extracted above for each disk
            disk_usage = psutil.disk_usage(device)

            # specific disk usage stats - assign to vars
            total_size = disk_usage.total
            total_used = disk_usage.used
            total_free = disk_usage.free
            total_used_percent = disk_usage.percent

