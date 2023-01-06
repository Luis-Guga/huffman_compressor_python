from .classes.node import Node
from tabulate import tabulate
import csv

HEADER_MAX_DIGITS = 16


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


def get_decoding_dict_from_encoding_dict(encoding_dict: dict()):
    decoding_dict = dict()

    for key in encoding_dict:
        decoding_dict[encoding_dict[key]] = key

    return decoding_dict


def get_byte_list(bin_text: str):
    byte_list = bytearray()

    # by convention, the first char of a 8-char group will be on the left
    for i in range(0, len(bin_text), 8):
        byte = int(bin_text[i:i+8], 2)
        byte_list.append(byte)

    return byte_list


def print_encoding(tree: Node, symbol_frequency: list()):
    # get tree encoding dictionary
    encoding_dict: dict() = get_encoded_dict(tree)

    table = list()
    for (char, freq) in symbol_frequency:
        table.append(['%r' % (char), freq, encoding_dict[char]])

    print(tabulate(tabular_data=[['Encoding scheme: ']],
                   tablefmt='fancy_outline'))
    headers = ['CHAR', 'OCCURENCES', 'ENCODING']
    print(tabulate(table, headers, tablefmt='fancy_outline'))


def save_encoding(tree: Node, symbol_frequency: list(), file: str):
    encoding_dict: dict() = get_encoded_dict(tree)

    with open(file, 'w', encoding='utf-8') as out_table:
        csv_writer = csv.writer(out_table)
        csv_writer.writerow(['CHAR', 'OCCURENCES', 'ENCODING'])
        for (char, freq) in symbol_frequency:
            csv_writer.writerow([char, freq, encoding_dict[char]])


def save_binary(string: str, file: str):
    with open(file, 'w', encoding='utf-8') as out_bin:
        out_bin.write(string)


def print_statistics(message: str, encoded: str):
    print("========= STATISTICS =========")
    print("Original text size: %d bits" % (len(message)*8))
    print("Encoded text size: %d bits" % (len(encoded)))
    print("Size reduction: %d%%" % (100 - 100*len(encoded)/(len(message)*8)))
    print("==============================")


def build_header(symbol_frequency: list):
    table = str()
    header_size = str()

    for (char, freq) in symbol_frequency:
        table += char + str(freq)
    header_size += str(len(table)).zfill(HEADER_MAX_DIGITS)
    return header_size + table


def parse_compressed_file(file: str):
    symbol_frequency = dict()
    with open(file, 'rb') as input_file:
        header_size = input_file.read(HEADER_MAX_DIGITS)
        header = input_file.read(int(header_size)).decode()
        text = input_file.read()

    symbol_frequency: dict = build_table_from_header(header)

    padded_bits = int(chr(text[-1]))
    bin_encoded_text = restore_bin_encoded_text(text)
    bin_encoded_text = bin_encoded_text[:-(padded_bits+8)]

    return [symbol_frequency, bin_encoded_text]


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
    with open(file, 'r', encoding='utf-8') as input_file:
        # read everything at once. This way there are less function calls in comparison to as if one would read line by line
        message: str = input_file.read()
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


def get_encoded_text(origin_text: str, encoding_dict: dict):
    encoded_text = str()
    for char in origin_text:
        encoded_text += encoding_dict[char]

    return encoded_text


def restore_bin_encoded_text(encoded: str):
    bin_encoded_text = str()
    for ch in encoded:
        bin_encoded_text += bin(ch).replace('0b', '').zfill(8)

    return bin_encoded_text


def get_decoded_text(encoded_text: str, decoding_dict: dict):
    decoded_text = str()
    moving_window = str()
    for ch in encoded_text:
        if moving_window in decoding_dict:
            decoded_text += decoding_dict[moving_window]
            moving_window = str()
        moving_window += ch
    if moving_window in decoding_dict:
        decoded_text += decoding_dict[moving_window]
        moving_window = str()
    return decoded_text


def write_encoded_text_to_file(header: str, encoded_text: str, file: str):
    encoded_text, count_padding = add_padding(encoded_text)
    with open(file, 'w') as output_file:
        # write the encoding table
        output_file.write(header)

    with open(file, 'ab') as output_file:
        # convert encoded text in bytes to write to the file
        byte_list: list = get_byte_list(encoded_text)
        output_file.write(bytes(byte_list))
        output_file.write(count_padding.encode('utf-8'))


def add_padding(text: str):
    count_padding = count_padding_bits(text)
    text += '0' * count_padding
    return text, str(count_padding)


def count_padding_bits(text: str):
    return 8 - (len(text) % 8)
