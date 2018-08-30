print "Importing modules..."
import main_default as md
TOOL_NAMES = [item for item in dir(md) if item.strip("_") == item]
del md
from main_default import *
import os
assert "Data" in os.listdir(os.getcwd())
DATA_PATH = os.path.join(os.getcwd(),"Data")
import IO.ParseAll as pall

class Project():
    def __init__(self,directory):
        assert (os.path.basename(directory) in list_projects(
                os.path.dirname(directory))
            ), "Please give a valid project directory"
        self._root_directory = directory
        self.current_directory = directory
        
    def ls(self):
        return os.listdir(self.current_directory)
    
    def open_directory(self,name):
        """
        If name is a folder, changes the current directory to inside the folder.
        If name is a file, returns the loaded object of that file.
        """
        assert name in self.ls(), "Valid folder by name {} not found in current directory".format(name)
        assert "." not in name, "Valid folder by name {} not found in current directory".format(name)
        self.current_directory = os.path.join(self.current_directory,name)
        
    def open_project(self,name):
        return open_project(name,directory=self.current_directory)
    
    def load(self,*names):
        """
        If name is a folder, returns all objects within that file.
        If name is a file, returns the loaded object of that file.
        """
        full_names = self._recursively_access_filenames(*names)
        object_list = [pall.load_object(name) for name in full_names]
        if len(object_list) == 1:
            return object_list[0]
        else:
            return object_list
        
    def _recursively_access_filenames(self,*names):
        full_names = [os.path.join(self.currentfile,name) for name in names]
        def recurse(name):
            if "." in name:
                return [name]
            else:
                return_list = []
                for item in os.listdir(os.path.join(self.currentfile,name)):
                    return_list += recurse(os.path.join(os.path.join(self.currentfile,name),item))
                return return_list
        return_list = []
        for item in full_names:
            return_list += recurse(item)
        return return_list
        
    @property
    def default_kwargs(self):
        with open(os.path.join(self.rootfile,"default_params.params")) as dpamfile:
            default_param_str = dpamfile.read()
        return pall.params_to_dict(default_param_str)
    
def list_projects(directory=DATA_PATH):
    file_list = os.listdir(directory)
    folder_list = [item for item in file_list if "." not in item]
    project_list = [item for item in folder_list if "default_params.params" in os.listdir(os.path.join(DATA_PATH,item))]
    return project_list

def open_project(name,directory=DATA_PATH):
    return Project(os.path.join(directory,name))
    
def list_tools():
    return TOOL_NAMES

#class Project():
#    def __init__(self,projectname):
#        assert projectname in list_projects()
#        self.rootfile = os.path.join(DATA_PATH,projectname)
#        self.currentfile = self.rootfile
#        for item in TOOLS_TUPLE:
#            print item
#            self.__dict__[item.FUNC_NAME] = self._functionise(item.function)
#            
#    def _functionise(self,function):
#        def return_function(objectlist,**parameters):
#            with open(os.path.join(self.rootfile,"default_params.params")) as dpamfile:
#                default_param_str = dpamfile.read()
#            parameterkwargs = pall.params_to_dict(default_param_str)
#            for key in parameters:
#                if key == 'output_filepath': parameterkwargs[key] = os.path.join(self.currentfile,parameters[key])
#                else: parameterkwargs[key] = parameters[key]
#            function(parameterkwargs,objectlist)
#        return return_function
#        
#    def ls(self):
#        """
#        Lists all files present in the current directory.
#        """
#        return os.listdir(self.currentfile)
#        
#    def open(self,name):
#        """
#        If name is a folder, changes the current directory to inside the folder.
#        If name is a file, returns the loaded object of that file.
#        """
#        assert name in self.ls(), "Valid file by name {} not found in current directory".format(name)
#        if "." not in name:
#            self.currentfile = os.path.join(self.currentfile,name)
#        else:
#            return pall.load_object(os.path.join(self.currentfile,name))
#            
#    def open_to_list(self,names,objlist,paramstr = ""):
#        """
#        Adds objects at names to list
#        """
#        for name in names:
#            assert name in self.ls()
#        new_names = self.scour_files(names)
#        for item in pall.parse_to_objects(paramstr,[os.path.join(self.currentfile,name) for name in new_names])[1]:
#            objlist.append(item)
#            
#    def open_gui(self,name):
#        """
#        """
#        assert name in self.ls(), "Valid file by name {} not found in current directory".format(name)
#        if "." in name:
#            return pall.loadui(os.path.join(self.currentfile,name))
#            
#    def back(self):
#        if self.currentfile != self.rootfile:
#            self.currentfile = os.path.dirname(self.currentfile)
#        else: print "You're already in the project main directory."
#        
#    def scour_files(self,names):
#        full_names = [os.path.join(self.currentfile,name) for name in names]
#        def recurse(name):
#            if "." in name:
#                return [name]
#            else:
#                return_list = []
#                for item in os.listdir(os.path.join(self.currentfile,name)):
#                    return_list += recurse(os.path.join(os.path.join(self.currentfile,name),item))
#                return return_list
#        return_list = []
#        for item in full_names:
#            return_list += recurse(item)
#        return return_list
        
