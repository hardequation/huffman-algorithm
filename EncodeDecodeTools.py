from Node import Node
from Tree import HuffmanTree


# _______________________ENCODE tools_____________________________
def to_zmh(file_name):
    with open(file_name, "rb") as input, open(file_name + '.zmh', 'wb') as output:
        byte_text = []

        byte = input.read(1)

        # if file is empty
        if byte == b"":
            output.write(b"")
            return

        # read by byte
        while len(byte) > 0:
            byte = ord(byte)
            byte_text.append(byte)
            byte = input.read(1)

        # create list with distinct symbols sorted by their frequencies
        sorted_frequencies = getSortedFrequency(byte_text)

        # create Huffman tree for coding
        tree = getHuffmanTree(sorted_frequencies)

        # get dictionary with symbols and their code
        codes = createCodes(tree)

        # create sequence of '0' and '1'
        encoded_text = encode(byte_text, codes)

        # translate str of 0 and 1 to binary code
        binary_code = to_binary(encoded_text)

        output.write(bytes(binary_code))


def getSortedFrequency(text):
    frequency = {}
    for s in text:
        if s in frequency.keys():
            frequency[s] += 1
        else:
            frequency[s] = 1
    return sorted(frequency.items(), key=lambda x: x[1], reverse=False)


def getHuffmanTree(frequencies):
    # create one-node Huffman tree for every symbol
    trees = [HuffmanTree(Node(sym, freq)) for sym, freq in frequencies]

    # create one big Huffman tree from one-node trees by merging two nodes with lowest frequencies
    while len(trees) != 1:
        # create new node by merging two nodes with lowest frequencies
        new_tree = trees[0] + trees[1]
        # del two old nodes with lowest frequencies
        del [trees[0:2]]
        # insert new node
        trees += [new_tree]
        # sort to save frequencies order
        trees = sorted(trees, key=lambda x: x.node.frequency)

    return trees[0]


def createCodes(tree, prefix='', codes={}):
    # if it's a leaf
    if tree.left is None and tree.right is None:
        if prefix == '':
            # if text is from only one symbol
            codes[tree.node.symbol] = '0'
        else:
            codes[tree.node.symbol] = prefix
        return codes

    left = createCodes(tree.left, prefix + '0')
    right = createCodes(tree.right, prefix + '1')

    # else merge left and right dicts
    for k, v in right.items():
        left[k] = v

    return left


def encode(bytes_text, codes):
    encoded_text = ''

    # encode text
    for s in bytes_text:
        encoded_text += codes[s]

    # add zeros for byte format
    excess_zeros_cnt = 8 - len(encoded_text) % 8

    # how much zeros we added on last step
    excess_zeros_info = "{0:08b}".format(excess_zeros_cnt)

    encoded_text += ('0' * excess_zeros_cnt) + excess_zeros_info

    if len(encoded_text) % 8 != 0:
        print("Encoded text contains wrong count of bits")
        exit(0)

    # also we need dictionary with symbols and their codes to decode
    encoded_text += getBinaryDictionary(codes)

    return encoded_text


def to_binary(encoded_text):
    bin_code = bytearray()

    if len(encoded_text) % 8 != 0:
        print("Count of 0 and 1 in encoded text is not divisible by 8")
        exit(0)

    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i + 8]
        bin_code.append(int(byte, 2))
    return bin_code


def getBinaryDictionary(codes):
    res = ''
    for sym, code in codes.items():
        # get binary code of symbol and add meaningless zeros at start for byte format
        symbol_byte_code = bin(sym)[2:].rjust(8, '0')

        # get length of code to distinguish codes '0', '01', '001' etc.
        len_code = bin(len(code))[2:].rjust(8, '0')

        # get binary code of symbol code
        byte_code = code.rjust(8, '0')
        res += symbol_byte_code + len_code + byte_code

    # also we should know how much distinct symbols we have
    count_of_unique_symbols = bin(len(codes))[2:].rjust(8, '0')
    res += count_of_unique_symbols

    return res


# _______________________DECODE tools_____________________________

def from_zmh(file_name):
    with open(file_name, "rb") as input, open("output", "wb") as output:
        bits = []

        byte = input.read(1)

        if byte == b"":
            output.write(b"")
            return

        # read by byte and create list of bytes
        while len(byte) > 0:
            byte = ord(byte)
            bin_byte = bin(byte)[2:].rjust(8, '0')
            bits.append(bin_byte)
            byte = input.read(1)

        # get count of distinct symbols in text
        count_of_unique_symbols = int(bits[-1], 2)

        # extract dictionary with symbols and their codes in binary format
        # info about 1 symbol = symbol code + code length + code = 3 bytes
        # info about dictionary = info about 1 symbol * count_of_unique_symbols = 3 bytes * count_of_unique_symbols
        dictionary_bytes = bits[-count_of_unique_symbols * 3 - 1: -1]
        codes = readCodes(dictionary_bytes, count_of_unique_symbols)

        # decode bytes
        text = bits[:-count_of_unique_symbols * 3 - 1]
        decoded_text = decode(text, codes)

        output.write(bytes(decoded_text))


def decode(encoded_text, codes):
    # read text with additional zeros
    text = "".join(encoded_text[:-1])

    # read byte with count of additional zeros
    additional_zeros_cnt = int(encoded_text[-1], 2)

    # remove additional zeros that we added for byte format
    bin_text = text[:-additional_zeros_cnt]

    # decode text
    current_code = ''
    decoded_code = bytearray()
    for bit in bin_text:
        current_code += bit
        if current_code in codes:
            decoded_code.append(codes[current_code])
            current_code = ''
    return decoded_code


def readCodes(encoded_text, dict_size):
    codes = {}
    # read by triple of symbol, code length and its code
    for i in range(0, dict_size * 3, 3):
        sym = int(encoded_text[i], 2)
        len_code = int(encoded_text[i + 1], 2)
        code = encoded_text[i + 2][-len_code:]

        codes[code] = sym

    return codes