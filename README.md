# huffman_compressor_python
#### Video Demo:  <URL HERE>
#### Description:
This project was developed with the intention of implementing the following functionalities:
- file compression using the Huffman Algorithm
- analysis of command-line arguments
- save and print statistics of the compression process

Operation of the main program:
1. Acquire arguments from the command-line
2. Analyze them
3. Read the file to be compressed/uncompressed
4. Implement the Huffman compression process
     4.1.
     (Compression): After acquiring the text present in the input file,
     a list is assembled consisting of the character and its respective number of 
     occurrences in the read text.

     (Decompression): After the acquisition of the text present in the compressed input file,
     the header is read and the list of occurrences of symbols is reassembled
     through it. In addition, the text is encoded by the huffman
     tree and the padding added to the compressed text 
     (read 4.5.-Compression)


     4.2.
     (Compression): From the frequency list, we assemble the 
     Huffman tree, where each node of the tree represents the sum of the least frequent elements
     present in the list.
     
     Example: 'aaaaaaaaabbbbbbcccccccdddddea'
     Frequency: [('a', 10), ('b', 8), ('c', 7), ('d', 4), ('e', 1)]        
     Tree:
     [('a', 10), ('b', 8), ('c', 7), ('d', 4), ('e', 1)]
     [('a', 10), ('b', 8), ('c', 7), ('de', 5)]
     [('a', 10), ('b', 8), ('cde', 12)]
     [('cde', 12, ('ab', 18)]
     [('cdeab', 30)]
                                   cdeab
                         |-----------30-----------|
                         |                        |
                      cde                         ab   
               |-------12-------|           |-----18-----|
               |                |           |            |
              de                |           |            |
          |---5---|             |           b:8          a:10
          |       |             |
          e:1     d:4           c:7                       
                                

     (Decompression): After having the list of occurrence of the symbols again,
     the Huffman-tree is reassembled as in the compression step above.

     4.3.
     (Compression/Decompression): Following from the Huffman tree, each child node is
     signed with the value '0' (left child) or '1' (right child).
     Tree:
                         0-----------30-----------1
                         |                        |
               0-------12-------1           0-----18-----1
               |                |           |            |
          0---5---1             |           b:8          a:10
          |       |             |
          e:1     d:4           c:7
     From these signatures the tree is traversed and the dictionary is created:
     the code for d would be '000' in this example, and the code for a would be '11'.

     4.4.
     (Compression): From the dictionary, the encoded text is assembled.
     (Decompression): The reverse dictionary is assembled to facilitate decoding: {'d':'000'} -> {'000':'e'}

     4.5.
     (Compression): The header is written to the file. In addition, a variable padding is added to the converted
     converted text, because it is necessary that the size of the text to be written is divisible by 8, otherwise
     the operating system itself will pad the text with random bits, which would cause problems in decompression, since 
     every bit can change the symbol that will be restored. It is important to note that padding is added only
     ONCE AT THE END OF THE FILE. This means that all symbols are joined into a single string before
     conversion, so that it is necessary to do the padding only one time.  
     Example:
          Suppose the text to be compressed ends with 'a', as in the example in 4.2.
          'a' = '11', padding = 6 bits, 'a' with padding: '11000000'
          End of the compressed text:
          bytes(int('11000000', 2)) + '6' <--- padding information 

     After writing the header and constructing the padding, the huffman-encoded text (series of '1's and '0's)
     is converted to its byte value and then written to the file.
     Example: 
          '1110010010001101' = 'abcdeac' is converted to [228, 141] = [int('11100100', 2), int('10001101', 2)] <--- Conversion values
          this list is then converted to a byte object and written to the output file.

     (Decompression): After the decoding dictionary has been constructed, it only reads if the encoded huffman text
     acquired in 4.1, decodes it from the dictionary, and writes it to the output file
                           
5. Save the compression/decompression to the file the user wants
6. Optionally print/save statistics