print "Done!"

#fixing: put h,k,l in subfiles, 
#if __name__ == "__main__":
#    p = Project("ZnO Comparisons")
#    import numpy as np
#    obj_list = []
#    p.open_to_list(['Element info'],obj_list)
##    p.open("Finalise")
##    p.open("Output")
##    p.open("hk3pho")
##    p.open_to_list(['tim_lehner_mapping.map'],obj_list)
##    crystalname = "Phonon Lattice & Basis"
##    dat_list = []
##    for l in np.arange(3.12,3.21,0.01):
##        dat_list.append(p.open("phonon_hkl_3_leh_{}_{}.npy".format(l,"_".join(crystalname.split(" ")))))
##    full_data = np.stack(dat_list)
##    del dat_list
##        pho_list = []
##        p.open_to_list(['pplane'],pho_list,"condition = lambda hkl: [hkl[2] == {}]".format(l-3))
##        for crystalname in ("Phonon Lattice & Basis","Canonical Lattice & Basis","XRD Lattice Phonon Basis"):
##            p.back()
##            p.back()
##            crys_list = []
##            p.open_to_list([crystalname],crys_list)
##            p.open("Output")
##            p.open("hk3pho")
##            arbparams = dict(temperature=30, output_filepath = "phonon_hkl_3_leh_{}_{}.npy".format(l,"_".join(crystalname.split(" "))),vector_1_limits = "x: 1 1024 4",vector_2_limits = "y: 1 1024 4", vector_3_limits = "{}".format(l),energy_limits = "y: -75 75 10", mode_limits = "i: all",vector_1_map = "1 0 0",vector_2_map = "0 1 0",vector_3_hkl = "0 0 1",use_neutrons=True)
##            p.phonon_intensity(obj_list+pho_list+crys_list,**arbparams)
#    import numpy as np
#    import matplotlib.pyplot as plt
#    def gaussianise(image,factor):
#        numb1,numb2 = image.shape
#        gauss = np.meshgrid(np.arange(numb1)-(numb1/2),np.arange(numb2)-(numb2/2))
#        gauss = (gauss[0]**2 + gauss[1]**2).transpose()
#        gauss = np.exp(-gauss/factor)
#        gauss = gauss / gauss.sum()
#        cgauss = np.fft.fft2(gauss)
#        returnpic = np.roll(np.roll(np.abs(np.fft.fft2(cgauss*np.fft.fft2(image))),numb2/2),numb1/2,axis=0)
#        return returnpic
#    for crystalname in ("Canonical Lattice & Basis","XRD Lattice Canonical Basis"):
#        #cycle through 4 crystals: canonical, phonons, XRD for each
#        for freeaxisname in ("l",):
#            #cycle through h , k , l
#            vec0 = [0,0,0]
#            vec1 = [0,0,0]
#            vec2 = [int(item == freeaxisname) for item in ("h","k","l")]
#            vec2c = [item for item in vec2]
#            vec0[vec2c.index(0)] = 1
#            vec2c[vec2.index(0)] = ""
#            vec1[vec2c.index(0)] = 1            
#            obj_list = []
#            p.open_to_list(['{}_plane.map'.format(freeaxisname),'Element info','{}_phonon_slice.npz'.format(freeaxisname)],obj_list)
#            p.open("Finalise")
#            p.open_to_list([crystalname],obj_list)
#            p.open("Output")
#            p.open(crystalname)
#            p.open("hkl".replace(freeaxisname,"x"))
#            for displacement in (0,):
#                #cycle through -2,-1,0,1,2
#                #make phonon
#                arbparams = dict(temperature=293.15,output_filepath = "phonon_disp_{}.npy".format(displacement),vector_1_limits = "x: 1 1025 1",vector_2_limits = "y: 1 1025 1", vector_3_limits = "{}".format(displacement), energy_limits = "i: -25 25 0.25", mode_limits = "i: all",vector_1_map = "{} {} {}".format(*vec0),vector_2_map = "{} {} {}".format(*vec1),vector_3_hkl = "{} {} {}".format(*vec2))
#                p.phonon_intensity(obj_list,**arbparams)
#                #make bragg
#                arbparams["output_filepath"] = "bragg_disp_{}.npy".format(displacement)
#                p.bragg_intensity(obj_list,**arbparams)
#            p.back()
#            p.back()
#            p.back()
#            p.back()
#                
#                                            