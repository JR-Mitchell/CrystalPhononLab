import GUI.TraitsImports as tts

import IO.Basis as bas
import IO.Lattice as lat
import IO.Elements as ele
import IO.Phonons as pho
import IO.Images as img
import IO.Maps as maps
import IO.Peaks as peaks
import IO.XRDImages as Ximg
import IO.DatImages as Dimg
OBJECT_LOADERS = {'bas':bas,'lat':lat,'ele':ele,'phonon':pho,'npz':pho,'map':maps,'peak':peaks,'img':Ximg,'npy':Dimg}

class DefaultItem(tts.HasTraits):
    data = tts.Str()
    view = tts.View(tts.Item("data",editor=tts.CodeEditor()))
    
    def save(self,filename):
        string = self.data
        with open(filename,"w") as writeFile:
            writeFile.write(string)
    
class ParseObject(tts.HasTraits):
    data = tts.Any()
    view = tts.View(tts.InstanceUItem("data"))  
    
    def save(self,filename):
        self.data.save(filename)  

def loadui(filepath):
    extension = filepath.split(".")[-1]
    if extension == "phonon":
        qvectors,evalues,evectors,qlastdigits,header_dict = pho.load_initiating_data_from_filepath(filepath)
        return pho.PhononItem(header=header_dict,qvectors=qvectors,evalues=evalues,evectors=evectors,qlastdigits=qlastdigits)
    elif extension == "npz":
        qvectors,evalues,evectors,qlastdigits = pho.load_arrays_from_npz(filepath)
        return pho.PhononItem(qvectors=qvectors,evalues=evalues,evectors=evectors,qlastdigits=qlastdigits)
    elif extension in ("jpg","png"):
        return img.ImageItem(filepath)
    elif extension == "img":
        return Ximg.XRDImageItem(filepath)
    elif extension == "npy":
        return Dimg.DatImageItem(filepath)
    else:
        with open(filepath,"r") as readFile:
            string = readFile.read()
        return DefaultItem(data=string)
        
def parse_to_objects(parameters,filename_list):
    parameter_dict = params_to_dict(parameters)
    if "condition" in parameter_dict:
        file_list = [load_object(filename,eval(parameter_dict["condition"])) for filename in filename_list]
    else:
        file_list = [load_object(filename) for filename in filename_list]
    return parameter_dict,file_list
    
def params_to_dict(parameters):
    #remove comments
    lines = parameters.split("\n")
    lines = [line.strip().split("#")[0].strip() for line in lines]
    lines = [[line.split("=")[0],"=".join(line.split("=")[1:])] for line in lines]
    lines = [[subitem.strip() for subitem in line] for line in lines]
    lines = [item for item in lines if item[0] != ""]
    return dict(lines)
    
def load_object(filepath,condition=lambda x:x==x):
    extension = filepath.split(".")[-1]
    assert extension in OBJECT_LOADERS
    print "Loading in {}".format(filepath)
    try:
        return OBJECT_LOADERS[extension].load_object_from_filepath(filepath,condition)
    except:
        return OBJECT_LOADERS[extension].load_object_from_filepath(filepath)

def get_objects_from_list(objectlist,**names):
    object_types = {key:item.DEFAULT_OBJECT for key,item in OBJECT_LOADERS.items()}
    return_dict = {}
    assert all([name in object_types for name in names]), (
        "An invalid identifier was passed to get_objects_from_list")
    for name in names:
        sublist = [item for item in objectlist if isinstance(item,object_types[name])]
        if names[name] != "any":
            assert len(sublist) == names[name], (
                "{} objects of type {} loaded.".format(("Not enough","Too many")[int(len(sublist) > names[name])],name))
        else: assert len(sublist) > 0, (
            "Object(s) of type {} expected but not found.".format(name))
        return_dict[name] = sublist
    return return_dict