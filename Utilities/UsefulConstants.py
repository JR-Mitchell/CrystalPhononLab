"""
Defining a few constants in units relevant to the meV energy scales
and other things going on in the phonon calculations
"""
from scipy.constants import Boltzmann, hbar, e, Avogadro

k_B = 1000*Boltzmann / e #The Boltzmann constant in units meV/K
h_bar = 1000*hbar / e #The reduced Planck constant in units meV/s
meV_to_recip_cm = 8.06554 #Conversion factor from meV to reciprocal cm