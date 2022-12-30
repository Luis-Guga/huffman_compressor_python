import argparse
import sys

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
    argparser: argparse.ArgumentParser = define_program_args()
    args: argparse.Namespace = argparser.parse_args()

    if args_complete(args):
        argparser.print_usage()
        sys.exit(argparser.prog + ": too few comamnd-line arguments")


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
