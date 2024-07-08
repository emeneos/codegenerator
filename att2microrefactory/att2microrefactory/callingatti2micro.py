import ctypes
from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt

# Define the C structure (matching your C++ header file)
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
        ('chunksz', ctypes.c_int),
        ('verbose', ctypes.c_bool)  # Ensure 'verbose' is the last field
    ]

# Load the shared library
my_dll = ctypes.CDLL('/home/osboxes/Documents/atti2micro.so')

# Load the .mat file
data = loadmat('/home/osboxes/Documents/test_data.mat')

# Extract data (including the mask)
atti = data['atti'].astype(np.float64)
gi = data['gi'].astype(np.float64)
bi = data['bi'].astype(np.float64)
mask = data['mask'].astype(np.bool_)
mask = np.ones(mask.shape)

# Ctypes Pointers
atti_ptr = atti.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
gi_ptr = gi.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
bi_ptr = bi.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
mask_ptr = mask.ctypes.data_as(ctypes.POINTER(ctypes.c_bool))

# Prepare output arrays
atti_dims = atti.shape[:3]
lambdapar = np.zeros(atti_dims, dtype=np.float64,order='F')
lambdaperp = np.zeros(atti_dims, dtype=np.float64,order='F')
f = np.zeros(atti_dims, dtype=np.float64,order='F')

# Output array pointers
lambdapar_ptr = lambdapar.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
lambdaperp_ptr = lambdaperp.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
f_ptr = f.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

# Initialize options (adjust values as needed)
lpar = np.ones(atti_dims, dtype=np.float64)
lpar_ptr = lpar.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

options_instance = Options(
    lambda_=0.006, tl=1.0e-7, tu=0.9999999, ADC0=3.0e-3,
    usef=False, bth=1, mlperp=0.01e-3, mu=5.0e-5,
    nu=0.0, nmax=100, dl=1.0e-8, dC=1.0e-6, 
    regf=True, lpar=lpar_ptr, forcelpar=False, nolpwarn=False, 
    fmin=0.01, fmax=1.0, mask=mask_ptr, chunksz=10000, verbose=False
)

# DLL Function Call
atti2micro = getattr(my_dll, '_Z10atti2microPKdS0_S0_PK9struct0_TPdS4_S4_')

atti2micro.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(Options),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double)
]
atti2micro.restype = None

# Call the C++ function
atti2micro(atti_ptr, gi_ptr, bi_ptr, ctypes.byref(options_instance),
           lambdapar_ptr, lambdaperp_ptr, f_ptr)


# Data Visualization (slice 5)
sl = 3 

# Extract slice data
F = f[:, :, sl].T
LPA = lambdapar[:, :, sl].T
LPP = lambdaperp[:, :, sl].T

# Colormap
cmap = 'gray'

# Create figure and subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle(f'Micro-Structure Model (Slice {sl})')

# Plot f (non-free water)
im1 = axes[0].imshow(F, cmap=cmap, vmin=0, vmax=1)
fig.colorbar(im1, ax=axes[0])
axes[0].set_title('f (non-free water)')
axes[0].axis('off')

# Plot lambdapar (parallel diffusivity)
im2 = axes[1].imshow(LPA, cmap=cmap, vmin=1.5e-3, vmax=3.0e-3)
fig.colorbar(im2, ax=axes[1])
axes[1].set_title('λ∥ (mm²/s)')
axes[1].axis('off')

# Plot lambdaperp (perpendicular diffusivity)
im3 = axes[2].imshow(LPP, cmap=cmap, vmin=0, vmax=0.3e-3)
fig.colorbar(im3, ax=axes[2])
axes[2].set_title('λ⊥ (mm²/s)')
axes[2].axis('off')

# Save the figure
plt.savefig(f'test_slice_{sl}.png') 

# Show the figure (optional)
plt.show()