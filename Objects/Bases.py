import numpy as np
from ScatteringLengths.AtomicFormFactor import ElementScatterFactor

class Basis():
    """
    Describes the position (in terms of bravais lattice vectors) of
    a single atom in an atomic basis, alongside the form factor
    identifier and any kwargs for rendering differentiation
    """
    def __init__(self,atom,pos,**kwargs):
        """
        Describes the position (in terms of bravais lattice vectors) of
        a single atom in an atomic basis, alongside the form factor
        identifier and any kwargs for rendering differentiation
        
            :param pos:  Object    - Object describing the position of
                                     the atom relative to any lattice
                                     site, in terms of basis vectors.
                                     Must cast to an np.ndarray of 
                                     shape (3L,) 
            :param form_factor: String  - Identifier for the atom
                                          species present, e.g 'O' for
                                          Oxygen. For full details see
                                          ScatteringLengths docs
                                          
        For kwargs, see documentation of in-use rendering module.
        """
        self.atom = atom
        self.pos = np.array(pos)
        assert pos.shape == (3L,)
        self.kwargs = kwargs
        
    def add_kwarg(self,kwargdict):
        kwargkey = kwargdict.keys()[0]
        if self.atom in kwargdict[kwargkey]:
            self.kwargs[kwargkey] = kwargdict[kwargkey][self.atom]
        
    @property
    def xray_scatter_factor(self):
        return ElementScatterFactor(self.atom,using_neutrons=False)
        
    @property
    def neutron_scatter_factor(self):
        if "coh_b" in self.kwargs:
            return ElementScatterFactor(self.atom,using_neutrons=True,coh_b=float(self.kwargs["coh_b"]))
        else:
            print "Warning: no coh_b found for neutron scattering"
            self.neutron_form_factor = ElementScatterFactor(self.atom,using_neutrons=True)
        

class BasisList(list):
    """
    A wrapper for list specifically for storing Basis objects.
    """
    def __init__(self,*args):
        """
        A wrapper for list specifically for storing Basis objects.
        """
        if len(args) == 0: newArgs = []
        else: newArgs = [item if isinstance(item,Basis) 
            else _unpack_to_basis(*item) for item in args]
        list.__init__(self,newArgs)
        
    def add_kwargs(self,kwargdict):
        for item in self:
            item.add_kwarg(kwargdict)
            
        
def _unpack_to_basis(*args):
    if isinstance(args[-1],dict):
        return_basis = Basis(*args[:-1],**args[-1])
    else:
        return_basis = Basis(*args)
    return return_basis