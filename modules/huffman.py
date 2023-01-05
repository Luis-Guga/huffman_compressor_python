from .classes.node import Node
from tabulate import tabulate
import csv


# pseudo-end-of-file to add to the compressed file.
PSEUDO_EOF: str = chr(255)


def create_tree(tree: list()):
    while len(tree) > 1:
        # get the two least frequent symbols of the list to build the tree
        (sym1, freq1) = tree[-1]
        (sym2, freq2) = tree[-2]

        # remove them after the acquisition because we will turn the symbols into nodes
        tree = tree[:-2]

        # build the node of the tree
        node = Node((sym1, freq1), (sym2, freq2))

        # add node to the tree
        tree.append((node, freq1 + freq2))

        # resort the tree, so that the tree stays updated
        tree = sorted(tree, key=lambda n: n[1], reverse=True)

    return tree


def get_encoded_dict(node: Node, left: bool() = False, encoding: str() = ''):
    if type(node) is str:
        return {node: encoding}

    (l, r) = node.children()
    encoded = dict()
    encoded.update(get_encoded_dict(l[0], True, encoding + '0'))
    encoded.update(get_encoded_dict(r[0], False, encoding + '1'))

    return encoded


def str_to_bytes(text: str):
    byte_list = list()

    # must count how many bits we have for an integer
    bit_count = 0

    # current byte being built
    byte = 0

    # by convention, the first char of a 8-char group will be on the left
    for ch in text:
        # at the end of the byte, reset all the auxiliar variables and append the byte to the list
        if bit_count == 8:
            byte_list.append(byte)
            bit_count = 0
            byte = 0

        # build the currenct byte by shifting the 1's to the left, because the conversion from str to integer is needed
        # example: 0010110001 would be converted to 44 and 64 (not 2). the most important is to have the prefix correctly
        byte |= int(ch) << (7-bit_count)
        bit_count += 1

    byte_list.append(byte)

    return byte_list


def print_encoding(tree: Node, symbol_frequency: list()):
    # get tree encoding dictionary
    huffman_dict: dict() = get_encoded_dict(tree)

    table = list()
    for (char, freq) in symbol_frequency:
        table.append([char, freq, huffman_dict[char]])

    print(tabulate(tabular_data=[['Encoding scheme: ']],
                   tablefmt='fancy_outline'))
    headers = ['CHAR', 'OCCURENCES', 'ENCODING']
    print(tabulate(table, headers, tablefmt='fancy_outline'))


def save_encoding(tree: Node, symbol_frequency: list(), file: str):
    huffman_dict: dict() = get_encoded_dict(tree)

    with open(file, 'w') as out_table:
        csv_writer = csv.writer(out_table)
        csv_writer.writerow(['CHAR', 'OCCURENCES', 'ENCODING'])
        for (char, freq) in symbol_frequency:
            csv_writer.writerow([char, freq, huffman_dict[char]])


def save_binary(string: str, file: str):
    with open(file, 'w') as out_bin:
        out_bin.write(string)


def print_statistics(message: str, encoded: str):
    print("========= STATISTICS =========")
    print("Original text size: %d bits" % (len(message)*8))
    print("Encoded text size: %d bits" % (len(encoded)))
    print("Size reduction: %d%%" % (100 - 100*len(encoded)/(len(message)*8)))
    print("==============================")


def build_header(symbol_frequency: list):
    table = str()
    for (char, freq) in symbol_frequency:
        table += char + str(freq)
    return table


def parse_compressed_file(file: str):
    symbol_frequency = dict()

    with open(file, 'r') as input_file:
        text: str = input_file.read()
        header, text = pop_header(text)
        symbol_frequency: dict = build_table_from_header(header)

    return [symbol_frequency, text]


def pop_header(text: str):
    header = str()
    for i in range(len(text)):
        if text[i] == PSEUDO_EOF:
            header += text[i] + text[i+1]
            break
        header += text[i]
    text = text[len(header):]
    return [header, text]


def build_table_from_header(header: str):
    symbol_frequency = dict()
    occurences = str()
    symbol = str()
    got_occurences = False
    got_symbol = False
    for char in header:
        if not got_symbol and not char.isdecimal():
            symbol += char
        elif not got_occurences and char.isdecimal():
            got_symbol = True
            occurences += char
        else:
            got_symbol = False
            got_occurences = False
            symbol_frequency[symbol] = int(occurences)
            occurences = str()
            symbol = char
    symbol_frequency[symbol] = int(occurences)
    return symbol_frequency


def parse_uncompressed_file(file: str):
    with open(file, 'r') as input_file:
        # read everything at once. This way there are less function calls in comparison to as if one would read line by line
        message: str = input_file.read()

        message += PSEUDO_EOF
        symbol_frequency: dict = get_frequency_table(message)

    return (symbol_frequency, message)


def get_frequency_table(text: str):
    symbol_frequency = dict()
    # iterate through the message in the provided file (or as input on command-line) to count the most frequent symbols
    for symbol in text:

        # add the symbols and its frequency to the list, so that we can access them later to create the huffman's tree
        if symbol in symbol_frequency:
            symbol_frequency[symbol] += 1
        else:
            symbol_frequency[symbol]: int = 1

    return symbol_frequency


def get_encoded_text(origin_text: str, huffman_dict: dict):
    encoded_text = str()
    for char in origin_text:
        encoded_text += huffman_dict[char]

    return encoded_text


def write_encoded_text_to_file(header: str, encoded_text: str, file: str):
    with open(file, 'w') as output_file:
        # write the encoding table
        output_file.write(header)

        # convert every 32 chars into a 32 bit integer, the function returns a list of 32 bit integers
        byte_list: list = str_to_bytes(encoded_text)
        for byte in byte_list:
            output_file.write(chr(byte))
            print(chr(byte), end='')
        print()
