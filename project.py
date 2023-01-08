""" 
:date: 2023-01-08
:version: 1.0.0
:authors:
    - Luís Hartmann
:description: Compresses texts using Huffman's compression algorithm 

A detailed functional description is available in README.md


The programmer's prayer is always a good start:

    Our program, who art in memory,
    called by thy name;
    thy operating system run;
    thy function be done at runtime
    as it was on development.
    Give us this day our daily output.
    And forgive us our code duplication,
    as we forgive those who
    duplicate code against us.
    And lead us not into frustration;
    but deliver us from GOTOs.
    For thine is algorithm,
    the computation, and the solution,
    looping forever and ever.
    Return;
"""

import argparse
import sys
import os
import csv
from modules.huffman import Huffman, NotCompressable, EmptyFile, NoHeader, InvalidPadding


def main():
    # user's input possibilities need to be defined
    argparser: argparse.ArgumentParser = define_program_args()

    args: argparse.Namespace = argparser.parse_args()

    # the user needs to provide or an input message or input file, and define if the input will be compressed or decompressed
    if args_incomplete(args):
        argparser.print_usage()
        sys.exit(argparser.prog + ": too few comamnd-line arguments")

    # the user should not be able to decompress a self-generated message, because of the header, padding and other definitions.
    if args_mutex(args) and args.decompress:
        argparser.print_usage()
        sys.exit(argparser.prog +
                 ": error: arguments -d/--decompress: not allowed woth argument -m/--message")

    huffman = Huffman()
    try:
        if args.file:
            if args.compress:
                huffman.parse_uncompressed_file(args.file)

            else:
                huffman.parse_compressed_file(args.file)

        else:
            huffman.decoded_text = args.message

    except FileNotFoundError:
        sys.exit(argparser.prog + ": file does not exist")
    except EmptyFile:
        sys.exit(argparser.prog + ": cannot compress empty file/string")
    except NotCompressable:
        sys.exit(argparser.prog +
                 ": only extended-ascii/utf8 encoded files are compressable")
    except NoHeader:
        sys.exit(argparser.prog + ": given compressed file has no table header")
    except ValueError:
        sys.exit(argparser.prog +
                 ": given compressed file has no valid table header")
    except InvalidPadding:
        sys.exit(argparser.prog +
                 ": the acquired padding (%d bits) is not possible" % (huffman.padding_count))

    huffman.build_symbol_heap()

    # sort the frequency table to ease the transformation of the list in the huffman's tree
    huffman.sort_symbol_heap()

    # create the huffman tree from the symbol frequency table
    huffman.build_tree()

    # interpret the tree and assign '0' to the left child node and '1' to the right child node of each node
    huffman.build_encoding_dict()

    if args.verbose:
        print("Algorithm's generated table:")
        huffman.print_encoding()

    if args.compress:
        huffman.build_header()

        if args.verbose:
            print("Header added to the encoded file:")
            print(huffman.header)
            print()

        huffman.build_encoded_text()

        huffman.write_encoded_text_to_file(args.output)

        if args.verbose:
            if args.file:
                print_statistics_with_input_file(
                    huffman, args.file, args.output)
            else:
                print_statistics_with_written_message(huffman,
                                                      args.message, args.output)

    else:
        huffman.build_decoding_dict_from_encoding_dict()
        huffman.build_decoded_text()
        with open(args.output, 'w') as output_file:
            output_file.write(huffman.decoded_text)

    if args.save_encoded_binary:
        print("The encoded binary will be saved in: " +
              args.save_encoded_binary)
        save_binary(huffman.encoded_text, args.save_encoded_binary)

    if args.save_encoding_table:
        TABLE_FILE = "huffman_encoding_table.csv"
        print("The encoding table will be saved in: " + args.save_encoding_table)
        save_encoding_table(huffman.encoding_dict,
                            huffman.symbol_heap, args.save_encoding_table)


