import ctypes
from scipy.io import loadmat
import numpy as np

# Define the C structures according to your C++ definitions
class OptionsAtti2Micro(ctypes.Structure):
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

class OptionsMicro2Shodf(ctypes.Structure):
    _fields_ = [
        ('L', ctypes.c_int),
        ('lambda_', ctypes.c_double),
        ('tl', ctypes.c_double),
        ('tu', ctypes.c_double),
        ('ADC0', ctypes.c_double),
        ('optimal', ctypes.c_bool),
        ('mask', ctypes.POINTER(ctypes.c_bool)),
        ('chkmod', ctypes.c_bool),
        ('flperp', ctypes.c_double),
        ('Flperp', ctypes.c_double),
        ('chunksz', ctypes.c_int),
        ('recrop', ctypes.c_bool),
        ('bth', ctypes.c_int)
    ]

# Load the shared libraries
atti2micro_dll = ctypes.CDLL('/home/osboxes/Documents/newdll/newdll.so')
micro2shodf_dll = ctypes.CDLL('/home/osboxes/Documents/micro2shodf/micro2shodf.so')

# Load the .mat file
data = loadmat('/home/osboxes/Documents/test_data.mat')

# Extract data
atti = data['atti'].astype(np.float32)
gi = data['gi'].astype(np.float64)
bi = data['bi'].astype(np.float64)
mask = data['mask'].astype(np.bool_)

# Create ctypes pointers from numpy arrays
atti_ptr = atti.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
gi_ptr = gi.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
bi_ptr = bi.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
mask_ptr = mask.ctypes.data_as(ctypes.POINTER(ctypes.c_bool))

# Prepare output arrays for atti2micro
atti_dims = atti.shape[:3]  # This extracts the sizes of the first three dimensions
lambdapar = np.zeros(atti_dims, dtype=np.float64)
lambdaperp = np.zeros(atti_dims, dtype=np.float64)
f = np.zeros(atti_dims, dtype=np.float64)

# Convert numpy arrays to ctypes pointers for outputs
lambdapar_ptr = lambdapar.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
lambdaperp_ptr = lambdaperp.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
f_ptr = f.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

# Initialize options for atti2micro
options_atti2micro = OptionsAtti2Micro(lambda_=0.006, tl=1.0e-7, tu=0.9999999, ADC0=3.0e-3,
                                       usef=False, bth=1, mlperp=0.01e-3, mu=5.0e-5,
                                       verbose=False, L=6, nu=0.0, nmax=100,
                                       dl=1.0e-8, dC=1.0e-6, regf=True, lpar=None,
                                       forcelpar=False, nolpwarn=False, fmin=0.01,
                                       fmax=1, mask=mask_ptr, chunksz=10000)

# Configure the DLL function call for atti2micro
atti2micro = getattr(atti2micro_dll, '_Z10atti2microPKfPKdS2_PK9struct1_TPdS6_S6_')  # Adjusted for mangled name

atti2micro.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(OptionsAtti2Micro),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double)
]
atti2micro.restype = None

# Call the atti2micro function
atti2micro(atti_ptr, gi_ptr, bi_ptr, ctypes.byref(options_atti2micro),
           lambdapar_ptr, lambdaperp_ptr, f_ptr)

# Output results of atti2micro
print("Lambdapar:", lambdapar.shape)
print("Lambdaperp:", lambdaperp.shape)
print("Fractional anisotropy (f):", f.shape)

# Prepare output array for micro2shodf
L = 8  # Set to the desired SH order
K = (L + 1) * (L + 2) // 2
sh_dims = atti.shape[:3] + (K,)  # Correct dimensions for sh
sh = np.zeros(sh_dims, dtype=np.float64)
sh_ptr = sh.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

# Initialize options for micro2shodf
options_micro2shodf = OptionsMicro2Shodf(L=L, lambda_=0.0005, tl=1.0e-6, tu=1-1.0e-6, ADC0=3.0e-3,
                                         optimal=True, mask=mask_ptr, chkmod=True, flperp=0.001,
                                         Flperp=0.999, chunksz=1000, recrop=False, bth=1)

# Access the micro2shodf function using its mangled name
micro2shodf = getattr(micro2shodf_dll, '_Z11micro2shodfPfPKdS1_S1_S1_PK9struct0_TRN5coder5arrayIdLi4EEE')

micro2shodf.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(OptionsMicro2Shodf),
    ctypes.POINTER(ctypes.c_double)
]
micro2shodf.restype = None

# Call the micro2shodf function
micro2shodf(atti_ptr, gi_ptr, bi_ptr, lambdapar_ptr, lambdaperp_ptr,
            ctypes.byref(options_micro2shodf), sh_ptr)

# Output results of micro2shodf
print("SH coefficients (sh):", sh.shape)
