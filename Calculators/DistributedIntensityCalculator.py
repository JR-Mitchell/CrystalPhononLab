#functions take crystal, phonons, vector grid, kwargs
#in intensitycalculator, args go:
#crystal,phonons,energy_limits,vector_grid,temperature=273.15,N=1e23,use_neutrons=False,flip_energies=False,print_info=True
#these functions should distribute in threads/processes depending on settings

import numpy as np
from .IntensityCalculator import calculate_dispersion

MAX_PROCESSES = 2
MAX_DIMENSION_LIMITS = 105840000

def arange(*vector_limits):
    length = len(vector_limits)
    assert length in (1,3)
    if len(vector_limits) == 3: return np.arange(*vector_limits)
    else: return np.array(vector_limits)

def set_maximum_processes_multiprocessing(max_processes):
    """
    Sets the number of processes to create when splitting calculations into multiple steps.
    
        :param max_processes: Integer   -The number of processes to create
    """
    global MAX_PROCESSES
    assert isinstance(max_processes,int), "The argument 'max_processes' must be an integer."
    print "Changing maximum processes for multiprocess calculations from {} to {}".format(MAX_PROCESSES,max_processes)
    MAX_PROCESSES = max_processes
    
def set_maximum_dimensional_limits(max_limits):
    """
    Sets the approximate limit of the product of all calculation dimensions with which to determine whether to split a calculation into multiple parts 
    """
    global MAX_DIMENSION_LIMITS
    print "Changing maximum dimension limits from {} to {}".format(MAX_DIMENSION_LIMITS,max_limits)
    MAX_DIMENSION_LIMITS = max_limits

def phonon_intensity(crystal,phonons,qvector_grid,energy_limits=("integrate",-25.0,25.0,0.25),mode_limits=("integrate","all"),integration_dimensions=[],temperature=273.15,N=1e23,use_neutrons=False,flip_energy_axis=False,print_info=True):
    """
    Calculates the single phonon scattering intensity for a particular crystal and particular Q (momentum exchange) vectors.
    If the calculation is a large one, it will be distributed between multiple processes and performed in multiple linear steps to ensure no memory overflows and close-to-linear calculation time.
    
        :param crystal: tuple (BravaisLattice,Basis)    -The particular crystal through which diffraction occurs
        :param phonons: PhononSlice     -Phonon information, as loaded from a CASTEP .phonon file or created with slice_phonons()
        :param qvector_grid: np.ndarray     -A numpy array of shape (*dimensions,3) where the last axis is the h,k and l value of each point. 
        :kwarg energy_limits: tuple (string,...)    -The energy limits of the calculation. The first string, none-case-sensitive, may be "integrate" or "i" for an integration, "multiple" or "m", meaning that energy will be an extra dimension in the returned array, or "single" or "s" for one single energy level.
                                                     If "single" or "s", the tuple is 2-length and the second value is a number representing the energy, in meV, to use.
                                                     If anything else, the tuple is 4-length, (string,minimum value,maximum value,step) such that values are calculated from an energy of 'minimum value' meV to 'maximum value' meV in intervals of 'step' meV
        :kwarg mode_limits: tuple (string,...)      -As above, except for the available phonon modes rather than energy levels. As mode identifiers are integers, no 'step' value is needed for integration / multiple values. One may also use the string "all" to specify selection of or integration over all present modes.
        :kwarg integration_dimensions: tuple (int,...)  -If there is to be an integration over Q vectors, this specifies which dimensions of qvector_grid to integrate over. Each integer must refer to a dimension of qvector_grid.
        :kwarg temperature: number  -The thermodynamic temperature, in Kelvin, of the system.
        :kwarg N: number    -The number of atoms present in the system.
        :kwarg use_neutrons: bool   -By default, calculations for x-ray scattering are made. This boolean determines whether neutron scattering calculations should be made instead.
        :kwarg flip_energy_axis: bool   -Whether to flip the energy axis in the returned data
        :kwarg print_info: bool     -Whether to give detailed printed updates to the console about the progress made during the calculation 
        :return intensity_grid: np.ndarray  -The calculated single phonon scattering intensity. Consider a qvector_grid of shape (*dimensions,3). Then intensities in shape (*dimensions,energy,modes) are calculated, and then specified dimensions are integrated over.
                                             Example: if qvector_grid is 2 dimensional, the first being in the h direction, the second in the k direction, energy limits is ("multiple",-25.0,25.0,0.25), mode limits is ("integrate","all"), and integration_dimensions is [1] then the returned array will have dimensions (h,energy)
    """
    #Checking all parameters are correct; don't want duck typing throwing up errors half the way through a 2 hour long calculation
    #! NEEDS DOING
    
    #Working out whether the calculation needs to be split into multiple steps
    number_of_modes = phonons.evalues.shape[1] 
    dimension_limit = MAX_DIMENSION_LIMITS/number_of_modes #Each calculation calculates over all modes, so these are automatically counted
    number_dimensions = len(qvector_grid.shape[:-1]) + int(energy_limits[0].lower().strip() in ("integrate","multiple","i","m"))  #! NOTE: QVECTOR GRID: IS IT JUST QVECS OR IS IT MULTIPLE???
    single_dimension_limit = int(np.floor(np.power(dimension_limit,1.0/number_dimensions))) #Each dimension is split into subsections of this size
    lengths = np.array(list(qvector_grid.shape[:-1]) + [len(arange(*energy_limits[1:]))]) #Lengths of each dimension
    multiples = np.ceil(lengths/float(single_dimension_limit)).astype(int) #How many times each dimension must be split
    multiples_indices = multiples > 1 #Which dimensions need to be split
    
    #Actual calculation
    if any(multiples_indices): #The calculation is to be split
        assert False, "Calculations of this size are not yet implemented." #! NEEDS DOING
    else: #Basic calculation
        intensity_grid = calculate_dispersion(crystal,phonons,energy_limits,qvector_grid,temperature,N,use_neutrons,flip_energy_axis,print_info)
    
    #Making integrations/slicings
    qvector_dims = len(qvector_grid.shape[:-1])
    #First, cut down modes
    if mode_limits[0].lower().strip() in ("integrate","i","multiple","m"):
        grid_slice = tuple([slice(None) for dimension in range(qvector_dims + 1)] + [slice(mode_limits[1],mode_limits[2],1)])
        intensity_grid = intensity_grid[grid_slice]
    else:
        grid_slice = tuple([slice(None) for dimension in range(qvector_dims + 1)] + [mode_limits[1]])
        intensity_grid = intensity_grid[grid_slice]
    
    new_integration_dimensions = list(integration_dimensions)
    if energy_limits[0].lower().strip() in ("integrate","i"): new_integration_dimensions += [qvector_dims + 1]
    if mode_limits[0].lower().strip() in ("integrate","i"): new_integration_dimensions += [qvector_dims + 2]
    #Deal with the integrations
    new_integration_dimensions.sort(reverse=True)
    for dimension in new_integration_dimensions:
        intensity_grid.sum(dimension)
    return intensity_grid
    
