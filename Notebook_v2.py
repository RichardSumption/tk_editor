import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from hashlib import md5

def main():
    app = App()
    app.mainloop()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Notebook')
        self.option_add('*tearOff',tk.FALSE)
        self.tree_status = 'visible'
        self.editor_status = 'visible'
        self.filename = ""
        self.modified = False
        self.untitled_count = 1
        self.mode = 'file'

        # Create a Full size panedWindow object
        self.panel = tk.PanedWindow(self, bd=5, bg='green', orient='horizontal')
        self.panel.pack(fill='both', expand=1)

        # Create status bar at the bottom of screen
        self.status_bar = Statusbar(self)

        # --------------------- MENU ------------------------#
        self.menubar = Menuclass(self)
        self.config(menu=self.menubar)

        # ------------------- SIDEBAR (file list) -----------------------#
        self.leftframe = tk.Frame()
        self.panel.add(self.leftframe, minsize=5)

        self.filetree = Sideframe(self.leftframe)
        self.filetree.pack(side='left', fill='both')

        # ----------------  MAIN FRAME (editor) ----------------------#
        self.rightframe = tk.Frame()
        self.panel.add(self.rightframe)
        self.nb = Pageframe(self.rightframe)

        # Create initial tab and 'Add' tab
        self.nb.add(Tab(FileDir='Untitled'), text='Untitled')
        self.nb.add(Tab(FileDir='f'), text=' + ')

        # Create tab right-click menu
        self.tab_right_click_menu = tk.Menu(self.nb)
        self.tab_right_click_menu.add_command(label="New Tab", command=self.new_file)

        self.tree_status = 'visible'
        self.modified = False

        self.bind_class('Text', '<Button-3>', self.right_click)
        self.nb.bind("<Button-2>", self.close_tab)
        self.nb.bind('<<NotebookTabChanged>>', self.tab_change)
        self.nb.bind('<Button-3>', self.right_click_tab)

        self.folder_img = tk.PhotoImage(file="icons/folder.png").subsample(3, 3)
        self.picture_img = tk.PhotoImage(file="icons/picture.png").subsample(3, 3)
        self.file_img = tk.PhotoImage(file="icons/file.png").subsample(3, 3)

        self.filetree.treetoggle_button = tk.Button(self.filetree, text="FILE TREE ⮟", anchor="w", bd=0, relief='flat', command=self.tree_toggle, width=31)
        self.filetree.treetoggle_button.pack(side='top', fill='both')
        print(self.panel.sash_coord(0))
        # --------------- Function Library ------------------#
    def enable_bindings(self, option):
        self.mode = option
        if self.mode == "file":
            self.nb.bind("<control-w>", self.close_tab)
            self.bind("<Control-s>", self.save_binding)
            self.bind("<MouseWheel>", self.nb.mousewheel_move)
#            self.bind("<Key>", self.nb.show_lines)
        else:
            self.filetree.tv.bind("<ButtonRelease-1>", self.on_tv_click)
            self.bind("<Control-s>", self.save_binding)
            self.bind("<MouseWheel>", self.nb.mousewheel_move)
