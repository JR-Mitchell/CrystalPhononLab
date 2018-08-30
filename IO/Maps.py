import numpy as np
import Objects.Maps as maps

DEFAULT_OBJECT = maps.Map

def load_object_from_filepath(filepath):
    return np.loadtxt(filepath).view(maps.Map)