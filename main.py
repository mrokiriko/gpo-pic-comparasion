from PIL import Image
import imagehash
from os import listdir
from os.path import isfile, join
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import random
import time
import distance

folder_path = 'data_exact' # одно и то же изображения
# folder_path = 'data_sensual' # смысловое


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
    # print(distance.hamming(hash_one, hash_two))
    # return distance.hamming(hash_one, hash_two) <= 10
    return abs(hash_one - hash_two) <= 20
    # return False
    # return random.random() < 0.5


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


class Pic:

    hist = ''
    ihash = ''

    def __init__(self, name, pack_name):
        self.name = name
        self.pack_name = pack_name

    def set_hist(self):
        self.hist = get_hist(folder_path + '/' + self.pack_name + '/' + self.name)

    def set_ihash(self):
        self.ihash = get_imagehash(folder_path + '/' + self.pack_name + '/' + self.name)


def get_pics_from_folder(path_to_folder):
    pic_packs = listdir(path_to_folder)
    print(pic_packs)

    all_pics = []
    for pack in pic_packs:
        path_to_pack = path_to_folder + '/' + pack
        pics_in_pack = listdir(path_to_pack)
        for pic_in_pack in pics_in_pack:
            pic_obj = Pic(pic_in_pack, pack)
            pic_obj.set_hist()
            pic_obj.set_ihash()
            all_pics.append(pic_obj)

    # all_pics = [f for f in listdir(path_to_folder) if is_pic(join(path_to_folder, f))]

    # all_pics.sort()
    # all_pics = all_pics[0:8]
    return all_pics


def get_all_pics_from(path_to_folder):
    pic_packs = listdir(path_to_folder)
    print(pic_packs)

    all_pics = []
    for pack in pic_packs:
        path_to_pack = path_to_folder + '/' + pack
        pics_in_pack = listdir(path_to_pack)
        for pic_in_pack in pics_in_pack:
            pic_obj = Pic(pic_in_pack, pack)
            pic_obj.set_hist()
            pic_obj.set_ihash()
            all_pics.append(pic_obj)

    # all_pics = [f for f in listdir(path_to_folder) if is_pic(join(path_to_folder, f))]

    # all_pics.sort()
    # all_pics = all_pics[0:8]
    return all_pics


# Press the green button in the gutter to run the script.
if __name__ == '__main__':


    # pic_packs = get_pics_from_folder(folder_path)
    #pics = get_all_pics_from('exact_pics')

    folder = 'exact_pics'
    pics = listdir(folder)

    comparisons = 0
    right_comparisons = 0
    wrong_comparisons = 0

    same_comparisons = 0
    right_same_comparisons = 0
    wrong_same_comparisons = 0
    difference_comparisons = 0
    right_difference_comparisons = 0
    wrong_difference_comparisons = 0

    hashes = {}

    pic_a = get_imagehash('exact_pics/spidermanpoint_04.jpg')
    pic_b = get_imagehash('exact_pics/spidermanpoint_01.jpg')

    print('hash for spidermanpoint_04', str(pic_a))
    print('hash for spidermanpoint_01', str(pic_b))

    hash_diff = abs(pic_a - pic_b)
    found_same = hash_diff <= 20
    print(hash_diff)
    print('Images are different')


    # img = cv2.imread('exact_pics/spidermanpoint_04.jpg', 0)
    # template = cv2.imread('exact_pics/spidermanpoint_01.jpg', 0)

    exit()

    #
    # for i in range(1, 21):
    #     hashes = {}
    #     categories = {}
    #
    #     start_time = time.time()

    for pic_a in pics:
        for pic_b in pics:

            category_a = pic_a.split("_")[0]
            category_b = pic_b.split("_")[0]
            are_same = category_a == category_b

            if pic_a not in hashes:
                #hashes[pic_a] = get_hist(folder + '/' + pic_a) # Гистограммы
                hashes[pic_a] = get_imagehash(folder + '/' + pic_a) # pHash

            if pic_b not in hashes:
                #hashes[pic_b] = get_hist(folder + '/' + pic_b) # Гистограммы
                hashes[pic_b] = get_imagehash(folder + '/' + pic_b) # pHash

            comparisons += 1
            # found_same = are_similar_hists(hashes[pic_a], hashes[pic_b]) # Гистограммы
            # found_same = are_similar_hashes(hashes[pic_a], hashes[pic_b]) # pHash

            # print(distance.hamming(hash_one, hash_two))
            # return distance.hamming(hash_one, hash_two) <= 10

            hash_diff = abs(hashes[pic_a] - hashes[pic_b])
            found_same = hash_diff <= 20


            # hash_diff = distance.hamming(str(hashes[pic_a]), str(hashes[pic_b]))
            # found_same = hash_diff <= 11

            stat = [0, 0, 0, 0]
            # if category_a in categories:
            #     stat = categories[category_a]

            if are_same:
                same_comparisons += 1

                if are_same == found_same:
                    right_same_comparisons += 1
                    stat[0] += 1
                    # print(pic_a, pic_b, hash_diff)
                else:
                    wrong_same_comparisons += 1
                    stat[1] += 1
                    print(pic_a, pic_b, hash_diff)
            else:
                difference_comparisons += 1

                if are_same == found_same:
                    right_difference_comparisons += 1
                    stat[2] += 1
                else:
                    wrong_difference_comparisons += 1
                    stat[3] += 1


            # if are_same == found_same:
            #     right_comparisons += 1
            # else:
            #     wrong_comparisons += 1
            #     #print(pic_a, hashes[pic_a])
            #     #print(pic_b, hashes[pic_b])

            # categories[category_a] = stat

        # print("Прогон #" + str(i))
        # print("--- %s seconds ---" % (time.time() - start_time))


    # for key, category in categories.items():
    #     print(key + '\t' + str(category[0]) + '\t' + str(category[1]) + '\t' + str(category[2]) + '\t' + str(category[3]))
    #
    # print(categories)
    #
    # # print('comparisons were made:', comparisons)
    # # print('right ones:', right_comparisons)
    # # print('wrong ones:', wrong_comparisons)
    #
    # print('')
    # print('сравнения похожих изображений:', same_comparisons)
    # print('угадал что два изображения похожи:', right_same_comparisons)
    # print('не угадал что два изображения похожи:', wrong_same_comparisons)
    #
    # print('')
    # print('сравнения разных изображений:', difference_comparisons)
    # print('угадал что изображения разные:', right_difference_comparisons)
    # print('не угадал что изображения разные:', wrong_difference_comparisons)

    exit()

    print(pic_packs)

    for pic in pic_packs:
        print(pic.name, '|', pic.pack_name)

    for pic_a in pic_packs:
        for pic_b in pic_packs:
            if pic_a.name == pic_b.name and pic_a.pack_name == pic_b.pack_name:
                continue

            result_hist = are_similar_hists(pic_a.hist, pic_b.hist)
            result_ihash = are_similar_hashes(pic_a.ihash, pic_b.ihash)
            print(pic_a.name, 'and', pic_b.name, '[', pic_a.pack_name, ',', pic_b.pack_name, ']', 'IS', result_hist, 'or', result_ihash)
            if result_hist or result_ihash:
                print('COCK')


    # pics_hashes = get_pic_hashes(pics, hashing_function)
    #
    # res = compare_pics_by(pics_hashes, compare_function)
    #
    # output_correctness(res)
    #
    # print('использовался', method)
