import numpy as np

from Utilities.UsefulConstants import h_bar,k_B,Avogadro,e,meV_to_recip_cm
from ScatteringLengths.AtomicFormFactor import ElementScatterFactor
from Calculators.VectorTransform import apply_vector_map

##This is all m=1 stuff. Todo: calculate m=0 stuff

#Notes for improvement
#A lot of this is just things copied and pasted over and over again.
#All this should take HKL grids along w/ other stuff and do primary calculations.

def bose_einstein(energy,T):
    return 1/(np.exp(energy/(k_B*T)) - 1)
    
def delta(energies,fineness):
    deltas = np.zeros(energies.shape) + 1 #(energy,qlen_1,qlen_2,qlen_3,modes)
    deltas[(energies)**2 > (fineness)**2] = 0
    return deltas   

def arange(*vector_limits):
    length = len(vector_limits)
    assert length in (1,3)
    if len(vector_limits) == 3: return np.arange(*vector_limits)
    else: return np.array(vector_limits)
    
#! TODO: MAKE ANY N VECTOR GRID GENERATABLE
def generate_vector_grid(vector_1,vector_1_limits,vector_2,vector_2_limits,vector_3,vector_3_limits,mapping=None,is_mapped=[False,False,False]):
    q_range_1,q_range_2,q_range_3 = arange(*vector_1_limits),arange(*vector_2_limits),arange(*vector_3_limits)
    vectors_correct = [None,None,None]
    ranges_correct = [None,None,None]
    for i in (0,1,2):
        if is_mapped[i]:
            vectors_correct[i] = apply_vector_map((vector_1,vector_2,vector_3)[i],mapping[:3])
            if mapping.shape == (4L,3L):
                ranges_correct[i] = (q_range_1,q_range_2,q_range_3)[i] - np.dot((vector_1,vector_2,vector_3)[i],mapping[3])
            else:
                ranges_correct[i] = (q_range_1,q_range_2,q_range_3)[i]     
        else:
            vectors_correct[i] = (vector_1,vector_2,vector_3)[i]
            ranges_correct[i] = (q_range_1,q_range_2,q_range_3)[i]
    q_range_1_correct,q_range_2_correct,q_range_3_correct = ranges_correct
    vector_1_correct,vector_2_correct,vector_3_correct = vectors_correct
            
    q_vectors_hkl = q_range_1_correct.reshape(len(q_range_1_correct),1,1,1)*vector_1_correct.reshape(1,1,1,3) + q_range_2_correct.reshape(1,len(q_range_2_correct),1,1)*vector_2_correct.reshape(1,1,1,3) + q_range_3_correct.reshape(1,1,len(q_range_3_correct),1)*vector_3_correct.reshape(1,1,1,3)
#    k_vectors_hkl = q_vectors_hkl - np.round(q_vectors_hkl)
#    q_vectors_cartesian = crystal.lattice.hkl_to_cartesian(q_vectors_hkl)
#    k_vectors_cartesian = crystal.lattice.hkl_to_cartesian(k_vectors_hkl)
    return q_vectors_hkl
    
