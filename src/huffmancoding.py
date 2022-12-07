import heapq


class HuffmanEncoder:

    # Constructs a Huffman encoder based on the given bit output stream.
    def __init__(self, bitout):
        self.output = bitout
        self.codetree = None

    # Encodes the given symbol and writes to the Huffman-coded output stream.
    def write(self, symbol):
        if not isinstance(self.codetree, CodeTree):
            raise ValueError("Invalid current code tree")
        bits = self.codetree.get_code(symbol)
        for b in bits:
            self.output.write(b)


# Reads from a Huffman-coded bit stream and decodes symbols.
class HuffmanDecoder:
    # Constructs a Huffman decoder based on the given bit input stream.
    def __init__(self, bitin):
        self.input = bitin
        self.codetree = None

    # Reads from the input stream to decode the next Huffman-coded symbol.
    def read(self):
        if not isinstance(self.codetree, CodeTree):
            raise ValueError("Invalid current code tree")
        currentnode = self.codetree.root
        while True:
            temp = self.input.read_no_eof()
            if temp == 0:
                nextnode = currentnode.leftchild
            elif temp == 1:
                nextnode = currentnode.rightchild
            else:
                raise AssertionError("Invalid value from read_no_eof()")

            if isinstance(nextnode, Leaf):
                return nextnode.symbol
            elif isinstance(nextnode, InternalNode):
                currentnode = nextnode
            else:
                raise AssertionError("Illegal node type")


class FrequencyTable:

    # Constructs a frequency table from the given sequence of frequencies.
    def __init__(self, freqs):
        self.frequencies = list(freqs)
        if len(self.frequencies) < 2:
            raise ValueError("At least 2 symbols needed")
        if any(x < 0 for x in self.frequencies):
            raise ValueError("Negative frequency")

    # Returns the number of symbols in this frequency table. The result is always at least 2.
    def get_symbol_limit(self):
        return len(self.frequencies)

    # Returns the frequency of the given symbol in this frequency table. The result is always non-negative.
    def get(self, symbol):
        self._check_symbol(symbol)
        return self.frequencies[symbol]

    # Sets the frequency of the given symbol in this frequency table to the given value.
    def set(self, symbol, freq):
        self._check_symbol(symbol)
        if freq < 0:
            raise ValueError("Negative frequency")
        self.frequencies[symbol] = freq

    # Increments the frequency of the given symbol in this frequency table.
    def increment(self, symbol):
        self._check_symbol(symbol)
        self.frequencies[symbol] += 1

    # Returns silently if 0 <= symbol < len(frequencies), otherwise raises an exception.
    def _check_symbol(self, symbol):
        if 0 <= symbol < len(self.frequencies):
            return
        else:
            raise ValueError("Symbol out of range")

    # Returns a string representation of this frequency table
    def __str__(self):
        result = ""
        for (i, freq) in enumerate(self.frequencies):
            result += "{}\t{}\n".format(i, freq)
        return result

    # Returns a code tree that is optimal for the symbol frequencies in this table.
    def build_code_tree(self):
        pqueue = []

        # Add leaves for symbols with non-zero frequency
        for (i, freq) in enumerate(self.frequencies):
            if freq > 0:
                heapq.heappush(pqueue, (freq, i, Leaf(i)))

        # Pad with zero-frequency symbols until queue has at least 2 items
        for (i, freq) in enumerate(self.frequencies):
            if len(pqueue) >= 2:
                break
            if freq == 0:
                heapq.heappush(pqueue, (freq, i, Leaf(i)))
        assert len(pqueue) >= 2

        # Repeatedly tie together two nodes with the lowest frequency
        while len(pqueue) > 1:
            x = heapq.heappop(pqueue)
            y = heapq.heappop(pqueue)
            z = (x[0] + y[0], min(x[1], y[1]), InternalNode(x[2], y[2]))
            heapq.heappush(pqueue, z)

        # Return the remaining node
        return CodeTree(pqueue[0][2], len(self.frequencies))


class CodeTree:

    # Constructs a code tree from the given tree of nodes and given symbol limit.
    def __init__(self, root, symbollimit):
        # Recursive helper function
        def build_code_list(node, prefix):
            if isinstance(node, InternalNode):
                build_code_list(node.leftchild, prefix + (0,))
                build_code_list(node.rightchild, prefix + (1,))
            elif isinstance(node, Leaf):
                if node.symbol >= symbollimit:
                    raise ValueError("Symbol exceeds symbol limit")
                if self.codes[node.symbol] is not None:
                    raise ValueError("Symbol has more than one code")
                self.codes[node.symbol] = prefix
            else:
                raise AssertionError("Illegal node type")

        if symbollimit < 2:
            raise ValueError("At least 2 symbols needed")
        # The root node of this code tree
        self.root = root
        # Stores the code for each symbol, or None if the symbol has no code.

        self.codes = [None] * symbollimit
        build_code_list(root, ())

    # Returns the Huffman code for the given symbol, which is a sequence of 0s and 1s.
    def get_code(self, symbol):
        if symbol < 0:
            raise ValueError("Illegal symbol")
        elif self.codes[symbol] is None:
            raise ValueError("No code for given symbol")
        else:
            return self.codes[symbol]


# A node in a code tree. This class has exactly two subclasses: InternalNode, Leaf.
class Node:
    pass


# An internal node in a code tree. It has two nodes as children.
class InternalNode(Node):
    def __init__(self, left, right):
        if not isinstance(left, Node) or not isinstance(right, Node):
            raise TypeError()
        self.leftchild = left
        self.rightchild = right


