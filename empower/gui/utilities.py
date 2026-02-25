import tkinter as tk
from tkinter import ttk


class RenderWindow(ttk.Frame):
	def __init__(self, parent, controller=None):
		super().__init__(parent)
		self.canvas_width = 480
		self.canvas_height = Display.DISPLAY_HEIGHT
		self.canvas_background = "white"
		self.canvas = tk.Canvas(
			self,
			width=self.canvas_width,
			height=self.canvas_height,
			bg=self.canvas_background
		)
		self.canvas.grid(row=0, column=0, sticky="nsew")


class Browser(ttk.Frame):
	def __init__(self, parent, controller=None):
		super().__init__(parent)
		self.tree = ttk.Treeview(self)
		self.tree.grid(row=0, column=0, sticky="nsew")


class Display(ttk.Frame):
	DISPLAY_HEIGHT = 480
	def __init__(self, parent, controller=None):
		super().__init__(parent)
		self.browser = Browser(self)
		self.render_window = RenderWindow(self)
		
		self.browser.grid(row=0, column=0, sticky="ns")
		self.render_window.grid(row=0, column=1, columnspan=2, sticky="ns")


class ProjectManager(ttk.Frame):
	def __init__(self, parent, controller=None):
		super().__init__(parent)
		self.projects = None
		self.root_item = None
		self.project_items = []

		self.frame = ttk.Labelframe(self, text="Project Manager")
		self.tree = ttk.Treeview(self.frame)

		self.tree.grid(row=0, column=0, sticky="nsew")
		self.frame.grid(row=0, column=0, sticky="nsew")

	def set_projects(self, value):
		self.projects = value
		self.update_projects()
		
	def update_projects(self):
		if self.projects is not None:
			self.project_items = []
			for item in self.tree.get_children():
				self.tree.delete(item)
			root = self.projects.tree.getroot()
			self.root_item = self.tree.insert("", tk.END, self.projects.get_name())
			for model in root.iter("HFSSModel"):
				name = model.get("Name")
				if name:
					self.project_items.append(self.tree.insert(self.root_item, tk.END, text=name))


class Properties(ttk.Frame):
	def __init__(self, parent, controller=None):
		super().__init__(parent)
		self.columns = ("Name", "Value", "Unit", "Evaluated Value")
		self.frame = ttk.Labelframe(self, text="Properties")
		self.tree = ttk.Treeview(self.frame, column=self.columns, show="headings")
		
		self.tree.column("Name", width=100, anchor="w")
		self.tree.column("Value", width=80, anchor="e")
		self.tree.column("Unit", width=60, anchor="center")
		self.tree.column("Evaluated Value", width=80, anchor="e")
		
		for column in self.columns:
			self.tree.heading(column, text=column)
			
		self.vertical_scroll = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
		self.horizontal_scroll = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
		self.tree.configure(yscrollcommand=self.vertical_scroll.set,
			xscrollcommand=self.horizontal_scroll.set)
		
		self.tree.grid(row=0, column=0)
		self.vertical_scroll.grid(row=0, column=1)
		self.horizontal_scroll.grid(row=1, column=0)
		self.frame.grid(row=0, column=0, sticky="nsew")


class MessageManager(ttk.Frame):
	def __init__(self, parent, controller=None):
		super().__init__(parent)
		self.frame = ttk.Labelframe(self, text="Message Manager")
		self.tree = ttk.Treeview(self.frame)
		
		self.tree.pack()
		self.frame.pack()


class ProgressViewer(ttk.Frame):
	def __init__(self, parent, controller=None,
			height=200, width=400):
		super().__init__(parent)
		
		self.frame = ttk.Labelframe(self, text="Progress")
		self.canvas = tk.Canvas(self.frame, height=height, width=width)
		self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.scrollbar.set)
		
		self.inner_frame = ttk.Frame(self.canvas)
		self.window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
		self.canvas.grid(row=0, column=0, sticky="nsew")
		self.scrollbar.grid(row=0, column=1, sticky="ns")
		
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		
		self.inner_frame.bind("<Configure>", self._on_frame_configure)
		self.canvas.bind("<Configure>", self._on_canvas_configure)
		
		self.items = []
		
		self.frame.grid(row=0, column=0)
		
	def _on_frame_configure(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
		
	def _on_canvas_configure(self, event):
		self.canvas.itemconfig(self.window, width=event.width)
		
	def add_item(self, text):
		item = Progress(self.inner_frame, text=text)
		item.pack(fill="x", padx=5, pady=3)
		self.items.append(item)
		
		return item


class Progress(ttk.Frame):
	def __init__(self, parent, text="", maximum=100):
		super().__init__(parent)
		
		self.label = ttk.Label(self, text=text, width=20, anchor="w")
		self.bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", maximum=maximum)
		self.label.grid(row=0, column=0, padx=5, sticky="w")
		self.progress.grid(row=0, column=1, padx=5, sticky="ew")
		self.columnconfigure(1, weight=1)
		
	def set(self, value):
		self.progress["value"] = value


class Status(ttk.Frame):
	def __init__(self, parent, controller=None):
		super().__init__(parent)
		self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
		self.label.pack(fill=tk.X)
		
	def set_status(self, format_string, *args):
		self.label.config(text=format_string % args)
		self.label.update_idletasks()
		
	def clear_status(self):
		self.label.config(text="")
		self.label.update_idletasks()

