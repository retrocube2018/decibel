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

            # append results to disctionary of lists
            #
            # - check key exists, if not add new entry
            if 'disk_usage' not in dict_device:

                dict_device = {'disk_usage' :  { device : {
                        'mount_point' : mount,
                        'filesystem' : filesystem,
                        'total_size' : total_size,
                        'total_used' : total_used,
                        'total_used_percent' : total_used_percent,
                        'total_free' : total_free,
                        }
                    }
                }
            # - if key present, append nested key entry to existing key
            else:

                dict_device['disk_usage'][device] = (
                    {'mount_point' : mount,
                     'filesystem': filesystem,
                     'total_size': total_size,
                     'total_used': total_used,
                     'total_used_percent': total_used_percent,
                     'total_free': total_free,
                    }
                )

    return dict_device


# =============================
# 5. DISK PERFORMANCE - IO r/w
# =============================

def disk_performance():

    dict_disk_perf = {}

    # disk performance counters - each physical disk
    disk_perf = psutil.disk_io_counters(perdisk=True)

    # loop disk performance dictionary
    for k_device, v_stats in disk_perf.items():

        # exclude "loop" devices (unecessary noise)
        filter = re.search('^loop.*$',k_device)

        if not filter:

            # specific IO stats exctract
            read_bytes = v_stats[2]
            write_bytes = v_stats[3]
            read_time = v_stats[4]
            write_time = v_stats[5]


            # Results add to nested disctionary
            #
            # - check if key exists, add new key if not present
            if not 'disk_perf' in dict_disk_perf:

                dict_disk_perf = {'disk_perf': { k_device: {
                        'read_bytes' : read_bytes,
                        'write_bytes' : write_bytes,
                        'read_time' : read_time,
                        'write_time' : write_time,
                        }
                    }
                }

            # append entry if key already exists
            else:

                dict_disk_perf['disk_perf'][k_device] = (
                    {'read_bytes' : read_bytes,
                     'write_bytes' : write_bytes,
                      'read_time' : read_time,
                      'write_time' : write_time,
                   }
                )


    return dict_disk_perf


# =====================================
# 6. SECUYRITY UPDATES - CHECK (APT)
# =====================================

def update_check_pkg():

    dict_update_pkg = {}

    # Run "apt-check" system script to check available updates
    update_check = subprocess.check_output(["/usr/lib/update-notifier/apt-check -p"],shell=True,stderr=subprocess.STDOUT)

    # convert output encoding - utf-7
    update_check = update_check.decode(encoding="utf-8")

    # split output on newline
    update_check = update_check.split("\n")

    # Append results to dictionary
    for line in update_check:

        if 'update_packages' not in dict_update_pkg:

            dict_update_pkg['update_packages'] = ([line])

        else:
            dict_update_pkg['update_packages'].append(line)

    return dict_update_pkg



def report_JSON():

    # combine multiple dictionaries into a single SUPER dictionary
    report = { **cpu_load(), **cpu_io_stats(), **mem_usage(), **disk_usage(), **disk_performance(), **update_check_pkg() }

    # convert json object (from dictionary)
    report_JSON = json.dumps(report,indent=4)

    # HTML LAYOUT (MAINTAIN FORMATTING/STYLE WHEN OUTPUT TO HTML) -- (Pygments)
    html_JSON = (highlight(report_JSON, PythonLexer(), HtmlFormatter()))
    print(html_JSON)



if __name__ == "__main__":
    header()
    report_JSON()
