from Node import Node
from Tree import HuffmanTree


# _______________________ENCODE tools_____________________________
def to_zmh(file_name):
    with open(file_name, "r", encoding="utf-8") as input, open(file_name + '.zmh', 'wb') as output:
        text = input.read().rstrip()

        if text == "":
            output.write(b"")
            return

        # create list with distinct symbols sorted by their frequencies
        sorted_frequencies = getSortedFrequency(text)

        # create Huffman tree for coding
        tree = getHuffmanTree(sorted_frequencies)

        # coding of symbols by tree
        codes = createCodes(tree)

        # create sequence of '0' and '1'
        encoded_text = encode(text, codes)

        # translate str to binary code
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
            codes[tree.node.symbol] = '0'
        else:
            codes[tree.node.symbol] = prefix
        return codes
    # else merge dicts of left and right
    return dict(createCodes(tree.left, prefix + '0'), **createCodes(tree.right, prefix + '1'))


def encode(text, codes):
    encoded_text = ''
    for s in text:
        encoded_text += codes[s]

    excess_zeros_cnt = 8 - len(encoded_text) % 8
    excess_zeros_info = "{0:08b}".format(excess_zeros_cnt)

    encoded_text = encoded_text + ('0' * excess_zeros_cnt) + excess_zeros_info
    if len(encoded_text) % 8 != 0:
        print("Encoded text contains wrong count of bits")
        exit(0)

    # also we need additional info in the end of file to be able to decode
    encoded_text += getBinarySymbolsCodes(codes)

    return encoded_text


def to_binary(encoded_text):
    bin_code = bytearray()
    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i + 8]
        bin_code.append(int(byte, 2))
    return bin_code


def getBinarySymbolsCodes(codes):
    res = ''
    for sym, code in codes.items():
        symbol_byte_code = to_bytes(bin(ord(sym))[2:])
        res += symbol_byte_code

        len_code = to_bytes(bin(len(code))[2:])
        byte_code = to_bytes(code)
        res += len_code + byte_code

    # also we should know how much distinct symbols we have
    count_of_unique_symbols = to_bytes(bin(len(codes))[2:])
    res += count_of_unique_symbols

    return res


def to_bytes(bits):
    # this function adds zeros at start for byte format because byte is 8 bits
    return '0' * (8 - len(bits) % 8) + bits


# _______________________DECODE tools_____________________________

def from_zmh(file_name):
    """
    format of zmh file:
    1. text
    2. additional zeros for translation to bytes
    3. 1 byte is count of additional zeros
    4. dictionary with symbols and their codes: sym1code1sym2code2...
    5. 1 byte is count of distinct symbols in text
    """
    with open(file_name, "rb") as input, open("output", "w", encoding="utf-8") as output:
        bits = []

        byte = input.read(1)

        if byte == b"":
            output.write("")
            return

        while len(byte) > 0:
            byte = ord(byte)
            bin_byte = bin(byte)[2:].rjust(8, '0')
            bits.append(bin_byte)
            byte = input.read(1)

        dict_size = int(bits[-1], 2)
        # extract dictionary with symbols and their codes in binary format
        code_bytes = bits[-dict_size * 3 - 1: -1]
        codes = readCodes(code_bytes, dict_size)

        decoded_text = decode(bits[:-dict_size * 3 - 1], codes)

        output.write(decoded_text)


def decode(encoded_text, codes):
    # read text with additional zeros
    text = "".join(encoded_text[:-1])

    # read byte with count of additional zeros
    additional_zeros_cnt = int(encoded_text[-1], 2)

    # remove additional zeros that we added for byte format
    bin_text = text[:-additional_zeros_cnt]

    current_code = ''
    decoded_code = ''
    for bit in bin_text:
        current_code += bit
        if current_code in codes:
            decoded_code += codes[current_code]
            current_code = ""
    return decoded_code


def readCodes(encoded_text, dict_size):
    codes = {}
    # read by pair of symbol and its code
    for i in range(0, dict_size * 3, 3):
        sym = chr(int(encoded_text[i], 2))
        len_code = int(encoded_text[i + 1], 2)
        code = encoded_text[i + 2][-len_code:]

        codes[code] = sym

    return codes
