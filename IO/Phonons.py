import GUI.TraitsImports as tts
import numpy as np
import Objects.Phonons as pho

DEFAULT_OBJECT = pho.PhononSlice

def load_object_from_filepath(filepath,condition=lambda x: x==x):
    extension = filepath.split(".")[-1]
    if extension == "phonon":
        qvectors,evalues,evectors,qlastdigits,header_dict = load_initiating_data_from_filepath(filepath,condition)
        return pho.PhononSlice(qvectors,evalues,evectors,qlastdigits,header_dict)
    else:
        qvectors,evalues,evectors,qlastdigits = load_arrays_from_npz(filepath,condition)
        return pho.PhononSlice(qvectors,evalues,evectors,qlastdigits)
    
def load_initiating_data_from_filepath(filepath,condition=lambda x: x==x):
    with open(filepath,"r") as saveFile:
        string = saveFile.read()
    headerSplit = string.split("END header")
    header_dict = read_header(headerSplit[0])
    if "Frequencies in" in header_dict:
        using_frequency = header_dict["Frequencies in"] == "cm-1"
    else: using_frequency = False                        
    qvectors,evalues,evectors,qlastdigits = read_body(headerSplit[1],using_frequency,condition)
    return qvectors,evalues,evectors,qlastdigits,header_dict
    
def load_arrays_from_npz(filepath,condition=lambda x: x==x):
    with np.load(filepath) as loaddata:
        aqvectors,aevalues,aevectors,aqlastdigits = [loaddata[item] for item in ('qv','eva','eve','ql')]
    conds = [condition(aqvector) for aqvector in aqvectors]
    matching_indices = np.array([sum(condsi).astype(float)/len(condsi) == 1 for condsi in conds])
    qvectors = aqvectors[matching_indices]
    evalues = aevalues[matching_indices]
    evectors = aevectors[matching_indices]
    qlastdigits = aqlastdigits[matching_indices]
    return qvectors,evalues,evectors,qlastdigits
    
def save_from_params(filepath,qvectors,evalues,evectors,qlastdigits,header_dict=None):
    extension = filepath.split(".")[-1]
    assert extension in ("npz","phonon")
    if extension == "npz": _save_type_npz(filepath,qvectors,evalues,evectors,qlastdigits)
    else:
        assert header_dict != None
        _save_type_phonon(filepath,qvectors,evalues,evectors,qlastdigits,header_dict)
        
def _save_type_npz(filepath,qvectors,evalues,evectors,qlastdigits):
    np.savez(filepath,qv=qvectors,eva=evalues,eve=evectors,ql=qlastdigits)
 
#! todo: write this shizzle   
def _save_type_phonon(filepath,qvectors,evalues,evectors,qlastdigits,header_dict):
    pass

def read_header(header):
    headerLines = header.strip().split("\n")
    header_dict = {}
    currentTitle = None
    for line in headerLines:
        line = line.strip()
        lineList = line.split("  ")
        if line.lower() == 'begin header': 
            pass
        elif len(lineList) == 1:
            header_dict[line] = []
            currentTitle = line
        elif currentTitle != None:
            header_dict[currentTitle].append(
                [item.strip() for item in lineList if item != ''])
        else:
            header_dict[lineList[0]] = lineList[-1].strip()
    return header_dict
    
def read_body(body,using_frequency,condition):
    bodySplit = body.split("q-pt=")[1:]
    point_data = [read_single_body_point(
        point,using_frequency) for point in bodySplit]
    point_blank_shapes = point_data[0][0].shape,point_data[0][1].shape,point_data[0][2].shape,[]
    point_data = [item for item in point_data if all(condition(item[0]))]
    point_data = sorted(point_data,key=lambda item: np.sqrt(((item[0]+np.array([0.5,0.5,0.5]))**2).sum(-1)))
    misshapen = [item[0].shape for item in point_data if item[0].shape != (3L,)]
    if len(misshapen) != 0:
        print misshapen,point_data[[item[0].shape for item in point_data].index(misshapen[0])][0]
    if len(point_data) > 0:
        qvectors = np.stack([item[0] for item in point_data])
        qlastdigits = np.stack([item[3] for item in point_data])
        evalues = np.stack([item[1] for item in point_data])
        evectors = np.stack([item[2] for item in point_data]).conjugate()
        return qvectors,evalues,evectors,qlastdigits
    else: return [np.zeros([0] + list(point_blank_shapes[i])) for i in (0,1,2,3)]
    
def read_single_body_point(point,using_frequency):
    qs = point.split("\n")[0]
    sp = point.split("Phonon Eigenvectors")
    evals = sp[0][len(qs):]
    evects = sp[1]
    qvector = np.array(qs.strip(" ").split()[1:-1],dtype=float)
    qlastdigit = float(qs.strip(" ").split()[-1])
    evals = np.array(evals.strip("\n").split(),dtype=float)
    evals = evals.reshape(evals.shape[0]/2,2)[:,1]
    evects = np.array(evects.strip("\n").split()[5:],dtype=float)
    evects = evects.reshape(evects.size/8,8)
    ions = int(max(evects[:,1]))
    evects = evects.reshape(int(evects.size/(8*ions)),ions,8)
    evects_vector = np.zeros((evects.shape[0],evects.shape[1],3),dtype=complex)
    for i in (0,1,2):
        evects_vector[:,:,i] += evects[:,:,2*(1+i)] + 1j*evects[:,:,3 + 2*i]
    if using_frequency: evals = evals * 0.1239842
    return (qvector,evals,evects_vector,qlastdigit) 

class PhononItem(tts.HasTraits):
    header = tts.Dict()
    qvectors = tts.Array()
    evalues = tts.Array()
    evectors = tts.Array()
    qlastdigits = tts.Array()
    view = tts.View("header",tts.Item("qvectors",editor=tts.TabularEditor(adapter=tts.TabularAdapter(columns=['h','k','l']))))
    
    def save(self,filename):
        save_from_params(filename,self.qvectors,self.evalues,self.evectors,self.qlastdigits,self.header)