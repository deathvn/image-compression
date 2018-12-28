from tkinter import *
from PIL import ImageTk, Image
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
import cv2
import numpy as np
from compressor import CompressorSelector
import os
title_font = ("Monospace", 13)
label_font = ("Monospace", 10)

class GUI(object):

    def __init__(self):
        self.root = Tk()
        self.setup_gui()
        self.compressor = CompressorSelector()
        self.img_file = None
        self.save_path = None
        self.compressed_file = None
        self.output_img_file = None

    def setup_gui(self):
        self.compression_label = Label(self.root, text="Compression Algorithm", font=label_font)
        self.compression_label.grid(row = 0, padx=2, pady=2)

        self.compression_algorithm = tkinter.ttk.Combobox(self.root, width=40)
        self.compression_algorithm['value'] = ("Huffman", "LZW", "JPEG-LS")
        self.compression_algorithm.bind("<<ComboboxSelected>>", self.set_selected_compression_algo)
        self.compression_algorithm.grid(row = 0, column=1, padx=2, pady=2)
        self.compression_algorithm.current(0)

        notebook = tkinter.ttk.Notebook(self.root)
        compress_tab = tkinter.ttk.Frame(notebook)
        decompress_tab = tkinter.ttk.Frame(notebook)
        notebook.add(compress_tab, text="Compress")
        notebook.add(decompress_tab, text="Decompress")
        notebook.grid(row = 1, column=0, columnspan=2, sticky=NSEW)

        

        self.img_button = Button(compress_tab, text="Image input", command=self.choose_image)
        self.img_button.grid(row=1, padx=2, pady=4)

        self.img = ImageTk.PhotoImage("RGB", (300, 300))
        self.panel = Label(compress_tab, image=self.img)
        self.panel.grid(row=1, column=1)

        self.resolution_label = Label(compress_tab, text="Resolution : ", font=label_font)
        self.resolution_label.grid(row=2, padx=2, pady=4)

        self.image_size_label = Label(compress_tab, text="Size : ", font=label_font)
        self.image_size_label.grid(row=3, padx=2, pady=5)

        self.save_path_button = Button(compress_tab, text="Choose save file", command=self.choose_save_file)
        self.save_path_button.grid(row=4, column=0, padx=5, pady=4)         

        self.save_path_label = Label(compress_tab, text = "", font=label_font)    
        self.save_path_label.grid(row=4, column=1, padx=5, pady=4)                            

        self.compress_button = Button(compress_tab, text="Compress", command=self.compress)
        self.compress_button.grid(row=5, column=1, padx=5, pady=4)

        self.file_button = Button(decompress_tab, text="File input", command=self.choose_compressed_file)
        self.file_button.grid(row=1, padx=2, pady=4)

        self.compressed_path_label = Label(decompress_tab, text = "", font=label_font)    
        self.compressed_path_label.grid(row=1, column=1, padx=5, pady=4)    

        self.save_image_button = Button(decompress_tab, text="Choose save file", command=self.choose_save_img_file)
        self.save_image_button.grid(row=2, padx=5, pady=4)     

        self.save_image_label = Label(decompress_tab, text = "", font=label_font)    
        self.save_image_label.grid(row=2, column=1, padx=5, pady=4)

        self.decompress_button = Button(decompress_tab, text="Decompress", command=self.decompress)
        self.decompress_button.grid(row=3, column=1, padx=5, pady=4)

        self.img_output = ImageTk.PhotoImage("RGB", (300, 300))
        self.panel_img_output = Label(decompress_tab, image=self.img)
        self.panel_img_output.grid(row=4, column=1)

        self.resolution_output_label = Label(decompress_tab, text="Resolution : ", font=label_font)
        self.resolution_output_label.grid(row=5, padx=2, pady=4)

        self.image_size_output_label = Label(decompress_tab, text="Size : ", font=label_font)
        self.image_size_output_label.grid(row=6, padx=2, pady=5)
                                    

    def set_selected_compression_algo(self, event):
        self.compressor.set_current_compressor_by_index(
            self.compression_algorithm.current())

    def set_selected_decompression_algo(self, event):
        self.compressor.set_current_compressor_by_index(
            self.decompression_algorithm.current())

    def compress(self):
        if self.img_file:                        
            output_size = self.compressor.encode(self.img_file, self.save_path)
            ratio = os.stat(self.img_file).st_size / output_size
            message = "Compress successfully\nSize of output file : " + str(output_size) + "bytes\nCompression ratio : " + str(ratio)
            if ratio < 1.0:
                message += "\nBad compress"
            tkinter.messagebox.showinfo("Title", message)
        
    def decompress(self):
        if self.compressed_file:
            output_img_size, resolution = self.compressor.decode(self.compressed_file, self.output_img_file)
            row, col = resolution[0], resolution[1]
            img = ImageTk.PhotoImage(Image.open(self.output_img_file).resize((int(col / 15), int(row / 15)), Image.ANTIALIAS))
            self.panel_img_output.configure(image=img)
            self.panel_img_output.image = img
            self.resolution_output_label.config(text="Resolution : " + str(col) + " x " + str(row))
            self.image_size_output_label.config(text="Size : " + str(output_img_size) + " bytes")


    def choose_save_file(self):       
        my_format = [("LZW", "*.lzw"), ("Huffman", "*.huff"), ("JPEG", "*.jpg")]
        file = tkinter.filedialog.asksaveasfilename(filetypes= my_format, title="Save file as...")
        if len(file) > 0:
            self.save_path = file
            self.save_path_label.config(text=self.save_path)
        else:
            self.save_path = None

    def choose_compressed_file(self):
        file = tkinter.filedialog.askopenfilename()
        if len(file) > 0:
            self.compressed_file = file
            self.compressed_path_label.config(text=file)
        else:
            self.compressed_file = None

    def choose_save_img_file(self):
        my_format = [("BMP", "*.bmp"), ("JPEG", "*.jpg"), ("PNG", "*.png")]
        file = tkinter.filedialog.asksaveasfilename(filetypes= my_format, title="Save file as...")
        if len(file) > 0:
            self.output_img_file = file
            self.save_image_label.config(text=file)
        else:
            self.output_img_file = None

    def choose_image(self):
        self.img_file = tkinter.filedialog.askopenfilename()    
        row, col, _ = cv2.imread(self.img_file).shape    
        img = ImageTk.PhotoImage(Image.open(self.img_file).resize((int(col / 15), int(row / 15)), Image.ANTIALIAS))        
        self.panel.configure(image=img)
        self.panel.image = img
        self.resolution_label.config(text="Resolution : " + str(col) + " x " + str(row))
        self.image_size_label.config(text="Size : " + str(os.stat(self.img_file).st_size) + " bytes")


    def run(self):
        self.root.mainloop()


if __name__ == '__main__':    
    gui = GUI()
    gui.run()
