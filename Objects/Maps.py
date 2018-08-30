import numpy as np

class Map(np.ndarray):
    pass
        
if __name__ == "__main__":
    a = np.random.rand(4,3)
    b = a.view(Map)