#            self.bind("<Key>", self.nb.show_lines)
            self.bind("<Control-Shift-S>", self.save_binding)

    def save_binding(self):
        pass

    def default_filename(self):
        self.untitled_count += 1
        return 'Untitled' + str(self.untitled_count-1)

    def right_click(self, event):
        self.menubar.right_click_menu.post(event.x_root, event.y_root)
        
    def right_click_tab(self, event):
        self.tab_right_click_menu.post(event.x_root, event.y_root)

    def close_tab(self, event=None):
        # Close the current tab (from file menu or keyboard.
        if event is None or event.type == str( 2 ):
            selected_tab = self.nb.current_tab()
        # Otherwise close the tab based on coordinates of center-click.
        else:
            try:
                index = event.widget.index('@%d,%d' % (event.x, event.y))
                selected_tab = self.nb.indexed_tab( index )
                if index == self.nb.index('end')-1:
                    return False
            except tk.TclError:
                return False
        # Prompt to save changes before closing tab
        if self.save_changes(selected_tab):
            # if the tab next to '+' is selected, select the previous tab to prevent
            # automatically switching to '+' tab when current tab is closed
            if self.nb.index('current') > 0 and self.nb.select() == self.nb.tabs()[-2]:
                self.nb.select(self.nb.index('current')-1)
            self.nb.forget( selected_tab )
        else:
            return False
        # Exit if last tab is closed
        if self.nb.index("end") <= 1:
            self.destroy()
        return True
    # -------------------File menu functions ----------------------#
    def new_file(self, *args):                
        # Create new tab
        new_tab = Tab(FileDir=self.default_filename())
        self.nb.insert( self.nb.index('end')-1, new_tab, text=new_tab.file_name)
        self.nb.select( new_tab )

    def open_file(self, *args):        
        # Open a file to open, returns the directory.
        file_dir = (filedialog.askopenfilename(initialdir=os.getcwd(),
                                               title="Select file",
                                               filetypes=(("Text files", "*.txt"), ("HTML files", "*.htm"), ("Python files", "*.py"), ("All files", "*.*"))))
        # If selected try to open the file. 
        print(file_dir)
        if file_dir:
            try:
                # Open the file.
                file = open(file_dir)
                # Create a new tab and insert at end.
                new_tab = Tab(FileDir=file_dir)
                self.nb.insert( self.nb.index('end')-1, new_tab, text=os.path.basename(file_dir))
                self.nb.select( new_tab )
                # Puts the contents of the file into the text widget.
                self.nb.current_tab().textbox.insert('end', file.read())
                # Update hash
                self.nb.current_tab().status = md5(self.nb.current_tab().textbox.get(1.0, 'end').encode('utf-8'))
#                self.nb.show_lines(e=None)
                self.status_bar.setText(file_dir)
            except:
                return

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder == "":
            return
        self.minsize(1200, 800)
        self.resizable(True, True)

        self.nb.pack(side='right', expand=True, fill='both')
        self.filetree.pack(side='left', fill='both')

        self.enable_bindings("folder")
        self.make_tv(folder)
        self.filetree.tv.pack(expand='true', anchor="n", fill='both')
        self.filetree.pack_forget()
        self.filetree.pack(side='left', fill='both')

