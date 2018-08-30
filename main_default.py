# import Tools.BraggCalculator as bragg #wiped
#import Tools.CrystalFromParams as cpam #replace with crystal initialisation
#import Tools.CrystalFromPhonons as cpho #replace with phonon tocrystal / crystal initialisation
#import Tools.ImageMappingFinder as mapp #include
#import Tools.IntensityCalculator as inte #include
#import Tools.PeakComparison as comp 
#import Tools.PeakFinder as find #needs redoing, ignore for now
#import Tools.PhononSlicer as slic #have dedicated slice mechanism; use for phonon importing as well as for pre-processing
# import Tools.TroubleshootQdot as qdot
#import Tools.BraggCalculator as brag #also part of intensity calculator
#import Tools.TroubleshootMapping as tmap #also part of intensity calculator
from Calculators.DistributedIntensityCalculator import phonon_intensity,bragg_intensity,scattering_intensity,set_maximum_processes_multiprocessing
from Calculators.IntensityCalculator import generate_vector_grid

#Done: Phonon intensity 
#To do: crystal initialisation from params and phonon, mapping finder, intensity calculator, slicer
#To do less urgent: make generate_grid work for any dims, determine if it's better to use Crystal objects or tuples; sort out.