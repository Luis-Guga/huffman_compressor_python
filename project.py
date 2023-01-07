import argparse
import sys
import os
from modules.huffman import Huffman, NotCompressable, EmptyFile, NoHeader, InvalidPadding
# removed the pseudo-eof. need to count the header size to read it and add padding info
""" The programmer's prayer is always a good start:


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


def main():
    # set the program arguments, so that the user's input can be checked
    argparser: argparse.ArgumentParser = define_program_args()

    # get the arguments already parsed to analyse them
    args: argparse.Namespace = argparser.parse_args()

    # check if the user provided input and output files and if the operation of compression or decompression was given
    if args_incomplete(args):
        argparser.print_usage()
        sys.exit(argparser.prog + ": too few comamnd-line arguments")

    if args_mutex(args) and args.decompress:
        argparser.print_usage()
        sys.exit(argparser.prog +
                 ": error: arguments -d/--decompress: not allowed woth argument -m/--message")

    huffman = Huffman()
    try:
        if args.file:
            if args.compress:
                # get the symbols frequency and the file text. the text is necessary for the compression
                huffman.parse_uncompressed_file(args.file)

            else:
                # get the symbols frequency and the file text. the text does not include the header, it was removed from the original compressed text
                huffman.parse_compressed_file(args.file)

        else:
            huffman.decoded_text = args.message
            # remove \r for portability issues
            huffman.build_frequency_table()

    except FileNotFoundError:
        sys.exit(argparser.prog + ": file does not exist")
    except EmptyFile:
        sys.exit(argparser.prog + ": cannot compress empty file")
    except NotCompressable:
        sys.exit(argparser.prog +
                 ": only extended-ascii/utf8 encoded files are compressable")
    except NoHeader:
        sys.exit(argparser.prog + ": given compressed file has no table header")
    except ValueError:
        sys.exit(argparser.prog + ": given compressed file has no table header")
    except InvalidPadding:
        sys.exit(argparser.prog +
                 ": the acquired padding (%d bits) is not possible" % (huffman.padding_count))

    # sort the list by occurence frequency to ease the transformation of the list in the huffman's tree
    huffman.sort_symbol_heap()

    # create the huffman tree. each node contains the sum of the occurrence frequency of its two children (if the node is not a leaf)
    huffman.build_tree()

    # interpret the tree and assign '0' to the left child node and '1' to the right child node of each node (if the node is not a leaf)
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

        # need to encode the text according to each character of the original text
        huffman.build_encoded_text()

        if args.save_encoded_binary:
            ENC_FILE = "huffman_encoded_binary.txt"
            print("The encoding table will be saved in: " + ENC_FILE)
            huffman.save_binary(ENC_FILE)

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

    if args.save_encoding_table:
        TABLE_FILE = "huffman_encoding_table.csv"
        print("The encoding table will be saved in: " + TABLE_FILE)
        huffman.save_encoding_table(TABLE_FILE)


def args_incomplete(args: argparse.Namespace):
    return (not args.file and not args.message) or (not args.compress and not args.decompress) or (not args.message and not args.output)


def args_mutex(args: argparse.Namespace):
    return args.decompress and args.message


def print_statistics_with_input_file(huffman: Huffman, input_file: str, output_file: str):
    output_file_stats = os.stat(output_file)
    input_file_stats = os.stat(input_file)
    print("Uncompressed file size: %d bytes" % (input_file_stats.st_size))
    print("Compressed file size: %d bytes" % (output_file_stats.st_size))
    print("+-- Header size: %d bytes" % (len(huffman.header)))
    print("+-- Padding bits added to the file: %d" % (huffman.padding_count))
    print("The compressed file is %.2d%% the size of the original file" %
          (100*output_file_stats.st_size/input_file_stats.st_size))


def print_statistics_with_written_message(huffman: Huffman, message: str, output_file: str):
    message_size = len(huffman.decoded_text)
    compressed_text_size = len(
        huffman.header) + len(huffman.byte_array) + 1


def define_program_args():
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
        into a csv file", action='store_true')

    argparser.add_argument("-s", "--save-encoded-binary", help="save the text encoded \
        in binary before converting it to UTF-8 code", action='store_true')

    return argparser


if __name__ == "__main__":
    main()
