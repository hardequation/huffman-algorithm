from Node import Node
from Tree import HuffmanTree


# _______________________ENCODE tools_____________________________
def to_zmh(file_name):
    byte_text = readBytes(file_name)

    if not byte_text:
        writeBytes(file_name + '.zmh', b"")
        return

    # create list with distinct symbols sorted by their frequencies
    sorted_frequencies = getSortedFrequency(byte_text)

    # create Huffman tree for coding
    tree = getHuffmanTree(sorted_frequencies)

    # get dictionary with symbols and their code
    codes = createCodes(tree)

    # create sequence of '0' and '1'
    encoded_text = encode(byte_text, codes)

    writeBytes(file_name + '.zmh', encoded_text)


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

    encoded_text = addZerosForByteFormat(encoded_text)

    # also we need dictionary with symbols and their codes to decode
    encoded_text += getBinaryDictionary(codes)

    encoded_text = to_binary(encoded_text)
    return encoded_text


def addZerosForByteFormat(bits):
    # add zeros for byte format
    excess_zeros_cnt = 8 - len(bits) % 8

    # how much zeros we added on last step
    excess_zeros_info = numToBits(excess_zeros_cnt)

    bits += ('0' * excess_zeros_cnt) + excess_zeros_info

    return bits


def to_binary(encoded_text):
    bin_code = bytearray()

    if len(encoded_text) % 8 != 0:
        print("Count of 0 and 1 in encoded text is not divisible by 8")
        exit(0)

    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i + 8]
        bin_code.append(bitsToInt(byte))
    return bin_code


def getBinaryDictionary(codes):
    res = ''
    for sym, code in codes.items():
        # get binary code of symbol and add meaningless zeros at start for byte format
        symbol_byte_code = numToBits(sym)

        # get length of code to distinguish codes '0', '01', '001' etc.
        len_code = numToBits(len(code))

        # get binary code of symbol code
        byte_code = code.rjust(8, '0')
        res += symbol_byte_code + len_code + byte_code

    # also we should know how much distinct symbols we have
    count_of_unique_symbols = numToBits(len(codes))
    res += count_of_unique_symbols

    return res


# _______________________DECODE tools_____________________________

def from_zmh(file_name):
    byte_text = readBytes(file_name)

    if not byte_text:
        writeBytes(file_name.split('.')[0], b"")
        return

    count_of_unique_symbols = byte_text[-1]

    # extract dictionary with symbols and their codes in binary format
    # info about 1 symbol = symbol code + code length + code = 3 bytes
    # info about dictionary = info about 1 symbol * count_of_unique_symbols = 3 bytes * count_of_unique_symbols
    dictionary_bytes = byte_text[-count_of_unique_symbols * 3 - 1: -1]
    codes = readCodes(dictionary_bytes, count_of_unique_symbols)

    # decode bytes
    text = byte_text[:-count_of_unique_symbols * 3 - 1]

    decoded_text = decode(text, codes)

    writeBytes(file_name.split('.')[0], decoded_text)


def decode(encoded_text, codes):
    # read byte with count of additional zeros
    additional_zeros_cnt = encoded_text[-1]

    bin_text = "".join([numToBits(byte) for byte in encoded_text[:-1]])
    # remove additional zeros that we added for byte format
    bin_text = bin_text[:-additional_zeros_cnt]

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
        sym = encoded_text[i]
        len_code = encoded_text[i + 1]
        code = numToBits(encoded_text[i + 2])[-len_code:]

        codes[code] = sym

    return codes


# -----------------------GENERAL tools-----------------------------

def readBytes(file_name):
    with open(file_name, "rb") as input:
        byte_text = []

        byte = input.read(1)

        # if file is empty
        if byte == b"":
            return []

        # read by byte
        while len(byte) > 0:
            byte = ord(byte)
            byte_text.append(byte)
            byte = input.read(1)

        return byte_text


def writeBytes(file_name, encoded_text):
    with open(file_name, 'wb') as output:
        output.write(bytes(encoded_text))


def numToBits(num):
    return bin(num)[2:].rjust(8, '0')


def bitsToInt(bits):
    return int(bits, 2)