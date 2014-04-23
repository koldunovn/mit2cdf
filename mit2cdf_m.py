import cvmit_tave
import multiprocessing

pool = multiprocessing.Pool(processes=24)

fileList = glob.glob('Ttave.*.data')
fileList.sort()

for i in range(len(fileList)):
    fileList[i]=fileList[i][6:16]

r = pool.map(cvmit_tave.cnv2netcdf, fileList)

