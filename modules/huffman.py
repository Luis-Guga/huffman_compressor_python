# from .classes.node import Node
from tabulate import tabulate
import csv

HEADER_TERMINATOR = chr(127)
HEADER_ELEMENT_SEPARATOR = chr(7)


class Node:
    def __init__(self, left=None, right=None):
        self._left = left
        self._right = right

    def children(self):
        return (self._left, self._right)

    def __str__(self):
        return f"{self._left}_{self._right}"


HEADER_MAX_DIGITS = 16


class Huffman:

    def __init__(self):
        self.symbol_heap = dict()
        self.encoding_dict = dict()
        self.decoding_dict = dict()
        self.header = str()
        self.header_size = int()
        self.decoded_text = str()
        self.byte_array = bytearray()
        self.encoded_text = str()
        self.tree = Node()
        self.padding_count = int()

    @property
    def symbol_heap(self):
        return self._symbol_heap

    @symbol_heap.setter
    def symbol_heap(self, symbol_heap):
        if symbol_heap == None:
            raise ValueError("Invalid list (None)")
        self._symbol_heap = symbol_heap

    @property
    def encoding_dict(self):
        return self._encoding_dict

    @encoding_dict.setter
    def encoding_dict(self, encoding_dict):
        if encoding_dict == None:
            raise ValueError(
                "Invalid encoding dictionary (None)")
        self._encoding_dict = encoding_dict

    @property
    def decoding_dict(self):
        return self._decoding_dict

    @decoding_dict.setter
    def decoding_dict(self, decoding_dict):
        if decoding_dict == None:
            raise ValueError(
                "Invalid decoding dictionary (None)")
        self._decoding_dict = decoding_dict

    @property
    def decoded_text(self):
        return self._decoded_text

    @decoded_text.setter
    def decoded_text(self, decoded_text):
        if decoded_text == None:
            raise ValueError("Invalid text")
        self._decoded_text = decoded_text

    @property
    def encoded_text(self):
        return self._encoded_text

    @encoded_text.setter
    def encoded_text(self, encoded_text):
        if encoded_text == None or len(encoded_text) == 1:
            raise ValueError("Invalid compressed text")
        self._encoded_text = encoded_text

    @property
    def byte_array(self):
        return self._byte_array

    @byte_array.setter
    def byte_array(self, byte_array):
        if byte_array == None or len(byte_array) == 1:
            raise ValueError("Invalid encoded message")
        self._byte_array = byte_array

    def build_frequency_table(self):
        # iterate through the message in the provided file (or as input on command-line) to count the most frequent symbols
        for symbol in self.decoded_text:
            # add the symbols and its frequency to the list, so that we can access them later to create the huffman's tree
            if symbol in self.symbol_heap:
                self.symbol_heap[symbol] += 1
            else:
                self.symbol_heap[symbol]: int = 1

    def build_tree(self):
        symbol_heap: list() = self.symbol_heap

        while len(symbol_heap) > 1:
            # get the two least frequent symbols of the list to build the tree
            (sym1, freq1) = symbol_heap[-1]
            (sym2, freq2) = symbol_heap[-2]

            # remove them after the acquisition because we will turn the symbols into nodes
            symbol_heap = symbol_heap[:-2]

            # build the node of the self.symbol_heap
            node = Node((sym1, freq1), (sym2, freq2))

            # add node to the self.symbol_heap
            symbol_heap.append((node, freq1 + freq2))

            # resort the tree, so that the tree stays updated
            symbol_heap = sorted(
                symbol_heap, key=lambda n: n[1], reverse=True)

        self.tree = symbol_heap[0][0]

    def build_encoding_dict(self):
        self.encoding_dict = self.__build_encoding_dict_helper__(self.tree)

    def __build_encoding_dict_helper__(self, node: Node, left: bool() = False, encoding: str() = ''):
        if type(node) is str:
            return {node: encoding}

        (l, r) = node.children()

        encoded = dict()

        encoded.update(self.__build_encoding_dict_helper__(
            l[0], True, encoding + '0'))
        encoded.update(self.__build_encoding_dict_helper__(
            r[0], False, encoding + '1'))

        return encoded

    def build_decoding_dict_from_encoding_dict(self):
        for key in self.encoding_dict:
            self.decoding_dict[self.encoding_dict[key]] = key

    def build_header(self):
        table = str()
        for (char, freq) in self.symbol_heap:
            table += char + str(freq) + HEADER_ELEMENT_SEPARATOR
        self.header = table + HEADER_TERMINATOR

    def build_heap_from_header(self):
        header_element_list = list()
        header_element_list = self.header.split(HEADER_ELEMENT_SEPARATOR)
        header_element_list.pop()
        for element in header_element_list:
            self.symbol_heap[element[0]] = int(element[1:])

    def build_encoded_text(self):
        for char in self.decoded_text:
            self.encoded_text += self.encoding_dict[char]

    def sort_symbol_heap(self):
        self.symbol_heap = sorted(self.symbol_heap.items(),
                                  key=lambda l: l[1], reverse=True)

    def get_byte_list(self):
        # by convention, the first char of a 8-char group will be on the left
        for i in range(0, len(self.encoded_text), 8):
            byte = int(self.encoded_text[i:i+8], 2)
            self.byte_array.append(byte)

    def parse_uncompressed_file(self, file: str):
        with open(file, 'r', encoding='utf-8') as input_file:
            # read everything at once. This way there are less function calls in comparison to as if one would read line by line
            self.decoded_text = input_file.read()
            self.build_frequency_table()

    def parse_compressed_file(self, file: str):
        tmp = list()
        with open(file, 'rb') as input_file:
            tmp = input_file.read().split(
                str.encode(HEADER_TERMINATOR), maxsplit=1)
            self.header = tmp[0].decode()
            self.byte_array = tmp[1]
        self.build_heap_from_header()
        padded_bits = int(chr(self.byte_array[-1]))
        self.restore_bin_encoded_text()
        self.encoded_text = self.encoded_text[:-(padded_bits+8)]

    def restore_bin_encoded_text(self):
        for ch in self.byte_array:
            self.encoded_text += bin(ch).replace('0b', '').zfill(8)

    def build_decoded_text(self):
        moving_window = str()
        for ch in self.encoded_text:
            if moving_window in self.decoding_dict:
                self.decoded_text += self.decoding_dict[moving_window]
                moving_window = str()
            moving_window += ch

        self.decoded_text += self.decoding_dict[moving_window]

    def write_encoded_text_to_file(self, file: str):
        self.add_padding()
        with open(file, 'w') as output_file:
            # write the encoding table
            output_file.write(self.header)

        with open(file, 'ab') as output_file:
            # convert encoded text in bytes to write to the file
            self.get_byte_list()
            output_file.write(bytes(self.byte_array))
            output_file.write(str(self.padding_count).encode('utf-8'))

    def add_padding(self):
        self.padding_count = self.count_padding_bits()
        self.encoded_text += '0' * self.padding_count

    def count_padding_bits(self):
        return 8 - (len(self.encoded_text) % 8)

    def save_encoding_table(self, file: str):
        with open(file, 'w', encoding='utf-8') as out_table:
            csv_writer = csv.writer(out_table)
            csv_writer.writerow(['CHAR', 'OCCURENCES', 'ENCODING'])
            for (char, freq) in self.symbol_heap:
                csv_writer.writerow([char, freq, self.encoding_dict[char]])

    def save_binary(self, file: str):
        with open(file, 'w', encoding='utf-8') as out_bin:
            out_bin.write(self.encoded_text)

    def print_statistics(self, encoded_file, decoded_file):
        table = list()

        print(tabulate(tabular_data=[
              ["STATISTICS"]], tablefmt='fancy_outline'))

        table.append(["Original text size ", str(
            len(self.decoded_text)*8) + " bits"])

        table.append(["Encoded text size ", str(
            len(self.encoded_text)*8) + " bits"])

        table.append(["Size reduction", str((100 - 100 *
                     len(self.encoded_text)/(len(self.decoded_text)*8))) + "%%"])

        print(tabulate(table, tablefmt='fancy_outline'))

    def print_encoding(self):
        table = list()
        for (char, freq) in self.symbol_heap:
            table.append(['%r' % (char), freq, self.encoding_dict[char]])

        headers = ['CHAR', 'OCCURENCES', 'ENCODING']
        print(tabulate(table, headers, tablefmt='fancy_outline'))