# A leaf node in a code tree. It has a symbol value.
class Leaf(Node):
    def __init__(self, sym):
        if sym < 0:
            raise ValueError("Symbol value must be non-negative")
        self.symbol = sym


class CanonicalCode:
    def __init__(self, codelengths=None, tree=None, symbollimit=None):
        if codelengths is not None and tree is None and symbollimit is None:
            # Check basic validity
            if len(codelengths) < 2:
                raise ValueError("At least 2 symbols needed")
            if any(cl < 0 for cl in codelengths):
                raise ValueError("Illegal code length")

            # Copy once and check for tree validity
            codelens = sorted(codelengths, reverse=True)
            currentlevel = codelens[0]
            numnodesatlevel = 0
            for cl in codelens:
                if cl == 0:
                    break
                while cl < currentlevel:
                    if numnodesatlevel % 2 != 0:
                        raise ValueError("Under-full Huffman code tree")
                    numnodesatlevel //= 2
                    currentlevel -= 1
                numnodesatlevel += 1
            while currentlevel > 0:
                if numnodesatlevel % 2 != 0:
                    raise ValueError("Under-full Huffman code tree")
                numnodesatlevel //= 2
                currentlevel -= 1
            if numnodesatlevel < 1:
                raise ValueError("Under-full Huffman code tree")
            if numnodesatlevel > 1:
                raise ValueError("Over-full Huffman code tree")

            # Copy again
            self.codelengths = list(codelengths)

        elif tree is not None and symbollimit is not None and codelengths is None:
            # Recursive helper method
            def build_code_lengths(node, depth):
                if isinstance(node, InternalNode):
                    build_code_lengths(node.leftchild, depth + 1)
                    build_code_lengths(node.rightchild, depth + 1)
                elif isinstance(node, Leaf):
                    if node.symbol >= len(self.codelengths):
                        raise ValueError("Symbol exceeds symbol limit")

                    if self.codelengths[node.symbol] != 0:
                        raise AssertionError("Symbol has more than one code")
                    self.codelengths[node.symbol] = depth
                else:
                    raise AssertionError("Illegal node type")

            if symbollimit < 2:
                raise ValueError("At least 2 symbols needed")
            self.codelengths = [0] * symbollimit
            build_code_lengths(tree.root, 0)

        else:
            raise ValueError("Invalid arguments")

    # Returns the symbol limit for this canonical Huffman code..
    def get_symbol_limit(self):
        return len(self.codelengths)

    # Returns the code length of the given symbol value. The result is 0
    def get_code_length(self, symbol):
        if 0 <= symbol < len(self.codelengths):
            return self.codelengths[symbol]
        else:
            raise ValueError("Symbol out of range")

    # Returns the canonical code tree for this canonical Huffman code.

    def to_code_tree(self):
        nodes = []
        for i in range(max(self.codelengths), -1, -1):  # Descend through code lengths
            assert len(nodes) % 2 == 0
            newnodes = []

            # Add leaves for symbols with positive code length i
            if i > 0:
                for (j, codelen) in enumerate(self.codelengths):
                    if codelen == i:
                        newnodes.append(Leaf(j))

            # Merge pairs of nodes from the previous deeper layer
            for j in range(0, len(nodes), 2):
                newnodes.append(InternalNode(nodes[j], nodes[j + 1]))
            nodes = newnodes

        assert len(nodes) == 1
        return CodeTree(nodes[0], len(self.codelengths))


# A stream of bits that can be read. Because they come from an underlying byte stream,
class BitInputStream:

    # Constructs a bit input stream based on the given byte input stream.
    def __init__(self, inp):
        self.input = inp
        self.currentbyte = 0
        self.numbitsremaining = 0

    # Reads a bit from this stream. Returns 0 or 1 if a bit is available, or -1 if
    def read(self):
        if self.currentbyte == -1:
            return -1
        if self.numbitsremaining == 0:
            temp = self.input.read(1)
            if len(temp) == 0:
                self.currentbyte = -1
                return -1
            self.currentbyte = temp[0]
            self.numbitsremaining = 8
        assert self.numbitsremaining > 0
        self.numbitsremaining -= 1
        return (self.currentbyte >> self.numbitsremaining) & 1

    # Reads a bit from this stream. Returns 0 or 1 if a bit is available, or raises an EOFError
    def read_no_eof(self):
        result = self.read()
        if result != -1:
            return result
        else:
            raise EOFError()

    # Closes this stream and the underlying input stream.
    def close(self):
        self.input.close()
        self.currentbyte = -1
        self.numbitsremaining = 0


class BitOutputStream:

    # Constructs a bit output stream based on the given byte output stream.
    def __init__(self, out):
        self.output = out
        self.currentbyte = 0
        self.numbitsfilled = 0

    # Writes a bit to the stream. The given bit must be 0 or 1.
    def write(self, b):
        if b not in (0, 1):
            raise ValueError("Argument must be 0 or 1")
        self.currentbyte = (self.currentbyte << 1) | b
        self.numbitsfilled += 1
        if self.numbitsfilled == 8:
            towrite = bytes((self.currentbyte,))
            self.output.write(towrite)
            self.currentbyte = 0
            self.numbitsfilled = 0

    # Closes this stream and the underlying output stream. If called when this
    def close(self):
        while self.numbitsfilled != 0:
            self.write(0)
        self.output.close()
