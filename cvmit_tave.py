#!/usr/bin/env python

# Converts binary MITgcm snapshots to netCDF.
#
# usage:
# cvmit_tave.py 0000010957
# or:
# python cvmit_tave.py 0000010957
# 
# You have to modify variables in the beggining of the file to match your setup.
#
# Dependencies:
#
# python-netCDF4
# numpy
#
# The output is close to the one produced by Arne Biastoch's
# FORTRAN program, but there are couple differences:
#
# - Sea ice related variables have zeros not NaNs in the wet points
#   where they are zero.
#
# - Calculation of the landmask based on Salinity (TS grid), U(U grid) and V (V grid) fields.
#   I assume that there are land points where values are zero.
#
# In order to save new variable you have to:
#    - add it's name to the "Variables to save" dictionary (2D or 3D)
#    - add another elif statement to the "Properties of the variables:" section
#
# Nikolay Koldunov koldunovn@gmail.com
# latest version: https://github.com/koldunovn/mit2cdf
#


import numpy as np
from netCDF4 import Dataset
import os
import sys
import time

numlist =  str(sys.argv[1])
Nx=480
Ny=416
Nr=50
expnam='POL06'
startDate='01-JAN-2000 00:00:00'
timeUnits = "seconds         "
deltaTclock=1200.
#iBinaryPrec=32.

# Gridding parameters
delZ= np.array([1.000000e+01, 1.000000e+01, 1.000000e+01, 1.000000e+01, 1.000000e+01,
       1.000000e+01, 1.000000e+01, 1.001000e+01, 1.003000e+01, 1.011000e+01,
       1.032000e+01, 1.080000e+01, 1.176000e+01, 1.342000e+01, 1.604000e+01,
       1.982000e+01, 2.485000e+01, 3.110000e+01, 3.842000e+01, 4.650000e+01,
       5.500000e+01, 6.350000e+01, 7.158000e+01, 7.890000e+01, 8.515000e+01,
       9.018000e+01, 9.396000e+01, 9.658000e+01, 9.825000e+01, 9.925000e+01,
       1.000100e+02, 1.013300e+02, 1.045600e+02, 1.113300e+02, 1.228300e+02,
       1.390900e+02, 1.589400e+02, 1.808300e+02, 2.035500e+02, 2.265000e+02,
       2.495000e+02, 2.725000e+02, 2.955000e+02, 3.185000e+02, 3.415000e+02,
       3.645000e+02, 3.875000e+02, 4.105000e+02, 4.335000e+02, 4.565000e+02])
phiMin=0.
thetaMin=0.
# np.array of delX values 
delX = np.ones(Nx); 
# np.array of delY values
delY = np.ones(Ny)

FillValue=-1.0e+23

# Do we need byteswap? Usually you need it if files
# were created on the big-endian machine, and conversion is
# happening on the little-endian machine (or vice versa).
byteswap = 1

# Parameter that will be used for masking. Should be 3d, usually salinity, U and V
paramFillTS = 'Stave'
paramFillU  = 'uVeltave'
paramFillV  = 'uVeltave'

# Value that will be used for masking
valueFill = 0.

#do we need compression?
czip = True

# level of compression (from 1 (fastest) to 9 (slowest))
compr = 4

#netCDF version
#Options:
#NETCDF3_CLASSIC, NETCDF3_64BIT, NETCDF4_CLASSIC, and NETCDF4
netcdfVersion = 'NETCDF4'


#Variables to save:
# 2D
variables = {'AREAtave':True,
             'HEFFtave':True,
             'ETAtave':True,
             'PHLtave':True,
             'UICEtave':True,
             'VICEtave':True,
             'HSNOWtave':False,
             'HSALTtave':False,
             'QNETtave':True,
             'QSWtave':True,
             'EmPmRtave':True,
             'FUtave':True,
             'FVtave':True,
             'UWINDtave':False,
             'VWINDtave':False,
             'sFluxtave':True,
             'tFluxtave':True,
             'uFluxtave':True,
             'vFluxtave':True}
#3D
variables3d ={'Ttave':True,
              'Stave':True,
              'uVeltave':True,
              'vVeltave':True,
              'wVeltave':True
              }

