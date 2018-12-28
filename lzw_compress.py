import os
import numpy as np
import io
import sys
import argparse

class LZW(object):
    def __init__(self):                
        pass

    def convert_12bit(self, code):
        code_12bit = bin(code)[2:]        
        while len(code_12bit) < 12:
            code_12bit = "0" + code_12bit
        return code_12bit  

    def encode(self, input, output):    
        #image = cv2.imread(input, 1)
        #sequence = np.concatnate(sequence[0], sequence[1], sequence[2]).tolist()
        #sequence, _, _ = cv2.split(image)
        #sequence = sequence.flatten().tolist()
        self.dict_size = 256
        self.dict = {}                         
        for i in range(0, 256):
            self.dict[chr(i)] = i
        print("Size of original file : %d bytes" % (os.stat(input).st_size))
        with open(input, "rb") as image_file:
            sequence = bytearray(image_file.read())        
        s = str(chr(sequence[0]))
        on_left = True
        n_pixels = len(sequence)  
        buffer = ["", "", ""]      
        with open(output,"wb") as encoded_file:
            for i in range(1, n_pixels):
                c = str(chr(sequence[i]))
                temp = s + c
                if temp in self.dict.keys():                    
                    s = temp                 
                else:
                    code = self.dict[s]
                    code_12_bit = self.convert_12bit(code)
                    if on_left:
                        buffer[0] = code_12_bit[0:8]
                        buffer[1] = code_12_bit[8:12] + "0000"
                    else:
                        buffer[1] = buffer[1][0: 4] + code_12_bit[0 : 4]
                        buffer[2] = code_12_bit[4:12]
                        for i in range(0, 3):                            
                            byte = bytes([int(buffer[i], 2)])
                            encoded_file.write(byte)
                            buffer[i] = 0

                    on_left = not on_left
                    if self.dict_size < 4096:
                        self.dict[temp] = self.dict_size
                        self.dict_size += 1                    
                    s = c
            if s:
                code = self.dict[s]                
                code_12_bit = self.convert_12bit(code)
                if on_left:
                    buffer[0] = code_12_bit[0:8]
                    buffer[1] = code_12_bit[8:12] + "0000"
                    encoded_file.write(bytearray([int(buffer[0], 2)]))
                    encoded_file.write(bytearray([int(buffer[1], 2)]))
                else:
                    buffer[1] = buffer[1][0 : 4] + code_12_bit[0 : 4]
                    buffer[2] = code_12_bit[4:12]
                    for i in range(0, 3):
                        byte = bytes([int(buffer[i], 2)])
                        encoded_file.write(byte)
                        buffer[i] = 0
        print("Size of encoded file : %d bytes" % (os.stat(output).st_size))        
        #print("number of overlap sequences : ", count)
        #print("Number of entry in dictionary  : ", len(self.dict.keys()))
        #print("Lenght of encoded_seqd : ", len(encoded_seq), " | maximum value : ", max(encoded_seq))                                

    def convert_byte_to_int(self, byte_1, byte_2, is_left):
        code_1 = bin(byte_1)[2:]
        code_2 = bin(byte_2)[2:]
        while len(code_1) < 8: 
            code_1 = "0" + code_1
        if len(code_1) == 32:
                code_1 = code_1[24:32]
        while len(code_2) < 8: 
            code_2 = "0" + code_2
        if len(code_2) == 32:
                code_2 = code_2[24:32]
        if is_left:
            return int(code_1 + code_2[:4], 2)
        else:
            return int(code_1[4:8] + code_2, 2)             

    def decode(self, input, output):
        self.dict = [None] * 4096
        self.dict_size = 256
        is_left = True                      
        for i in range(0, 256):            
                self.dict[i] = chr(i)     
        decode = []               
        encoded_file = open(input, "rb")        
        image_file = open(output, "wb")         
        buffer= [None, None, None]            
        buffer[0] = int.from_bytes(encoded_file.read(1), byteorder='little')
        buffer[1] = int.from_bytes(encoded_file.read(1), byteorder='little')
        prev_code = self.convert_byte_to_int(buffer[0], buffer[1], is_left)
        is_left = not is_left
        decode.extend(list(self.dict[prev_code]))          
        s=""
        while True:         
            curr_code = None
            if is_left:
                b = encoded_file.read(1)
                if not b: 
                    break                
                buffer[0] = int.from_bytes(b, byteorder='little')
                b = encoded_file.read(1)
                if not b: 
                    break                
                buffer[1] = int.from_bytes(b, byteorder='little')
                curr_code = self.convert_byte_to_int(buffer[0], buffer[1], is_left)
            else:
                b = encoded_file.read(1)
                if not b: 
                    break                
                buffer[2] = int.from_bytes(b, byteorder='little')                
                curr_code = self.convert_byte_to_int(buffer[1], buffer[2], is_left)
            is_left = not is_left
            if curr_code >= self.dict_size:
                if self.dict_size < 4096:
                    self.dict[self.dict_size] = self.dict[prev_code] + self.dict[prev_code][0]
                self.dict_size +=1
                decode.extend(list(self.dict[prev_code] + self.dict[prev_code][0]))                          
            else:
                if self.dict_size < 4096:
                    self.dict[self.dict_size] = self.dict[prev_code] + self.dict[curr_code][0]
                self.dict_size += 1
                decode.extend(list(self.dict[curr_code]))                              
            prev_code = curr_code

        encoded_file.close()
        decode = [ord(x) for x in decode]
        image_file.write(bytearray(decode))
        image_file.close()
                    



if __name__ == '__main__':
    compressor = LZW()
    parser = argparse.ArgumentParser(description='Tools for encode and decode image using LZW algorithm')
    parser.add_argument('-m', '--mode', help='Select encode mode (1 for encode or 2 for decode)')
    parser.add_argument('-i', '--input', help='input file path')
    parser.add_argument('-o', '--output', help='output file path')
    args = parser.parse_args()
    if args.mode == '1':
        compressor.encode(args.input, args.output)
    else:
        compressor.decode(args.input, args.output)





