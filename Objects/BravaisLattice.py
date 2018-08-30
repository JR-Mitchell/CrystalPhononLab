import numpy as np
from Calculators.VectorTransform import apply_vector_map

class BravaisLattice():
    """
    Defines and holds information about the vectors of any particular 
    kind of Bravais lattice: the vectors as written in cartesian, and
    the equivalent axial distances and angles."""
    def __init__(self,*args,**kwargs):
        """
        Defines and holds information about the vectors of any 
        particular kind of Bravais lattice: the vectors as written in 
        cartesian, and the equivalent axial distances and angles.
        May be initialised in two ways:
            
        WAY 1 (Vectors):
            :param vector1: Object    - Object describing the cartesian
                                        lengths of the first lattice 
                                        vector, in units of Angstrom. 
                                        Must cast to an np.ndarray of
                                        shape (3L,) 
            :param vector2: Object    - As above but for the second 
                                        lattice vector
            :param vector3: Object    - As above but for the third 
                                        lattice vector
                                        
        WAY 2 (Axial distances & angles):
            :param lengths: Object    - Object describing the axial 
                                        distances (i.e side lengths) 
                                        of the lattice unit cell, 
                                        sometimes called a, b and c, in
                                        units of Angstrom. Must cast to 
                                        an np.ndarray of shape (3L,)
            :param angles:  Object    - Object describing the axial
                                        angles of the lattice unit cell,
                                        sometimes called alpha, beta 
                                        and gamma, in units of Degrees.
                                        Must cast to an np.ndarray of 
                                        shape (3L,)
        """
        if len(args) == 2: #lengths & angles
            self._lengths = a,b,c = np.array(args[0])
            self._angles = alph,beta,gamm = np.deg2rad(np.array(args[1]))
            vec1,vec2 = [a,0,0],[b*np.cos(gamm),b*np.sin(gamm),0]
            cx,cy = (c*np.cos(beta),
            c*(np.cos(alph) - np.cos(beta)*np.cos(gamm))/(np.sin(gamm)))
            vec3 = [cx,cy,np.sqrt(c**2 - cx**2 - cy**2)]
            self.vectors = np.array([vec1,vec2,vec3])
        elif len(args) == 3: # 3 vectors
            self._vectors = vec1,vec2,vec3 = np.array(args)
            a,b,c = [np.sqrt(np.dot(self.vectors[i],self.vectors[i])) 
            for i in (0,1,2)]
            self.angles = np.array([np.arcsin(np.dot(vec2,vec3)/(b*c)),
            np.arcsin(np.dot(vec1,vec3)/(a*c)),
            np.arcsin(np.dot(vec1,vec2)/(a*b))])
            self.lengths = np.array([a,b,c])
        else: raise AssertionError(
            "Arguments must be in given forms; read the darn docstrings")
            
        #Calculating reciprocal lattice vectors
        vecs = self.vectors
        self.volume = vol = abs(np.dot(vecs[0],np.cross(vecs[1],vecs[2])))
        self.recip = np.array([(2*np.pi*np.cross(vecs[i],vecs[j]))/(vol)
        for i,j in ((1,2),(2,0),(0,1))])
            
    @property
    def vectors(self):
        if hasattr(self,'_vectors'): return self._vectors
        else:
            a,b,c = self._lengths
            alph,beta,gamm = self._angles
            vec1,vec2 = [a,0,0],[b*np.cos(gamm),b*np.sin(gamm),0]
            cx,cy = (c*np.cos(beta),
            c*(np.cos(alph) - np.cos(beta)*np.cos(gamm))/(np.sin(gamm)))
            vec3 = [cx,cy,np.sqrt(c**2 - cx**2 - cy**2)]
            return np.array([vec1,vec2,vec3])
            
    @vectors.setter
    def vectors(self,value):
        assert value.shape == (3L,3L)
        self._vectors = value
        
    @property
    def lengths(self):
        if hasattr(self,'_lengths'): return self._lengths
        else: return np.array([np.sqrt(
            np.dot(self._vectors[i],self._vectors[i])
            ) for i in (0,1,2)])
            
    @lengths.setter
    def lengths(self,value):
        assert value.shape == (3L,)
        self._lengths = value
        
    @property
    def angles(self):
        if hasattr(self,'_angles'): return self._angles
        else:    
            a,b,c = self.lengths
            vec1,vec2,vec3 = self._vectors
            return np.array([np.arcsin(np.dot(vec2,vec3)/(b*c)),
                np.arcsin(np.dot(vec1,vec3)/(a*c)),
                np.arcsin(np.dot(vec1,vec2)/(a*b))])
                
    @angles.setter
    def angles(self,value):
        assert value.shape == (3L,)
        self._angles = value
        
    @property
    def volume(self):
        vecs = self.vectors
        return abs(np.dot(vecs[0],np.cross(vecs[1],vecs[2])))
        
    @property
    def recip(self):
        vecs = self.vectors
        vol = self.volume
        return np.array([(2*np.pi*np.cross(vecs[i],vecs[j]))/(vol)
            for i,j in ((1,2),(2,0),(0,1))])
        
    @property
    def recip_antimap(self):
        return np.linalg.inv(self.recip)
        
    def scale(self,scale_factors,mode='vectoral'):
        """
        Returns a new set of lattice vectors multiplied by given scale
        factor(s). E.g if self.vectors == [1,0,0],[0,1,0],[0,0,1],
        self.scale(2) gives a new BravaisLattice instance newObj
        w/ newObj.vectors == [2,0,0],[0,2,0],[0,0,2].
        Can also be specified by dimensions; e.g if self.vectors
        == [1,0,0],[-0.5,0.866,0],[0,0,1.633], self.scale([3,2,1])
        gives a new BravaisLattice instance newObj w/ newObj.vectors
        == [3,0,0],[-1,1.732,0],[0,0,1.633] if mode is 'vectoral'
        (i.e scale along the bravais vector directions) or newObj w/
        vectors [3,0,0],[-1.5,1.732,0],[0,0,1.633] if mode is 'cartesian'
        (i.e scale along x,y,z) 
        """
        assert mode in ['vectoral','cartesian'], (
        "Keyword argument mode of BravaisLattice.scale must be either"+
        " 'vectoral' or 'cartesian'.")
        if mode == 'vectoral':
            scaledVecs = (self.vectors.transpose()
                * np.array(scale_factors)).transpose()
        else:
            scaledVecs = self.vectors * np.array(scale_factors)
        return BravaisLattice(*scaledVecs)
     
    def abc_to_cartesian(self,abc):
        """
        Takes a vector in the form [A,B,C] (i.e vector = A*a + B*b + C*c
        where a,b,c are the bravais lattice vectors) and converts it
        to cartesian, i.e [vx,vy,vz].
        """
        return apply_vector_map(abc,self.vectors)   
          
    def hkl_to_cartesian(self,hkl):
        """
        Takes a vector in the form [h,k,l] (i.e vector = h*(a*) + k*(b*) + l*(c*)
        where a*,b*,c* are the reciprocal lattice vectors) and converts it
        to reciprocal cartesian, ie [vx*,vy*,vz*]
        """
        return apply_vector_map(hkl,self.recip)  
        
    def cartesian_to_hkl(self,cartesian):
        """
        Takes a vector in the form [vx*,vy*,vz*] and converts it
        to [h,k,l] form, i.e vector = h*(a*) + k*(b*) + l*(c*)
        where a*,b*,c* are the reciprocal lattice vectors
        """
        return apply_vector_map(cartesian,self.recip_antimap) 