#!/usr/bin/env python

# List files to get timestep numbers
# and feed them to cvmit_tave.py script
#
# Nikolay Koldunov koldunovn@gmail.com
# latest version: https://github.com/koldunovn/mit2cdf
#

import glob
import os
import cvmit_tave

fileList = glob.glob('Ttave.*.data')
fileList.sort()

for name in fileList:
    cvmit_tave.cnv2netcdf(name[6:16])


