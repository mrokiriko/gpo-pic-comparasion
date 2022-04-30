from PIL import Image
import imagehash
from os import listdir
from os.path import isfile, join
import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import random
import numpy as np
from matplotlib import pyplot as plt
import time

folder_path = 'data_exact'  # одно и то же изображения


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
    return abs(hash_one - hash_two) <= 20
    # return False
    # return random.random() < 0.5


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


def are_same_template(img, template, threshold=0.8, resize_iterations=1, step=0.01):
    img_height = np.size(img, 0)
    img_width = np.size(img, 1)

    percent = 0.2
    template = get_template(template, percent)

    template_height = np.size(template, 0)
    template_width = np.size(template, 1)

    # print('template itself width and height:')
    # print(template_width, template_height)

    # во сколько раз надо уменьшить шаблон или итогове изображение
    scalability_h = img_height / (template_height / (2 * percent))
    scalability_w = img_width / (template_width / (2 * percent))
    # print('scalability_h', scalability_h)
    # print('scalability_w', scalability_w)

    scalability = scalability_h

    if scalability_h > 1:
        dim = (int(img_width / scalability), int(img_height / scalability))
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    else:
        dim = (int(template_width * scalability), int(template_height * scalability))
        template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)

    for i in range(0, resize_iterations):
        # print('iteration #', i)

        template_height = np.size(template, 0)
        template_width = np.size(template, 1)
        dim = (int(template_width * (1 - step * i)), int(template_height * (1 - step * i)))
        template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)

        # cv2.imshow('in this image', img)
        # cv2.waitKey(0)
        # cv2.imshow('search for this template', template)
        # cv2.waitKey(0)

        if are_same_iteration(img, template, threshold):
            return True

    return False


def are_same_iteration(img, template, threshold=0.8):
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    # print(res)

    loc = np.where(res >= threshold)
    # print('loc')
    # print(loc)

    found_templates = 0

    # сюда занесем первую точку найденного шаблона
    first_x = -1
    first_y = -1

    # здесь хранятся максимальные отступы от первой точки
    x_diff = 0
    y_diff = 0

    w, h = template.shape[::-1]

    for pt in zip(*loc[::-1]):
        # cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        found_templates += 1

        if first_y < 0 and first_x < 0:
            first_x = pt[0]
            first_y = pt[1]

        x_change = abs(first_x - pt[0])
        y_change = abs(first_y - pt[1])

        if x_change > x_diff:
            x_diff = x_change

        if y_change > y_diff:
            y_diff = y_change

        if found_templates > 20:
            break

    img_height = np.size(img, 0)
    img_width = np.size(img, 1)

    # в пределеах скольких пикселей мы считаем что все шаблоны найдены корректно
    x_tolerance = img_width * 0.03
    y_tolerance = img_height * 0.03

    # print('found_templates:', found_templates)
    # print('x_diff:', x_diff)
    # print('y_diff:', y_diff)
    # print('x_tolerance:', x_tolerance)
    # print('y_tolerance:', y_tolerance)

    if found_templates > 0 and x_diff <= x_tolerance and y_diff <= y_tolerance:
        return True

    return False


def get_template(template, percent):
    template_height = np.size(template, 0)
    template_width = np.size(template, 1)

    if template_height < template_width:
        square_half_side = int(template_height * percent / 2)
    else:
        square_half_side = int(template_width * percent / 2)

    # вырезать квадрат посередине изображения-шаблона
    height_from = int((template_height / 2) - square_half_side)
    height_to = int((template_height / 2) + square_half_side)
    width_from = int((template_width / 2) - square_half_side)
    width_to = int((template_width / 2) + square_half_side)

    # print('img.shape')
    # print(img.shape)
    # print(height_from, height_to, height_to - height_from)
    # print(width_from, width_to, width_to - width_from)
    #
    # print('img width and height:')
    # print(img_width, img_height)
    # print('template image width and height:')
    # print(template_width, template_height)

    return template[height_from:height_to, width_from:width_to]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # pic_packs = get_pics_from_folder(folder_path)
    # pics = get_all_pics_from('exact_pics')

    folder = 'exact_pics'
    # pics = listdir(folder)
    # pics = listdir(folder)[70:95]
    # pics = listdir(folder)[:20]
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
    pics_data = {}

    categories = {}

    start_time = time.time()

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

            hash_diff = abs(hashes[pic_a] - hashes[pic_b])

            comparisons += 1

            found_same = False
            if hash_diff <= 10:
                found_same = True
            elif hash_diff < 30:

                min_size = 400

                if pic_a not in pics_data:
                    pic = cv2.imread('exact_pics/' + pic_a, 0)

                    pic_height = np.size(pic, 0)
                    pic_width = np.size(pic, 1)
                    if pic_height > min_size:
                        scalability = pic_height / min_size
                        dim = (int(pic_width / scalability), int(pic_height / scalability))
                        pic = cv2.resize(pic, dim, interpolation=cv2.INTER_AREA)

                    pics_data[pic_a] = pic

                if pic_b not in pics_data:
                    pic = cv2.imread('exact_pics/' + pic_b, 0)

                    pic_height = np.size(pic, 0)
                    pic_width = np.size(pic, 1)
                    if pic_height > min_size:
                        scalability = pic_height / min_size
                        dim = (int(pic_width / scalability), int(pic_height / scalability))
                        pic = cv2.resize(pic, dim, interpolation=cv2.INTER_AREA)

                    pics_data[pic_b] = pic

                template = pics_data[pic_a]
                img = pics_data[pic_b]

                found_same = are_same_template(img, template, 0.9, 8, 0.02)  # Template Matching

            stat = [0, 0, 0, 0]
            if category_a in categories:
                stat = categories[category_a]

            if are_same:
                same_comparisons += 1

                if are_same == found_same:
                    right_same_comparisons += 1
                    stat[0] += 1
                    print('S A M E', pic_a, pic_b)
                else:
                    wrong_same_comparisons += 1
                    stat[1] += 1
            else:
                difference_comparisons += 1

                if are_same == found_same:
                    right_difference_comparisons += 1
                    stat[2] += 1
                else:
                    wrong_difference_comparisons += 1
                    stat[3] += 1

            if are_same == found_same:
                right_comparisons += 1
            else:
                wrong_comparisons += 1
                print(pic_a, pic_b)
                print('Are they same?', are_same)
                print('Did program found they are same?', found_same)
                print('Hash difference is', hash_diff)
                # print(pic_a, hashes[pic_a])
                # print(pic_b, hashes[pic_b])

            categories[category_a] = stat

    for key, category in categories.items():
        print(key + '\t' + str(category[0]) + '\t' + str(category[1]) + '\t' + str(category[2]) + '\t' + str(category[3]))

    # print('comparisons were made:', comparisons)
    # print('right ones:', right_comparisons)
    # print('wrong ones:', wrong_comparisons)

    print("--- %s seconds ---" % (time.time() - start_time))

    print('')
    print('сравнения похожих изображений:', same_comparisons)
    print('угадал что два изображения похожи:', right_same_comparisons)
    print('не угадал что два изображения похожи:', wrong_same_comparisons)

    print('')
    print('сравнения разных изображений:', difference_comparisons)
    print('угадал что изображения разные:', right_difference_comparisons)
    print('не угадал что изображения разные:', wrong_difference_comparisons)
