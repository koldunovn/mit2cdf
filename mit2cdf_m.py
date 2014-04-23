import cvmit_tave
import multiprocessing

try:
    nproc = sys.argv[1]
except:
    print "You have to provide proper number of processers"
    sys.exit(1)

pool = multiprocessing.Pool(processes=int(nproc))


for i in range(len(fileList)):
    fileList[i]=fileList[i][6:16]

r = pool.map(cvmit_tave.cnv2netcdf, fileList)

