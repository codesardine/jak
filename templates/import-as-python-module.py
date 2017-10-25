try:
    from j.AK import Api, AppWindow

except Exception as err:
    print("Ops something went wrong: " + str(err))
    
class applicationWindow(AppWindow):
    """
    extends AK.AppWindow functionality
    """

    def __init__(self):

        super(applicationWindow, self).__init__()
        
        # Some code here        
   
        self.connect("delete-event", Gtk.main_quit)
        

def main():
    AppWindow()
    Gtk.main()
    
main()