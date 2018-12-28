from dahuffman import HuffmanCodec

import numpy as np
import cv2
import pickle
import sys


def save_obj(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def load_obj(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


class Predictive(object):
    def __init__(self, _num_rows):
        '''Params:
        - num_rows: numbers of rows for prediction,
        '''
        self.num_rows = _num_rows
        pass

    def predImg(self, img, output):
        '''Get prediction image. (not including first m rows)'''
        ret = np.empty((img.shape[0], img.shape[1]))
        ret[:self.num_rows, :] = img[:self.num_rows, :]
        # sum_px_val_rows = np.sum(self.img, axis=1)
        # total_px_val = np.sum(sum_px_val_rows[:self.num_rows])
        # num_px = self.num_rows * self.img.shape[1]

        # for row in range(self.num_rows, self.img.shape[0]):
        #     for col in range(0, self.img.shape[1]):
        #         if col != 0:
        #             total_px_val += self.img[row, col]
        #             num_px += 1
        #         ret[row - self.num_rows, col] = round(total_px_val / num_px)

        #     total_px_val -= sum_px_val_rows[row - self.num_rows]
        for row in range(self.num_rows, img.shape[0]):
            for col in range(0, img.shape[1]):
                if col == 0:
                    ret[row,
                        col] = round((ret[row - 1, col] + ret[row - 1, col + 1]) / 2)
                else:
                    ret[row, col] = round((
                        ret[row, col - 1] + ret[row - 1, col - 1] +
                        ret[row - 1, col]) / 3)

        return ret[self.num_rows:, :]

    def predErrImg(self, img):
        '''Get prediction error image. (not including first m rows)'''
        ret = img[self.num_rows:, :] - self.predImg(img)

        unique, counts = np.unique(ret, return_counts=True)

        return ret

    def encode(self, img):
        # encode first m rows
        data = []
        for row in range(0, self.num_rows):
            data += img[row].tolist()
        codec_first_rows = HuffmanCodec.from_data(data)
        encoded_first_rows = codec_first_rows.encode(data)

        # encode remain rows
        prediction_error_img = self.predErrImg(img)
        data = []
        for row in range(0, img.shape[0] - self.num_rows):
            data += prediction_error_img[row].tolist()
        codec_remaining_rows = HuffmanCodec.from_data(data)
        encoded_remaining_rows = codec_remaining_rows.encode(data)

        # return {'height': self.img.shape[0],
        #         'width': self.img.shape[1],
        #         'codec_first_rows': codec_first_rows,
        #         'encoded_first_rows': encoded_first_rows,
        #         'codec_remaining_rows': codec_remaining_rows,
        #         'encoded_remaining_rows': encoded_remaining_rows}
        return (img.shape[0], img.shape[1], codec_first_rows, encoded_first_rows, codec_remaining_rows, encoded_remaining_rows)

    def decode(self, encoded_img):
        # Load encoded image
        # height = encoded_img['height']
        # width = encoded_img['width']
        # codec_first_rows = encoded_img['codec_first_rows']
        # encoded_first_rows = encoded_img['encoded_first_rows']
        # codec_remaining_rows = encoded_img['codec_remaining_rows']
        # encoded_remaining_rows = encoded_img['encoded_remaining_rows']
        height, width, codec_first_rows, encoded_first_rows, codec_remaining_rows, encoded_remaining_rows = encoded_img

        # Symbol Decoder
        first_rows = codec_first_rows.decode(encoded_first_rows)
        first_rows = np.array(first_rows).reshape(-1, width)

        remaining_rows = codec_remaining_rows.decode(encoded_remaining_rows)
        remaining_rows = np.array(remaining_rows).reshape(-1, width)

        img = np.zeros((height, width))

        img[:first_rows.shape[0], :] = first_rows

        # Predictor
        for row in range(first_rows.shape[0], height):
            for col in range(0, width):
                if col == 0:
                    img[row, col] = round(
                        (img[row - 1, col] + img[row - 1, col + 1]) / 2)
                else:
                    img[row, col] = round(
                        (img[row, col - 1] + img[row - 1, col] + img[row - 1, col - 1]) / 3)
        img[first_rows.shape[0]:, :] += remaining_rows

        return img.astype(np.uint8)

    def compress(self, input_path, output_path):
        img = cv2.imread(input_path)
        if len(img.shape) == 2:
            encoded_img = self.encode(img)
        else:
            encoded_img = [self.encode(img[:, :, 0]), self.encode(img[:, :, 1]),
                    self.encode(img[:, :, 2])]
        save_obj(encoded, output_path)

    def extract(self, input_path, output_path):
        encoded_img = cv2.imread(input_path)
        try:
            save_obj(self.decode(encoded_img), output_path)
        except ValueError:
            save_obj(np.stack((self.decode(encoded_img[0]), self.decode(encoded_img[1]), self.decode(encoded_img[2])), axis=-1), output_path)


if __name__ == '__main__':
    # img = cv2.imread('./Images/lena512color.tiff')
    # jpg_ls = Predictive(1)
    # encoded_img = jpg_ls.compress(img)
    # save_obj(encoded_img, './EncodedImages/lena512color.tiff.encoded')

    # encoded_img = load_obj('./EncodedImages/lena512color.tiff.encoded')
    # decoded_img = jpg_ls.extract(encoded_img)

    # print(decoded_img.shape)
    # cv2.imshow('figure', decoded_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    command = sys.argv[1]
    file_path = sys.argv[2]

    jpg_ls = Predictive(1)
    if command == 'encode':
        img = cv2.imread(file_path)
        encoded_img = jpg_ls.compress(img)
        save_obj(encoded_img, file_path + '.compressed')
    elif command == 'decode':
        encoded_img = load_obj(file_path)
        decoded_img = jpg_ls.extract(encoded_img)
