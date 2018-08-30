import Objects.Elements as ele
import os

DEFAULT_OBJECT = ele.Element

def load_object_from_filepath(filepath):
    with open(filepath,"r") as readFile:
        string = readFile.read()
    lines = string.split("\n")
    lines = [line.strip().split(":") for line in lines]
    lines = [[subline.strip() for subline in line] for line in lines]
    subdict = dict(lines)
    myname = os.path.basename(filepath).split(".")[0]
    return ele.Element([[myname,subdict]])
    
def save_subdict_to_filepath(subdict,filepath):
    items = subdict.items()
    element_string = "\n".join([":".join(keyval) for keyval in items])
    with open(filepath,"w") as writeFile:
        writeFile.write(element_string) 