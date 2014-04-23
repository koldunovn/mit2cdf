# List files to get timestep numbers
# and feed them to cvmit_tave.py script
#
# Parallel version of the script to use with IPython parallel. 
# One has to specify number of threads!
#
# Nikolay Koldunov koldunovn@gmail.com
# latest version: https://github.com/koldunovn/mit2cdf
#

from IPython.parallel import Client
from subprocess import Popen, PIPE
import glob
import os
import cvmit_tave
import time 

#os.system('ipcluster start -n 4 &')
#def launch_cluster(n=2, *args):
#    return Popen(['ipcluster', 'start', '-n', str(n)] + list(args), stdout=PIPE, stderr=PIPE)

#def stop_cluster():
#    return Popen(['ipcluster', 'stop'], stdout=PIPE, stderr=PIPE)

#launch_cluster()

#time.sleep(2.)

c = Client()
dv = c[:]

fileList = glob.glob('Ttave.*.data')[0:6]
fileList.sort()

for i in range(len(fileList)):
    fileList[i]=fileList[i][6:16]

dv.map_sync(cvmit_tave.cnv2netcdf, fileList)

#stop_cluster()

#os.system('ipcluster stop')
