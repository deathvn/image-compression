import numpy as np
import sys
import os
import cv2
import heapq
import io
from collections import defaultdict
from huffman_compress import Huffman
from lzw_compress_pixel import LZWPixel
from predictive_compress import Predictive

class CompressorSelector(object):
    def __init__(self):
        self.compressors = []
        self.compressors.append(("huffman", Huffman()))
        self.compressors.append(("lzw", LZWPixel()))      
        self.compressors.append(("JPEG", Predictive(1))) 
        self.current_compressor = self.compressors[0]
    
    def set_current_compressor_by_name(self, name):
        if name == "LZW":
            self.current_compressor = self.compressors[0]
        elif name == "Huffman":
            self.current_compressor = self.compressors[1]
        elif name == "JPEG":
            self.current_compressor = self.compressors[2]
        print("Current compressor : ", self.current_compressor[0])

    def set_current_compressor_by_index(self, index):
        self.current_compressor = self.compressors[index]        
        print("Current compressor : ", self.current_compressor[0])
    
    def encode(self, img, output):
        self.current_compressor[1].encode(img, output)        
        output_size = os.stat(output).st_size
        return output_size 
    def decode(self, input, img):
        self.current_compressor[1].decode(input, img)
        output = cv2.imread(img)
        height, width, _ = output.shape
        return os.stat(img).st_size, (height, width)




