from empower.gui.mainwindow import MainWindow
from empower.ansys import AnsysParser
import xml.etree.ElementTree as ET
import os
import re


class Application:
    def __init__(self):
        self.projects = []
        
        self.main_window = MainWindow(self)
        self.main_window.mainloop()
        
    def read(self, filename):
        if not os.path.exists(filename):
            messagebox.showerror("Error", "Selected file does not exist.")
            return
            
        with open(filename, 'r') as file:
            content = file.read()
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            Project.parse(projects=self.projects, tree=tree)
        except ET.ParseError as e:
            messagebox.showerror("File Parse Error", f"Failed to read file:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
            
    def save(self):
        pass
        
    def save_as(self, filename):
        if self.projects:
            extension = os.path.splittext(filename)[1].lower()
            try:
                if ext == ".emp":
                    Project.tree.write(filename, encoding="utf-8", xml_declaration=True)
                elif ext == ".aedt":
                    with open(filename, "w") as f:
                        tree = Project.get_tree()
                        root_element = tree.getroot()
                        root_node = AnsysParser.convert_xml(root_element)                        
                        AnsysParser.write(node=root_node, file=f)
                else:
                    messagebox.showerror("Unsupported file type", "Only supports .emp and .aedt")
            except Exception as e:
                messagebox.showerror("Could not save file", str(e))


class ProjectElement:
    def __init__(self, element):
        name = element.get("Name")


class Project:
    filename = None
    name = None
    tree = None
    projects = []
    def __init__(self, tree=None, filename=None):
        if tree is not None:
            Project.parse(tree)
        else:
            #Project.tree = None
            Project.projects.append(self)
        
        if filename is not None:
            Project.filename = filename

    @classmethod
    def create_tree(cls): # Create tree from projects?
        root = ET.Element('AnsoftProject')
        for project in self.projects:
            ET.SubElement(root, 'HFSSModel', {'Name' : project.name})
        Project.tree = ET.ElementTree(root)

    @classmethod
    def get_tree(cls):
        Project.create_tree()
        return Project.tree
        
    @classmethod
    def parse(cls, projects, tree):
        Project.projects = []
        for model in root.iter("HFSSModel"):
            Project.projects.append(ProjectElement(model))
            
        
    @classmethod
    def get_name(cls):
        if Project.filename is not None:
            basename = os.path.basename(filename)
            return os.path.splitext(basename)[0]
    
'''
import xml.etree.ElementTree as ET

# 1. Create the root element
root = ET.Element('person_data')

# 2. Add a child element 'person' to the root
person = ET.SubElement(root, 'person', {'id': '1'}) # Added attribute 'id'

# 3. Add child elements 'name' and 'age' to 'person'
name = ET.SubElement(person, 'name')
age = ET.SubElement(person, 'age')

# 4. Set text content for the child elements
name.text = 'John Doe'
age.text = '30'

# 5. Create the ElementTree instance with the root
tree = ET.ElementTree(root)

# 6. Write the tree to an XML file
# Use xml_declaration=True and encoding='utf-8' for a well-formed XML file
try:
    tree.write('person.xml', encoding='utf-8', xml_declaration=True)
except IOError as e:
    print(f"Error writing file: {e}")

# To print the XML to the console, you can use tostring()
# import xml.etree.ElementTree as ET
# print(ET.tostring(root, encoding='utf-8').decode('utf-8'))

'''