# Properties of the variables:
def gatrib(parname):
        '''Return attrubutes for known variables'''
           
        if (parname == 'HEFF') or (parname == 'HEFFtave'):
                sname = 'heff'
                name  = 'Eff. Ice Thickness'
                unit  = 'm'
                grid  = 'TS'
     
        elif (parname == 'AREA') or (parname == 'AREAtave'):
                sname = 'area' 
                name  = 'Ice Concentration'
                unit  = ' '
                grid  = 'TS'
        
        elif (parname == 'T') or (parname == 'Ttave'):
                sname = 'temp'
                name = 'Potential Temperature'
                unit = 'deg. C'
                grid = 'TS'
        
        elif (parname == 'S') or (parname == 'Stave'):
                sname = 'salt'
                name = 'Salinity'
                unit = 'PSU'
                grid = 'TS'
        
        elif (parname == 'uVel') or (parname == 'uVeltave'):
                sname = 'u'
                name = 'Zonal Velocity'
                unit = 'm/s'
                grid = 'U'
       
        elif (parname == 'vVel') or (parname == 'vVeltave'):
                sname = 'v'
                name = 'Meridional Velocity'
                unit = 'm/s'
                grid = 'V'
       
        elif (parname == 'wVel') or (parname == 'wVeltave'):
                sname = 'w'
                name = 'Vertical Velocity'
                unit = 'm/s'
                grid = 'W'
                
        elif (parname == 'ETA') or (parname == 'ETAtave'):
                sname = 'zeta'
                name = 'Sea Surface Height'
                unit = 'm'
                grid = 'TS'
      
        elif (parname == 'PHL') or (parname == 'PHLtave'):
                sname = 'phl'
                name = 'Bottom Dyn. Height Anom.'
                unit = 'm2/s2'
                grid = 'TS'
      
        elif (parname == 'UICE') or (parname == 'UICEtave'):
                sname = 'uice'
                name = 'Zonal Ice Velocity'
                unit = 'm/s'
                grid = 'U'
      
        elif (parname == 'VICE') or (parname == 'VICEtave'):
                sname = 'vice'
                name = 'Meridional Ice Velocity'
                unit = 'm/s'
                grid = 'V'
    
     
        elif (parname == 'HSNOW') or (parname == 'HSNOWtave'):
                sname = 'hsnow'
                name = 'Eff. Snow Thickness'
                unit = 'm'
                grid = 'TS'

        elif (parname == 'HSALT') or (parname == 'HSALTtave'):
                sname = 'hsalt'
                name = 'Eff. Ice Salinity'
                unit = 'g/m2'
                grid = 'TS'

        elif (parname == 'QNET') or (parname == 'QNETtave'):
                sname = 'qnet'
                name = 'Net upward surface heat flux (including shortwave)'
                unit = 'W/m2'
                grid = 'TS'

        elif (parname == 'QSW') or (parname == 'QSWtave'):
                sname = 'qsw'
                name = 'Net upward shortwave radiation'
                unit = 'W/m2'
                grid = 'TS'

        elif (parname == 'EmPmR') or (parname == 'EmPmRtave'):
                sname = 'emp'
                name = 'Net upward freshwater flux'
                unit = 'kg/m2/s'
                grid = 'TS'

        elif (parname == 'FU') or (parname == 'FUtave'):
                sname = 'fu'
                name = 'Zonal surface wind stress'
                unit = 'N/m2'
                grid = 'U'
                

        elif (parname == 'FV') or (parname == 'FVtave'):
                sname = 'fv'
                name = 'Meridional surface wind stress'
                unit = 'N/m2'
                grid = 'V'

        elif (parname == 'UWIND') or (parname == 'UWINDtave'):
                sname = 'uwnd'
                name = 'Zonal Wind'
                unit = 'm/s'
                grid = 'U'

        elif (parname == 'VWIND') or (parname == 'VWINDtave'):
                sname = 'vwnd'
                name = 'Meridional Wind'
                unit = 'm/s'
                grid = 'V'
        
        elif (parname == 'sFlux') or (parname == 'sFluxtave'):
                sname = 'sflux'
                name = 'salt flux'
                unit = 'psu.kg/m2/s'
                grid = 'TS'
        
        elif (parname == 'tFlux') or (parname == 'tFluxtave'):
                sname = 'tflux'
                name = 'Heat flux'
                unit = 'W/m2'
                grid = 'TS'
                
        elif (parname == 'uFlux') or (parname == 'uFluxtave'):
                sname = 'uflux'
                name = 'surface momentum flux'
                unit = 'N/m2'
                grid = 'U'
        
        elif (parname == 'vFlux') or (parname == 'vFluxtave'):
                sname = 'vflux'
                name = 'surface momentum flux'
                unit = 'N/m2'
                grid = 'U'

        else:
                sname = parname
                name = parname
                unit = 'some'
                grid = 'TS'

        return sname, name, unit, grid

