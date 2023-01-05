import argparse
import sys
import modules.huffman as huffman

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

    if args_mutex(args):
        argparser.print_usage()
        sys.exit(argparser.prog +
                 ": error: arguments -o/--output: not allowed woth argument -m/--message")

    try:
        if args.file:
            if args.compress:
                # get the symbols frequency and the file text. the text is necessary for the compression
                symbol_frequency, text = huffman.parse_uncompressed_file(
                    args.file)
            else:
                # get the symbols frequency and the file text. the text does not include the header, it was removed from the original compressed text
                symbol_frequency, text = huffman.parse_compressed_file(
                    args.file)
        else:
            text = args.message
            symbol_frequency = huffman.get_frequency_table(text)

    except FileNotFoundError:
        sys.exit(argparser.prog + ": file does not exist")

    # check for one or zero because a pseudo EOF was appended to the file text while counting the characters occurence, it is not possible to have a
    # single character in a compressed file, because the table size that is written to the file has a minimum of 3 characters: <char, char_freq, pseudo-eof>
    if len(symbol_frequency) < 2:
        sys.exit(argparser.prog + ": input file is empty")

    # sort the list by occurence frequency to ease the transformation of the list in the huffman's tree
    symbol_frequency = sorted(symbol_frequency.items(),
                              key=lambda l: l[1], reverse=True)

    # copy the list. it will repesent the tree as a unique element of the list
    tree: list = symbol_frequency

    # create the huffman tree. each node contains the sum of the occurrence frequency of its two children (if the node is not a leaf)
    tree = huffman.create_tree(tree)

    # interpret the tree and assign '0' to the left child node and '1' to the right child node of each node (if the node is not a leaf)
    huffman_dict: dict() = huffman.get_encoded_dict(tree[0][0])

    if args.compress:
        header = huffman.build_header(symbol_frequency)

        # need to encode the text according to each character of the original text
        encoded_text = huffman.get_encoded_text(text, huffman_dict)
        print("Text written")
        if args.output:
            huffman.write_encoded_text_to_file(
                header, encoded_text, args.output)
    else:
        # decompress things, but first see if the content is identical to the written content
        print("Text read:")
        print(text)

    if args.verbose:
        if args.compress:
            huffman.print_statistics(text, encoded_text)

        huffman.print_encoding(tree[0][0], symbol_frequency)

    if args.save_encoding_table:
        TABLE_FILE = "huffman_encoding_table.csv"
        print("The encoding table will be saved in: " + TABLE_FILE)
        huffman.save_encoding(tree[0][0], symbol_frequency, TABLE_FILE)

    if args.save_encoded_binary:
        ENC_FILE = "huffman_encoded_binary.txt"
        print("The encoding table will be saved in: " + ENC_FILE)
        huffman.save_binary(encoded_text, ENC_FILE)


def args_incomplete(args: argparse.Namespace):
    return (not args.file and not args.message) or (not args.compress and not args.decompress) or (not args.message and not args.output)


def args_mutex(args: argparse.Namespace):
    return args.output and args.message


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
        "-o", "--output", help="compressor's output file (default: terminal)", type=str)

    argparser.add_argument("-v", "--verbose", help="show encoding table and \
        processing texts", action='store_true')

    argparser.add_argument("-t", "--save-encoding-table", help="save encoding scheme \
        into a csv file", action='store_true')

    argparser.add_argument("-s", "--save-encoded-binary", help="save the text encoded \
        in binary before converting it to UTF-8 code", action='store_true')

    return argparser


if __name__ == "__main__":
    main()