def bragg_intensity(crystal,qvector_grid,temperature=273.15,N=1e23,use_neutrons=False,print_info=True):
    pass #! NEEDS DOING

def scattering_intensity(crystal,phonons,qvector_grid,energy_limits=("integrate",-25.0,25.0,0.25),mode_limits=("integrate","all"),integration_dimensions=[],temperature=273.15,N=1e23,use_neutrons=False,flip_energy_axis=False,print_info=True):
    phonon = phonon_intensity(crystal,phonons,qvector_grid,energy_limits,temperature,N,use_neutrons,flip_energy_axis,print_info)
    bragg = bragg_intensity(crystal,qvector_grid,temperature,N,use_neutrons,print_info)
    return phonon,bragg


#   #Top limit is 200 210 210 1 12 = 105840000
#    #First: always div by modes. Then, take floor of powered root equal to number of non-const dims
#    num_modes = phonons.evalues.shape[1]
#    dimension_limit = 105840000 / num_modes
#    num_dimensions = sum([(len(item) == 3) for item in energy_limits,vector_1_limits,vector_2_limits,vector_3_limits])
#    single_dimension_limit = int(np.floor(np.power(dimension_limit,1.0/num_dimensions)))
#    lengths = np.array([len(arange(*item)) for item in energy_limits,vector_1_limits,vector_2_limits,vector_3_limits],dtype=float)
#    multiples = np.ceil(lengths/float(single_dimension_limit)).astype(int)
#    multiples_indices = multiples > 1
#    if any(multiples_indices):
#        print "Specified ranges too large for single calculation. Splitting along {} dimensions by {}".format(np.array(['energy','vector 1','vector 2','vector 3'])[multiples_indices],multiples[multiples_indices])
#        vector_grid = calc.generate_vector_grid(crystal,vector_1,vector_1_limits,vector_2,vector_2_limits,vector_3,vector_3_limits,maps[0],ismapped)
#        #split energies
#        arange_to_lims = lambda range_arr: (range_arr[0],range_arr[-1]+range_arr[1]-range_arr[0],range_arr[1]-range_arr[0])
#        energy_limit_list = [arange_to_lims(item) for item in np.array_split(arange(*energy_limits),multiples[0])]
#        #split vectors
#        q_vector_grid_list = np.array_split(vector_grid[0],multiples[1],0) #list of arrays
#        q_vector_grid_list = [np.array_split(xsection,multiples[2],1) for xsection in q_vector_grid_list] #list of list of arrays
#        q_vector_grid_list = [[np.array_split(ysection,multiples[3],2) for ysection in xsection] for xsection in q_vector_grid_list] #list of list of list of arrays
#        k_vector_grid_list = np.array_split(vector_grid[1],multiples[1],0) #list of arrays
#        k_vector_grid_list = [np.array_split(xsection,multiples[2],1) for xsection in k_vector_grid_list] #list of list of arrays
#        k_vector_grid_list = [[np.array_split(ysection,multiples[3],2) for ysection in xsection] for xsection in k_vector_grid_list] #list of list of list of arrays
#        
#        nonsummedlist = [('x:' in parameterkwargs[name] or 'y:' in parameterkwargs[name]) for name in ('energy_limits','vector_1_limits','vector_2_limits','vector_3_limits','mode_limits')]
#        
#        numdone = 0
#        full_subdatas = []
#        for eindex,energy_subsection in enumerate(energy_limit_list):
#            esub_data = []
#            xindex = 0
#            for x_qvector_subsection,x_kvector_subsection in zip(q_vector_grid_list,k_vector_grid_list):
#                xsub_data = []
#                yindex = 0
#                for y_qvector_subsection,y_kvector_subsection in zip(x_qvector_subsection,x_kvector_subsection):
#                    ysub_data = []
#                    zindex = 0
#                    for z_qvector_subsection,z_kvector_subsection in zip(y_qvector_subsection,y_kvector_subsection):
#                        print "Calculating subsection {} of {} ({}%)".format(np.array([eindex+1,xindex+1,yindex+1,zindex+1],dtype=int)[multiples_indices],multiples[multiples_indices], 100 * numdone / float(multiples.prod()))
#                        subsection_data = calc.calculate_dispersion(crystal,phonons,energy_subsection,(z_qvector_subsection,z_kvector_subsection),temperature,N,use_neutrons,flip_energies,print_info=True)
#                        if not "all" in parameterkwargs['mode_limits']: 
#                            modelims = numerical_limits(parameterkwargs['mode_limits'])
#                            assert modelims.shape == (2L,)
#                            subsection_data = subsection_data[:,:,:,:,int(modelims[0]):int(modelims[1])]
#                        for index in (4,3,2,1,0):
#                            if not nonsummedlist[index]: subsection_data = subsection_data.sum(index)
#                        ysub_data.append(subsection_data)     
#                        zindex += 1      
#                        numdone += 1             
#                    if nonsummedlist[3]: ysub_data = np.concatenate(ysub_data,sum(nonsummedlist[:3]))
#                    else: ysub_data = sum(ysub_data)
#                    xsub_data.append(ysub_data)
#                    yindex += 1
#                if nonsummedlist[2]: xsub_data = np.concatenate(xsub_data,sum(nonsummedlist[:2]))
#                else: xsub_data = sum(xsub_data)
#                esub_data.append(xsub_data)
#                xindex += 1
#            if nonsummedlist[1]: esub_data = np.concatenate(esub_data,sum(nonsummedlist[:1]))
#            else: esub_data = sum(esub_data)
#            full_subdatas.append(esub_data)
#        if nonsummedlist[0]: full_data = np.concatenate(full_subdatas,0)
#        else: full_data = sum(full_subdatas)        
#    else:
#        vector_grid = calc.generate_vector_grid(crystal,vector_1,vector_1_limits,vector_2,vector_2_limits,vector_3,vector_3_limits,maps[0],ismapped)
#        full_data = calc.calculate_dispersion(crystal,phonons,energy_limits,(vector_grid[0],vector_grid[1]),temperature,N,use_neutrons,flip_energies,print_info=True)
#        #(energy,qlen_1,qlen_2,qlen_3,modes)