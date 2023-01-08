# from .classes.node import Node
from tabulate import tabulate


HEADER_TERMINATOR = chr(127)
HEADER_ELEMENT_SEPARATOR = chr(7)

""" 
The convention adoptet for this module is to treat all the encoding, building, writtig logic in itself, 
so the user only needs to call the functions after initializing a Huffman object with some encoded or 
decoded text.

It means that the majority of the functions do not even have a return values and parameters, because they 
use object-internal attributes to do the logic.
"""


class EmptyFile(Exception):
    pass


class NotCompressable(Exception):
    pass


class NoHeader(Exception):
    pass


class InvalidPadding(Exception):
    pass


class UnsortedHeap(Exception):
    pass


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
    def header(self):
        return self._header

    @header.setter
    def header(self, header):
        if header == None:
            raise ValueError(
                "Invalid header")
        self._header = header

    @property
    def header_size(self):
        return self._header_size

    @header_size.setter
    def header_size(self, header_size):
        if header_size == None:
            raise ValueError(
                "Invalid header size")
        self._header_size = header_size

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
        if encoded_text == None:
            raise ValueError("Invalid compressed text")
        self._encoded_text = encoded_text

    @property
    def byte_array(self):
        return self._byte_array

    @byte_array.setter
    def byte_array(self, byte_array):
        if byte_array == None:
            raise ValueError("Invalid encoded message")
        self._byte_array = byte_array

    @property
    def padding_count(self):
        return self._padding_count

    @padding_count.setter
    def padding_count(self, padding_count):
        if padding_count == None:
            raise ValueError(
                "Invalid header size")
        self._padding_count = padding_count

    def build_symbol_heap(self):
        """
        Builds a frequency table (MinHeap) based on the symbols encountered in the decoded text

        :param self:
            :self.decoded_text: decoded plain text given for compression
            :self.symbol_heap: frequency table to be build
        :type self: Huffman
            :self.decoded_text: str
            :symbol_heap: dict
        """
        # iterate through the message in the provided file (or as input on command-line) to count the most frequent symbols
        for symbol in self.decoded_text:
            # add the symbols and its frequency to the list, so that we can access them later to create the huffman's tree
            if symbol in self.symbol_heap:
                self.symbol_heap[symbol] += 1
            else:
                self.symbol_heap[symbol]: int = 1

    def build_tree(self):
        """
        Builds the Huffman Tree from the symbol frequency table

        :param self:
            :self.symbol_heap: frequency table to build the tree
            :self.tree: tree to be build
        :type self: Huffman
            :symbol_heap: dict
            :self.tree: Node
        :raise ValueError: if frequency table is empty
        :raise UnsortedHeap: if frequency table is not sorted
        """
        if not self.symbol_heap:
            raise ValueError(
                "The given symbol heap is empty.\nHit: Use the method Huffman.build_symbol_heap()")
        elif sorted(dict(self.symbol_heap).items(), key=lambda l: l[1], reverse=True) != self.symbol_heap:
            raise UnsortedHeap(
                "The given frequency needs to be initially sorted.\nHint: Use the method Huffman.sort_symbol_heap()")

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
        """
        Builds encoding dict based on the build Huffman Tree

        :param self:
            :self.tree: built tree
        :type self: Huffman
            :self.tree: Node
        :raise ValueError: if the Huffman Tree was not build
        """
        if self.tree._right == None and self.tree._left == None:
            raise ValueError(
                "The Huffman Tree needs to be build before building the encoding dictionary.\nHint: Use the method Huffman.build_tree()")

        self.encoding_dict = self.__build_encoding_dict_helper__(self.tree)

    def __build_encoding_dict_helper__(self, node: Node, encoding: str() = ''):
        """
        Builds encoding dict based on the children of the current given node

        It assigns each children with it's respective encoding ("0" for left child, "1" for right child), and 
        keeps calling itself recursivelly, until it reaches a leaf. The point of reaching the leaf is that, in
        the Huffman Tree, only the leaf contain the character. So once a leaf is reached, the key value of
        the dictionary can be added with its respective encoding.

        :param self: so that the method can call itself
        :type self: Huffman
        :param node: the node whose children are to be assigned with 1 or 0. 
        :type node: Node
        :encoding: encoding value built until the current node, it will always be appended until a leaf is reached.
        :return encoded: encoded dictionary build from the children of the current node
        :rtype: dict
        """
        # once a leaf is reached (i.e., the character itself),
        # return all the encoding done from the top of the tree,
        # and also the character which will be the key to the encoding value in the dictionary
        if type(node) is str:
            return {node: encoding}

        # get the node's children to assign them
        (l, r) = node.children()

        encoded = dict()

        # this dictionary will be updated with every subdictionary build from the LEFT child of the current node
        encoded.update(self.__build_encoding_dict_helper__(
            l[0], encoding + '0'))

        # this dictionary will be updated with every subdictionary build from the RIGHT child of the current node
        encoded.update(self.__build_encoding_dict_helper__(
            r[0], encoding + '1'))

        return encoded

    def build_decoding_dict_from_encoding_dict(self):
        """
        Once the encoding dict is built, build the decoding dict (i.e.: value becomes key and previous key becomes value)

        :param self:
            :self.encoding_dict: necessary to build the reversed dictionary
            :self.decoding_dict: reversed dictionary to be build
        :type self: Huffman
            :self.encoding_dict: dict
            :self.decoding_dict: dict
        :raise ValueError: it the encoding dict was not built yet
        """

        if not self.encoding_dict:
            raise ValueError(
                "Given encoding dictionary is empty.\nHint: Use the method Huffman.build_encoding_dict()")

        for key in self.encoding_dict:
            self.decoding_dict[self.encoding_dict[key]] = key

    def build_header(self):
        """
        Creates the header to the encoded file.
        Header format:
            <symbol><occurences><HEADER_ELEMENT_SEPARATOR>...<symbol><occurences><HEADER_ELEMENT_SEPARATOR><HEADER_TERMINATOR>


        :param self:
            :self.symbol_heap: necessary to build the dictionary
        :type self: Huffman
            :self.symbol_heap: dict
        :raise ValueError: if the encoding dict was not built yet
        """

        table = str()
        for (char, freq) in self.symbol_heap:
            table += char + str(freq) + HEADER_ELEMENT_SEPARATOR
        self.header = table + HEADER_TERMINATOR

    def build_heap_from_header(self):
        """
        Builds frequency table from header
        Header format:
            <symbol><occurences><HEADER_ELEMENT_SEPARATOR>...<symbol><occurences><HEADER_ELEMENT_SEPARATOR><HEADER_TERMINATOR>

        :param self:
            :self.header: contains the list with separator
        :type self: Huffman
            :self.header: str
        :raise ValueError: if the header has invalid format
        """
        header_element_list = list()
        header_element_list = self.header.split(HEADER_ELEMENT_SEPARATOR)
        header_element_list.pop()
        for element in header_element_list:
            self.symbol_heap[element[0]] = int(element[1:])

    def build_encoded_text(self):
        """
        Builds the encoded using the encoding dict

        :param self:
            :self.encoding_dict: contains the encoding table
        :type self: Huffman
            :self.encoding_dict: dict
        :raises EmptyFile: if no input text is provided
        """
        if not self.decoded_text:
            raise EmptyFile

        for char in self.decoded_text:
            self.encoded_text += self.encoding_dict[char]

    def sort_symbol_heap(self):
        """
        Sorts the frequency table, sorting key is symbol occurence

        :raises ValueError: if an empty frequency table is provided
        """

        if not self.symbol_heap:
            raise ValueError(
                "Cannot sort empty frequency table.\nHit: Use the method Huffman.build_symbol_heap()")

        self.symbol_heap = sorted(self.symbol_heap.items(),
                                  key=lambda l: l[1], reverse=True)

    def get_byte_list(self):
        """
        Converts the binary encoded text into real bytes

        Example: 
            01011101101011010101010111
            Gets converted to:
            [93, 173, 87]

        :param self:
            :self.encoded_text: array that contains the huffman encoded text
            :self.byte_array: array that contains the converted list
        :type self: Huffman
            :self.encoded_text: str
            :self.byte_array: bitearray 
        """
        # by convention, the first char of a 8-char group will be on the left
        for i in range(0, len(self.encoded_text), 8):
            byte = int(self.encoded_text[i:i+8], 2)
            self.byte_array.append(byte)

    def parse_uncompressed_file(self, file: str):
        """
        Reads file and gets its text

        :raises EmptyFile:
        :raises NotCompressable: if text is not ascii(utf8) text
        """
        with open(file, 'r', encoding='utf-8') as input_file:
            # read everything at once. This way there are less function calls in comparison to as if one would read line by line
            self.decoded_text = input_file.read()

            if not self.decoded_text:
                raise EmptyFile("Cannot compress empty file")
            if not self.decoded_text.isascii():
                raise NotCompressable(
                    "Only extended-ascii/utf8 encoded files are compressable")

    def parse_compressed_file(self, file: str):
        """
        Reads compressed file, decodes the header, recovers the frequency table and the huffman encoded text 

        :raises EmptyFile:
        :raises NoHeader:
        """
        tmp = list()
        with open(file, 'rb') as input_file:
            tmp = input_file.read().split(
                str.encode(HEADER_TERMINATOR), maxsplit=1)

            if not tmp:
                raise EmptyFile("Cannot decompress empty file")

            self.header = tmp[0].decode()

            if not self.header:
                raise NoHeader(
                    "Given compressed file has no valid table header")

            self.byte_array = tmp[1]

        self.build_heap_from_header()
        self.padding_count = int(chr(self.byte_array[-1]))
        if self.padding_count >= 8:
            raise InvalidPadding(
                "The acquired padding (%d bits) is not possible" % (self.padding_count))
        self.recover_bin_encoded_text()
        self.encoded_text = self.encoded_text[: -(self.padding_count+8)]

    def recover_bin_encoded_text(self):
        """
        From the bytearray object gotten from the file, recover the encoded huffman message 
        """

        for ch in self.byte_array:
            # Converts byte to str, removes the 0b in the beginning and padds the converted value with 8,
            # so that the zeros are not lost in the bin conversion.
            self.encoded_text += bin(ch).replace('0b', '').zfill(8)

    def build_decoded_text(self):
        """
        From the recovered huffman encoded message, recover the decoded text using the decoding table built previously

        :raises ValueError: if no decoding table is given or if there is no encoded text available
        or if no decoding dictionary is supplied
        """
        if not self.encoded_text:
            raise ValueError(
                "No huffman encoded message supplied.\nHint: Use the method Huffman.parse_compressed_file()")
        if not self.decoding_dict:
            raise ValueError(
                "No decoding dictionary supplied.\nHint: Use the method Huffman.build_decoding_dict_from_encoding_dict()")

        moving_window = str()
        for ch in self.encoded_text:
            if moving_window in self.decoding_dict:
                self.decoded_text += self.decoding_dict[moving_window]
                moving_window = str()
            moving_window += ch

        self.decoded_text += self.decoding_dict[moving_window]

    def write_encoded_text_to_file(self, file: str):
        """
        From the recovered huffman encoded message, recover the decoded text using the decoding table built previously

        :raises ValueError: if there is no encoded text to convert in bytes to write to the file
        :raises NoHeader: if no header was acquired before writting process
        """
        if not self.header:
            raise NoHeader(
                "File header is empty.\nHint: Use method Huffman.build_header()")
        if not self.encoded_text:
            raise ValueError(
                "No huffman encoded text was given.\nHint: Use method Huffman.build_encoded_text()")

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
        """
        Adds padding to the encoded text. Every char MUST HAVE 8 bits, so the encoded text must be divisible by 8 and padding
        can be necessary.

        """
        self.padding_count = self.count_padding_bits()
        self.encoded_text += '0' * self.padding_count

    def count_padding_bits(self):
        return (8 - (len(self.encoded_text) % 8)) % 8

    def print_encoding(self):
        table = list()
        for (char, freq) in self.symbol_heap:
            table.append(['%r' % (char), freq, self.encoding_dict[char]])

        headers = ['CHAR', 'OCCURENCES', 'ENCODING']
        print(tabulate(table, headers, tablefmt='fancy_outline'))
