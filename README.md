mit2cdf
=======

Converts binary MITgcm snapshots to netCDF.

The output is close to the one produced by Arne Biastoch's
FORTRAN program, but there are couple differences:

- Sea ice related variables have zeros not NaNs in the wet points
   where they are zero.

- Calculation of the landmask based on Salinity (TS grid), U(U grid) and V (V grid) fields.
   I assume that there are land points where values are zero.

In order to save new variable you have to:
- add it's name to the "Variables to save" dictionary (2D or 3D)
- add another `elif` statement to the "Properties of the variables:" section

Usage
=====

`cvmit_tave.py 0000010957`

**or:**

`python cvmit_tave.py 0000010957`
 
You have to modify variables in the beggining of the file to match your setup.

Dependencies:
=============

python-netCDF4

numpy

=====
Nikolay Koldunov koldunovn@gmail.com

latest version: https://github.com/koldunovn/mit2cdf


