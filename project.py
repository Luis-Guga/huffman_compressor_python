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
    # set the program arguments, so that we can check the user's input
    argparser: argparse.ArgumentParser = define_program_args()

    # get the arguments already parsed to analyse them
    args: argparse.Namespace = argparser.parse_args()

    # check if the user provided input and output files
    if args_complete(args):
        argparser.print_usage()
        sys.exit(argparser.prog + ": too few comamnd-line arguments")

    # initialize the variable as a dictinary, because the insertion gets easier
    symbol_frequency = dict()
    try:
        with open(args.file, 'r') as input_file:
            # read everything at once. This way there are less function calls in comparison to as if one would read line by line
            message: str = input_file.read()

            # iterate through the message in the provided file (or as input on command-line) to count the most frequent symbols
            for symbol in message:

                # add the symbols and its frequency to the list, so that we can access them later to create the huffman's tree
                if symbol in symbol_frequency:
                    symbol_frequency[symbol] += 1
                else:
                    symbol_frequency[symbol] = 1

    except FileNotFoundError:
        sys.exit(argparser.prog + ": input file does not exist")

    # sort the list to ease the transformation of the list in the huffman's tree
    symbol_frequency = sorted(symbol_frequency.items(),
                              key=lambda l: l[1], reverse=True)

    # copy the list. it will later repesent the tree
    tree = symbol_frequency

    # create the huffman tree. each node contains the sum of the occurrence frequency of its two children (it the node is not a leaf)
    tree = huffman.create_tree(tree)

    # interpretate the tree and assign '0' to the left child node and '1' to the right child node of each node (if the node is not a leaf)
    huffman_dict: dict() = huffman.get_encoded_message(tree[0][0])

    huffman.print_encoding(tree[0][0], symbol_frequency)


def args_complete(args: argparse.Namespace):
    return not args.file and not args.message


def define_program_args():
    argparser = argparse.ArgumentParser(
        prog="project.py",
        description="Compresses data from a given string in the command-line or from a file\
            using the Huffman's compression algorithm"
    )

    argparser.add_argument(
        "-f", "--file", help="file to be compressed", type=str)

    argparser.add_argument(
        "-o", "--output", help="compressor's output file (default: terminal)", default=sys.stdout,
        type=str)

    argparser.add_argument("-m", "--message", help="input a smaller message\
        to see how it would be compressed.", type=str)

    return argparser


if __name__ == "__main__":
    main()
