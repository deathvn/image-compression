import cv2
import numpy as np
import sys
import os
import pickle
import argparse
import io

class LZWPixel(object):
    def __init__(self):
        pass        
    
    def encode(self, input, output):
        img = cv2.imread(input)
        original_shape = img.shape
        string = img.reshape(-1)

        self.dict = dict()
        dict_size = 256
        for i in range(256):
            self.dict[chr(i)] = i 

        code = list()
        s = ""
        for i in range(len(string)):
            c = chr(string[i])
            temp = s + c
            if temp in self.dict.keys():
                s = temp
            else:
                code.append(self.dict[s])
                self.dict[temp] = dict_size
                dict_size += 1
                s = c
        if s:
            code.append(self.dict[s])
        with open(output, "wb") as f:
            pickle.dump((code, original_shape), f)
        print("Finished")
    
    def decode(self, input, output):
        with open(input, "rb") as f:
            code, original_shape = pickle.load(f)
        self.dict = dict()
        dict_size = 256
        for i in range(256):
            self.dict[i] = chr(i) 
    
        #result = io.StringIO()
        img = ""
        w = chr(code.pop(0))
        img += w
        for k in code:
            if k in self.dict.keys():
                entry = self.dict[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                raise ValueError('Bad compressed k: %s' % k)
            img += entry    
            # Add w+entry[0] to the dictionary.
            self.dict[dict_size] = w + entry[0]
            dict_size += 1
            w = entry
        #img = result.getvalue()
        img = [ord(x) for x in img]
        img = np.array(img, dtype=np.uint8).reshape(original_shape)
        cv2.imwrite(output, img)

if __name__ == '__main__':    
    compressor = LZWPixel()
    '''
    parser = argparse.ArgumentParser(description='Tools for encode and decode image using LZW algorithm')
    parser.add_argument('-m', '--mode', help='Select encode mode (1 for encode or 2 for decode)')
    parser.add_argument('-i', '--input', help='input file path')
    parser.add_argument('-o', '--output', help='output file path')
    args = parser.parse_args()
    if args.mode == '1':
        compressor.encode(args.input, args.output)
    else:
        compressor.decode(args.input, args.output)
    '''
    compressor.decode("test/my_images/pic.lzw", "test/my_images/pic_encode.bmp")
        
        

            



