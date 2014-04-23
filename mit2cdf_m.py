import cvmit_tave
import multiprocessing
import sys

try:
    nproc = sys.argv[1]
except:
    print "You have to provide proper number of processers"
    sys.exit(1)

pool = multiprocessing.Pool(processes=int(nproc))

fileList = glob.glob('Ttave.*.data')[0:6]
fileList.sort()

for i in range(len(fileList)):
    fileList[i]=fileList[i][6:16]

r = pool.map(cvmit_tave.cnv2netcdf, fileList)

