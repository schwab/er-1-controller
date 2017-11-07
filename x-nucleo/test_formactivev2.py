import npyscreen 

def test():
    # These lines create the form and populate it with widgets.
    # A fairly complex screen in only 8 or so lines of code - a line for each control.
    F  = npyscreen.ActionFormV2WithMenus(name = "Welcome to Npyscreen",)
 
    ms = F.add(npyscreen.MultiLineActionWithShortcuts, max_height=4, value = [1,], name="Pick One", 
            values = ["Option1","Option2","Option3"], scroll_exit=True)
     
    root = F.new_menu()
    root.addItem('test', curses.beep)
     
    # This lets the user play with the Form.
    F.edit()


if __name__ == "__main__":
    test()
    