# Define functions that will read MITgcm binary data:
def rmeta(filename):
        ''' Reads .meta file and return information about .data file.
        Usage: rmeta(filename)

        Input:
         filename = name of the .meta file (with .meta extention)
        
        Output:
         ndim                - Number of dimensions.
         xdim                - Xdim
         ydim                - Ydim
         zdim                - Zdim
         datatype                - Datatype
         nrecords                - Number of records.
         timeStepNumber        - Time step number

        '''
        
        ifile = open(filename, 'r')
        lines = ifile.readlines()
        ifile.close()

        ndim = int(lines[0].split()[3])
        ydim = int(lines[2].split()[0][:-1])
        xdim = int(lines[3].split()[0][:-1])

        if ndim == 2:
                increm = 0
                zdim = 1
        elif ndim == 3:
                zdim = int(lines[4].split()[0][:-1])
                increm = 1
        else:
                print("unsupported number of dimensions")
        
        datatype         = lines[5+increm].split()[3][1:-1]
        nrecords          = int(lines[6+increm].split()[3])
        
        if any("timeStepNumber" in s for s in lines):
                timeStepNumber = int(lines[7+increm].split()[3])
        else:
                timeStepNumber = 1        
        
        return ndim, xdim, ydim, zdim, datatype, nrecords, timeStepNumber

def mitbin2(filename, bswap=1, meta=None):
        '''Uses rmeta to get inforamtion about the file and return field extracted from it.
        
        Usage: mitbin2(filename, [bswap], [meta])
        
        Input:
         filename - path to the file.
         bswap - do we need a byte swap? Yes (1) or no (0) [default 1]
         meta        - None - flag to fix problem with wrong adxx*.meta files.
                         If meta = 'xx', use .meta file from xx files
        
        Output:
         nrecords*zdim*xdim*ydim numpy array of data.
        '''
        
        fd_data = open(filename, 'rb')
        if meta == None:
                ndim, xdim, ydim, zdim, datatype, nrecords, timeStepNumber = rmeta(filename[:-4]+"meta")
        elif meta == 'xx':
                ndim, xdim, ydim, zdim, datatype, nrecords, timeStepNumber = rmeta(filename[2:-4]+"meta")
        
        size = nrecords*zdim*xdim*ydim
        
        shape = (nrecords,zdim,xdim,ydim)
        
        data = np.fromfile(file=fd_data, dtype = datatype, count=size)
        
        data = data.reshape(shape)
        if bswap==1:
                data = data.byteswap()
        
        #data[np.isnan(data)] = 0

        fd_data.close()
        
        return data


# Grid creation

Lat_v = np.empty(Ny, dtype='float32')
Lat_t = np.empty(Ny, dtype='float32')
Lat_v[0]=phiMin
Lat_t[0]=phiMin+delY[0]*0.5
for j in range(1,Ny):
    Lat_v[j]=Lat_v[j-1]+delY[j-1]
    Lat_t[j]=Lat_t[j-1]+delY[j-1]

Lon_u = np.empty(Nx, dtype='float32')
Lon_t = np.empty(Nx, dtype='float32')
Lon_u[0]=thetaMin
Lon_t[0]=thetaMin+delX[0]*0.5
for i in range(1,Nx):
     Lon_u[i]=Lon_u[i-1]+delX[i-1]
     Lon_t[i]=Lon_t[i-1]+delX[i-1]

