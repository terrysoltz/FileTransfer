# Python Ver. 3.6.0
#
# Author: Terry Soltz
#
# Purpose: File backup GUI exercise for Tech Academy
#           Demonstrate use of Tkinter and file management
#
# Tested OS: Windows 10

# Import required modules
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os
import shutil
from pathlib import Path
import time
import datetime
import sqlite3

# Define selectFrame class, which will hold functionality for selecting
# current folder from directory tree and displaying contents
class selectFrame(Frame):
    def __init__(self, master, selType, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

        # Configure Frame
        self.configure(bg = '#f0f0f0')
        self.master = master
        self.selType = selType

        self.curPath = Path(os.getcwd())

        # Load images
        self.upArrow = PhotoImage(file = "levelup.gif").subsample(x = 6, y = 6)
        self.folder = PhotoImage(file = "folder_icon2.gif").subsample(x = 4, y = 4)
        self.file = PhotoImage(file = "file_icon.gif").subsample(x = 8, y = 8)
        
        # Define and add widgets
        if selType == 'source':
            pathText = 'Source Folder:'
        elif selType == 'dest':
            pathText = 'Destination Folder'
        self.lbl_folder = ttk.Label(self, text = pathText, style = 'myLabel.TLabel')
        self.lbl_folder.grid(row = 0, column = 0, padx = (10, 0), pady = (10, 0), sticky = 'w')
        self.lbl_path = Label(self, text = '', width = 47, height = 2, wraplength = 335, anchor = 'w',
                                  background = 'white', borderwidth = 1, relief = SUNKEN, justify = LEFT)
        self.lbl_path.grid(row = 1, column = 0, padx = (10, 0), sticky = 'e')
        self.lbl_contents = ttk.Label(self, text = 'Contents:', style = 'myLabel.TLabel')
        self.lbl_contents.grid(row = 2, column = 0, padx = (10, 0), pady = (5, 0), sticky = 'w')
        self.btn_upLevel = ttk.Button(self, image = self.upArrow, command = lambda: self.upLevel())
        self.btn_upLevel.grid(row = 1, column = 1, sticky = 'w')
        

        # Treeview and scrollbar
        self.scroll_contents = ttk.Scrollbar(self, orient = VERTICAL)
        self.tree_contents = ttk.Treeview(self, columns = ('Filename'), height = 7, displaycolumns = 0,
                                    yscrollcommand = self.scroll_contents.set, selectmode = 'browse')
        self.tree_contents.column('#0', width = 40, anchor = 'center')
        self.tree_contents.column(0, width = 290)
        self.tree_contents.heading(0, text = 'Filename', anchor = 'w')
        self.scroll_contents.config(command = self.tree_contents.yview)
        self.tree_contents.bind("<Double-Button-1>", lambda event: self.newFolder(event))
        self.scroll_contents.grid(row = 3, column = 1, padx = (0, 5), pady = (0, 10), sticky = 'nws')
        self.tree_contents.grid(row = 3, column = 0, padx = (10, 0), pady = (0, 10), sticky = 'nes')
        
        # Add call to refresh here
        self.refreshFrame()

    # Updates path label and listbox contents to reflect current folder
    def refreshFrame(self):
        self.lbl_path.config(text = self.curPath)
        for i in self.tree_contents.get_children():
            self.tree_contents.delete(i)
        fileList = os.listdir(self.curPath)
        for fileName in fileList:
            newPath = Path(self.curPath / fileName)
            if newPath.is_dir():
                self.tree_contents.insert('', 'end', values = (fileName,), image = self.folder)
            else:
                self.tree_contents.insert('', 'end', values = (fileName,), image = self.file)

    # Set new path to parent of current path and refresh and clear transfer listbox
    def upLevel(self):
        if self.selType == 'source':
            appFrame.clearTransfer(fileApp)
        if Path(self.curPath).parent.exists():
            self.curPath = Path(self.curPath).parent
            self.refreshFrame()

    # Check if double clicked item is folder, and if so, sets current path
    # to new folder and refreshes. Also clears transfer listbox.
    def newFolder(self, event):
        if self.selType == 'source':
            appFrame.clearTransfer(fileApp)
        fileList = event.widget
        select = fileList.focus()
        treeData = fileList.item(select)
        fileName = treeData['values'][0]
        newPath = Path(self.curPath / fileName)
        if newPath.is_dir():
            self.curPath = newPath
            self.refreshFrame()
        else:
            messagebox.showwarning('Invalid Selection', 'The selected item is not a folder')

# Define appFrame class, which will hold the framework of the app and define
# the root window settings
class appFrame(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

        # Configure window
        self.master = master
        self.master.minsize(775, 560)
        self.master.maxsize(775, 560)
        self.centerWindow(775, 560)
        self.master.title("File Transfer Utility")
        self.master.configure(bg = "#f0f0f0")
        self.configure(bg = "#f0f0f0", bd = 5)
        self.pack(fill = BOTH)
        #self.grid_propagate(False)
        
        # Protocol method is Tkinter built-in method to catch
        # if user clicks upper corner "X" on Windows
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.ask_quit())
        arg = self.master

        # Add selection frames
        self.source = selectFrame(self, 'source')
        self.source.grid(row = 2, column = 0, columnspan = 3, sticky = 'new')
        self.destination = selectFrame(self, 'dest')
        self.destination.grid(row = 2, column = 4, sticky = 'new')

        # Add widgets
        self.lbl_instHead = ttk.Label(self, text = "Instructions:", style = 'myLabel.TLabel')
        self.lbl_instHead.grid(row = 0, column = 0, columnspan = 5, padx = 10, pady = (5, 0), sticky = 'w')
        self.lbl_instructions = ttk.Label(self, text = "Please select a source folder \
from which you wish to back up recently modified text files.\nNext, hit \
the Check Files button to see if there are files that need to be archived. \n\
Then, select the destination folder for archived files. \nFinally, click the \
Copy Files button to archive the listed files.",
                                          style = 'instructions.TLabel')
        self.lbl_instructions.grid(row = 1, column = 0, columnspan = 5, padx = 10, pady = (0, 5), sticky = 'w')
        self.btn_check = ttk.Button(self, text = 'Check Files', command = lambda: self.checkFiles())
        self.btn_check.grid(row = 3, column = 0, padx = (40, 0), pady = 10, sticky = 'w')
        self.btn_copy = ttk.Button(self, text = 'Copy Files', command = lambda: self.copyFiles())
        self.btn_copy.grid(row = 3, column = 1, columnspan = 2, padx = (0, 10), pady = 10, sticky = 'w')
        self.lbl_transfer = ttk.Label(self, text = 'The following text files have been modified since the last archive action:',
                                      style = 'myLabel.TLabel', wraplength = 320)
        self.lbl_transfer.grid(row = 4, column = 0, columnspan = 3, padx = (10, 0),
                               pady = (5, 0), sticky = 'w')
        
        # Listbox and scrollbar
        self.scroll_transfer = ttk.Scrollbar(self, orient = VERTICAL)
        self.lst_transfer = Listbox(self, width = 55, height = 5, exportselection = 0, borderwidth = 1, relief = SUNKEN,
                                    yscrollcommand = self.scroll_transfer.set, activestyle = 'none')
        self.scroll_transfer.config(command = self.lst_transfer.yview)
        self.scroll_transfer.grid(row = 5, column = 2, padx = (0, 5), pady = (0, 10), sticky = 'nws')
        self.lst_transfer.grid(row = 5, column = 0, columnspan = 2, padx = (10, 0), pady = (0, 10), sticky = 'nes')

        # subframe with last update information
        self.frm_lastCheck = Frame(self, bd = 1, relief = SUNKEN, bg = "#ffffff")
        self.frm_lastCheck.grid(row = 3, column = 4, rowspan = 3, padx = 10, pady = 10)
        self.lbl_lastCheck = ttk.Label(self.frm_lastCheck, text = 'Files last archived:',
                                       style = 'myLabel.TLabel', background = "#ffffff")
        self.lbl_lastCheck.grid(row = 0, column = 0, padx = 20, pady = (10, 5))
        self.lbl_checkDate = ttk.Label(self.frm_lastCheck, text = '', background = "#ffffff")
        self.lbl_checkDate.grid(row = 1, column = 0, padx = 20, pady = (5, 15))
        self.checkTime()
        

    def centerWindow(self, w, h):
        # Get overall screen width and height (Windows specific)
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        # calculate appropriate x and y values to center frame
        x = int((screen_width / 2) - (w / 2))
        y = int((screen_height / 2) - (h / 2))
        centerGeo = self.master.geometry('{}x{}+{}+{}'.format(w, h, x, y))
        return centerGeo

    def ask_quit(self):
        if messagebox.askokcancel('Exit Program', 'Okay to exit program?'):
            # Close app
            self.master.destroy()
            os._exit(0)
        
    # Checks contents of current source folder to see if any are text files
    # that have been modified since the last update and if so, adds them to listbox
    def checkFiles(self):
        # Get source file path
        curPath = self.source.curPath

        # Cycle through files in current source folder, and check files to see
        # if they should be listed
        fileList = os.listdir(curPath)
        for fileName in fileList:
            if fileName.endswith(".txt"):
                modifiedTime = os.stat(Path(curPath / fileName)).st_mtime
                if modifiedTime > self.lastCheck:
                    self.lst_transfer.insert(END, fileName)

    # Copy files shown in transfer listbox to destination folder
    def copyFiles(self):
        srcPath = self.source.curPath
        destPath = self.destination.curPath
        fileList = self.lst_transfer.get(0, END)
        if len(fileList) > 0:
            for file in fileList:
                shutil.copy(Path(srcPath / file), Path(destPath / file))
            self.destination.refreshFrame()
            messagebox.showinfo('File Transfer', 'Files successfully copied to: \n ' + str(destPath))
            self.lastCheck = int(time.time())
            with sqlite3.connect('archive_date.db') as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO tbl_archive VALUES(?)", (self.lastCheck,))
            self.checkTime()
            self.clearTransfer()
        else:
            messagebox.showwarning('No Files Selected', 'There were no files selected to be copied')

    def clearTransfer(self):
        self.lst_transfer.delete(0, END)
        
    # Check database and update most recent archive time
    def checkTime(self):
        with sqlite3.connect('archive_date.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT time FROM tbl_archive ORDER BY time DESC")
            self.lastCheck = cur.fetchone()[0]
            self.lbl_checkDate.config(text = time.ctime(self.lastCheck))
            
        
if __name__ == '__main__':

    #Check database and initialize if empty
    with sqlite3.connect('archive_date.db') as conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS tbl_archive(time INTEGER)")
        cur.execute("SELECT COUNT(*) FROM tbl_archive")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("INSERT INTO tbl_archive VALUES (0)")
            
    # Build main window and call application
    root = Tk()
    myStyle = ttk.Style()
    myStyle.configure('myLabel.TLabel', font = ('Helvetica', '10', 'bold'))
    myStyle.configure('instructions.TLabel', font = ('Helvetica', '10'))
    fileApp = appFrame(root)
    root.mainloop()
