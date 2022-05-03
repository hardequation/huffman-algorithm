from Node import Node


class HuffmanTree:
    def __init__(self, node, left=None, right=None):
        self.node = node
        self.left = left
        self.right = right

    def __add__(self, other):
        freq = self.node.frequency + other.node.frequency
        return HuffmanTree(Node(None, freq), self, other)

    def __repr__(self, level=0):
        ret = "\t" * level + ('None' if self.node.symbol is None else self.node.symbol)
        ret += ' '
        ret += str(self.node.frequency)
        ret += "\n"
        if self.left is not None:
            ret += self.left.__repr__(level + 1)
        if self.right is not None:
            ret += self.right.__repr__(level + 1)
        return ret