Dep_w = np.empty(Nr+1, dtype='float32') 
Dep_w[0]=0.
for k in range(1,Nr+1):
    Dep_w[k]=Dep_w[k-1]+delZ[k-1]

Dep_t = np.empty(Nr, dtype='float32')
for k in range(0,Nr):
     Dep_t[k]=(Dep_w[k]+Dep_w[k+1])*0.5
#Dep_w = Dep_w[:-1]

# Create masks for different grids:

maskTS = mitbin2('./'+paramFillTS+'.'+numlist+'.data')
maskU = mitbin2('./'+paramFillTS+'.'+numlist+'.data')
maskV = mitbin2('./'+paramFillTS+'.'+numlist+'.data')

maskTS[maskTS!=0]=1.
maskU[maskTS!=0]=1.
maskV[maskTS!=0]=1.

# Remove file if it's already exist
os.system('rm '+numlist+'.cdf')

print(numlist+'.cdf')

fw = Dataset(numlist+'.cdf', 'w', format=netcdfVersion )

# Global atributes:
fw.title = 'expnam'
fw.history = 'Created ' + time.ctime()

#Dimensions:
fw.createDimension('x_t', Lon_t.shape[0])
fw.createDimension('x_u', Lon_u.shape[0])
fw.createDimension('Depth_t', Dep_t.shape[0])
fw.createDimension('Depth_w', Dep_w.shape[0])
fw.createDimension('y_t', Lat_t.shape[0])
fw.createDimension('y_v', Lat_v.shape[0])
fw.createDimension('Time', None)

x_t = fw.createVariable('x_t', 'f', ('x_t',))
x_t.long_name = "X on T grid" 
x_t.units = " " 
x_t[:] = Lon_t[:]

x_u = fw.createVariable('x_u', 'f', ('x_u',))
x_u.long_name = "X on U grid" 
x_u.units = " " 
x_u[:] = Lon_u[:]

Depth_t = fw.createVariable('Depth_t', 'f',('Depth_t',))
Depth_t.long_name = "Depth of T grid points  "
Depth_t.units = "meters          "
Depth_t.positive = "down"
Depth_t.edges = "Depth_w"
Depth_t[:] = Dep_t[:]

Depth_w = fw.createVariable('Depth_w', 'f', ('Depth_w',)) 
Depth_w.long_name = "Depth at bottom of T box"
Depth_w.units = "meters          " 
Depth_w.positive = "down" 
Depth_w[:] = Dep_w[:]

y_t = fw.createVariable('y_t', 'f', ('y_t',)) 
y_t.long_name = "Y on T grid" 
y_t.units = " "
y_t[:] = Lat_t[:]

y_v = fw.createVariable('y_v', 'f',('y_v',))
y_v.long_name = "Y on V grid" 
y_v.units = " "
y_v[:] = Lat_v[:]

Time = fw.createVariable('Time', 'f', ('Time',))
Time.long_name = "Time                    "
Time.units = timeUnits
Time.time_origin = startDate
Time[:] = int(numlist)*deltaTclock

# Select 2D variables to use
variables_to_use = {}
for parameter in variables:
    if variables[parameter] == True:
        variables_to_use[parameter] = variables[parameter]

# Select 3D variables to use
variables_to_use3d = {}
for parameter in variables3d:
    if variables3d[parameter] == True:
        variables_to_use3d[parameter] = variables3d[parameter]

