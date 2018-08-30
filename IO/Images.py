import GUI.TraitsImports as tts

class ImageItem(tts.HasTraits):
    image = tts.Instance(tts.ImageResource)
    view = tts.View(tts.Item("image",editor=tts.ImageEditor(scale=True,preserve_aspect_ratio = True)))
    
    def __init__(self,filename,*args,**kwargs):
        tts.HasTraits.__init__(self,*args,**kwargs)
        self.image = tts.ImageResource(filename)        