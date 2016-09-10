from xml.etree.ElementTree import ElementTree, Element


# read xml and put it into tree, you can use it like this: tree = read_xml("XXX.xml")
def read_xml(in_path):
    tree = ElementTree()
    tree.parse(in_path)
    return tree


# write to file you point to,like this: write_xml(tree,"config,xml")
def write_xml(tree, out_path):
    tree.write(out_path, encoding="utf-8", xml_declaration=True)


# kv_map means the map contain attribute and attribute value, this method can judge whether node include this kv_map
# use like this: if_match(node,{"name":"Bob"})
def if_match(node, kv_map):
    for key in kv_map:
        if node.get(key) != kv_map.get(key):
            return False
    return True


# As you can see, this meth use to find node, you can use it like: find_nodes(tree,{parent node}/{child node})
def find_nodes(tree, path):
    return tree.findall(path)


# find node accurately, you can use it like this:get_node_by_keyvalue(nodes,"{attribute_name}":"{attribute_value}")
def get_node_by_keyvalue(nodelist, kv_map):
    result_nodes = []
    for node in nodelist:
        if if_match(node, kv_map):
            result_nodes.append(node)
    return result_nodes


# change node properties,like this: change_node_properties(nodes,{"attribute_name":"attribute_value"},false)
def change_node_properties(nodelist, kv_map, is_delete=False):
    for node in nodelist:
        for key in kv_map:
            if is_delete:
                if key in node.attrib:
                    del node.attrib[key]
            else:
                node.set(key, kv_map.get(key))


# change node text,like this: change_node_text(nodes,"hello world",true,false)
def change_node_text(nodelist, text, is_add=False, is_delete=False):
    for node in nodelist:
        if is_add:
            node.text += text
        elif is_delete:
            node.text = ""
        else:
            node.text = text


# create a node ,like this :create_node("person", {"age":"15","money":"200000"}, "this is the first content")
def create_node(tag, property_map, content):
    element = Element(tag, property_map)
    element.text = content
    return element


# add a child node,like this:add_child_node(result_nodes, a)
def add_child_node(nodelist, element):
    for node in nodelist:
        node.append(element)


# this can del node accurately
# like this:del_node_by_tagkeyvalue(del_parent_nodes, "chain", {"{attribute_name}": "{attribute_value}"})
def del_node_by_tagkeyvalue(nodelist, tag, kv_map):
    for parent_node in nodelist:
        children = parent_node.getchildren()
        for child in children:
            if child.tag == tag and if_match(child, kv_map):
                parent_node.remove(child)