from main_terminal import *
import main_gui 

def create_window():
    """
    Creates a window with graphical user interface enabling more intuitive use.
    Takes no arguments, returns nothing.
    """
    assert False, "GUI window not yet implemented"
    
if __name__ == "__main__":
    if raw_input("Create a GUI window? ").lower().strip() in ("true","yes","y"):
        create_window()
    else: print "Try list_tools() or create a Project()."