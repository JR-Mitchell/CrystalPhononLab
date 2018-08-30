import GUI.TraitsImports as tts
import numpy as np
import tempfile as temp
import os
import matplotlib.pyplot as plt
from Objects.DatImages import DatImage

DEFAULT_OBJECT = DatImage

def load_object_from_filepath(filepath):
    return_image = np.load(filepath).view(DatImage)
    return return_image

class DatImageItem(tts.HasTraits):
    image = tts.Instance(tts.ImageResource)
    data = tts.Instance(DatImage)
    cutoff = tts.Float()
    view = tts.View(tts.VGroup('cutoff',tts.Item("image",editor=tts.ImageEditor(scale=True,preserve_aspect_ratio = True),resizable=True,springy=True)),resizable=True)
    
    def __init__(self,filename,*args,**kwargs):
        tts.HasTraits.__init__(self,*args,**kwargs)
        self.data = load_object_from_filepath(filename)
        self.cutoff = float(np.ceil(np.log10(self.data.max())))
        self.render()
        
    @tts.on_trait_change('cutoff')
    def render(self):
        data_copy = self.data.copy().astype(float)
        data_copy[data_copy > 10**(self.cutoff)] = np.nan
        with temp.NamedTemporaryFile(suffix=".png",delete=False) as tempfile:
            plt.imsave(fname=tempfile,arr=data_copy,cmap='jet')
            filepath = tempfile.name
        self.image = tts.ImageResource(filepath)
        os.unlink(filepath)
        
    def save(self,filename):
        assert filename.split(".")[-1] == "png"
        data_copy = self.data.copy().astype(float)
        data_copy[data_copy > 10**(self.cutoff)] = np.nan
        plt.imsave(fname=filename,arr=data_copy,cmap='jet')
        self.image = tts.ImageResource(filename)