def calculate_bragg(crystal,q_vectors_hkl,temperature=273.15,N=1e23,use_neutrons=False,print_info=True):
    k_vectors_hkl = q_vectors_hkl - np.round(q_vectors_hkl)
    q_vectors_cartesian = crystal.lattice.hkl_to_cartesian(q_vectors_hkl)
    k_vectors_cartesian = crystal.lattice.hkl_to_cartesian(k_vectors_hkl)
    q_diff_min = np.sqrt((q_vectors_cartesian**2).sum(-1).flatten())
    q_diff_min = (q_diff_min[1:] - q_diff_min[:-1]).min()
    if use_neutrons:
        scattering_factors = [ElementScatterFactor(base.atom,True,float(base.kwargs["coh_b"])).f(np.sqrt((q_vectors_cartesian**2).sum(-1))) for base in crystal.basis_list]
    else:
        scattering_factors = [ElementScatterFactor(base.atom,False).f(np.sqrt((q_vectors_cartesian**2).sum(-1))) for base in crystal.basis_list]
        
    def iterator():
        for index,atom in enumerate(crystal.basis_list):
            front_term = scattering_factors[index] #(qlen_1,qlen_2,qlen_3)
            exp_term = np.exp(1j * (q_vectors_cartesian*crystal.lattice.abc_to_cartesian(atom.pos).reshape(1,1,1,3)).sum(-1)) #(qlen_1,qlen_2,qlen_3)
            temp_term = 1
            yield front_term*exp_term*temp_term
    sum_over_basis = sum(iterator())
    sum_over_basis_squared = np.abs(sum_over_basis * sum_over_basis.conjugate()) #(qlen_1,qlen_2,qlen_3)
    print k_vectors_cartesian.shape
    distfrombragg = (k_vectors_cartesian**2).sum(-1)
    print distfrombragg.shape
    print (distfrombragg[:,1:] < distfrombragg[:,:-1]).shape
    minima = np.concatenate([np.ones((1,distfrombragg.shape[1],1),dtype=bool), 
        distfrombragg[1:] < distfrombragg[:-1]]) & np.concatenate([distfrombragg[:-1] < distfrombragg[1:],
        np.ones((1,distfrombragg.shape[1],1),dtype=bool)]) & np.concatenate([np.ones((distfrombragg.shape[0],1,1),dtype=bool),
        distfrombragg[:,1:] < distfrombragg[:,:-1]],1) & np.concatenate([distfrombragg[:,:-1] < distfrombragg[:,1:],
        np.ones((distfrombragg.shape[0],1,1),dtype=bool)],1)
    return sum_over_basis_squared * minima * N          
    
