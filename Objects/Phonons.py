import numpy as np
from Calculators.VectorTransform import apply_vector_map,vector_closest_map

class PhononSlice():
    def __init__(self,qvectors,evalues,evectors,qlastdigits,header_dict={}):
        self.header_dict = header_dict
        self.qvectors = qvectors
        self.evalues = evalues
        self.evectors = evectors
        self.qlastdigits = qlastdigits
        
    def map_closest_indices(self,q_vectors,pre_map = None):
        if pre_map is not None:
            phonon_qvectors_mapped = apply_vector_map(self.qvectors,pre_map)
        else:
            phonon_qvectors_mapped = self.qvectors
        return vector_closest_map(phonon_qvectors_mapped,q_vectors)
        
    @property
    def params(self):
        return self.qvectors,self.evalues,self.evectors,self.qlastdigits,self.header_dict
        
    @property
    def norm_evectors(self):
        evectors = self.evectors.copy()
        evect_mags = np.sqrt(np.real(evectors*evectors.conj()).sum(-1))
        return_evectors = (evectors.transpose() / evect_mags.transpose()).transpose()
        return return_evectors
        
class PhononMultiSlice(PhononSlice):
    def __init__(self,*slices,**mismatch_exceptions):
        PhononSlice.__init__(self,*slices[0].params)
        for slic in slices:
            for key,item in slic.header_dict.items():
                if key in self.header_dict and not key in mismatch_exceptions:
                    try:
                        assert item == self.header_dict[key], ("A PhononMultiSlice "+
                            "instance has been initialised with files containing"+
                            " mismatching headers. Either check that the files "+
                            "are valid to be used in conjunction or pass a "+
                            "keyword argument for any header identifiers where"+
                            " mismatches are unimportant. Mismatching "+
                            "key: {}".format(key))
                    except ValueError:
                        assert (item == self.header_dict[key]).all(), ("A PhononMultiSlice "+
                            "instance has been initialised with files containing"+
                            " mismatching headers. Either check that the files "+
                            "are valid to be used in conjunction or pass a "+
                            "keyword argument for any header identifiers where"+
                            " mismatches are unimportant. Mismatching "+
                            "key: {}".format(key))
                elif not key in mismatch_exceptions:
                    self.header_dict[key] = item
        self.qvectors = np.concatenate([qslice.qvectors for qslice in slices])
        self.evalues = np.concatenate([qslice.evalues for qslice in slices])
        self.evectors = np.concatenate([qslice.evectors for qslice in slices])
        self.qlastdigits = np.concatenate([qslice.qlastdigits for qslice in slices])