# Save 2D variables
for parameter in sorted(variables_to_use.iterkeys()):
    fname = './'+parameter+'.'+numlist+'.data'
    print fname
    ndim, xdim, ydim, zdim, datatype, nrecords, timeStepNumber = rmeta(fname[:-4]+"meta")
    sname, name, unit, grid = gatrib(parameter)
    
    # Select grid
    if ndim == 2:
        if grid == 'TS':
            dimTuple = ('Time', 'y_t', 'x_t',)
        
        elif grid == 'U':
            dimTuple = ('Time', 'y_t', 'x_u',)
        
        elif grid == 'V':
            dimTuple = ('Time', 'y_v', 'x_t',)
        
        else:
            raise Exception("The grid is not specified.\n For 2d variables can be 'TS','U' or 'V' ")
    
    # Create variable
    parVar = fw.createVariable(sname, 'f', dimTuple , fill_value=FillValue, zlib=czip, complevel=compr)
    parVar.long_name = name
    parVar.units = unit
    parVar.missing_value = FillValue
    parVar.grid = grid
    
    # Load data from binary file
    varValues = mitbin2(fname)
    
    # Mask and put the data in to the netCDF variable
    if ndim == 2:
    	if (grid == 'TS') or (grid =='W') :
    	    varValues = np.where(varValues[:,0,:,:] < -1.0e+20, FillValue, varValues[:])
            varValues = np.where(maskTS[:,0,:,:]==0, FillValue, varValues[:])
            parVar[:] = varValues[:,0,:,:]
        elif grid == 'U':
     	    varValues = np.where(varValues[:,0,:,:] < -1.0e+20, FillValue, varValues[:])
            varValues = np.where(maskU[:,0,:,:]==0, FillValue, varValues[:])
            parVar[:] = varValues[:,0,:,:]       	
        elif grid == 'V':
      	    varValues = np.where(varValues[:,0,:,:] < -1.0e+20, FillValue, varValues[:])
            varValues = np.where(maskV[:,0,:,:]==0, FillValue, varValues[:])
            parVar[:] = varValues[:,0,:,:]         	
    else:
        raise Exception("Grid dimensions should be 2D (plus time)")
    
    # Save data to disk
    fw.sync

#Same for 3D variables    
for parameter in sorted(variables_to_use3d.iterkeys()):
    fname = './'+parameter+'.'+numlist+'.data'
    print fname
    ndim, xdim, ydim, zdim, datatype, nrecords, timeStepNumber = rmeta(fname[:-4]+"meta")
    sname, name, unit, grid = gatrib(parameter)
    
    if ndim == 3:
        if grid == 'TS':
            dimTuple = ('Time', 'Depth_t', 'y_t', 'x_t',)
        
        elif grid == 'U':
            dimTuple = ('Time', 'Depth_t', 'y_t', 'x_u',)
        
        elif grid == 'V':
            dimTuple = ('Time', 'Depth_t', 'y_v', 'x_t',)
            
        elif grid == 'W':
            dimTuple = ('Time', 'Depth_w', 'y_t', 'x_t',)
        
        else:
            raise Exception("The grid is not specified.\n For 3d variables can be 'TS','U','V' or 'W' ")
            
            
    parVar = fw.createVariable(sname, 'f', dimTuple , fill_value=FillValue,  zlib=czip, complevel=compr)
    parVar.long_name = name
    parVar.units = unit
    parVar.missing_value = FillValue
    #parVar._FillValue = FillValue
    parVar.grid = grid

    varValues = mitbin2(fname)

    if ndim == 3:
        if grid == 'TS':
            varValues = np.where(varValues[:] < -1.0e+20, FillValue, varValues[:])
            varValues = np.where(maskTS[:]==0, FillValue, varValues[:])
            parVar[:] = varValues[:]
        elif grid == 'U':
            varValues = np.where(varValues[:] < -1.0e+20, FillValue, varValues[:])
            varValues = np.where(maskU[:]==0, FillValue, varValues[:])
            parVar[:] = varValues[:]
        elif grid == 'V':
            varValues = np.where(varValues[:] < -1.0e+20, FillValue, varValues[:])
            varValues = np.where(maskV[:]==0, FillValue, varValues[:])
            parVar[:] = varValues[:]
        elif grid == 'W':
            varValues = np.where(varValues[:] < -1.0e+20, FillValue, varValues[:])
            varValues = np.where(maskTS[:]==0, FillValue, varValues[:])
            varValues = np.concatenate((varValues,varValues[:,-1:,:,:]), axis=1)
            parVar[:] = varValues[:]
    else:
        raise Exception("Grid dimensions should be 3D (plus time)")
    fw.sync
        
fw.close()