def calculate_dispersion(crystal,phonons,energy_limits,vector_grid,temperature=273.15,N=1e23,use_neutrons=False,flip_energies=False,print_info=True):
    modes_number = phonons.evalues.shape[1]
    # atoms_number = phonons.evalues.shape[2]
    q_vectors_cartesian,k_vectors_cartesian = vector_grid #(qlen_1,qlen_2,qlen_3,xyz)
    assert q_vectors_cartesian.size < 1200000
    if use_neutrons:
        scattering_factors = [ElementScatterFactor(base.atom,True,float(base.kwargs["coh_b"])).f(np.sqrt((q_vectors_cartesian**2).sum(-1))) for base in crystal.basis_list]
    else:
        scattering_factors = [ElementScatterFactor(base.atom,False).f(np.sqrt((q_vectors_cartesian**2).sum(-1))) for base in crystal.basis_list]
    if print_info: print "Mapping values to nearest phonon q-points..."
    index_map = phonons.map_closest_indices(k_vectors_cartesian,pre_map = crystal.lattice.recip)
    eigenvectors_nearest = phonons.norm_evectors[index_map] #(qlen_1,qlen_2,qlen_3,modes,ions,xyz)
    eigenvalues_nearest = phonons.evalues[index_map] #(qlen_1,qlen_2,qlen_3,modes)
    if print_info: print "Summation over basis atoms..."
    eigenvectors_deconstructed = [item for item in np.moveaxis(eigenvectors_nearest,4,0)]     #shape from (qlen_1,qlen_2,qlen_3,modes,ions,xyz) to ions[(qlen_1,qlen_2,qlen_3,modes,xyz)]  

    def iterator():
        for index,atom in enumerate(crystal.basis_list):
            masses_au = np.array(atom.kwargs["mass"],dtype=float)
            masses_kg = 0.001*masses_au / Avogadro
            front_term = scattering_factors[index]/np.sqrt(masses_kg) #(qlen_1,qlen_2,qlen_3)
            q_vectors_tiled = np.moveaxis(np.tile(q_vectors_cartesian,(modes_number,1,1,1,1)),0,3)     #shape from (qlen_1,qlen_2,qlen_3,xyz) to (qlen_1,qlen_2,qlen_3,modes,xyz)
            dot_term = (q_vectors_tiled*(eigenvectors_deconstructed[index])).sum(-1) #(qlen_1,qlen_2,qlen_3,modes)
            exp_term = np.exp(1j * (q_vectors_tiled*crystal.lattice.abc_to_cartesian(atom.pos).reshape(1,1,1,1,3)).sum(-1)) #(qlen_1,qlen_2,qlen_3,modes)
            square_disp = 3 *(0.5 + bose_einstein(eigenvalues_nearest/h_bar,temperature))*(h_bar**2)/(masses_au*eigenvalues_nearest) #(qlen_1,qlen_2,qlen_3,modes)
            square_disp = square_disp * (10**(20) * e) / Avogadro ##Getting into units of A**2
            temp_term = np.exp(-square_disp*np.sqrt((q_vectors_tiled**2).sum(-1)/3)) #shape: (qlen_1,qlen_2,qlen_3,modes)
            yield front_term.reshape(*(list(front_term.shape)+[1]))*dot_term*exp_term*temp_term
    sum_over_basis = sum(iterator())
    sum_over_basis_squared = np.abs(sum_over_basis * sum_over_basis.conjugate()) #(qlen_1,qlen_2,qlen_3,modes)

    if print_info: print "Calculation of Bose-Einstein distribution factors for modes..."
    if len(energy_limits) == 3: fineness = energy_limits[2] * 0.501
    else: fineness = 0.25
    energies = arange(*energy_limits).astype(float)
    energies[abs(energies) < 0.001] = 0.001
    number_term = bose_einstein(eigenvalues_nearest,temperature) #(qlen_1,qlen_2,qlen_3,modes)
    number_term_closest = bose_einstein(energies,temperature)
    delta_plus_term = delta(energies.reshape(energies.shape[0],1,1,1,1) + eigenvalues_nearest.reshape(1,*eigenvalues_nearest.shape),fineness) #(energy,qlen_1,qlen_2,qlen_3,modes)
    delta_minus_term = delta(energies.reshape(energies.shape[0],1,1,1,1) - eigenvalues_nearest.reshape(1,*eigenvalues_nearest.shape),fineness) #(energy,qlen_1,qlen_2,qlen_3,modes)
    if flip_energies:
        delta_bose_einstein = (number_term.reshape(1,*number_term.shape) + 0)*(delta_plus_term) + (number_term.reshape(1,*number_term.shape) + 1)*(delta_minus_term) #(energy,qlen_1,qlen_2,qlen_3,modes)
        delta_bose_einstein_closest = (number_term_closest.reshape(len(number_term_closest),1,1,1,1) + 0)*(delta_plus_term) + (number_term_closest.reshape(len(number_term_closest),1,1,1,1) + 1)*(delta_minus_term) #(energy,qlen_1,qlen_2,qlen_3,modes)
    else:
        delta_bose_einstein = (number_term.reshape(1,*number_term.shape) + 1)*(delta_plus_term) + (number_term.reshape(1,*number_term.shape) + 0)*(delta_minus_term) #(energy,qlen_1,qlen_2,qlen_3,modes)
        delta_bose_einstein_closest = (number_term_closest.reshape(len(number_term_closest),1,1,1,1) + 1)*(delta_plus_term) + (number_term_closest.reshape(len(number_term_closest),1,1,1,1) + 0)*(delta_minus_term) #(energy,qlen_1,qlen_2,qlen_3,modes)
    delta_bose_einstein[np.logical_not(np.isfinite(delta_bose_einstein))] = delta_bose_einstein_closest[np.logical_not(np.isfinite(delta_bose_einstein))]
    front_term = h_bar/(eigenvalues_nearest*meV_to_recip_cm) #(qlen_1,qlen_2,qlen_3,modes)
    sum_over_basis_squared[front_term == np.inf] = 0
    front_term[front_term == np.inf] = 0
    if print_info: print "Creating full mode terms..."
    modes_full_term = front_term*sum_over_basis_squared*delta_bose_einstein * 0.5 * N * 6.582119514e-13 / 5.308834822494756e-12
    return modes_full_term #(energy,qlen_1,qlen_2,qlen_3,modes)

