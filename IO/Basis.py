import numpy as np
import Objects.Bases as bas

DEFAULT_OBJECT = bas.BasisList

def load_object_from_filepath(filepath):
    with open(filepath,"r") as readFile:
        string = readFile.read()
    lines = string.split("\n")
    lines = [line.strip().split(",") for line in lines]
    lines = [[subline.strip() for subline in line] for line in lines]
    lines = [[line[0],np.array(line[1:],dtype=float)] for line in lines]
    bases = [bas.Basis(line[0],line[1]) for line in lines]
    basislist = bas.BasisList(*bases)
    return basislist