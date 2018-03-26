import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pickle
import os
from draggableWidget import *

class ToDo(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Untitled - To do")
        
        self.minsize(116, 25)
        self.geometry("400x300")

        self.protocol("WM_DELETE_WINDOW", self.closeWindow)

        self.filename = None
        
        self.menuBar = MenuBar(self)

        self.taskFrame = TaskFrame(self)
        self.taskFrame.pack(fill=tk.BOTH, expand=True)
        self.taskFrame.lift()

        self.updateTasks()

        try:
            self.loadData()
        except:
            raise

    def closeWindow(self, *args, **kwargs):
        if "1" in self.winfo_geometry().split("+")[0].split("x"):
            self.geometry("400x300")
            
        self.saveData()
        self.destroy()

    def loadData(self, *args, **kwargs):
        with open(os.getcwd()+"\\programData.pkl", "rb") as f:
            data = pickle.load(f)
 
        self.open(filename=data["filename"])

    def saveData(self, *args, **kwargs):
        data = {"size": self.winfo_geometry(), "filename": self.filename}
        
        with open(os.getcwd()+"\\programData.pkl", "wb") as f:
            pickle.dump(data, f)

    def new(self, *args, **kwargs):
        self.taskFrame.tasks = []
        self.title("Untitled - To Do")
        self.updateTasks()

    def open(self, *args, **kwargs):
        geometry = self.winfo_geometry()
        tasks = self.taskFrame.tasks
        title = self.title()

        try:
            self.filename = self.taskFrame.open(*args, **kwargs)

            if "\\" in self.filename:
                filename = self.filename.split("\\")[-1].replace(".todo", "")
            else:
                filename = self.filename.split("/")[-1].replace(".todo", "")
            
            self.title("{} - To Do".format(filename))
        except FileNotFoundError:
            self.taskFrame.tasks = tasks
            self.title(title)

        self.geometry(geometry)
        self.saveData()

    def save(self, *args, **kwargs):
        try:
            filename = self.taskFrame.save(*args, **kwargs)

            self.title("{} - To Do".format(filename))
        except PermissionError:
            pass
        
        self.saveData()

    def updateTasks(self, *args, **kwargs):
        self.taskFrame.updateTasks()

    def addTask(self, *args, **kwargs):
        geometry = self.winfo_geometry()
        self.taskFrame.addTask(*args, **kwargs)
        self.geometry(geometry)

    def addGroup(self, *args, **kwargs):
        geometry = self.winfo_geometry()
        group = self.taskFrame.addGroup(*args, **kwargs)
        self.geometry(geometry)
        self.taskFrame.frameConfig()

        return group

class TaskFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = tk.Frame(master=parent)

        self.scroll = tk.Scrollbar(self.parent, orient=tk.VERTICAL)
        self.scroll.grid(row=0, column=1, sticky="nse")
        self.canvas = tk.Canvas(self.parent, bd=0, highlightthickness=0,
                                yscrollcommand=self.scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll.config(command=self.canvas.yview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        tk.Frame.__init__(self, *args, master=self.canvas, **kwargs)
        self.id = self.canvas.create_window(0, 0, window=self, anchor=tk.NW,
                                            height=self.canvas.winfo_height())

        self.columnconfigure(0, weight=1)

        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self._configure_canvas)
        self.bind("<Configure>", self._configure_interior)
        self.canvas.bind_all("<MouseWheel>", self._mousewheel)

        self.tasks = []

    def _configure_interior(self, *args, **kwargs):
        size = (self.winfo_reqwidth(), self.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.winfo_reqwidth())

            wrap = self.winfo_width() - 30
            if wrap < 0:
                wrap = 0

            for task in self.tasks:
                task.config(wraplength=wrap)

    def _configure_canvas(self, *args, **kwargs):
        if (self.winfo_reqwidth() != self.canvas.winfo_width() or
            self.winfo_reqheight() != self.canvas.winfo_height()):
            self.canvas.itemconfigure(self.id, width=self.canvas.winfo_width(),
                                      height=self.canvas.winfo_height())

    def _mousewheel(self, event):
        self.canvas.yview_scroll(int(-(event.delta/120)), "units")
        if self.canvas.canvasy(0) < 0:
            self.canvas.yview_moveto(0)
        
    def frameConfig(self, *args, **kwargs):
        if "width" in kwargs.keys():
            width = kwargs.pop("width")
        else:
            width = self.winfo_reqwidth()
            
        self.canvas.config(width=width)
        self.canvas.itemconfigure(self.id, width=self.canvas.winfo_width())

    def grid(self, *args, **kwargs):
        self.parent.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.parent.pack(*args, **kwargs)

    def open(self, *args, **kwargs):
        if "filename" in kwargs.keys():
            filename = kwargs.pop("filename")
        else:
            filename = askopenfilename(parent=self.parent,
                                       filetypes=[("To Do Files", "*.todo")],
                                       defaultextension=".todo")

        with open(filename, "rb") as f:
            data = pickle.load(f)

        self.tasks = []
        for task in data:
            self.addTask(**task)

        return filename

    def save(self, *args, **kwargs):
        if "filename" in kwargs.keys():
            filename = kwargs.pop("filename")
        else:
            filename = asksaveasfilename(parent=self.parent,
                                         filetypes=[("To Do Files", "*.todo")],
                                         defaultextension=".todo")

        data = self.getTasks()

        with open(filename, "wb") as f:
            pickle.dump(data, f)

        return filename

    def updateTasks(self, *args, **kwargs):
        for widget in self.grid_slaves():
            widget.grid_forget()
            
        count = 0
        for task in self.tasks:
            task.grid(row=count, column=0, sticky="w")

            count += 1

    def addTask(self, *args, **kwargs):
        if "update" in kwargs.keys():
            update = kwargs.pop("update")
        else:
            update = True
            
        self.tasks.append(TaskCheckbutton(self, *args, **kwargs))

        if update:
            self.updateTasks()

    def getTasks(self, *args, **kwargs):
        output = []
        for task in self.tasks:
            output.append({"text": task["text"], "value": task.get()})

        return output

class DraggableFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, *args, master=parent, **kwargs)

        self.pressed = False
        
        self.bind("<Button-3>", self.press)
        self.bind("<ButtonRelease-3>", self.release)
        self.bind("<Motion>", self.move)

    def press(self, event):
        self.pressed = True
        self.x = event.x
        self.y = event.y
        self.lift()
        self.config(borderwidth=1, relief=tk.RIDGE)

    def release(self, event):
        self.pressed = False
        self.config(borderwidth=0, relief=tk.FLAT)

        y = (event.widget.winfo_pointery()
             - self.master.winfo_rooty())

        parents = []
        for task in self.master.tasks:
            parents.append(task.parent)

        height = 0
        for i in range(len(self.master.tasks)):
            if self.winfo_y() < 5:
                item = self.master.tasks.pop(parents.index(self))
                self.master.tasks.insert(0, item)
                break
            
            task = self.master.tasks[i]
            height += task.parent.winfo_height()

            if (task != self
                and y < height - task.parent.winfo_height() / 2):
                item = self.master.tasks.pop(parents.index(self))
                self.master.tasks.insert(i, item)
                break
            elif i == len(self.master.tasks) - 1:
                item = self.master.tasks.pop(parents.index(self))
                self.master.tasks.append(item)
                        
        self.master.updateTasks()

    def move(self, event):
        if self.pressed:
            y = (event.widget.winfo_pointery()
                 - self.master.winfo_rooty() - self.y)

            if y < 0:
                y = 0
            elif (y > self.master.winfo_height() - self.winfo_height()):
                y = (self.master.winfo_height() - self.winfo_height())

            self.place(x=0, y=y)        

class TaskCheckbutton(tk.Checkbutton):
    def __init__(self, parent, *args, **kwargs):
        self.var = tk.BooleanVar()

        if "notes" in kwargs.keys():
            self.notes = kwargs.pop("notes")
        else:
            self.notes = ""

        if "value" in kwargs.keys():
            self.var.set(kwargs.pop("value"))

        if "space" in kwargs.keys():
            self.space = kwargs.pop("space")
        else:
            self.space = 0

        self.parent = DraggableFrame(parent)#tk.Frame(master=parent)

        self.spaceLabel = tk.Label(self.parent, text=" "*self.space)
        self.spaceLabel.grid(row=0, column=0, sticky="ew")
                         
        tk.Checkbutton.__init__(self, *args, master=self.parent,
                                variable=self.var, justify=tk.LEFT, **kwargs)
        self.grid_configure(row=0, column=1, sticky="w")

        self.bind("<Button-3>", self.parent.press)
        self.bind("<ButtonRelease-3>", self.parent.release)
        self.bind("<Motion>", self.parent.move)

        #self.pressed = False
        
        """self.bind("<Button-3>", self.press)
        self.bind("<ButtonRelease-3>", self.release)
        self.bind("<Motion>", self.move)

    def press(self, event):
        self.pressed = True
        self.x = event.x
        self.y = event.y
        self.parent.lift()
        self.parent.config(borderwidth=1, relief=tk.RIDGE)

    def release(self, event):
        self.pressed = False
        self.parent.config(borderwidth=0, relief=tk.FLAT)

        y = (event.widget.winfo_pointery()
             - self.parent.master.winfo_rooty())

        if self.parent.winfo_y() < 5:
            self.parent.master.tasks.pop(self.parent.master.tasks.index(self))
            self.parent.master.tasks.insert(0, self)
        else:
            height = 0
            for i in range(len(self.parent.master.tasks)):
                task = self.parent.master.tasks[i]
                height += task.parent.winfo_height()

                if (task != self and y < height - task.parent.winfo_height() / 2):
                    self.parent.master.tasks.pop(
                        self.parent.master.tasks.index(self))
                    self.parent.master.tasks.insert(i, self)
                    
                    break
                elif i == len(self.parent.master.tasks) - 1:
                    self.parent.master.tasks.pop(
                            self.parent.master.tasks.index(self))
                    self.parent.master.tasks.append(self)
                        
        self.parent.master.updateTasks()

    def move(self, event):
        if self.pressed:
            y = (event.widget.winfo_pointery()
                 - self.parent.master.winfo_rooty() - self.y)

            if y < 0:
                y = 0
            elif (y > self.parent.master.winfo_height()
                  - self.parent.winfo_height()):
                y = (self.parent.master.winfo_height()
                     - self.parent.winfo_height())

            self.parent.place(x=0, y=y)"""
        
    def get(self, *args, **kwargs):
        return self.var.get()

    def grid(self, *args, **kwargs):
        self.parent.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.parent.pack(*args, **kwargs)

class MenuBar(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, *args, master=parent, **kwargs)
        self.master.config(menu=self)

        self.fileMenu = tk.Menu(self, tearoff=False)
        self.fileMenu.add_command(label="New List", command=self.new,
                                  accelerator="Ctrl+N")
        self.fileMenu.add_command(label="Open...", command=self.open,
                                  accelerator="Ctrl+O")
        self.fileMenu.add_command(label="Save", command=self.save,
                                  accelerator="Ctrl+S")
        self.fileMenu.add_command(label="Save As...", command=self.saveAs,
                                  accelerator="Ctrl+Shift+S")
        self.add_cascade(label="File", menu=self.fileMenu)

        self.editMenu = tk.Menu(self, tearoff=False)
        self.editMenu.add_command(label="Add Task", command=self.addTask)
        self.add_cascade(label="Edit", menu=self.editMenu)

        self.master.bind("<Control-n>", self.new)
        self.master.bind("<Control-o>", self.open)
        self.master.bind("<Control-s>", self.save)
        self.master.bind("<Control-S>", self.saveAs)

    def new(self, *args, **kwargs):
        self.master.new()

    def open(self, *args, **kwargs):
        self.master.open()

    def save(self, *args, **kwargs):
        if self.master.filename != None:
            self.master.save(filename=self.master.filename)

    def saveAs(self, *args, **kwargs):
        self.master.save()

    def addTask(self, *args, **kwargs):
        def ok(*args, **kwargs):
            self.master.addTask(text=entry.get().strip(),
                                notes=text.get("0.0", tk.END).strip())
            window.destroy()
            
        window = tk.Toplevel(self.master, padx=7, pady=5)
        window.title("Add Task")
        window.resizable(False, False)

        label1 = tk.Label(window, text="Label:")
        label1.grid(row=0, column=0, sticky="w")

        entry = tk.Entry(window, width=40)
        entry.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=2)

        label2 = tk.Label(window, text="Notes:")
        label2.grid(row=2, column=0, sticky="w")

        text = tk.Text(window, width=40, height=5)
        text.grid(row=3, column=0, sticky="nsew", pady=2)

        scroll = tk.Scrollbar(window)
        scroll.grid(row=3, column=1, sticky="nse", pady=2)

        text.config(yscrollcommand=scroll.set)
        scroll.config(command=text.yview)

        buttonFrame = tk.Frame(window)
        buttonFrame.grid(row=4, column=0, columnspan=2)

        okButton = ttk.Button(buttonFrame, text="Ok", command=ok)
        okButton.grid(row=0, column=0, padx=2, pady=2)

        cancelButton = ttk.Button(buttonFrame, text="Cancel",
                                  command=window.destroy)
        cancelButton.grid(row=0, column=1, padx=2, pady=2)

        entry.focus_force()

if __name__ == "__main__":
    todo = ToDo()
    todo.mainloop()
