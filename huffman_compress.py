import numpy as np
import sys
import os
import cv2
import heapq
from collections import defaultdict

class Huffman():
    def left(self, x):
        return x*2+1
    def right(self, x):
        return x*2+2

    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)

        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-1*extra_padding]

        return encoded_text

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if(len(padded_encoded_text) % 8 != 0):
            print("Encoded text not padded properly")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    def encode(self, path, out_path):
        #Read image
        tail = (path.split('.')[-1])
        if (tail == 'pgm'):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        else:
            img = cv2.imread(path)

        _shape = img.shape
        img2 = img.flatten()


        #en Code
        frequency = defaultdict(int)
        code = defaultdict(int)

        for num in img2:
            frequency[num] += 1

        heap = [[weight, [symbol, '']] for symbol, weight in frequency.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        huff = sorted(heapq.heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
        _dict = [_shape, huff]
        np.save(out_path + ".dict.npy", _dict)

        #print enCode data
        for hu in huff:
            code[hu[0]] = hu[1]

        en_code=""
        #arr = []
        for t in img2:
            en_code += code[t]
            #arr.append(code[t])

        f = open(out_path, "wb")
        padded_encoded_text = self.pad_encoded_text(en_code)
        b = self.get_byte_array(padded_encoded_text)
        f.write(bytes(b))
        f.close()



    def decode(self, path, out_path):
        #Load data
        _dict = np.load(path+".dict.npy")
        _shape = _dict[0]
        huff = _dict[1]
        with open(path, "rb") as file:
            bit_string = ""

            byte = file.read(1)
            while(byte != ""):
                if (len(byte) == 0):
                    break
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)

            en_code = self.remove_padding(bit_string)

        #Re Build code_tree
        code_tree = np.full(2**(1 + len(huff[len(huff)-1][1])), int(-1))
        for hu in huff:
            point = 0
            for kk in hu[1]:
                if (kk == '0'):
                    point = self.left(point)
                else:
                    point = self.right(point)
            code_tree[point] = int(hu[0])

        #de Code
        p = 0
        de_code = []

        for tt in en_code:
            if (tt=='0'):
                p = self.left(p)
            else:
                p = self.right(p)
            k = code_tree[p]
            if (k != -1):
                de_code.append(k)
                p = 0

        de_code = np.array(de_code)
        de_code = np.reshape(de_code, _shape)
        cv2.imwrite(out_path, de_code)

if __name__ == '__main__':
    if (len(sys.argv) != 4):
        print("Usage: python huffmanIMG [encode, decode] <input_name> <output_name>")
    else:
        comand = sys.argv[1]
        file_name = sys.argv[2]
        out_file = sys.argv[3]
        c = Huffman()
        if (comand == "encode"):
            c.encode(file_name, out_file)
        elif (comand == "decode"):
            c.decode(file_name, out_file)
        else:
print("Usage: python huffmanIMG [encode, decode] <input_name> <output_name>")
