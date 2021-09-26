from PIL import Image
import imagehash
from os import listdir
from os.path import isfile, join
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys

folder_path = 'compare_pics'


# def are_similar_phash(pic_a, pic_b, folder_path):
#     # ToDo try out other image hashing
#     # https://pypi.org/project/ImageHash/
#     pic_a_path = folder_path + '/' + pic_a
#     pic_b_path = folder_path + '/' + pic_b
#     pic_a_hash = get_imagehash(pic_a_path)
#     pic_b_hash = get_imagehash(pic_b_path)
#     # return pic_a_hash == pic_b_hash
#     return abs(pic_a_hash - pic_b_hash) < 10


def are_similar_hashes(hash_one, hash_two):
    # return hash_one == hash_two
    return abs(hash_one - hash_two) <= 20


def are_similar_hists(histogram_a, histogram_b):
    r = cv2.compareHist(histogram_a, histogram_b, cv2.HISTCMP_BHATTACHARYYA)
    # print(r)
    # print(r < -100)
    return r <= 0.1


def get_imagehash(pic):
    return imagehash.phash(Image.open(pic))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def is_pic(path):
    if '.DS_Store' in path:
        return False
    return isfile(path)


def get_hist(pic):
    # img = cv2.imread(folder_path + '/' + pic, 0)
    img = cv2.imread(pic, 0)
    return cv2.calcHist([img], [0], None, [256], [0, 256])


def get_pic_hashes(pics, hash_function):
    pics_hists = []
    for index, pic in enumerate(pics):
        pic_path = folder_path + '/' + pic
        # print(pic_path)
        # pics_hashes.append(get_imagehash(pic_path))
        pics_hists.append(hash_function(pic_path))
    return pics_hists


def compare_pics_by(hashes, cmp_func):

    similar_count = 0
    similar_comparisons = 0

    different_count = 0
    different_comparisons = 0

    for index_a, hash_a in enumerate(hashes):
        # print(index_a, '-', pic_a)
        for index_b, hash_b in enumerate(hashes):

            # изображение распределены в папке по 4 штуки
            are_really_similar = index_a // 4 == index_b // 4
            are_similar_by_hash = cmp_func(hash_a, hash_b)

            print(pics[index_a], '/', pics[index_b], '(', are_really_similar, ',', are_similar_by_hash, ')')

            if are_really_similar:
                similar_comparisons += 1
                if are_similar_by_hash:
                    similar_count += 1
            else:
                different_comparisons += 1
                if not are_similar_by_hash:
                    different_count += 1

            # if are_really_similar == are_similar_by_hash:
            #     comparisons_correct += 1

    return [similar_count, similar_comparisons, different_count, different_comparisons]


def output_correctness(arr):

    similar_count = arr[0]
    similar_comparisons = arr[1]

    different_count = arr[2]
    different_comparisons = arr[3]

    correct_percent = round(similar_count / similar_comparisons * 100 * 100) / 100
    print('было сравнено', similar_comparisons, 'похожих изображений.',
          similar_count, 'из них были правильно угаданы', correct_percent, '%')

    correct_percent = round(different_count / different_comparisons * 100 * 100) / 100
    print('было сравнено', different_comparisons, 'не похожих друг на друга изображений.',
          different_count, 'из них были правильно угаданы', correct_percent, '%')


def get_pics_from_folder(path_to_folder):
    # Похожие изображения в папке должны идти друг за другом блоками по 4
    all_pics = [f for f in listdir(path_to_folder) if is_pic(join(path_to_folder, f))]
    all_pics.sort()
    # all_pics = all_pics[0:8]
    return all_pics


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    if len(sys.argv) >= 2 and sys.argv[1] == 'phash':
        method = 'способ pHash'
        hashing_function = get_imagehash
        compare_function = are_similar_hashes
    else:
        method = 'способ Кристины (гистограммы)'
        hashing_function = get_hist
        compare_function = are_similar_hists

    pics = get_pics_from_folder(folder_path)

    pics_hashes = get_pic_hashes(pics, hashing_function)

    res = compare_pics_by(pics_hashes, compare_function)

    output_correctness(res)

    print('использовался', method)
