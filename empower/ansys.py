import re
import xml.etree.ElementTree as ET


class Node:
    def __init__(self, tag):
        self.tag = tag
        self.attributes = {}
        self.entries = []
        self.children = []

    def __repr__(self):
        return f"Node({self.tag})"


class AnsysParser:
    def __init__(self, filename):
        pass

    @classmethod
    def convert(cls, node):
        elem = ET.Element(node.tag)

        for k, v in node.attributes.items():
            elem.set(k, str(v))

        for entry in node.entries:
            if entry["type"] == "call":
                e = ET.SubElement(elem, entry["name"])
                for i, arg in enumerate(entry["args"]):
                    e.set(f"arg{i}", str(arg))

            elif entry["type"] == "list":
                e = ET.SubElement(elem, entry["name"])
                e.set("count", str(entry["count"]))
                e.text = ",".join(str(v) for v in entry["values"])

        for child in node.children:
            elem.append(AnsysParser.convert(child))

        return elem

    @classmethod
    def convert_xml(cls, elem):
        node = Node(elem.tag)

        # Convert attributes
        for k, v in elem.attrib.items():
            node.attributes[k] = AnsysParser.parse_xml_value(v)

        # Process children
        for child in elem:

            # -----------------------------------------
            # Function-style entry (arg0, arg1, ...)
            # -----------------------------------------
            arg_keys = sorted([k for k in child.attrib if k.startswith("arg")])

            if arg_keys:
                args = [AnsysParser.parse_xml_value(child.attrib[k]) for k in arg_keys]

                node.entries.append({
                    "type": "call",
                    "name": child.tag,
                    "args": args
                })
                continue

            # -----------------------------------------
            # List-style entry (count + text)
            # -----------------------------------------
            if "count" in child.attrib and child.text:
                values = [AnsysParser.parse_xml_value(v.strip())
                          for v in child.text.split(",")]

                node.entries.append({
                    "type": "list",
                    "name": child.tag,
                    "count": int(child.attrib["count"]),
                    "values": values
                })
                continue

            # -----------------------------------------
            # Nested block
            # -----------------------------------------
            node.children.append(AnsysParser.convert_xml(child))

        return node

    @classmethod
    def parse(cls, filename):
        with open(filename, "r") as f:
            lines = f.readlines()

        root = None
        stack = []

        for raw_line in lines:
            if not raw_line.strip():
                continue

            indent = len(raw_line) - len(raw_line.lstrip())
            line = raw_line.strip()

            # --------------------------------------------------
            # BEGIN
            # --------------------------------------------------
            if line.startswith("$begin"):
                tag = re.search(r"'(.*?)'", line).group(1)
                node = Node(tag)

                if stack:
                    stack[-1][1].children.append(node)
                else:
                    root = node

                stack.append((indent, node))

            # --------------------------------------------------
            # END
            # --------------------------------------------------
            elif line.startswith("$end"):
                stack.pop()

            # --------------------------------------------------
            # Attribute
            # --------------------------------------------------
            elif "=" in line and not "(" in line:
                key, val = line.split("=", 1)
                stack[-1][1].attributes[key.strip()] = AnsysParser.parse_value(val)

            # --------------------------------------------------
            # Entry (function style)
            # --------------------------------------------------
            elif "(" in line and ")" in line:
                name = line[:line.index("(")]
                params = line[line.index("(")+1:line.index(")")]

                args = []
                if params.strip():
                    args = [parse_value(p) for p in params.split(",")]

                stack[-1][1].entries.append({
                    "type": "call",
                    "name": name,
                    "args": args
                })

            # --------------------------------------------------
            # Entry (list style)
            # --------------------------------------------------
            elif "[" in line and "]" in line:
                name = line[:line.index("[")]
                content = line[line.index("[")+1:line.index("]")]
                count_part, values_part = content.split(":", 1)

                count = int(count_part)
                values = [AnsysParser.parse_value(v) for v in values_part.split(",")]

                stack[-1][1].entries.append({
                    "type": "list",
                    "name": name,
                    "count": count,
                    "values": values
                })

        return root

    @classmethod
    def parse_value(cls, val):
        val = val.strip()

        if val.lower() in ("true", "false"):
            return val.lower() == "true"
        if re.fullmatch(r"-?\d+", val):
            return int(val)
        if re.fullmatch(r"-?\d+\.\d+", val):
            return float(val)
        if val.startswith("'") and val.endswith("'"):
            return val[1:-1]

        return val

    @classmethod
    def parse_xml_value(cls, val):
        """Convert XML string values into int/float/bool if possible."""
        if val.lower() in ("true", "false"):
            return val.lower() == "true"

        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return val
        
    @classmethod
    def write(cls, node, file, indent=0):
        space = "\t" * indent

        file.write(f"{space}$begin '{node.tag}'\n")

        # Attributes
        for k, v in node.attributes.items():
            if isinstance(v, str):
                v = f"'{v}'"
            file.write(f"{space}    {k}={v}\n")

        # Entries
        for entry in node.entries:
            if entry["type"] == "call":
                args = []
                for a in entry["args"]:
                    if isinstance(a, str):
                        args.append(f"'{a}'")
                    else:
                        args.append(str(a))
                file.write(f"{space}    {entry['name']}({', '.join(args)})\n")

            elif entry["type"] == "list":
                vals = []
                for v in entry["values"]:
                    if isinstance(v, str):
                        vals.append(f"'{v}'")
                    else:
                        vals.append(str(v))
                file.write(f"{space}    {entry['name']}[{entry['count']}: {', '.join(vals)}]\n")

        # Children
        for child in node.children:
            AnsysParser.write(child, file, indent + 4)

        file.write(f"{space}$end '{node.tag}'\n")

# Usage
"""
xml_root = AnsysParser.convert(root)
tree = ET.ElementTree(xml_root)
tree.write("output.emp", encoding="utf-8", xml_declaration=True)
with open("output.aedt", "w") as f:
    AnsysParser.write(root, f)
    
tree = ET.parse("input.emp")
root_element = tree.getroot()
root_node = xml_to_node(root_element)
with open("input.aedt", "w") as f:
    write_node(root_node, f)
"""

# Example input
"""  
$begin 'project'
    version=1
    active=True

    component('motor', 10)
    offsets[2: 15, 30]

    $begin 'subsystem'
        name='control'
    $end 'subsystem'

$end 'project'
"""

# Parsed object
"""
Node(project)
  attributes: {version:1, active:True}
  entries: [...]
  children: [Node(subsystem)]
"""

