#!/usr/bin/env python3.8
from project import save_encoding_table, save_binary, define_program_args
from modules.huffman import Huffman
import pytest
import os
TEST_FILE = 'huffman_test_file'

# PROJECT.PY TESTS


def test_define_program_args():
    argparser = define_program_args()
    assert argparser


def test_save_binary():
    encoded_text = '10101011101010111010110101011'
    save_binary(encoded_text, TEST_FILE)
    with open(TEST_FILE, 'r') as test_file:
        read_text = test_file.read()
    os.remove(TEST_FILE)
    assert read_text == encoded_text


def test_save_binary_exception():
    with pytest.raises(ValueError):
        encoded_text = ''
        save_binary(encoded_text, TEST_FILE)


def test_save_encoding_table():
    huffman = Huffman()
    huffman.decoded_text = 'aaaaaaaabbbbbbbcccccc\'\'\'\'\'' + \
        chr(127)*4 + '>>>'
    huffman.build_symbol_heap()
    huffman.sort_symbol_heap()
    huffman.build_tree()
    huffman.build_encoding_dict()
    save_encoding_table(huffman.encoding_dict, huffman.symbol_heap, TEST_FILE)
    with open(TEST_FILE, 'r') as test_file:
        row = test_file.readline()
        for element in ["CHAR", "OCCURENCES", "ENCODING"]:
            assert element in row
        lines = test_file.readlines()
        for row in lines:
            char, occ, encoding = row.replace('\n', '').split(',', maxsplit=3)
            assert char.isascii()
            assert occ.isnumeric()
            assert {'0', '1'} == set(encoding) or {'0'} == set(
                encoding) or {'1'} == set(encoding)
    os.remove(TEST_FILE)


def test_save_encoding_table_empty_dict():
    huffman = Huffman()
    huffman.decoded_text = 'aaaaaaaabbbbbbbcccccc\'\'\'\'\'' + \
        chr(127)*4 + '>>>'
    huffman.build_symbol_heap()
    huffman.sort_symbol_heap()
    huffman.build_tree()
    huffman.build_encoding_dict()
    huffman.symbol_heap = dict()
    with pytest.raises(ValueError):
        save_encoding_table(huffman.encoding_dict,
                            huffman.symbol_heap, TEST_FILE)


def test_huffman_sort_symbol_heap():
    huffman = Huffman()
    freq_table = [('a', 8), ('b', 7), ('c', 6),
                  ('\'', 5), (chr(127), 4), ('>', 3)]

    huffman.decoded_text = 'aaaaaaaabbbbbbbcccccc\'\'\'\'\'' + \
        chr(127)*4 + '>>>'
    huffman.build_symbol_heap()
    huffman.sort_symbol_heap()

    assert list(freq_table) == huffman.symbol_heap


# HUFFMAN MODULE TESTS
