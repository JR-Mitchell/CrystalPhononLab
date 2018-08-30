import numpy as np

class Crystal():
    """
    Allows construction of a specific crystal system characteristics 
    from a Bravais lattice and atomic basis.
    """
    def __init__(self,basis_list,lattice):
        """
        Allows construction of a specific crystal system characteristics 
        from a Bravais lattice and atomic basis.
        
            :param basis_list: [Basis ...]  - List of Basis objects
                                            forming the system basis
            :param lattice: BravaisLattice  - The Bravais lattice
                                            defining the system structure
        """
        assert isinstance(basis_list, list) or isinstance(basis_list, tuple),(
        "Argument 1 of Crystal __init__ must be a list of objects"+
        " castable into an np.ndarray of numbers of shape (3L,)")
        self.basis_list = basis_list
        self.lattice = lattice
        
    def yield_lattice(self,shape):
        """
        Yields a specifically shaped tesselation of unit cells
        as a structural array of positions for each atom in the basis.
        For example, in rendering a crystal one could iterate through,
        plotting with respective characteristics & kwargs for each
        basis atom.
        
            :param shape: [Integer ...] - Length-3 list/tuple detailing
                                        the number of cells for the 
                                        tesselation in the direction of
                                        each bravais unit vector.
                                        
            :yield: (np.ndarray(shape = *shape,3),form_factor,dict kwargs)
        """
        xvect,yvect,zvect = self.lattice.vectors
        for basis in self.basis_list:
            basisPos = basis.pos
            basisDict = basis.kwargs
            sizes = [item for item in shape]
            for i in (0,1,2):
                if basisPos[i] == 0: sizes[i] += 1
                points = np.zeros((sizes[0],sizes[1],sizes[2],3))
                for x in range(sizes[0]):
                    for y in range(sizes[1]):
                        for z in range(sizes[2]):
                            points[x,y,z,:] = ((basisPos[0]+x)*xvect
                            + (basisPos[1]+y)*yvect +
                            (basisPos[2]+z)*zvect)
                yield (points,basisDict)