def troubleshooting_calculate_mapped_vector_grid(crystal,phonons,vector_grid):
    q_vectors_cartesian,k_vectors_cartesian,q_vectors_hkl = vector_grid #(qlen_1,qlen_2,qlen_3,xyz)
    print "Mapping values to nearest phonon q-points..."
    index_map = phonons.map_closest_indices(k_vectors_cartesian,pre_map = crystal.lattice.recip)
    return phonons.qvectors[index_map]
    
def troubleshooting_calculate_dot_terms(crystal,phonons,energy_limits,vector_grid,temperature=273.15,N=1e23,use_neutrons=False,flip_energies=False,print_info=True):
    modes_number = phonons.evalues.shape[1]
    # atoms_number = phonons.evalues.shape[2]
    q_vectors_cartesian,k_vectors_cartesian,q_vectors_hkl = vector_grid #(qlen_1,qlen_2,qlen_3,xyz)
    assert q_vectors_cartesian.size < 1200000
    if print_info: print "Mapping values to nearest phonon q-points..."
    index_map = phonons.map_closest_indices(k_vectors_cartesian,pre_map = crystal.lattice.recip)
    eigenvectors_nearest = phonons.norm_evectors[index_map] #(qlen_1,qlen_2,qlen_3,modes,ions,xyz)
    if print_info: print "Summation over basis atoms..."
    eigenvectors_deconstructed = [item for item in np.moveaxis(eigenvectors_nearest,4,0)]     #shape from (qlen_1,qlen_2,qlen_3,modes,ions,xyz) to ions[(qlen_1,qlen_2,qlen_3,modes,xyz)]  

    def iterator():
        for index,atom in enumerate(crystal.basis_list):
            q_vectors_tiled = np.moveaxis(np.tile(q_vectors_cartesian,(modes_number,1,1,1,1)),0,3)     #shape from (qlen_1,qlen_2,qlen_3,xyz) to (qlen_1,qlen_2,qlen_3,modes,xyz)
            dot_term = (q_vectors_tiled*(eigenvectors_deconstructed[index])).sum(-1) #(qlen_1,qlen_2,qlen_3,modes)
            yield dot_term
    all_dot_terms = np.stack([item for item in iterator()])
    return all_dot_terms
    
def troubleshooting_calculate_exp_terms(crystal,phonons,energy_limits,vector_grid,temperature=273.15,N=1e23,use_neutrons=False,flip_energies=False,print_info=True):
    modes_number = phonons.evalues.shape[1]
    # atoms_number = phonons.evalues.shape[2]
    q_vectors_cartesian,k_vectors_cartesian,q_vectors_hkl = vector_grid #(qlen_1,qlen_2,qlen_3,xyz)
    assert q_vectors_cartesian.size < 1200000
    if print_info: print "Mapping values to nearest phonon q-points..."
    if print_info: print "Summation over basis atoms..."

    def iterator():
        for index,atom in enumerate(crystal.basis_list):
            q_vectors_hkl_tiled = np.moveaxis(np.tile(q_vectors_hkl,(modes_number,1,1,1,1)),0,3)     #shape from (qlen_1,qlen_2,qlen_3,xyz) to (qlen_1,qlen_2,qlen_3,modes,xyz)
            exp_term = np.exp(1j * 2 * np.pi * (q_vectors_hkl_tiled*atom.pos.reshape(1,1,1,1,3)).sum(-1)) #(qlen_1,qlen_2,qlen_3,modes)
            yield exp_term
    all_dot_terms = np.stack([item for item in iterator()])
    return all_dot_terms
    
#A mapping is a 3x3 array which transforms in recip space. You're gonna want to load one which transforms from hkl to image dimensions.