import time
import psutil
import threading
from datetime import datetime
from test import conclude, resource
from mongodb import connections

### TESTING ###
this_process = psutil.Process()
temp = this_process.as_dict(["pid", "create_time"])
#resource("pid", temp["pid"])
#resource("create_time", datetime.fromtimestamp(temp["create_time"]))

# Lightweight data analytic process id
print("[Core] Lightweight Data Analytic Process ID: " + str(temp["pid"]))
print("[Core] Please ignore this program message, because it's contain all component message")

from middleware_subscriber import main_process as subscribe
from analytic import main_process as listen_raw 
from web_server import main_process as run_server

# Create thread for each component's main process
# Daemon must True, because all process need to closed if parent closed
#for process in [run_server]:
for process in [subscribe, listen_raw, run_server]:
    thread = threading.Thread(target=process)
    thread.setDaemon(True)
    thread.start()

### TESTING ###
#attribute_list = ["cpu_percent", "memory_percent", "io_counters"]

try:
    # Infinite loop
    while True:
        '''
        temp = this_process.as_dict(attribute_list)
        for attr in attribute_list:
            if attr == "io_counters":
                resource("disk_read", round(temp[attr][2] / 1048576, 1))
                resource("disk_write", round(temp[attr][3] / 1048576, 1))
            else:
                resource(attr, round(temp[attr], 1))
        '''
        time.sleep(1)
except:
    print("[Core] Lightweight Data Analytic Program Closed")
    #conclude()
    exit(0)
