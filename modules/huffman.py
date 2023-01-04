from .classes.node import Node


def create_tree(tree: list()):
    while len(tree) > 1:
        # get the two least frequent symbols of the list to build the tree of the tree
        (sym1, freq1) = tree[-1]
        (sym2, freq2) = tree[-2]

        # we also remove them after the aquisition because we will turn the symbols into nodes
        tree = tree[:-2]

        # build the node of the tree
        node = Node((sym1, freq1), (sym2, freq2))

        # add node to the tree
        tree.append((node, freq1 + freq2))

        # resort the tree, so that the tree stays updated
        tree = sorted(tree, key=lambda n: n[1], reverse=True)

    return tree


def get_encoded_message(node: Node, left: bool() = False, encoding: str() = ''):
    if type(node) is str:
        return {node: encoding}

    (l, r) = node.children()
    encoded = dict()
    encoded.update(get_encoded_message(l[0], True, encoding + '0'))
    encoded.update(get_encoded_message(r[0], False, encoding + '1'))

    return encoded


def print_encoding(tree: Node, symbol_frequency: list()):
    huffman_dict: dict() = get_encoded_message(tree)

    for (char, freq) in symbol_frequency:
        print('%r->%s' % (char, huffman_dict[char]))
