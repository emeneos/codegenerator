import ctypes
from scipy.io import loadmat
import numpy as np

# Define the C structure according to your C++ definitions
class Options(ctypes.Structure):
    _fields_ = [
        ('lambda_', ctypes.c_double),
        ('tl', ctypes.c_double),
        ('tu', ctypes.c_double),
        ('ADC0', ctypes.c_double),
        ('usef', ctypes.c_bool),
        ('bth', ctypes.c_int),
        ('mlperp', ctypes.c_double),
        ('mu', ctypes.c_double),
        ('verbose', ctypes.c_bool),
        ('L', ctypes.c_int),
        ('nu', ctypes.c_double),
        ('nmax', ctypes.c_int),
        ('dl', ctypes.c_double),
        ('dC', ctypes.c_double),
        ('regf', ctypes.c_bool),
        ('lpar', ctypes.POINTER(ctypes.c_double)),
        ('forcelpar', ctypes.c_bool),
        ('nolpwarn', ctypes.c_bool),
        ('fmin', ctypes.c_double),
        ('fmax', ctypes.c_double),
        ('mask', ctypes.POINTER(ctypes.c_bool)),
        ('chunksz', ctypes.c_int)
    ]

# Load the shared library
my_dll = ctypes.CDLL('/home/osboxes/Documents/newdll/newdll.so')

# Load the .mat file
data = loadmat('/home/osboxes/Documents/test_data.mat')

# Extract data
atti = data['atti'].astype(np.float32)
gi = data['gi'].astype(np.float64)
bi = data['bi'].astype(np.float64)

# Create ctypes pointers from numpy arrays
atti_ptr = atti.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
gi_ptr = gi.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
bi_ptr = bi.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

# Prepare output arrays
atti_dims = atti.shape[:3]  # This extracts the sizes of the first three dimensions
lambdapar = np.zeros(atti_dims, dtype=np.float64)
lambdaperp = np.zeros(atti_dims, dtype=np.float64)

f = np.zeros(188870, dtype=np.float64)

# Convert numpy arrays to ctypes pointers for outputs
lambdapar_ptr = lambdapar.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
lambdaperp_ptr = lambdaperp.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
f_ptr = f.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

# Initialize options
options_instance = Options(lambda_=0.006, tl=1.0e-7, tu=0.9999999, ADC0=3.0e-3,
                           usef=False, bth=1, mlperp=0.01e-3, mu=5.0e-5,
                           verbose=False, L=6, nu=0.0, nmax=100,
                           dl=1.0e-8, dC=1.0e-6, regf=True, lpar=None,
                           forcelpar=False, nolpwarn=False, fmin=0.01,
                           fmax=1, mask=None, chunksz=10000)

# Configure the DLL function call
atti2micro = getattr(my_dll, '_Z10atti2microPKfPKdS2_PK9struct1_TPdS6_S6_')  # Adjusted for mangled name

atti2micro.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(Options),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double)
]
atti2micro.restype = None

# Call the function
atti2micro(atti_ptr, gi_ptr, bi_ptr, ctypes.byref(options_instance),
           lambdapar_ptr, lambdaperp_ptr, f_ptr)

# Output results
print("Lambdapar:", lambdapar)
print("Lambdaperp:", lambdaperp)
print("Fractional anisotropy (f):", f)
