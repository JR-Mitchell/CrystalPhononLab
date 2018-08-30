import GUI.TraitsImports as tts
from Objects.XRDImages import XRDImage
import numpy as np
import tempfile as temp
import os
import matplotlib.pyplot as plt

DEFAULT_OBJECT = XRDImage

def load_object_from_filepath(filepath):
    return_image = XRDImage()
    return_image.load(filepath)
    return return_image

class XRDImageItem(tts.HasTraits):
    image = tts.Instance(tts.ImageResource)
    data = tts.Instance(XRDImage)
    header = tts.Dict()
    cutoff = tts.Float()
    view = tts.View(tts.VGroup('cutoff','header',tts.Item("image",editor=tts.ImageEditor(scale=True,preserve_aspect_ratio = True),resizable=True,springy=True)),resizable=True)
    
    def __init__(self,filename,*args,**kwargs):
        tts.HasTraits.__init__(self,*args,**kwargs)
        self.data = XRDImage()
        self.data.load(filename)
        img_data = self.data.data
        self.cutoff = float(np.ceil(np.log10(img_data.max())))
        self.render()
        
    @tts.on_trait_change('cutoff')
    def render(self):
        data_copy = self.data.data.copy().astype(float)
        data_copy[data_copy > 10**(self.cutoff)] = np.nan
        with temp.NamedTemporaryFile(suffix=".png",delete=False) as tempfile:
            plt.imsave(fname=tempfile,arr=data_copy,cmap='jet')
            filepath = tempfile.name
        self.image = tts.ImageResource(filepath)
        os.unlink(filepath)
        
    def save(self,filename):
        assert filename.split(".")[-1] == "png"
        data_copy = self.data.data.copy().astype(float)
        data_copy[data_copy > 10**(self.cutoff)] = np.nan
        plt.imsave(fname=filename,arr=data_copy,cmap='jet')
        self.image = tts.ImageResource(filename)