def save_encoding_table(encoding_dict: dict, symbol_heap: dict, file: str):
    if not encoding_dict:
        raise ValueError("Cannot save empty encoding dict")
    if not symbol_heap:
        raise ValueError("Cannot save empty symbol frequency table")

    with open(file, 'w', encoding='utf-8') as out_table:
        csv_writer = csv.writer(out_table)
        csv_writer.writerow(['CHAR', 'OCCURENCES', 'ENCODING'])
        for (char, freq) in symbol_heap:
            csv_writer.writerow([char, freq, encoding_dict[char]])


def save_binary(encoded_text: str, file: str):
    if not encoded_text:
        raise ValueError("Cannot save empty encoded text")

    with open(file, 'w', encoding='utf-8') as out_bin:
        out_bin.write(encoded_text)


def print_statistics_with_input_file(huffman: Huffman, input_file: str, output_file: str):
    """ 
    Prints compression statistics on the terminal

    :param huffman: Huffman class object to get header size
    :type huffman: Huffman
    :param input_file: file that got compressed/decompressed
    :type input_file: str
    :param output_file: file to which the compression/decompression was written
    :type output_file: str
    """
    output_file_stats = os.stat(output_file)
    input_file_stats = os.stat(input_file)
    print("Uncompressed file size: %d bytes" % (input_file_stats.st_size))
    print("Compressed file size: %d bytes" % (output_file_stats.st_size))
    print("+-- Header size: %d bytes" % (len(huffman.header)))
    print("+-- Padding bits added to the file: %d" % (huffman.padding_count))
    print("The compressed file is %.2d%% the size of the original file" %
          (100*output_file_stats.st_size/input_file_stats.st_size))


def print_statistics_with_written_message(huffman: Huffman, message: str, output_file: str):
    """ 
    Prints compression statistics on the terminal if a message was manually written from the user

    :param huffman: Huffman class object to get header size
    :type huffman: Huffman
    :param message: file that got compressed
    :type message: str
    :param output_file: file to which the compression/decompression was written
    :type output_file: str
    """
    message_size = len(huffman.decoded_text)
    compressed_text_size = len(
        huffman.header) + len(huffman.byte_array) + 1


def args_incomplete(args: argparse.Namespace):
    """ 
    Determine if the program's input arguments are incomplete

    :param args: program arguments
    :type args: argparse.Namespace
    :return: value indicating if the args arre complete or incomplete
    :rtype: bool
    """
    return (not args.file and not args.message) or (not args.compress and not args.decompress)


def args_mutex(args: argparse.Namespace):
    """ 
    Performs a mutual exclusion between two arguments. This mutual exclusion
    was not possible through the add_mutually_exclusive_groups, so I made it
    manually

    :param args: program arguments
    :type args: argparse.Namespace
    :return: value indicating if the arguments are used at the same time
    :rtype: bool 
    """
    # This mutex was not possible throught the ArgumentParser class
    return args.decompress and args.message


def define_program_args():
    """ 
    Sets the possible command-line arguments and options.

    :return: object containing all command-line configurations
    :rtype: ArgumentParser
    """
    argparser = argparse.ArgumentParser(
        prog="project.py",
        description="Compresses data from a given string in the command-line or from a file\
            using the Huffman's compression algorithm"
    )
    mutex_group = argparser.add_mutually_exclusive_group()
    mutex_group.add_argument(
        "-c", "--compress", help="compress file", action='store_true')

    mutex_group.add_argument("-d", "--decompress",
                             help="decompress file", action='store_true')

    mutex_group2 = argparser.add_mutually_exclusive_group()
    mutex_group2.add_argument(
        "-f", "--file", help="file to be compressed", type=str)

    mutex_group2.add_argument("-m", "--message", help="input a smaller text\
        to see how it would be compressed.", type=str)

    argparser.add_argument(
        "-o", "--output", help="compressor's output file", type=str, required=True)

    argparser.add_argument("-v", "--verbose", help="show encoding table and \
        processing texts", action='store_true')

    argparser.add_argument("-t", "--save-encoding-table", help="save encoding scheme \
        into a csv file", type=str)

    argparser.add_argument("-s", "--save-encoded-binary", help="save the text encoded \
        in binary before converting it to UTF-8 code", type=str)

    return argparser


if __name__ == "__main__":
    main()
