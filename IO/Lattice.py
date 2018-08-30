import numpy as np
import Objects.BravaisLattice as lat

DEFAULT_OBJECT = lat.BravaisLattice

def load_object_from_filepath(filepath):
    with open(filepath,"r") as readFile:
        string = readFile.read()
    numbers = string.split(" ")
    lenno = len(numbers)
    assert lenno in (6,9)
    if len(numbers) == 6:
        lengths = np.array(numbers[0:3],dtype=float)
        angles = np.array(numbers[3:6],dtype=float)
        return lat.BravaisLattice(lengths,angles)
    else:
        vec1 = np.array(numbers[0:3],dtype=float)
        vec2 = np.array(numbers[3:6],dtype=float)
        vec3 = np.array(numbers[6:9],dtype=float)
        return lat.BravaisLattice(vec1,vec2,vec3)