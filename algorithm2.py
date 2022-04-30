from PIL import Image
import imagehash
from os import listdir
import cv2
import sys
import numpy as np

# New Template + imagehash algorithm


def get_imagehash(pic):
    return imagehash.phash(Image.open(pic))


def are_same_template(img, template, threshold, resize_iterations, step):
    img_height = np.size(img, 0)
    img_width = np.size(img, 1)

    percent = 0.2
    template = get_template(template, percent)

    template_height = np.size(template, 0)
    template_width = np.size(template, 1)

    scalability = img_height / (template_height / (2 * percent))

    if scalability > 1:
        dim = (int(img_width / scalability), int(img_height / scalability))
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    else:
        dim = (int(template_width * scalability), int(template_height * scalability))
        template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)

    for i in range(0, resize_iterations):

        template_height = np.size(template, 0)
        template_width = np.size(template, 1)
        dim = (int(template_width * (1 - step * i)), int(template_height * (1 - step * i)))
        template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)

        if are_same_iteration(img, template, threshold):
            return True

    return False


def are_same_iteration(img, template, threshold):
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

    for pt in zip(*loc[::-1]):
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

    return template[height_from:height_to, width_from:width_to]


if __name__ == '__main__':

    # folder = 'exact_pics'
    # threshold_a = 10
    # threshold_b = 30
    # threshold_c = 0.9
    # resize_iterations = 8
    # step = 0.02
    # min_size = 400

    folder = sys.argv[1]
    threshold_a = float(sys.argv[2])
    threshold_b = float(sys.argv[3])
    threshold_c = float(sys.argv[4])
    resize_iterations = int(sys.argv[5])
    step = float(sys.argv[6])
    min_size = int(sys.argv[7])

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

    for pic_a in pics:
        for pic_b in pics:
            category_a = pic_a.split("_")[0]
            category_b = pic_b.split("_")[0]
            are_same = category_a == category_b

            if pic_a not in hashes:
                hashes[pic_a] = get_imagehash(folder + '/' + pic_a)

            if pic_b not in hashes:
                hashes[pic_b] = get_imagehash(folder + '/' + pic_b)

            hash_diff = abs(hashes[pic_a] - hashes[pic_b])

            comparisons += 1

            found_same = False
            if hash_diff <= threshold_a:
                found_same = True
            elif hash_diff < threshold_b:

                if pic_a not in pics_data:
                    pic = cv2.imread(folder + '/' + pic_a, 0)

                    pic_height = np.size(pic, 0)
                    pic_width = np.size(pic, 1)
                    if pic_height > min_size:
                        scalability = pic_height / min_size
                        dim = (int(pic_width / scalability), int(pic_height / scalability))
                        pic = cv2.resize(pic, dim, interpolation=cv2.INTER_AREA)

                    pics_data[pic_a] = pic

                if pic_b not in pics_data:
                    pic = cv2.imread(folder + '/' + pic_b, 0)

                    pic_height = np.size(pic, 0)
                    pic_width = np.size(pic, 1)
                    if pic_height > min_size:
                        scalability = pic_height / min_size
                        dim = (int(pic_width / scalability), int(pic_height / scalability))
                        pic = cv2.resize(pic, dim, interpolation=cv2.INTER_AREA)

                    pics_data[pic_b] = pic

                template = pics_data[pic_a]
                img = pics_data[pic_b]

                found_same = are_same_template(img, template, threshold_c, resize_iterations, step)

            stat = [0, 0, 0, 0]
            if category_a in categories:
                stat = categories[category_a]

            if are_same:
                same_comparisons += 1

                if are_same == found_same:
                    right_same_comparisons += 1
                    stat[0] += 1
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

    print('сравнения похожих изображений:', same_comparisons)
    print('угадал что два изображения похожи:', right_same_comparisons)
    print('не угадал что два изображения похожи:', wrong_same_comparisons)
    print('')
    print('сравнения разных изображений:', difference_comparisons)
    print('угадал что изображения разные:', right_difference_comparisons)
    print('не угадал что изображения разные:', wrong_difference_comparisons)