#        self.nb.current_tab.configure(state='disabled')
        self.mode = "folder"   

    def save_changes(self, tab):
        # Check if any changes have been made, returns False if user chooses to cancel rather than select to save or not.
        if md5(tab.textbox.get(1.0, 'end').encode('utf-8')).digest() != tab.status.digest():
            # Select the tab being closed is not the current tab, select it.
            if self.nb.current_tab() != tab:
                self.nb.select(tab)
            m = messagebox.askyesnocancel('Editor', 'Do you want to save changes to ' + tab.file_name + '?' )
            # If None, cancel.
            if m is None:
                return False
            # else if True, save.
            elif m is True:
                return self.save_file()
            # else don't save.
            else:
                pass

        return True

    def save_file(self, *args):
        curr_tab = self.nb.current_tab()
        # If filename is empty or Untitled, use save_as to get save information from user. 
        if not curr_tab.file_name:
            return self.save_as_file()
        # Otherwise save file to directory, overwriting existing file or creating a new one.
        else:
            with open(curr_tab.file_name, 'w') as file:
                file.write(curr_tab.textbox.get(1.0, 'end'))
            # Update hash
            curr_tab.status = md5(curr_tab.textbox.get(1.0, 'end').encode('utf-8'))
            return True

    def save_as_file(self):
        curr_tab = self.nb.current_tab()
        # Gets file directory and name of file to save.
        file_dir = (filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Select file", filetypes=(("Text files", "*.txt"), ("HTML files", "*.htm"), ("Python files", "*.py"), ("All files", "*.*"))))
        # Return if cancelled
        if not file_dir:
            return False
        curr_tab.file_dir = file_dir
        curr_tab.file_name = os.path.basename(file_dir)
        self.nb.tab( curr_tab, text=curr_tab.file_name)
        # Writes text widget's contents to file.
        file = open(file_dir, 'w')
        file.write(curr_tab.textbox.get(1.0, 'end'))
        file.close()
        # Update hash
        curr_tab.status = md5(curr_tab.textbox.get(1.0, 'end').encode('utf-8'))
        self.status_bar.setText(file_dir)
        return True

    def exit(self):        
        # Check if any changes have been made.
        for i in range(self.nb.index('end')-1):
            if self.close_tab() is False:
                break
    # -------------------- open folder functions -------------------#
    def make_tv(self, folder):
        if folder == '':
            return
        self.directory = folder
        self.tv_items = {}
        self.file_contents = {}

        self.filetree.tv.heading("#0", anchor="w")
        self.file_path = os.path.abspath(self.directory)
        tv_item = self.filetree.tv.insert("", 'end', text=" "+self.file_path.replace("\\", "/").split('/')[-1], open=True, image=self.filetree.folder_img)
        def traverse_dir(parent, path):
            for file in os.listdir(path):
                full_path=os.path.join(path, file)
                self.tv_items[file] = full_path
                try:
                    with open(self.tv_items[file], "r", encoding="utf-8") as f:
                        try:
                            self.file_contents[file] = {"content": f.read(), "readable": True}
                        except:
                            self.file_contents[file] = {"content": "", "readable": False}
                except: pass
                isdir = os.path.isdir(full_path)
                if isdir:
                    id=self.filetree.tv.insert(parent, 'end', text=" "+file, open=False, tags=r"{}".format(full_path), image=self.filetree.folder_img)
                    traverse_dir(id, full_path)
                else:
                    id=self.filetree.tv.insert(parent, 'end', text=" "+file, open=False, tags=r"{}".format(full_path), image=self.filetree.file_img)
        traverse_dir(tv_item, self.file_path)

    def on_tv_click(self, e):
        selected_item = self.filetree.tv.focus()
        values = self.filetree.tv.item(selected_item)
        if os.path.isdir(self.tv_items[values['text'][1:]]):
            return
        self.filename = self.tv_items[values["text"][1:]]
        self.nb.pack(expand=True, fill='both', padx=(5,0))
        self.editor_status == "visible"
#        self.nb.configure(state='normal')
#        self.nb.linenums.pack()
        print(self.filename)
        if self.file_contents[values['text'][1:]]["readable"]:
            new_tab = Tab(FileDir=self.filename)
            self.nb.insert( self.nb.index('end')-1, new_tab, text=new_tab.file_name)
            self.nb.select( new_tab )
            # Open the file.
            file = open(self.filename)
            # Puts the contents of the file into the text widget.
            self.nb.current_tab().textbox.insert('end', file.read())
            # Update hash
            self.nb.current_tab().status = md5(self.nb.current_tab().textbox.get(1.0, 'end').encode('utf-8'))
            path, justname = os.path.split(self.filename)
            self.nb.tab('current', text=justname)
            self.status_bar.setText(justname)
        else:
            self.nb.current_tab.pack_forget()
            self.editor_status = "hidden"
            messagebox.showerror('Error', "Couldn't display file.")
            self.nb.current_tab.delete("1.0","end")
            self.nb.current_tab.insert("1.0", "There was an error displaying the file.")
            self.nb.current_tab.configure(state='disabled')
    # --------------------- formatting functions -------------------#
    def cut_text(self):
        # Copies selection to the clipboard, then deletes selection.
        try: 
            sel = self.nb.current_tab().textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(sel)
            self.nb.current_tab().textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass

    def copy_text(self):
        # Clears the clipboard, copies selected contents.
        try: 
            sel = self.nb.current_tab().textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(sel)
        # If no text is selected.
        except tk.TclError:
            pass

    def paste_text(self):
        try: 
            self.nb.current_tab().textbox.insert(tk.INSERT, self.clipboard_get())
        except tk.TclError:
            pass

    def delete(self):
        # Delete the selected text.
        try:
            self.nb.current_tab().textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass

    def tab_change(self, event):
        # If last tab was selected, create new tab
        if self.nb.select() == self.nb.tabs()[-1]:
            self.new_file()

    def show_tree(self):
        self.filetree.treetoggle_button.pack(side='top', fill='both')
        self.filetree.treetoggle_button.configure(text="FILE TREE ⮟", width=31, anchor='w', font=('JetBrains Mono', 8))
        self.filetree.tv.pack(expand=True, anchor='n', fill='both')
        self.panel.sash_place(0,200,5)
        self.tree_status = "visible"
    
    def hide_tree(self):
        self.filetree.tv.pack_forget()
        self.filetree.treetoggle_button.pack_forget()
        self.filetree.treetoggle_button.pack(side='top', fill='both')
        self.filetree.treetoggle_button.configure(text="F\nI\nL\nE\n\nT\nR\nE\nE\n⮞", width=3, anchor='center', font=('JetBrains Mono', 8))
        self.panel.sash_place(0, 30,5)
        self.tree_status = "hidden"

    def tree_toggle(self):
        if self.tree_status == "visible":
            self.hide_tree()
        else:
            self.show_tree()

class Tab(ttk.Frame):
    def __init__(self, *args, FileDir):
        ttk.Frame.__init__(self, *args)
        self.textbox = self.create_text_widget()
        self.file_dir = None
        self.file_name = os.path.basename(FileDir)
        self.status = md5(self.textbox.get(1.0, 'end').encode('utf-8'))
        
    def create_text_widget(self):
        # Horizontal Scroll Bar
        xscrollbar = tk.Scrollbar(self, orient='horizontal')
        xscrollbar.pack(side='bottom', fill='x')

        # Vertical Scroll Bar
        yscrollbar = tk.Scrollbar(self)
        yscrollbar.pack(side='right', fill='y')

        # Create Text Editor Box
        textbox = tk.Text(self, relief='sunken', borderwidth=0, wrap='none')
        textbox.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, undo=True, autoseparators=True)

        # Pack the textbox
        textbox.pack(fill='both', expand=True)

        # Configure Scrollbars
        xscrollbar.config(command=textbox.xview)
        yscrollbar.config(command=textbox.yview)

        return textbox

