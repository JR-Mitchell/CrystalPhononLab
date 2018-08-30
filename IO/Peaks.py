import numpy as np
import Objects.Peaks as peaks

DEFAULT_OBJECT = peaks.Peaks

def load_object_from_filepath(filepath):
    return np.loadtxt(filepath).view(peaks.Peaks)