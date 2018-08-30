import numpy as np

def apply_vector_map(vector,mapping):
    """
    Takes an np.ndarray of shape (*subshape,4L) where the last 
    dimension is in the mapping basis and returns the same basis but with
    the last dimension in hkl basis.
    """
    if mapping.shape == (4L,3L):
        vector = vector - mapping[3] #4th vector is offset
        print vector
    homeSlice = [slice(None,None,None)]*(len(vector.shape) - 1)
    hSlice = tuple(homeSlice + [0]) #slice in form [: for item in ss,0]
    kSlice = tuple(homeSlice + [1]) #slice in form [: for item in ss,1]
    lSlice = tuple(homeSlice + [2]) #slice in form [: for item in ss,2]
    shapedh = np.tile(mapping[0],[num for num in vector.shape[:-1]]+[1])
    shapedk = np.tile(mapping[1],[num for num in vector.shape[:-1]]+[1])
    shapedl = np.tile(mapping[2],[num for num in vector.shape[:-1]]+[1])
    returnArr = np.zeros(vector.shape)
    for slic in (hSlice,kSlice,lSlice): returnArr[slic] = shapedh[slic]*vector[hSlice] + shapedk[slic]*vector[kSlice] + shapedl[slic]*vector[lSlice]
    return returnArr
    
def vector_closest_map(initial_vectors,final_vectors):
    final_vectors_flat = final_vectors.flatten().reshape(final_vectors.size/3,3)
    sqrt_dimension = int(np.ceil(np.sqrt(final_vectors.size/3)))
    def iterator():
        for i in range(sqrt_dimension):
            #initial_vectors in #ilen,3
            subsection = final_vectors_flat[i*sqrt_dimension:(i+1)*sqrt_dimension] #sslen,3
            q_displacements = initial_vectors.reshape(1,*initial_vectors.shape) - subsection.reshape(subsection.shape[0],1,subsection.shape[1])
            q_distances = np.sqrt((q_displacements**2).sum(-1))
            yield q_distances.argmin(1)
    index_map_flat = np.concatenate([item for item in iterator()])
    return index_map_flat.reshape(final_vectors.shape[:-1])