class Sideframe(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.tree_status = "visible"

        self.tv = ttk.Treeview(self, show='tree')

        self.folder_img = tk.PhotoImage(file="icons/folder.png").subsample(3, 3)
        self.picture_img = tk.PhotoImage(file="icons/picture.png").subsample(3, 3)
        self.file_img = tk.PhotoImage(file="icons/file.png").subsample(3, 3)

class Pageframe(ttk.Notebook):
    def __init__(self, parent):
        ttk.Notebook.__init__(self, parent)
        self.parent = parent

        self.enable_traversal()
        self.pack(expand=1, fill="both")
        self.bind("<B1-Motion>", self.move_tab)

    # Get the object of the current tab.
    def current_tab(self):
        return self.nametowidget( self.select() )

    def indexed_tab(self, index):
        return self.nametowidget( self.tabs()[index] )

    # Move tab position by dragging tab
    def move_tab(self, event):
        '''
        Check if there is more than one tab.

        Use the y-coordinate of the current tab so that if the user moves the mouse up / down
        out of the range of the tabs, the left / right movement still moves the tab.
        '''
        if self.index("end") > 1:
            y = self.current_tab().winfo_y() - 5

            try:
                self.insert( min( event.widget.index('@%d,%d' % (event.x, y)), self.index('end')-2), self.select() )
            except tk.TclError:
                pass

    def show_lines(self, e):
        pass
    
    def mousewheel_move(self, e):
        pass

class Menuclass(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # Define the menu's to include
        self.file_menu = tk.Menu(self.parent)
        self.edit_menu = tk.Menu(self.parent)
        self.database_menu = tk.Menu(self.parent)
        self.view_menu = tk.Menu(self.parent)
        self.go_menu = tk.Menu(self.parent)
        self.run_menu = tk.Menu(self.parent)
        self.terminal_menu = tk.Menu(self.parent)
        self.help_menu = tk.Menu(self.parent)
        # Create tab right-click menu
        self.tab_right_click_menu = tk.Menu(self.parent)

        self.tab_right_click_menu.add_command(label="New Tab", command=self.parent.new_file)


        self.add_cascade(menu=self.file_menu, label='File')
        self.add_cascade(menu=self.edit_menu, label='Edit')
        self.add_cascade(menu=self.database_menu, label='Database')
        self.add_cascade(menu=self.view_menu, label='View')
        self.add_cascade(menu=self.go_menu, label='Go')
        self.add_cascade(menu=self.run_menu, label='Run')
        self.add_cascade(menu=self.terminal_menu, label='Terminal')
        self.add_cascade(menu=self.help_menu, label='Help')

        self.file_menu_item()
        self.edit_menu_item()
        self.database_menu_item()
        self.view_menu_item()
        self.go_menu_item()
        self.run_menu_item()
        self.terminal_menu_item()
        self.help_menu_item()

           # Create right-click menu.
        self.right_click_menu = tk.Menu(self.parent)
        self.right_click_menu.add_command(label="Undo", command='None')
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Cut", command=self.parent.cut_text)
        self.right_click_menu.add_command(label="Copy", command=self.parent.copy_text)
        self.right_click_menu.add_command(label="Paste", command=self.parent.paste_text)
        self.right_click_menu.add_command(label="Delete", command=self.parent.delete)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Close Tab", command=self.parent.close_tab)
        self.right_click_menu.add_command(label="Select All", command='None')
       
    def file_menu_item(self):
        self.file_menu.add_command(label = 'New', accelerator='Ctrl+n',command=self.parent.new_file)
        self.file_menu.add_command(label = 'Open', accelerator='Ctrl+o',command=self.parent.open_file)
        self.file_menu.add_command(label = 'Open Folder', accelerator='Ctrl+O',command=self.parent.open_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label = 'Save', accelerator='Ctrl+s',command=self.parent.save_file)
        self.file_menu.add_command(label = 'Save as', accelerator='Ctrl+S',command=self.parent.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label = "Close", accelerator='Ctrl+w',command=self.parent.close_tab)
        self.file_menu.add_command(label = "Exit", command=self.parent.exit)

    def edit_menu_item(self):
        self.edit_menu.add_command(label = 'Cut', accelerator='Ctrl+x', command=self.parent.cut_text)
        self.edit_menu.add_command(label = 'Copy', accelerator='Ctrl+c', command=self.parent.copy_text)
        self.edit_menu.add_command(label = 'Paste', accelerator='Ctrl+v', command=self.parent.paste_text)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label = 'Find', accelerator='Ctrl+f', command=None)
        self.edit_menu.add_command(label = 'Replace')

    def database_menu_item(self):
        self.oracle_sub_menu = tk.Menu(self.database_menu)
        self.database_menu.add_cascade(menu=self.oracle_sub_menu, label='Oracle Menu')
        self.mysql_sub_menu = tk.Menu(self.database_menu)
        self.database_menu.add_cascade(menu=self.mysql_sub_menu, label='MySQL Menu')
        self.postgres_sub_menu = tk.Menu(self.database_menu)
        self.database_menu.add_cascade(menu=self.postgres_sub_menu, label='PostgresQL Menu')
        self.mongo_sub_menu = tk.Menu(self.database_menu)
        self.database_menu.add_cascade(menu=self.mongo_sub_menu, label='MongoDB Menu')

        # Oracle Menu Items
        self.oracle_sub_menu.add_command(label = 'SQL')
        self.oracle_sub_menu.add_command(label = 'Performance')
        self.oracle_sub_menu.add_command(label = 'Scripts')
        self.oracle_sub_menu.add_command(label = 'Filesystems')
        self.oracle_sub_menu.add_command(label = 'Objects')

    def view_menu_item(self):
        self.view_menu.add_command(label = 'Appearance')
        self.view_menu.add_command(label = 'Open View')

    def go_menu_item(self):
        pass

    def run_menu_item(self):
        pass

    def terminal_menu_item(self):
        pass

    def help_menu_item(self):
        self.help_menu.add_command(label = 'Documentation')
        self.help_menu.add_command(label = 'Report Issue')
        self.help_menu.add_separator()
        self.help_menu.add_command(label = 'About')
   
class Statusbar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text = "Ready        ", anchor="e")
        self.label.pack(side="right")
        self.pack(side='bottom', fill='x', ipady=5)

    def setText(self, newText):
        self.label.config(text = newText)

if __name__ == "__main__":
    main()
